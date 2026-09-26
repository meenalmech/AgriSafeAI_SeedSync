import asyncio

from fastapi.testclient import TestClient

from app.risk_engine import assess
from app.weather import get_weather
from app.schemas import AssessmentRequest
from app.main import app


def test_default_language_is_malay():
    req = AssessmentRequest(
        crop="Rice",
        task="Pesticide spraying",
        planned_time="14:00",
        duration_minutes=60,
        worker_exposure_hours=4,
    )
    assert req.language == "ms"


def test_task_metadata_increases_risk_for_sensitive_conditions():
    r = assess(
        "Pesticide spraying",
        "Rice",
        31,
        75,
        15,
        35,
        5,
        True,
        "Demo Pesticide X",
        growth_stage="flowering",
        equipment="drone",
        workers_count=8,
    )
    assert r.score >= 45
    assert r.decision in {"MODIFY", "DELAY", "AVOID"}


def test_worker_vulnerability_adds_control_rule():
    r = assess("Field inspection", "Rice", 27, 65, 5, 10, 1, True, None, vulnerability_flags=["respiratory"])
    assert "WORKER_VULNERABILITY" in r.rules
    assert r.score >= 5


def test_assessment_returns_farmer_guidance():
    client = TestClient(app)
    response = client.post("/api/assessments", json={
        "crop": "Chili",
        "task": "Pesticide spraying",
        "planned_date": "2099-01-01",
        "planned_time": "07:00",
        "area": None,
        "duration_minutes": 60,
        "chemical": "Demo Pesticide X",
        "temperature_c": 28,
        "humidity_pct": 75,
        "wind_kmh": 6,
        "rain_probability_pct": 15,
        "worker_exposure_hours": 0,
        "ppe_complete": True,
        "demo_mode": True,
        "language": "ms",
    })
    body = response.json()
    assert response.status_code == 200
    assert body["ppe_checklist"]
    assert body["work_rest_plan"]["work_minutes"] == 45
    assert body["safety_timing"]["reentry_interval_hours"] == 24


def test_get_weather_uses_requested_date_and_time(monkeypatch):
    captured = {}

    class DummyResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    class DummyClient:
        def __init__(self, *args, **kwargs):
            self.params = None

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, params):
            captured["params"] = params
            return DummyResponse({
                "current": {"temperature_2m": 27.0, "relative_humidity_2m": 68, "wind_speed_10m": 10.2},
                "hourly": {
                    "time": ["2026-09-20T14:00", "2026-09-20T15:00"],
                    "temperature_2m": [31.5, 30.9],
                    "relative_humidity_2m": [72, 70],
                    "wind_speed_10m": [12.5, 11.1],
                    "precipitation_probability": [35, 28],
                },
            })

    monkeypatch.setattr("app.weather.httpx.AsyncClient", DummyClient)

    weather = asyncio.run(get_weather(3.139, 101.6869, target_date="2026-09-20", target_time="14:00"))

    assert weather["temperature_c"] == 31.5
    assert weather["humidity_pct"] == 72
    assert weather["wind_kmh"] == 12.5
    assert weather["rain_probability_pct"] == 35
    assert captured["params"]["start_date"] == "2026-09-20"
    assert captured["params"]["end_date"] == "2026-09-20"


def test_high_risk_spraying():
    r = assess("Pesticide spraying", "Chili", 34, 82, 18, 70, 4, False, "Demo Pesticide X")
    assert r.decision in {"DELAY", "AVOID"}
    assert r.score >= 55
    assert "SPRAY_WIND_ELEVATED" in r.rules
    assert "PPE_INCOMPLETE" in r.rules


def test_missing_chemical_is_incomplete():
    r = assess("Pesticide spraying", "Chili", 29, 70, 5, 10, 1, True, None)
    assert r.level == "INCOMPLETE"
    assert r.decision == "AVOID"
    assert "CHEMICAL_MISSING" in r.rules


def test_low_risk_basic_task():
    r = assess("Field inspection", "Chili", 27, 65, 5, 10, 1, True, None)
    assert r.decision == "PROCEED"
    assert r.score <= 30
