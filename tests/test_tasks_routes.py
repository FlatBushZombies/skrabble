from typing import Any, Dict
from pathlib import Path
import sys

from fastapi.testclient import TestClient

# Ensure project root (containing the `api` package) is on sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from api.main import app
from api.routes import tasks
from api.routes.tasks import WorkflowNotFoundError


client = TestClient(app)


def test_create_task_valid(monkeypatch) -> None:
    """POST /tasks/ with a valid plan should return a task_id and call the Temporal client helper."""

    recorded: Dict[str, Any] = {}

    async def fake_start_browser_task(plan: Dict[str, Any]) -> str:  # type: ignore[override]
        recorded["plan"] = plan
        return "task-123"

    monkeypatch.setattr(tasks, "start_browser_task", fake_start_browser_task)

    payload = {"steps": [{"action": "goto", "url": "https://example.com"}]}

    response = client.post("/tasks/", json=payload)

    assert response.status_code == 200
    assert response.json() == {"task_id": "task-123"}
    assert recorded["plan"]["steps"][0]["url"] == "https://example.com"


def test_create_task_missing_steps() -> None:
    """POST /tasks/ with an empty steps list should be rejected with 400."""

    response = client.post("/tasks/", json={"steps": []})

    assert response.status_code == 400
    body = response.json()
    assert body["detail"] == "steps required"


def test_read_task_status_ok(monkeypatch) -> None:
    """GET /tasks/{task_id} should proxy the status from Temporal client helper."""

    async def fake_get_task_status(task_id: str) -> Dict[str, Any]:  # type: ignore[override]
        return {"task_id": task_id, "status": "running"}

    monkeypatch.setattr(tasks, "get_task_status", fake_get_task_status)

    response = client.get("/tasks/abc123")

    assert response.status_code == 200
    assert response.json() == {"task_id": "abc123", "status": "running"}


def test_read_task_status_not_found(monkeypatch) -> None:
    """GET /tasks/{task_id} should map WorkflowNotFoundError to a 404 response."""

    async def fake_get_task_status(task_id: str) -> Dict[str, Any]:  # type: ignore[override]
        raise WorkflowNotFoundError("not found")

    monkeypatch.setattr(tasks, "get_task_status", fake_get_task_status)

    response = client.get("/tasks/missing")

    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "task not found"
