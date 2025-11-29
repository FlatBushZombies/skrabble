from fastapi import FastAPI
from routes.tasks import router as tasks_router

app = FastAPI(title="Skrabble API")
app.include_router(tasks_router, prefix="/tasks")

@app.get("/health")
def health():
    return {"status": "ok"}
