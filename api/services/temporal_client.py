import os
import uuid
from typing import Any, Dict

from temporalio.client import Client

from orchestrator.workflows.browser_task import BrowserTaskWorkflow

TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")

_client: Client | None = None


async def get_temporal_client() -> Client:
    """Return a shared Temporal client instance.

    Temporal clients are safe to reuse across requests and should generally be long-lived.
    """
    global _client
    if _client is None:
        _client = await Client.connect(TEMPORAL_ADDRESS)
    return _client


async def start_browser_task(plan: Dict[str, Any]) -> str:
    """Start a new browser task workflow and return its public task id."""
    task_id = str(uuid.uuid4())
    client = await get_temporal_client()
    await client.start_workflow(
        BrowserTaskWorkflow.run,
        task_id,
        plan,
        id=f"workflow-{task_id}",
        task_queue="browser-task-queue",
    )
    return task_id


async def get_task_status(task_id: str) -> Dict[str, Any]:
    """Query the workflow for its current status.

    This is used by the API to power a real-time task UI via polling or websockets.
    """
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id=f"workflow-{task_id}")
    return await handle.query(BrowserTaskWorkflow.get_state)
