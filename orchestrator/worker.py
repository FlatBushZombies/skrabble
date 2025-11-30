import os

from temporalio.client import Client
from temporalio.worker import Worker

from orchestrator.workflows.browser_task import BrowserTaskWorkflow
from worker.runner import execute_step

TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")


async def main() -> None:
    """Entry point for the Temporal worker process.

    This worker listens on the `browser-task-queue` queue for workflow and activity tasks.
    """
    client = await Client.connect(TEMPORAL_ADDRESS)
    worker = Worker(
        client,
        task_queue="browser-task-queue",
        workflows=[BrowserTaskWorkflow],
        activities=[execute_step],
    )
    await worker.run()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
