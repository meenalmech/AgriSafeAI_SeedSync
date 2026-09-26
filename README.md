# AgriSafe AI

## AI Farm Task Safety & Risk Prevention System

**Tagline:** Before You Work, Know the Risk.

AgriSafe AI is a Python based farm safety decision support application. A farmer selects a planned agricultural task and the system combines task, crop, weather, chemical, worker exposure and PPE information to produce an explainable safety decision.

The final safety decision is produced by a deterministic risk engine. AI and retrieval capabilities are used for document understanding, task understanding and explanations, but an LLM does not control the final safety gate.

## Final hackathon architecture

```text
Farmer Web UI
     |
     v
FastAPI Application
     |
     +--> Data Aggregation --> Weather / Farm / Chemical / Worker
     |
     +--> Business Logic
     |
     +--> Deterministic Risk Engine
     |       |
     |       +--> Hard safety rules
     |       +--> Risk scoring
     |       +--> Decision policy
     |
     +--> AI / RAG Layer
     |       |
     |       +--> SDS / safety document extraction
     |       +--> Knowledge retrieval
     |       +--> Explanation generation
     |
     +--> Decision Output
             |
             +--> PROCEED
             +--> MODIFY
             +--> DELAY
             +--> AVOID

SQLite SQL Database
     |
     +--> Assessment history
     +--> Audit information
     +--> Reference data
```

## What is included

* FastAPI Python backend
* Browser based farmer UI
* SQLite SQL database using SQLAlchemy
* Deterministic safety rules and explainable risk scoring
* Four decisions: PROCEED, MODIFY, DELAY, AVOID
* Safer time window search
* Open-Meteo live weather integration
* Explicit demo weather fallback
* Chemical reference data
* PDF and text document extraction
* Local RAG style knowledge retrieval
* Assessment history
* Docker and Docker Compose
* Healthcheck
* Automated risk engine tests
* Sample API requests

## Why SQLite for this version

SQLite is the selected SQL database for the hackathon solution because it is simple to deploy, requires no separate database server, works well for a single application instance, and keeps the demonstration portable.

The database file is stored in `runtime/agrisafe.db` when running locally and in a persistent Docker volume when running with Docker Compose.

For a future multi-instance production deployment, the database layer can be replaced by another SQL database without changing the application domain model because the application already uses SQLAlchemy.

## Quick start on Windows

1. Install Python 3.11 or newer.
2. Open PowerShell in this folder.
3. Create a virtual environment:

```powershell
python -m venv .venv
```

4. Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

5. Install dependencies:

```powershell
pip install -r requirements.txt
```

6. Start the application:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. Open:

`http://localhost:8000`

8. API documentation:

`http://localhost:8000/docs`

The SQLite database will be created automatically as `agrisafe.db` in the application directory for this local run.

## Quick start on macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker deployment

Install Docker Desktop, then run:

```bash
docker compose up --build
```

Open `http://localhost:8000`.

The SQLite database is persisted in the Docker volume named `agrisafe_data`.

To stop the application:

```bash
docker compose down
```

To stop it without deleting the database volume, use the command above without `-v`.

To remove the database as well:

```bash
docker compose down -v
```

## Demo scenario

Use this scenario during the hackathon presentation:

* Crop: Chili
* Task: Pesticide spraying
* Planned time: 2:00 PM
* Temperature: 34 C
* Humidity: 82 percent
* Wind: 18 km/h
* Rain probability: 70 percent
* Worker exposure: 4 hours
* PPE: incomplete
* Chemical: Demo Pesticide X

Expected result: elevated risk with a DELAY or AVOID decision and clear reasons.

Then use the safer time feature and demonstrate how lower wind, lower temperature and lower rain probability can change the risk profile.

## API examples

Health:

```bash
curl http://localhost:8000/api/health
```

Assessment:

```bash
curl -X POST http://localhost:8000/api/assessments \
  -H "Content-Type: application/json" \
  -d @docs/sample_assessment.json
```

Safer windows:

```bash
curl -X POST http://localhost:8000/api/safer-windows \
  -H "Content-Type: application/json" \
  -d @docs/sample_safer_window.json
```

Knowledge search:

```bash
curl "http://localhost:8000/api/knowledge/search?q=pesticide%20PPE%20wind"
```

## Important safety design

The application follows this pattern:

```text
Inputs
  -> deterministic rules
  -> risk score
  -> safety decision gate
  -> AI generated explanation
```

The LLM is not allowed to invent or override the safety decision. Chemical requirements must ultimately be verified against the current product label and SDS. Prototype thresholds must be validated by qualified agricultural and HSE professionals before real operational use.

## Project structure

```text
agrisafe_ai/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── schemas.py
│   ├── api.py
│   ├── risk_engine.py
│   ├── weather.py
│   ├── knowledge.py
│   ├── explanations.py
│   └── seed.py
├── data/
│   ├── chemicals.json
│   └── knowledge.json
├── docs/
│   ├── DEPLOYMENT.md
│   ├── sample_assessment.json
│   └── sample_safer_window.json
├── static/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── tests/
│   └── test_risk_engine.py
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
└── requirements.txt
```

## Production hardening roadmap

1. Validate every risk threshold with qualified HSE and agricultural experts.
2. Replace demo chemical records with verified current label and SDS records.
3. Add rule versioning and evidence references.
4. Add authentication and RBAC.
5. Add signed or immutable audit records.
6. Add a production vector database for approved safety documents.
7. Put the LLM behind a policy controlled explanation service.
8. Add monitoring for weather freshness, rule changes and API failures.
9. Add automated SQLite backups and restore testing for the deployed MVP.
10. For multiple application instances, move the SQLAlchemy database URL to a managed SQL database and keep the domain model unchanged.

## Disclaimer

This is a hackathon decision support prototype. It is not a certified occupational safety system and must not replace product labels, SDS documents, professional risk assessments, farm SOPs, medical advice or applicable laws. Real deployment requires formal safety validation and field testing.
