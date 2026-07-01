# RCA Engine — Architecture Guide

This document describes how the RCA Engine FastAPI service is organized and how to extend it correctly. Read this before adding endpoints, business logic, or shared helpers.

---

## What this service is

**RCA Engine** is a standalone HTTP API service for root-cause analysis workflows. It exposes versioned REST endpoints under `/api/v1`. Clients (internal tools, other Mercury services, or the Mercury SDK) call it over HTTP.

The codebase follows a **layered architecture**: each folder has one job. Code belongs in exactly one layer. If you are unsure where something goes, use the decision table in [Where does this code go?](#where-does-this-code-go).

---

## Repository layout

```
rca-engine/
├── app/
│   ├── main.py              # App factory — wires FastAPI + routers only
│   ├── config.py            # Environment-backed settings (no business logic)
│   ├── routes/              # HTTP: paths, methods, status codes, OpenAPI metadata
│   ├── controllers/         # Per-request orchestration — thin glue between HTTP and services
│   ├── services/            # Business logic, domain rules, external integrations
│   ├── schemas/             # Pydantic models — API contracts (request/response bodies)
│   └── utils/               # Stateless, reusable helpers with no domain ownership
├── main.py                  # Process entry — starts uvicorn
├── requirements.txt
├── .env.example
└── arch.md                  # This file
```

---

## Request flow

Every HTTP request must follow this path. **Do not skip layers or call upward.**

```
Client
  │
  ▼
routes/          ← defines URL, method, response_model, dependencies
  │
  ▼
controllers/     ← receives validated input, calls service(s), returns schema
  │
  ▼
services/        ← implements RCA rules, calls DB/APIs, builds domain result
  │
  ▼
schemas/         ← shapes data in/out of the API (and between controller ↔ service)
```

Optional cross-cutting use:

```
utils/           ← pure helpers used by services (or occasionally controllers)
config.py        ← read by services/main; never imported from routes
```

### Example: `GET /api/v1/health`

| Layer        | File                              | Responsibility                          |
|-------------|-----------------------------------|-----------------------------------------|
| Route       | `app/routes/health.py`            | Register `GET /health`, set `response_model` |
| Controller  | `app/controllers/health_controller.py` | Call `HealthService`, return `HealthResponse` |
| Service     | `app/services/health_service.py`  | Build health payload from config        |
| Schema      | `app/schemas/health.py`           | Define `HealthResponse` shape           |

---

## Layer responsibilities

### `app/routes/`

**Purpose:** HTTP surface area only.

**Belongs here:**
- `APIRouter` instances and route decorators (`@router.get`, `@router.post`, …)
- Path parameters, query parameters, request body binding via schemas
- `response_model`, `status_code`, `tags`, `summary`, `dependencies`
- One-line delegation to a controller method

**Does not belong here:**
- Business logic or RCA algorithms
- Database or external API calls
- Data transformation beyond what FastAPI/Pydantic do automatically
- Reusable helper functions (use `utils/`)

```python
# Correct
@router.post("/incidents/{incident_id}/analyze", response_model=AnalyzeResponse)
def analyze_incident(incident_id: str, body: AnalyzeRequest) -> AnalyzeResponse:
    return controller.analyze(incident_id, body)
```

---

### `app/controllers/`

**Purpose:** Orchestrate a single use case per endpoint — no heavy logic.

**Belongs here:**
- Mapping route inputs → service method arguments
- Calling one or more services for one HTTP action
- Returning a schema instance (or raising HTTP-aware exceptions if you add them later)
- Light coordination (e.g. call service A then service B for one endpoint)

**Does not belong here:**
- FastAPI decorators or router setup
- SQL queries, LLM prompts, file I/O, or long algorithms
- Pydantic model definitions (use `schemas/`)
- Generic string/date/parsing helpers (use `utils/`)

Controllers should stay **thin**. If a controller method grows past ~15–20 lines, move logic into a service.

---

### `app/services/`

**Purpose:** All business and domain behavior for RCA.

**Belongs here:**
- Root-cause analysis workflows
- Calls to databases, message queues, LLMs, Mercury SDK, third-party APIs
- Domain validation that is not purely HTTP-shaped
- Aggregating data from multiple sources into a result
- Building and returning schema instances (or domain objects later converted to schemas)

**Does not belong here:**
- `@router` decorators or HTTP status code decisions
- FastAPI `Depends` or `Request` objects
- Pydantic models that only describe HTTP JSON shape with no logic (use `schemas/`)
- Generic utilities unrelated to RCA (use `utils/`)

Services may import `config`, `schemas`, and `utils`. They must **not** import from `routes` or `controllers`.

---

### `app/schemas/`

**Purpose:** Data contracts — what the API accepts and returns.

**Belongs here:**
- Pydantic `BaseModel` classes for request bodies, response bodies, nested DTOs
- Field validation, examples, and documentation metadata for OpenAPI
- Shared shapes used by both routes (binding) and services (construction)

**Does not belong here:**
- Business rules (“if severity is critical, escalate…”) — that is `services/`
- HTTP routing or controller orchestration
- Functions that perform I/O or side effects

Keep schemas **dumb**: structure and validation only.

---

### `app/utils/`

**Purpose:** Small, stateless, reusable functions with no feature ownership.

**Belongs here:**
- Date/time formatting, safe JSON helpers, ID generators
- Shared parsing, retry wrappers, logging helpers
- Pure functions used across multiple services

**Does not belong here:**
- Feature-specific RCA logic (belongs in a `*_service.py`)
- HTTP or FastAPI types
- Classes that hold state or connect to external systems (belongs in `services/`)

If a util is only used by one service and encodes domain knowledge, prefer keeping it in that service until a second consumer appears.

---

### `app/config.py`

**Purpose:** Centralized settings from environment variables.

**Belongs here:**
- `pydantic-settings` `BaseSettings` class
- Defaults and env var names (`API_PREFIX`, `DEBUG`, API keys, DB URLs)

**Does not belong here:**
- Business logic
- Imports from `services`, `controllers`, or `routes`

---

### `app/main.py` and root `main.py`

**`app/main.py`** — creates the FastAPI app, mounts `api_router` with `settings.api_prefix`. No feature logic.

**`main.py` (repo root)** — runs uvicorn. No application logic.

---

## Where does this code go?

| You need to…                              | Put it in…        |
|------------------------------------------|-------------------|
| Add a new URL / HTTP method              | `routes/`         |
| Wire request → service for one endpoint  | `controllers/`    |
| Implement RCA or integration logic       | `services/`       |
| Define JSON request/response shape       | `schemas/`        |
| Share a generic helper across features   | `utils/`          |
| Add an env var or app-wide setting       | `config.py`       |
| Register a new router on the app         | `routes/__init__.py` + `app/main.py` (only if prefix changes) |

---

## Adding a new feature (checklist)

Use a consistent **feature slice** name, e.g. `incident`, `analysis`, `report`.

### 1. Schema — `app/schemas/<feature>.py`

Define request and response models.

```python
# app/schemas/incident.py
class AnalyzeRequest(BaseModel): ...
class AnalyzeResponse(BaseModel): ...
```

Export from `app/schemas/__init__.py` if the team re-exports public models.

### 2. Service — `app/services/<feature>_service.py`

Implement behavior. Return schema instances (or data the controller maps to schemas).

```python
# app/services/incident_service.py
class IncidentService:
    def analyze(self, incident_id: str, request: AnalyzeRequest) -> AnalyzeResponse:
        ...
```

### 3. Controller — `app/controllers/<feature>_controller.py`

Inject or construct the service; expose one method per route action.

```python
# app/controllers/incident_controller.py
class IncidentController:
    def __init__(self, incident_service: IncidentService | None = None) -> None:
        self._incident_service = incident_service or IncidentService()

    def analyze(self, incident_id: str, request: AnalyzeRequest) -> AnalyzeResponse:
        return self._incident_service.analyze(incident_id, request)
```

### 4. Routes — `app/routes/<feature>.py`

Register endpoints; delegate to the controller only.

```python
# app/routes/incident.py
router = APIRouter(prefix="/incidents")
controller = IncidentController()

@router.post("/{incident_id}/analyze", response_model=AnalyzeResponse)
def analyze_incident(incident_id: str, body: AnalyzeRequest) -> AnalyzeResponse:
    return controller.analyze(incident_id, body)
```

### 5. Register router — `app/routes/__init__.py`

```python
from app.routes.incident import router as incident_router

api_router.include_router(incident_router, tags=["incidents"])
```

### 6. Utils (optional)

Only if you extracted a **generic** helper used by the service.

---

## Dependency rules (import direction)

Allowed:

```
routes       → controllers, schemas
controllers  → services, schemas
services     → schemas, utils, config
utils        → stdlib / third-party only (no routes/controllers/services)
config       → pydantic-settings only
main         → routes, config
```

**Forbidden:**

- `services` → `controllers` or `routes`
- `schemas` → `services` or `controllers`
- `utils` → any app layer above services
- Putting business logic in `routes` or `schemas` to “save a file”

This keeps the graph acyclic and testable: services can be unit-tested without HTTP.

---

## Anti-patterns (do not do this)

| Anti-pattern | Why it is wrong | Correct place |
|-------------|-----------------|---------------|
| SQL/LLM calls inside a route | Couples HTTP to infrastructure | `services/` |
| Large algorithm in a controller | Hard to test and reuse | `services/` |
| Pydantic models defined inside routes | Contracts scattered | `schemas/` |
| `APIRouter` inside a service | Service depends on HTTP | `routes/` |
| Feature logic in `utils/` | Utils become a junk drawer | `services/` |
| Settings read in every file via `os.getenv` | Inconsistent defaults | `config.py` |
| Skipping controller and calling service from route | Breaks orchestration layer for multi-step flows | `controllers/` |

---

## Configuration and running

| Item | Location / value |
|------|------------------|
| Env template | `.env.example` |
| Settings class | `app/config.py` |
| API prefix | `API_PREFIX` (default `/api/v1`) |
| Interactive docs | `http://localhost:8000/docs` |
| OpenAPI JSON | `http://localhost:8000/openapi.json` |

```powershell
cd rca-engine
pip install -r requirements.txt
python main.py
# or: uvicorn app.main:app --reload
```

---

## Testing guidance (when you add tests)

Mirror the layers:

| Layer | Test focus |
|-------|------------|
| `services/` | Unit tests with mocked I/O — highest value |
| `controllers/` | Thin tests — service mocked |
| `routes/` | Integration/API tests with `TestClient` |
| `schemas/` | Validation edge cases |
| `utils/` | Pure function tests |

Do not test business rules only through HTTP if you can test the service directly.

---

## Naming conventions

| Artifact | Pattern | Example |
|----------|---------|---------|
| Route module | `<feature>.py` | `incident.py` |
| Controller class | `<Feature>Controller` | `IncidentController` |
| Service class | `<Feature>Service` | `IncidentService` |
| Schema module | `<feature>.py` | `incident.py` |
| Request/response models | `<Action>Request`, `<Action>Response` | `AnalyzeRequest` |

One feature typically spans four files (schema, service, controller, route) with the same base name.

---

## Summary

1. **Routes** speak HTTP and nothing else.
2. **Controllers** orchestrate one request → one use case.
3. **Services** own RCA and all side effects.
4. **Schemas** define data shapes only.
5. **Utils** hold generic helpers, not features.
6. **Imports flow downward** — never from services up to routes.

Following this structure keeps endpoints consistent, makes code review straightforward, and lets teammates add features without putting functions in the wrong place.
