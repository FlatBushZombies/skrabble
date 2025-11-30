# Testing Skrabble AI with a Real-time Task UI

This guide explains how to exercise the end-to-end stack (API → Temporal → worker)
and how to hook a simple real-time UI onto it using polling.

## 1. Start the stack locally

From the project root:

```bash
# build and run Temporal, Postgres, API, orchestrator and worker
docker compose up --build
```

This will expose:

- Temporal on `localhost:7233`
- API on `http://localhost:8000`

> Note: If you are running Temporal elsewhere, set `TEMPORAL_ADDRESS` in the
> environment for the API and orchestrator containers.

## 2. Create a task via the API

Send a POST request with a list of steps. For example, using `curl`:

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "steps": [
      { "action": "goto", "url": "https://example.org" },
      { "action": "screenshot", "path": "example.png" }
    ]
  }'
```

The API responds with:

```json
{"task_id": "<uuid>"}
```

Save this `task_id`; the real-time UI will use it to query status.

## 3. Poll task status (for a real-time UI)

The API exposes a status endpoint backed by a Temporal workflow query:

```http
GET /tasks/{task_id}
```

Example with `curl`:

```bash
curl http://localhost:8000/tasks/<task_id>
```

Example response:

```json
{
  "task_id": "<task_id>",
  "status": "running",
  "current_step_index": 0,
  "total_steps": 2,
  "last_error": null
}
```

The `status` field transitions through:

- `pending` – workflow created but not yet executing
- `running` – actively executing steps
- `completed` – all steps finished successfully
- `failed` – an unhandled error occurred in one of the steps

A real-time UI can poll this endpoint every 1–2 seconds and update a progress
bar or step list based on `current_step_index` and `total_steps`.

## 4. Wiring up a simple browser UI (example)

In any frontend (React, Vue, vanilla JS, etc.), you can:

1. Call `POST /tasks` to create a task.
2. Start a timer (e.g. `setInterval`) that calls `GET /tasks/{task_id}`.
3. Update the UI with the latest `status` and `current_step_index`.
4. Stop polling when `status` is `completed` or `failed`.

Pseudocode:

```js
async function createTask(plan) {
  const res = await fetch("http://localhost:8000/tasks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(plan),
  });
  const { task_id } = await res.json();
  return task_id;
}

function startStatusPolling(taskId, onUpdate) {
  const timer = setInterval(async () => {
    const res = await fetch(`http://localhost:8000/tasks/${taskId}`);
    const status = await res.json();
    onUpdate(status);

    if (status.status === "completed" || status.status === "failed") {
      clearInterval(timer);
    }
  }, 1000);

  return () => clearInterval(timer);
}
```

You can adapt this pattern for WebSockets or server-sent events if you prefer a
push-based model. The backend status API remains the same.

## 5. Inspecting workflows in Temporal Web UI

Temporal also exposes its own Web UI (port depends on your Temporal setup). Once
the stack is running, you can:

1. Open the Temporal Web UI in your browser.
2. Search for workflows with IDs matching `workflow-<task_id>`.
3. Inspect the event history to see each step execution and any errors.

This is useful for debugging when the API status reports `failed` or when
something unexpected happens during execution.

## 6. Common troubleshooting tips

- **`task not found` (404)**: The `task_id` is invalid or the workflow has not
  yet started. Double-check the ID returned from `POST /tasks`.
- **`failed to query task status` (502)**: The API cannot reach Temporal or the
  query handler. Ensure Temporal is running and `TEMPORAL_ADDRESS` is correct.
- **Browser worker errors**: Look at the logs for the `worker` service in Docker
  Compose; Playwright errors will surface there and in the Temporal workflow
  history.
