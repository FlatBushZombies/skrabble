from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator

try:  # Temporal SDK 1.19 and earlier
    from temporalio.client import WorkflowNotFoundError  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover - compatibility for newer SDK versions
    class WorkflowNotFoundError(Exception):
        """Fallback definition used when Temporal SDK no longer exposes WorkflowNotFoundError.

        The API layer relies on this type solely for distinguishing 404 vs 502
        when querying workflow status; actual Temporal errors are translated in
        the temporal_client helpers.
        """

        pass

from ..services.temporal_client import get_task_status, start_browser_task

router = APIRouter()


class Step(BaseModel):
    """Single browser automation step.

    This is intentionally minimal; real deployments can extend this schema.
    """

    action: Literal["goto", "click", "type", "screenshot"] = Field(..., description="Type of browser action to perform")
    url: Optional[str] = Field(None, description="Target URL for 'goto' actions")
    selector: Optional[str] = Field(None, description="CSS selector for 'click' or 'type' actions")
    text: Optional[str] = Field(None, description="Text to type for 'type' actions")
    path: Optional[str] = Field(None, description="Optional screenshot path override for 'screenshot' actions")

    @model_validator(mode='before')
    @classmethod
    def validate_required_fields(cls, data: Any) -> Any:
        action = data.get("action")
        if action == "goto" and not data.get("url"):
            raise ValueError("'url' is required for 'goto' action")
        if action in {"click", "type"} and not data.get("selector"):
            raise ValueError("'selector' is required for 'click' and 'type' actions")
        if action == "type" and data.get("text") is None:
            raise ValueError("'text' is required for 'type' action")
        return data


class TaskRequest(BaseModel):
    steps: List[Step] = Field(..., description="Ordered list of browser automation steps to execute")


@router.post("/", summary="Create a new browser task")
async def create_task(req: TaskRequest) -> Dict[str, str]:
    if not req.steps:
        raise HTTPException(status_code=400, detail="steps required")

    task_id = await start_browser_task(req.dict())
    return {"task_id": task_id}


@router.get("/{task_id}", summary="Get current status for a task")
async def read_task_status(task_id: str) -> Dict[str, Any]:
    """Return the current status of a task for use by real-time UIs.

    The response is backed by a Temporal workflow query and is safe to call frequently.
    """
    try:
        status = await get_task_status(task_id)
    except WorkflowNotFoundError as exc:  # type: ignore[misc]
        raise HTTPException(status_code=404, detail="task not found") from exc
    except Exception as exc:  # pragma: no cover - defensive guardrail
        raise HTTPException(status_code=502, detail="failed to query task status") from exc

    return status
