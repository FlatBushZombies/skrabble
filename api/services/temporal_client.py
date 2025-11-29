import uuid
from temporalio.client import Client
from orchestrator.workflows.browser_task import BrowserTaskWorkflow

async def start_browser_task(plan: dict) -> str:
    task_id = str(uuid.uuid4())
    client = await Client.connect("localhost:7233")
    await client.start_workflow(
        BrowserTaskWorkflow.run,
        task_id,
        plan,
        id=f"workflow-{task_id}",
        task_queue="browser-task-queue"
    )
    return task_id
