from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.temporal_client import start_browser_task

router = APIRouter()

class TaskRequest(BaseModel):
    steps: list

@router.post("/")
async def create_task(req: TaskRequest):
    if not req.steps:
        raise HTTPException(status_code=400, detail="steps required")
    task_id = await start_browser_task(req.dict())
    return {"task_id": task_id}
