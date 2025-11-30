from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from temporalio import workflow

STEP_TIMEOUT_SECONDS = 300


@workflow.defn
class BrowserTaskWorkflow:
    """Canonical workflow for executing a sequence of browser steps.

    The workflow keeps a small piece of state that can be queried by a real-time UI.
    """

    task_id: str = ""
    plan: Dict[str, Any] = field(default_factory=dict)  # type: ignore[assignment]
    current_step_index: int = 0
    total_steps: int = 0
    status: str = "pending"  # pending -> running -> completed / failed / cancelled
    last_error: Optional[str] = None

    @workflow.run
    async def run(self, task_id: str, plan: Dict[str, Any]) -> None:
        self.task_id = task_id
        self.plan = plan

        steps: List[Dict[str, Any]] = list(plan.get("steps", []))
        self.total_steps = len(steps)
        self.status = "running"

        for idx, step in enumerate(steps):
            self.current_step_index = idx
            try:
                await workflow.execute_activity(
                    "execute_step",
                    task_id,
                    step,
                    start_to_close_timeout=STEP_TIMEOUT_SECONDS,
                )
            except Exception as exc:  # pragma: no cover - surfaced via query
                self.status = "failed"
                self.last_error = str(exc)
                raise

        self.status = "completed"

    @workflow.query
    def get_state(self) -> Dict[str, Any]:
        """Return lightweight state for polling from the API/UI layer."""
        return {
            "task_id": self.task_id,
            "status": self.status,
            "current_step_index": self.current_step_index,
            "total_steps": self.total_steps,
            "last_error": self.last_error,
        }
