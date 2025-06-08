import asyncio
from typing import Union

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel

from online.application.agents import get_agent
from online.config import settings

load_dotenv()


class TaskRequest(BaseModel):
    """Request model for the agent task."""

    task: str


class TaskResponse(BaseModel):
    """Response model for the agent task."""

    result: str
    success: bool = True
    error: Union[str, None] = None


app = FastAPI()
agent = get_agent()

# API Key authentication
api_key_header = APIKeyHeader(name="Leo-API-Key")


async def get_api_key(api_key: str = Security(api_key_header)):
    """Validate API key"""
    expected_key = getattr(settings, 'LEO_SK', None)
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key not configured on server"
        )
    
    if api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key


@app.post("/v1/chat", response_model=TaskResponse, tags=["chat"])
async def run_agent_task(
    request: TaskRequest, 
    api_key: str = Depends(get_api_key)
) -> TaskResponse:
    """
    Run a task on the agent and get the result.
    
    This endpoint runs the agent task asynchronously and returns the result.
    Requires a valid API key in the Leo-API-Key header.
    """
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, agent.run, request.task)

        if isinstance(result, str):
            result_str = result
        else:
            result_str = str(result)

        return TaskResponse(result=result_str, success=True)

    except Exception as e:
        return TaskResponse(result="", success=False, error=str(e))


@app.get("/")
async def read_root():
    """Health check endpoint"""
    return {"message": "Leo API is running."}


@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "Leo API",
        "agent_name": agent.name,
        "agent_max_steps": agent.max_steps
    }