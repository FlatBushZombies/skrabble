# Skrabble AI — Architecture


## Overview
Skrabble AI executes long-running AI-driven browser tasks using a durable orchestrator (Temporal), a lightweight API (FastAPI), and browser automation workers (Playwright).


**Core goals**:
- Durable execution for tasks that may take minutes or hours
- Resilient to crashes and restarts
- Clear separation of concerns for maintainability


## Components


1. **API (FastAPI)**
- Receives tasks from users
- Validates and schedules tasks by starting Temporal workflows
- Exposes task status endpoints


2. **Temporal Orchestrator**
- Durable workflows + activities
- Responsible for checkpointing progress and retrying failed steps


3. **Browser Worker (Playwright)**
- Executes browser steps inside containers
- Produces artifacts (screenshots, HTML dumps)


4. **Storage & Artifacts**
- Postgres (Temporal requires persistence)
- S3-compatible storage for artifacts


## Data Flow
User → FastAPI → Temporal workflow → Activity call → Browser Worker → Artifacts stored → Workflow checkpoints state


## Reliability Guarantees
Temporal ensures deterministic replay and persistent event history, enabling safe retries and crash recovery.


## Diagram (sequence)


```mermaid
sequenceDiagram
participant User
participant API
participant Temporal
participant Worker
participant Storage


User->>API: POST /tasks (plan)
API->>Temporal: Start workflow
Temporal->>Worker: Execute step 1 (activity)
Worker->>Storage: Upload artifact
Worker-->>Temporal: Activity result
Temporal->>Worker: Execute step 2
Temporal-->>API: Emit status via callback/webhook
Temporal->>Temporal: Checkpoint