from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class AssessmentRequest(BaseModel):
    crop: str = Field(min_length=1, max_length=100)
    task: str = Field(min_length=1, max_length=100)
    planned_date: str | None = Field(default=None, min_length=1, max_length=20)
    planned_time: str = Field(min_length=1, max_length=40)
    area: str | None = Field(default=None, min_length=1, max_length=120)
    duration_minutes: int = Field(default=60, ge=15, le=720)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    chemical: str | None = Field(default=None, max_length=150)
    growth_stage: str | None = Field(default=None, max_length=80)
    equipment: str | None = Field(default=None, max_length=80)
    workers_count: int = Field(default=1, ge=1, le=200)
    vulnerability_flags: list[str] = Field(default_factory=list, max_length=6)
    temperature_c: float | None = Field(default=None, ge=-50, le=70)
    humidity_pct: float | None = Field(default=None, ge=0, le=100)
    wind_kmh: float | None = Field(default=None, ge=0, le=250)
    rain_probability_pct: float | None = Field(default=None, ge=0, le=100)
    worker_exposure_hours: float = Field(default=0, ge=0, le=24)
    ppe_complete: bool = False
    demo_mode: bool = False
    language: str = "ms"

    @model_validator(mode="after")
    def validate_planned_start(self):
        if not self.planned_date or not self.planned_time:
            return self
        try:
            planned = datetime.strptime(
                f"{self.planned_date} {self.planned_time}", "%Y-%m-%d %H:%M"
            )
        except ValueError as exc:
            raise ValueError("Planned date and time must be valid.") from exc
        if planned < datetime.now().astimezone().replace(tzinfo=None):
            raise ValueError("Planned date and time cannot be in the past.")
        return self


class AssessmentResponse(BaseModel):
    id: int
    created_at: datetime
    risk_score: int
    risk_level: str
    decision: str
    reasons: list[str]
    actions: list[str]
    rules_triggered: list[str]
    weather: dict
    assessment_status: str
    task_log: dict | None = None
    ppe_checklist: list[str] = Field(default_factory=list)
    work_rest_plan: dict | None = None
    safety_timing: dict | None = None
    chemical_info: dict | None = None
    language: str = "ms"


class SaferWindowRequest(BaseModel):
    crop: str
    task: str
    planned_date: str | None = None
    area: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    chemical: str | None = None
    growth_stage: str | None = None
    equipment: str | None = None
    workers_count: int = Field(default=1, ge=1, le=200)
    vulnerability_flags: list[str] = Field(default_factory=list, max_length=6)
    duration_minutes: int = Field(default=60, ge=15, le=720)
    worker_exposure_hours: float = Field(default=0, ge=0, le=24)
    ppe_complete: bool = False
    demo_mode: bool = False
    language: str = "ms"


class FarmerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    phone: str | None = Field(default=None, max_length=40)
    preferred_language: str = Field(default="ms", max_length=10)


class FarmCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    location: str | None = Field(default=None, max_length=160)


class PlotCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    crop: str | None = Field(default=None, max_length=100)
    area_hectares: float | None = Field(default=None, ge=0, le=100000)


class IncidentCreate(BaseModel):
    kind: str = Field(min_length=1, max_length=40)
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    description: str = Field(min_length=1, max_length=4000)
    farm_id: int | None = None
    plot_id: int | None = None


class AlertCreate(BaseModel):
    channel: str = Field(pattern="^(sms|whatsapp|email)$")
    message: str = Field(min_length=1, max_length=2000)
