import json
import csv
import io
import secrets
from pathlib import Path
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from pypdf import PdfReader
from .db import get_db
from .models import AlertQueue, Assessment, Farmer, Farm, Incident, Plot
from .schemas import AlertCreate, AssessmentRequest, AssessmentResponse, FarmerCreate, FarmCreate, IncidentCreate, PlotCreate, SaferWindowRequest
from .risk_engine import assess
from .seed import load_chemical, load_chemicals
from .weather import get_weather
from .knowledge import retrieve
from .config import settings
from .explanations import decision_summary, translate_result

router = APIRouter(prefix="/api")

TASK_CATALOGUE = [
    {"id": "pesticide-spraying", "label": "Pesticide spraying", "requires_chemical": True},
    {"id": "fertilizer-application", "label": "Fertilizer application", "requires_chemical": True},
    {"id": "tractor-operation", "label": "Tractor / machinery operation", "requires_chemical": False},
    {"id": "manual-harvesting", "label": "Manual harvesting", "requires_chemical": False},
    {"id": "livestock-handling", "label": "Livestock handling", "requires_chemical": False},
    {"id": "irrigation", "label": "Irrigation", "requires_chemical": False},
    {"id": "land-clearing", "label": "Land clearing", "requires_chemical": False},
    {"id": "greenhouse-work", "label": "Greenhouse work", "requires_chemical": False},
]


def _guidance(req, weather):
    profile = load_chemical(req.chemical)
    ppe = list(profile.get("required_ppe", [])) if profile else []
    if not ppe and "spray" in req.task.lower():
        ppe = ["Gloves", "Protective clothing", "Eye protection", "Follow the product label/SDS"]

    temperature = weather["temperature_c"]
    if temperature >= 35:
        work_rest = {"work_minutes": 20, "rest_minutes": 40, "hydration_minutes": 15, "message": "Kerja pendek, rehat di tempat teduh dan minum air dengan kerap."}
    elif temperature >= 32:
        work_rest = {"work_minutes": 30, "rest_minutes": 30, "hydration_minutes": 20, "message": "Buat rehat berkala dan tingkatkan pengambilan air."}
    else:
        work_rest = {"work_minutes": 45, "rest_minutes": 15, "hydration_minutes": 30, "message": "Kekalkan rehat dan penghidratan biasa."}

    safety_timing = {}
    if req.planned_date and req.planned_time:
        planned = datetime.strptime(f"{req.planned_date} {req.planned_time}", "%Y-%m-%d %H:%M")
        reentry_hours = int(profile.get("reentry_interval_hours", 0)) if profile else 0
        harvest_days = int(profile.get("preharvest_interval_days", 0)) if profile else 0
        safety_timing = {
            "reentry_at": (planned + timedelta(hours=reentry_hours)).isoformat() if reentry_hours else None,
            "harvest_safe_date": (planned.date() + timedelta(days=harvest_days)).isoformat() if harvest_days else None,
            "reentry_interval_hours": reentry_hours,
            "preharvest_interval_days": harvest_days,
        }

    return ppe, work_rest, safety_timing, profile


async def _resolve_weather(req):
    values = {
        "temperature_c": req.temperature_c,
        "humidity_pct": req.humidity_pct,
        "wind_kmh": req.wind_kmh,
        "rain_probability_pct": req.rain_probability_pct,
    }
    if all(v is not None for v in values.values()) and not (
        req.area or req.latitude is not None or req.longitude is not None
    ):
        return {**values, "source": "manual", "timestamp": None}
    return await get_weather(
        req.latitude,
        req.longitude,
        req.demo_mode,
        target_date=req.planned_date,
        target_time=req.planned_time,
        area=req.area,
    )


@router.get("/health")
def health():
    return {"status": "ok", "service": "agrisafe-ai"}


def _farmer_from_key(db: Session, api_key: str | None):
    if not api_key:
        raise HTTPException(status_code=401, detail="X-Farmer-Key is required.")
    farmer = db.query(Farmer).filter(Farmer.api_key == api_key).first()
    if not farmer:
        raise HTTPException(status_code=401, detail="Invalid farmer key.")
    return farmer


