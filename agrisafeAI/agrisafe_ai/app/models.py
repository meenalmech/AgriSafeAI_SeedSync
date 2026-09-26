from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    crop: Mapped[str] = mapped_column(String(100))
    task: Mapped[str] = mapped_column(String(100))
    planned_time: Mapped[str] = mapped_column(String(40))
    duration_minutes: Mapped[int] = mapped_column(Integer)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    chemical: Mapped[str | None] = mapped_column(String(150), nullable=True)
    temperature_c: Mapped[float] = mapped_column(Float)
    humidity_pct: Mapped[float] = mapped_column(Float)
    wind_kmh: Mapped[float] = mapped_column(Float)
    rain_probability_pct: Mapped[float] = mapped_column(Float)
    worker_exposure_hours: Mapped[float] = mapped_column(Float)
    ppe_complete: Mapped[bool] = mapped_column(default=False)
    risk_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(30))
    decision: Mapped[str] = mapped_column(String(30))
    reasons_json: Mapped[str] = mapped_column(Text)
    actions_json: Mapped[str] = mapped_column(Text)
    rules_json: Mapped[str] = mapped_column(Text)
    weather_source: Mapped[str] = mapped_column(String(100), default="manual")
    weather_timestamp: Mapped[str | None] = mapped_column(String(80), nullable=True)


class Farmer(Base):
    __tablename__ = "farmers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(10), default="ms")
    api_key: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class Farm(Base):
    __tablename__ = "farms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    farmer_id: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(120))
    location: Mapped[str | None] = mapped_column(String(160), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class Plot(Base):
    __tablename__ = "plots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    farm_id: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(120))
    crop: Mapped[str | None] = mapped_column(String(100), nullable=True)
    area_hectares: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="green")


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    farmer_id: Mapped[int] = mapped_column(Integer, index=True)
    farm_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    plot_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    kind: Mapped[str] = mapped_column(String(40))
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    description: Mapped[str] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    status: Mapped[str] = mapped_column(String(20), default="open")


class AlertQueue(Base):
    __tablename__ = "alert_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    farmer_id: Mapped[int] = mapped_column(Integer, index=True)
    channel: Mapped[str] = mapped_column(String(20))
    recipient: Mapped[str] = mapped_column(String(160))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="queued")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
