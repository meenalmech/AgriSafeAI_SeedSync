# AgriSafe AI Final Deployment Guide

## 1. Recommended hackathon setup

Use:

* Python 3.11+
* FastAPI
* SQLAlchemy
* SQLite SQL database
* Open-Meteo weather API
* Browser based UI
* Docker Desktop for repeatable deployment

No database server is required.

## 2. Windows local deployment

Open PowerShell in the `agrisafe_ai` directory.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Start:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

The SQLite database is created automatically.

## 3. Test the application

From the same activated environment:

```powershell
pytest -q
```

Expected result for the included risk engine tests is all tests passing.

Then test the health endpoint:

```powershell
Invoke-RestMethod http://localhost:8000/api/health
```

## 4. Docker deployment

Install Docker Desktop.

Build and start:

```powershell
docker compose up --build
```

Open:

```text
http://localhost:8000
```

The SQLite database is persisted in the `agrisafe_data` Docker volume.

View logs:

```powershell
docker compose logs -f agrisafe
```

Stop:

```powershell
docker compose down
```

The database remains because the volume is retained.

## 5. Reset the demo database

Only do this if you want a clean hackathon demonstration:

```powershell
docker compose down -v
docker compose up --build
```

## 6. Live weather

When coordinates are supplied, AgriSafe calls Open-Meteo.

For a fully offline hackathon demo, set `demo_mode=true` in the assessment request. Demo weather is intentionally labeled as demo data.

For safety-sensitive operation, do not silently substitute demo weather for missing live weather.

## 7. Environment configuration

The important values are:

```text
DATABASE_URL=sqlite:///./agrisafe.db
DEMO_WEATHER_ENABLED=true
LLM_ENABLED=false
MAX_UPLOAD_MB=10
```

For Docker, `DATABASE_URL` points to `/app/runtime/agrisafe.db` so the database survives container recreation.

## 8. Hackathon demo flow

1. Open the AgriSafe dashboard.
2. Select `Pesticide spraying`.
3. Select `Chili`.
4. Enter a planned time of 2:00 PM.
5. Enter or use demo weather.
6. Enter 4 hours of worker exposure.
7. Leave PPE incomplete.
8. Select `Demo Pesticide X`.
9. Run assessment.
10. Show the risk score, decision, reasons and actions.
11. Open safer windows.
12. Show a later lower risk window.
13. Change PPE to complete.
14. Reassess and demonstrate the effect of the changed input.
15. Open assessment history.

## 9. Production deployment note

SQLite is intentionally the final database for this hackathon package. It is suitable for a single application instance and simplifies deployment.

For a future high availability deployment with multiple application instances, use a managed SQL database and change only the database configuration plus the required SQL driver. The SQLAlchemy models and repository layer can remain largely unchanged.

Before real agricultural use, add authentication, authorization, HTTPS, backups, rule versioning, source evidence, expert validation, monitoring and a formal safety review.