@router.post("/farmers")
def create_farmer(req: FarmerCreate, db: Session = Depends(get_db)):
    farmer = Farmer(name=req.name, phone=req.phone, preferred_language=req.preferred_language, api_key=secrets.token_urlsafe(32))
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    return {"id": farmer.id, "name": farmer.name, "preferred_language": farmer.preferred_language, "api_key": farmer.api_key}


@router.get("/farmers/me")
def farmer_profile(x_farmer_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    farmer = _farmer_from_key(db, x_farmer_key)
    return {"id": farmer.id, "name": farmer.name, "phone": farmer.phone, "preferred_language": farmer.preferred_language}


@router.post("/farms")
def create_farm(req: FarmCreate, x_farmer_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    farmer = _farmer_from_key(db, x_farmer_key)
    farm = Farm(farmer_id=farmer.id, name=req.name, location=req.location)
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return {"id": farm.id, "name": farm.name, "location": farm.location}


@router.get("/farms")
def list_farms(x_farmer_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    farmer = _farmer_from_key(db, x_farmer_key)
    farms = db.query(Farm).filter(Farm.farmer_id == farmer.id).all()
    return [{"id": farm.id, "name": farm.name, "location": farm.location} for farm in farms]


@router.post("/farms/{farm_id}/plots")
def create_plot(farm_id: int, req: PlotCreate, x_farmer_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    farmer = _farmer_from_key(db, x_farmer_key)
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.farmer_id == farmer.id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found.")
    plot = Plot(farm_id=farm.id, name=req.name, crop=req.crop, area_hectares=req.area_hectares)
    db.add(plot)
    db.commit()
    db.refresh(plot)
    return {"id": plot.id, "farm_id": plot.farm_id, "name": plot.name, "crop": plot.crop, "status": plot.status}


@router.get("/farms/{farm_id}/plots")
def list_plots(farm_id: int, x_farmer_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    farmer = _farmer_from_key(db, x_farmer_key)
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.farmer_id == farmer.id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found.")
    plots = db.query(Plot).filter(Plot.farm_id == farm.id).all()
    return [{"id": plot.id, "name": plot.name, "crop": plot.crop, "area_hectares": plot.area_hectares, "status": plot.status} for plot in plots]


@router.post("/incidents")
def create_incident(req: IncidentCreate, x_farmer_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    farmer = _farmer_from_key(db, x_farmer_key)
    incident = Incident(farmer_id=farmer.id, farm_id=req.farm_id, plot_id=req.plot_id, kind=req.kind, severity=req.severity, description=req.description)
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return {"id": incident.id, "status": incident.status, "severity": incident.severity, "created_at": incident.occurred_at}


@router.get("/incidents")
def list_incidents(x_farmer_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    farmer = _farmer_from_key(db, x_farmer_key)
    incidents = db.query(Incident).filter(Incident.farmer_id == farmer.id).order_by(Incident.occurred_at.desc()).all()
    return [{"id": item.id, "kind": item.kind, "severity": item.severity, "description": item.description, "status": item.status, "occurred_at": item.occurred_at} for item in incidents]


@router.post("/alerts")
def queue_alert(req: AlertCreate, x_farmer_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    farmer = _farmer_from_key(db, x_farmer_key)
    if not farmer.phone and req.channel in {"sms", "whatsapp"}:
        raise HTTPException(status_code=400, detail="Add a phone number before queueing SMS or WhatsApp alerts.")
    alert = AlertQueue(farmer_id=farmer.id, channel=req.channel, recipient=farmer.phone or farmer.name, message=req.message)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return {"id": alert.id, "status": alert.status, "channel": alert.channel, "message": alert.message}


@router.get("/reports/hirarc.csv")
def export_hirarc_csv(x_farmer_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    farmer = _farmer_from_key(db, x_farmer_key)
    rows = db.query(Assessment).order_by(Assessment.created_at.desc()).limit(500).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Assessment ID", "Date", "Task", "Crop", "Risk score", "Risk level", "Decision", "Weather", "Controls"])
    for row in rows:
        writer.writerow([row.id, row.created_at.isoformat(), row.task, row.crop, row.risk_score, row.risk_level, row.decision, f"{row.temperature_c}C, {row.wind_kmh} km/h wind, {row.rain_probability_pct}% rain", row.actions_json])
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="agrisafe-hirarc-{farmer.id}.csv"'})


@router.get("/reports/hirarc.html", response_class=HTMLResponse)
def export_hirarc_html(x_farmer_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    farmer = _farmer_from_key(db, x_farmer_key)
    rows = db.query(Assessment).order_by(Assessment.created_at.desc()).limit(100).all()
    table = "".join(f"<tr><td>{row.created_at:%Y-%m-%d %H:%M}</td><td>{row.task}</td><td>{row.crop}</td><td>{row.risk_score}</td><td>{row.decision}</td><td>{row.actions_json}</td></tr>" for row in rows)
    return HTMLResponse(f"<html><head><title>AgriSafe HIRARC Report</title><style>body{{font-family:Arial;margin:32px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccc;padding:8px;text-align:left}}</style></head><body><h1>AgriSafe HIRARC-style Task Report</h1><p>Farmer: {farmer.name}</p><p>This decision-support report is a prototype record and does not replace a formal DOSH assessment.</p><table><tr><th>Date</th><th>Task</th><th>Crop</th><th>Score</th><th>Decision</th><th>Controls</th></tr>{table}</table></body></html>")


@router.get("/tasks")
def task_catalogue():
    return {"tasks": TASK_CATALOGUE}


@router.get("/chemicals")
def chemical_catalogue():
    return {
        "chemicals": [
            {key: item.get(key) for key in ["name", "category", "hazard_score", "required_ppe", "reentry_interval_hours", "preharvest_interval_days"]}
            for item in load_chemicals()
        ]
    }


@router.get("/emergency")
def emergency_guidance(language: str = "ms"):
    if language.lower() == "en":
        return {"title": "Emergency response", "poisoning": ["Stop work and move away from the exposure.", "Remove contaminated clothing and rinse skin or eyes with clean water.", "Call emergency services or go to the nearest clinic. Bring the product label/SDS."], "heat_stroke": ["Move the person to shade, cool them with water and remove excess clothing.", "Do not leave them alone. Call emergency services for confusion, fainting or seizures."]}
    return {"title": "Tindakan kecemasan", "poisoning": ["Hentikan kerja dan jauhkan diri daripada punca pendedahan.", "Tanggalkan pakaian tercemar dan bilas kulit atau mata dengan air bersih.", "Hubungi perkhidmatan kecemasan atau pergi ke klinik terdekat. Bawa label produk/SDS."], "heat_stroke": ["Bawa mangsa ke tempat teduh, sejukkan badan dengan air dan longgarkan pakaian.", "Jangan tinggalkan mangsa seorang diri. Hubungi kecemasan jika keliru, pengsan atau sawan."]}


@router.get("/weather")
async def weather_lookup(
    area: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    planned_date: str | None = None,
    planned_time: str | None = None,
    demo_mode: bool = False,
):
    try:
        return await get_weather(
            latitude,
            longitude,
            demo_mode,
            target_date=planned_date,
            target_time=planned_time,
            area=area,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/assessments", response_model=AssessmentResponse)
async def create_assessment(req: AssessmentRequest, db: Session = Depends(get_db)):
    try:
        weather = await _resolve_weather(req)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    result = assess(
        task=req.task,
        crop=req.crop,
        temperature_c=weather["temperature_c"],
        humidity_pct=weather["humidity_pct"],
        wind_kmh=weather["wind_kmh"],
        rain_probability_pct=weather["rain_probability_pct"],
        worker_exposure_hours=req.worker_exposure_hours,
        ppe_complete=req.ppe_complete,
        chemical=req.chemical,
        growth_stage=req.growth_stage,
        equipment=req.equipment,
        workers_count=req.workers_count,
        vulnerability_flags=req.vulnerability_flags,
    )
    display_result = translate_result(result, req.language)
    ppe_checklist, work_rest_plan, safety_timing, chemical_info = _guidance(req, weather)

    recent_duplicate = (
        db.query(Assessment)
        .filter(
            Assessment.created_at >= datetime.now(timezone.utc) - timedelta(seconds=30),
            Assessment.crop == req.crop,
            Assessment.task == req.task,
            Assessment.planned_time == req.planned_time,
            Assessment.duration_minutes == req.duration_minutes,
            Assessment.latitude == req.latitude,
            Assessment.longitude == req.longitude,
            Assessment.chemical == req.chemical,
            Assessment.temperature_c == weather["temperature_c"],
            Assessment.humidity_pct == weather["humidity_pct"],
            Assessment.wind_kmh == weather["wind_kmh"],
            Assessment.rain_probability_pct == weather["rain_probability_pct"],
            Assessment.worker_exposure_hours == req.worker_exposure_hours,
            Assessment.ppe_complete == req.ppe_complete,
        )
        .order_by(Assessment.created_at.desc())
        .first()
    )
    if recent_duplicate:
        stored_rules = json.loads(recent_duplicate.rules_json)
        translated_reasons = translate_result(
            type("DummyResult", (), {
                "score": recent_duplicate.risk_score,
                "level": recent_duplicate.risk_level,
                "decision": recent_duplicate.decision,
                "reasons": json.loads(recent_duplicate.reasons_json),
                "actions": json.loads(recent_duplicate.actions_json),
                "blockers": [],
                "rules": [],
            })(),
            req.language,
        )
        return AssessmentResponse(
            id=recent_duplicate.id,
            created_at=recent_duplicate.created_at,
            risk_score=recent_duplicate.risk_score,
            risk_level=recent_duplicate.risk_level,
            decision=recent_duplicate.decision,
            reasons=translated_reasons.reasons,
            actions=translated_reasons.actions,
            rules_triggered=[rule for rule in stored_rules if not rule.startswith("BLOCKER:")],
            weather={
                "temperature_c": recent_duplicate.temperature_c,
                "humidity_pct": recent_duplicate.humidity_pct,
                "wind_kmh": recent_duplicate.wind_kmh,
                "rain_probability_pct": recent_duplicate.rain_probability_pct,
                "source": recent_duplicate.weather_source,
                "timestamp": recent_duplicate.weather_timestamp,
            },
            assessment_status="INCOMPLETE" if any(rule.startswith("BLOCKER:") for rule in stored_rules) else "COMPLETE",
            ppe_checklist=ppe_checklist,
            work_rest_plan=work_rest_plan,
            safety_timing=safety_timing,
            chemical_info=chemical_info,
            language=req.language,
        )

    assessment = Assessment(
        crop=req.crop,
        task=req.task,
        planned_time=req.planned_time,
        duration_minutes=req.duration_minutes,
        latitude=req.latitude,
        longitude=req.longitude,
        chemical=req.chemical,
        temperature_c=weather["temperature_c"],
        humidity_pct=weather["humidity_pct"],
        wind_kmh=weather["wind_kmh"],
        rain_probability_pct=weather["rain_probability_pct"],
        worker_exposure_hours=req.worker_exposure_hours,
        ppe_complete=req.ppe_complete,
        risk_score=result.score,
        risk_level=result.level,
        decision=result.decision,
        reasons_json=json.dumps(display_result.reasons),
        actions_json=json.dumps(display_result.actions),
        rules_json=json.dumps(result.rules + [f"BLOCKER:{x}" for x in result.blockers]),
        weather_source=weather.get("source", "unknown"),
        weather_timestamp=weather.get("timestamp"),
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    status = "INCOMPLETE" if result.blockers else "COMPLETE"
    task_log = {
        "crop": req.crop,
        "task": req.task,
        "growth_stage": req.growth_stage,
        "equipment": req.equipment,
        "workers_count": req.workers_count,
        "planned_date": req.planned_date,
        "planned_time": req.planned_time,
        "duration_minutes": req.duration_minutes,
        "chemical": req.chemical,
        "ppe_complete": req.ppe_complete,
        "decision": result.decision,
        "recommended_action": display_result.actions[0] if display_result.actions else "Complete the safety checklist.",
    }
    return AssessmentResponse(
        id=assessment.id,
        created_at=assessment.created_at,
        risk_score=result.score,
        risk_level=result.level,
        decision=result.decision,
        reasons=display_result.reasons + [x for x in display_result.blockers if x not in display_result.reasons],
        actions=display_result.actions,
        rules_triggered=result.rules,
        weather=weather,
        assessment_status=status,
        task_log=task_log,
        ppe_checklist=ppe_checklist,
        work_rest_plan=work_rest_plan,
        safety_timing=safety_timing,
        chemical_info=chemical_info,
        language=req.language,
    )


@router.get("/assessments")
def list_assessments(db: Session = Depends(get_db)):
    rows = db.query(Assessment).order_by(Assessment.created_at.desc()).limit(50).all()
    return [
        {
            "id": r.id,
            "created_at": r.created_at,
            "crop": r.crop,
            "task": r.task,
            "risk_score": r.risk_score,
            "risk_level": r.risk_level,
            "decision": r.decision,
        }
        for r in rows
    ]


@router.post("/safer-windows")
async def safer_windows(req: SaferWindowRequest):
    # A deterministic demo forecast lets the hackathon feature work without a second external API.
    candidates = [
        {"label": "Now", "temperature_c": 34, "humidity_pct": 82, "wind_kmh": 18, "rain_probability_pct": 70},
        {"label": "+1 hour", "temperature_c": 33, "humidity_pct": 80, "wind_kmh": 15, "rain_probability_pct": 60},
        {"label": "+2 hours", "temperature_c": 31, "humidity_pct": 78, "wind_kmh": 10, "rain_probability_pct": 35},
        {"label": "+3 hours", "temperature_c": 29, "humidity_pct": 76, "wind_kmh": 7, "rain_probability_pct": 20},
        {"label": "+4 hours", "temperature_c": 28, "humidity_pct": 75, "wind_kmh": 6, "rain_probability_pct": 15},
    ]
    results = []
    for c in candidates:
        r = assess(
            task=req.task,
            crop=req.crop,
            temperature_c=c["temperature_c"],
            humidity_pct=c["humidity_pct"],
            wind_kmh=c["wind_kmh"],
            rain_probability_pct=c["rain_probability_pct"],
            worker_exposure_hours=req.worker_exposure_hours,
            ppe_complete=req.ppe_complete,
            chemical=req.chemical,
            growth_stage=req.growth_stage,
            equipment=req.equipment,
            workers_count=req.workers_count,
            vulnerability_flags=req.vulnerability_flags,
        )
        results.append({
            **c,
            "risk_score": r.score,
            "risk_level": r.level,
            "decision": r.decision,
            "why": r.reasons[:2],
            "best_action": r.actions[0] if r.actions else "Follow the task checklist.",
        })
    viable = [x for x in results if x["decision"] in {"PROCEED", "MODIFY"}]
    viable.sort(key=lambda x: x["risk_score"])
    return {"windows": results, "recommended": viable[0] if viable else None}


@router.get("/knowledge/search")
def knowledge_search(q: str):
    return {"query": q, "results": retrieve(q)}


@router.post("/documents/extract")
async def extract_document(file: UploadFile = File(...)):
    allowed = {"application/pdf", "text/plain"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=415, detail="Only PDF and text files are supported in the MVP.")
    content = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File is larger than {settings.max_upload_mb} MB.")
    text = ""
    if file.content_type == "application/pdf":
        temp = Path("/tmp") / f"agrisafe_{uuid4().hex}.pdf"
        temp.write_bytes(content)
        try:
            reader = PdfReader(str(temp))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        finally:
            temp.unlink(missing_ok=True)
    else:
        text = content.decode("utf-8", errors="replace")
    return {"filename": file.filename, "characters": len(text), "text_preview": text[:8000]}
