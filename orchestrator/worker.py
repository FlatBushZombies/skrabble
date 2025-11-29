from temporalio.worker import Worker
from temporalio.client import Client

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="browser-task-queue",
        workflows=[BrowserTaskWorkflow],
        activities=["worker.runner.execute_step"]
    )
    await worker.run()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
