from temporalio import workflow
from temporalio.workflow import signal_method

class BrowserTaskWorkflow:
    @workflow.run
    async def run(self, task_id: str, plan: dict):
        for step in plan.get("steps", []):
            # call activity to run step
            await workflow.execute_activity(
                "execute_step", task_id, step, start_to_close_timeout=300
            )
