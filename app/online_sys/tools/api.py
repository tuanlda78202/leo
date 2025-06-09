import ast
import asyncio
import json
import re
import sys
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security.api_key import APIKeyHeader
from opik.integrations.langchain import OpikTracer
from pydantic import BaseModel

from online import opik_utils
from online.application.agents import get_agent
from online.config import settings

load_dotenv()


class TaskRequest(BaseModel):
    """Request model for the agent task."""

    task: str


class ExecutionStep(BaseModel):
    """Model for agent execution steps."""

    step_number: int
    title: str
    description: str
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    observations: Optional[str] = None
    duration: Optional[float] = None
    timestamp: Optional[float] = None


class TaskResponse(BaseModel):
    """Response model for the agent task."""

    result: str
    success: bool = True
    error: Optional[str] = None
    execution_steps: List[ExecutionStep] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events for the API."""
    # Startup code
    opik_utils.configure()

    yield

    # Shutdown code
    try:
        opik_tracer = OpikTracer()
        opik_tracer.flush()
    except Exception as e:
        print(f"Error flushing Opik tracer: {e}")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api_key_header = APIKeyHeader(name="Leo-API-Key")


async def get_api_key(api_key: str = Security(api_key_header)):
    """Validate API key"""
    expected_key = getattr(settings, "LEO_SK", None)
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key not configured on server",
        )

    if api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key"
        )
    return api_key


class AgentCapture:
    def __init__(self):
        self.steps = []
        self.events = []
        self.step_counter = 0
        self.capturing = False
        self.current_observations = []
        self.current_step = None

    def add_event(self, event_type: str, data: Dict[str, Any]):
        """Add event to the list"""
        self.events.append({"type": event_type, "data": data, "timestamp": time.time()})

    def add_step(
        self,
        title: str,
        description: str,
        tool_name: str = None,
        tool_args: Dict = None,
    ):
        """Add a new step"""
        self.step_counter += 1
        step = {
            "step_number": self.step_counter,
            "title": title,
            "description": description,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "timestamp": time.time(),
            "duration": None,
            "observations": None,
        }
        self.steps.append(step)
        self.add_event("step", step)
        self.current_step = step
        return step

    def update_observations(self, observations: str):
        """Update current step with observations"""
        if self.current_step:
            self.current_step["observations"] = observations
            self.add_event(
                "step_update",
                {
                    "step_number": self.current_step["step_number"],
                    "observations": observations,
                },
            )


class LogInterceptor:
    """Intercept stdout to capture agent logs"""

    def __init__(self, capture: AgentCapture):
        self.capture = capture
        self.original_stdout = sys.stdout
        self.buffer = []
        self.in_observations = False
        self.observations_buffer = []

    def write(self, text):
        self.original_stdout.write(text)

        lines = text.strip().split("\n")
        for line in lines:
            if line.strip():
                self.process_line(line.strip())

    def flush(self):
        self.original_stdout.flush()

    def parse_tool_arguments(self, args_str: str) -> Dict[str, Any]:
        """Parse tool arguments from string"""
        try:
            args = ast.literal_eval(args_str)
            return args if isinstance(args, dict) else {"raw": args_str}
        except (ValueError, SyntaxError):
            try:
                # Try to parse as JSON
                args = json.loads(args_str)
                return args if isinstance(args, dict) else {"raw": args_str}
            except (ValueError, json.JSONDecodeError):
                # If all else fails, try to extract query manually
                query_match = re.search(r"'query':\s*'([^']*)'", args_str)
                if query_match:
                    return {"query": query_match.group(1)}

                # Or try double quotes
                query_match = re.search(r'"query":\s*"([^"]*)"', args_str)
                if query_match:
                    return {"query": query_match.group(1)}

                return {"raw": args_str}

    def process_line(self, line: str):
        """Process a single log line"""
        # Detect tool calls - handle both with and without box characters
        clean_line = re.sub(r"[│╰╮─]", "", line).strip()

        if "Calling tool:" in clean_line:
            tool_match = re.search(
                r"Calling tool: '([^']+)' with arguments: (.+)", clean_line
            )
            if tool_match:
                tool_name = tool_match.group(1)
                args_str = tool_match.group(2).strip()

                # Parse arguments
                tool_args = self.parse_tool_arguments(args_str)

                # Extract description based on tool type
                if tool_name == "web_search" and "query" in tool_args:
                    description = f"Searching for: {tool_args['query']}"
                elif tool_name == "iam":
                    description = "Checking system capabilities"
                elif tool_name == "final_answer":
                    description = "Finalizing the response"
                elif "query" in tool_args:
                    description = f"Using {tool_name}: {tool_args['query']}"
                else:
                    description = f"Using {tool_name} tool"

                self.capture.add_step(
                    title=f"Calling tool: {tool_name}",
                    description=description,
                    tool_name=tool_name,
                    tool_args=tool_args,
                )

        # Detect observations
        elif "Observations:" in clean_line:
            self.in_observations = True
            self.observations_buffer = [clean_line]

        elif self.in_observations:
            # Continue collecting observations until we hit a separator or new step
            if (
                line.startswith("━")
                or line.startswith("[Step")
                or line.startswith("Step")
                or "Duration" in line
            ):
                # End of observations
                if self.observations_buffer:
                    obs_text = "\n".join(self.observations_buffer)
                    self.capture.update_observations(obs_text)
                self.in_observations = False
                self.observations_buffer = []
            else:
                self.observations_buffer.append(clean_line)


async def stream_agent_execution_simple(task: str) -> AsyncGenerator[str, None]:
    """Simple streaming of agent execution"""

    capture = AgentCapture()

    try:
        # Initial step
        capture.add_step("Starting Agent", f"Processing query: {task}")
        yield f"data: {json.dumps(capture.events[-1])}\n\n"

        # Set up log interception
        interceptor = LogInterceptor(capture)
        original_stdout = sys.stdout

        try:
            # Intercept stdout
            sys.stdout = interceptor

            # Run agent
            agent = get_agent()

            # Simulate real-time by yielding events periodically
            loop = asyncio.get_event_loop()

            # Run agent in executor
            result_future = loop.run_in_executor(None, agent.run, task)

            # Poll for new events while agent runs
            last_event_count = len(capture.events)

            while not result_future.done():
                await asyncio.sleep(0.5)  # Check every 500ms

                # Yield any new events
                if len(capture.events) > last_event_count:
                    for event in capture.events[last_event_count:]:
                        yield f"data: {json.dumps(event)}\n\n"
                    last_event_count = len(capture.events)

            # Get final result
            result = await result_future

            # Yield any remaining events
            if len(capture.events) > last_event_count:
                for event in capture.events[last_event_count:]:
                    yield f"data: {json.dumps(event)}\n\n"

        finally:
            # Restore stdout
            sys.stdout = original_stdout

        # Final completion step
        capture.add_step("Agent Complete", "Finished processing")
        yield f"data: {json.dumps(capture.events[-1])}\n\n"

        # Send final result
        response_data = {
            "result": str(result),
            "success": True,
            "execution_steps": [
                ExecutionStep(**step).model_dump() for step in capture.steps
            ],
        }
        yield f"data: {json.dumps({'type': 'result', 'data': response_data})}\n\n"

    except Exception as e:
        # Send error
        error_data = {
            "result": "",
            "success": False,
            "error": str(e),
            "execution_steps": [
                ExecutionStep(**step).model_dump() for step in capture.steps
            ],
        }
        yield f"data: {json.dumps({'type': 'error', 'data': error_data})}\n\n"

    finally:
        # Always send done signal
        yield f"data: {json.dumps({'type': 'done'})}\n\n"


@app.post("/v1/chat/stream", tags=["chat"])
async def stream_agent_task(
    request: TaskRequest, api_key: str = Depends(get_api_key)
) -> StreamingResponse:
    """
    Stream agent execution in real-time
    """
    return StreamingResponse(
        stream_agent_execution_simple(request.task),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@app.post("/v1/chat", response_model=TaskResponse, tags=["chat"])
async def run_agent_task(
    request: TaskRequest, api_key: str = Depends(get_api_key)
) -> TaskResponse:
    """
    Run a task on the agent and get the result.

    This endpoint runs the agent task asynchronously and returns the result.
    Requires a valid API key in the Leo-API-Key header.
    """
    try:
        agent = get_agent()
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, agent.run, request.task)

        return TaskResponse(result=str(result), success=True)

    except Exception as e:
        return TaskResponse(result="", success=False, error=str(e))


@app.get("/")
async def read_root():
    """Health check endpoint"""
    return {"message": "Leo API is running."}


@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    agent = get_agent()
    return {
        "status": "healthy",
        "service": "Leo API",
        "agent_name": agent.name,
        "agent_max_steps": agent.max_steps,
    }
