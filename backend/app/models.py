"""Persistence models."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ValidationRecord(Base):
    __tablename__ = "validation_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True
    )
    status: Mapped[str] = mapped_column(String(16), index=True)
    record_count: Mapped[int] = mapped_column(Integer)
    average_pd: Mapped[float] = mapped_column(Float)
    observed_default_rate: Mapped[float] = mapped_column(Float)
    brier_score: Mapped[float] = mapped_column(Float)
    calibration_gap: Mapped[float] = mapped_column(Float)
    quality: Mapped[dict] = mapped_column(JSON)
    findings: Mapped[list] = mapped_column(JSON)
    calibration: Mapped[list] = mapped_column(JSON)
    policy: Mapped[dict] = mapped_column(JSON)
    trace_id: Mapped[str] = mapped_column(String(64), index=True)


class OperationalState(Base):
    __tablename__ = "operational_state"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

