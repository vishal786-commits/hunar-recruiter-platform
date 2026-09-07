from datetime import datetime
from typing import Any
from uuid import uuid4
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hunar_recruiter.db import Base


class JobDB(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    raw_jd: Mapped[str] = mapped_column(Text)

    parsed_jd: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    selected_agent_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
    )

    selected_agent_code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    candidates: Mapped[list["CandidateDB"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )


class CandidateDB(Base):
    __tablename__ = "candidates"

    __table_args__ = (
        UniqueConstraint(
            "job_id",
            "source_candidate_id",
            name="uq_job_source_candidate",
        ),
    )

    # ---------------------------------------------------------
    # Internal database ID
    # ---------------------------------------------------------

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # ---------------------------------------------------------
    # Which job produced this candidate?
    # ---------------------------------------------------------

    job_id: Mapped[str] = mapped_column(
        ForeignKey("jobs.id"),
        nullable=False,
    )

    # ---------------------------------------------------------
    # Original PDL/demo/source ID
    # ---------------------------------------------------------

    source_candidate_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    current_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    years_experience: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    skills: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    match_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    approved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    raw_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    job: Mapped["JobDB"] = relationship(
        back_populates="candidates",
    )

    screenings: Mapped[list["ScreeningDB"]] = relationship(
        back_populates="candidate",
        cascade="all, delete-orphan",
    )

class ScreeningDB(Base):
    __tablename__ = "screenings"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    candidate_id: Mapped[str] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
    )

    agent_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )

    agent_code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    hunar_call_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        unique=True,
    )

    request_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
    )

    lifecycle_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    recording_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    result: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    raw_hunar_response: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    candidate: Mapped["CandidateDB"] = relationship(
        back_populates="screenings",
    )