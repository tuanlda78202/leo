import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from online.application.agents import get_agent

load_dotenv()


class TaskRequest(BaseModel):
    """Request model for the agent task."""

    task: str


class TaskResponse(BaseModel):
    """Response model for the agent task."""

    result: Any


app = FastAPI()
agent = get_agent()


@app.post("/v1/chat", response_model=TaskResponse)
def run_agent_task(request: TaskRequest):
    """
    Run a task on the agent and get the result.
    """
    result = agent.run(request.task)
    return TaskResponse(result=result)


@app.get("/")
def read_root():
    return {"message": "Leo API is running."}
