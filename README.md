# RCA Engine

> A modular Root Cause Analysis (RCA) engine for AI applications built with FastAPI.

The RCA Engine analyzes AI application telemetry (traces, metrics, evaluations, and metadata) to identify the most probable root cause behind failures, performance degradation, hallucinations, latency spikes, and retrieval issues.

The project follows a clean layered architecture that makes it easy to extend with new analyzers, statistical models, data sources, and APIs.

---

## Features

- Modular Root Cause Analysis pipeline
- FastAPI REST API
- Layered architecture
- Health monitoring endpoint
- Environment-based configuration
- Easily extensible service layer
- Ready for AI observability integrations
- Designed for statistical and LLM-assisted RCA

---

## Architecture

```
Client
   │
   ▼
Routes
   │
   ▼
Controllers
   │
   ▼
Services
   │
   ▼
Schemas
```

Cross-cutting modules:

```
Config
Utils
```

The architecture keeps responsibilities separated, making the codebase scalable and maintainable.

---

## Repository Structure

```
rca-engine/
│
├── app/
│   ├── controllers/
│   ├── routes/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   ├── config.py
│   └── main.py
│
├── main.py
├── requirements.txt
├── .env.example
├── arch.md
└── README.md
```

---

## Technology Stack

- Python 3.11+
- FastAPI
- Pydantic
- Uvicorn

Future planned integrations include:

- MongoDB
- Neo4j
- Qdrant
- LangSmith
- Langfuse
- OpenTelemetry
- Phoenix
- Arize AI

---

## Installation

Clone the repository

```bash
git clone https://github.com/itsharsh01/rca-engine.git

cd rca-engine
```

Create a virtual environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

Copy the example environment file.

```bash
cp .env.example .env
```

Example configuration

```env
APP_NAME=RCA Engine
APP_VERSION=0.1.0
DEBUG=True
API_PREFIX=/api/v1
```

---

## Running the Application

Start the API server

```bash
python main.py
```

or

```bash
uvicorn app.main:app --reload
```

The server starts at

```
http://localhost:8000
```

---

## API Documentation

Interactive Swagger UI

```
http://localhost:8000/docs
```

ReDoc

```
http://localhost:8000/redoc
```

---

## Available Endpoints

### Health Check

```
GET /api/v1/health
```

Example Response

```json
{
    "status": "healthy",
    "service": "RCA Engine",
    "version": "0.1.0"
}
```

---

## Project Layers

### Routes

Defines API endpoints.

Responsible for:

- URL routing
- Request validation
- Response models
- OpenAPI documentation

---

### Controllers

Coordinates incoming requests.

Responsible for:

- Input orchestration
- Calling services
- Returning responses

---

### Services

Contains business logic.

Responsible for:

- RCA algorithms
- External integrations
- Statistical analysis
- Data processing

---

### Schemas

Pydantic models for

- Requests
- Responses
- Validation

---

### Utils

Reusable helper functions shared across the application.

---

## Development Workflow

```
Feature
   ↓
Route
   ↓
Controller
   ↓
Service
   ↓
Schema
```

Business logic should remain inside the **service layer**.

---

## Future Roadmap

- Statistical anomaly detection
- AI trace analysis
- Retrieval quality analysis
- LLM latency analysis
- Prompt failure detection
- Cost optimization analysis
- Hallucination detection
- Multi-agent RCA
- Knowledge graph reasoning
- Automated RCA report generation
- Dashboard support
- AI observability connectors
- Incident timeline reconstruction

---

## Contributing

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/new-feature
```

3. Commit your changes

```bash
git commit -m "Add new analyzer"
```

4. Push the branch

```bash
git push origin feature/new-feature
```

5. Open a Pull Request

---

## Project Status

Current Version

```
v0.1.0
```

Status

> Active Development

---

## License

This project is intended for internal development and research. Add an appropriate open-source license before public production use.

---

## Author

Developed by the Mercury AI Team.
