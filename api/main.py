from fastapi import FastAPI
from .routes.tasks import router as tasks_router

app = FastAPI(title="Skrabble API")
app.include_router(tasks_router, prefix="/tasks")


@app.get("/health")
def health() -> dict:
    """Liveness probe endpoint used by infrastructure and tests."""
    return {"status": "ok"}
