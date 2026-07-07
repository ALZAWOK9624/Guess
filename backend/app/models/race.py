"""Race and RaceHorse models — race management with horse snapshot."""

import enum
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class RaceStatus(str, enum.Enum):
    VOTING = "voting"
    LOCKED = "locked"
    SETTLED = "settled"


class Race(Base):
    __tablename__ = "races"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    # Race tag fields (replacing the old single grade field)
    age_range: Mapped[str] = mapped_column(String(20), nullable=False)
    sex_restriction: Mapped[str] = mapped_column(String(20), nullable=False)
    race_grade: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False)
    distance: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[RaceStatus] = mapped_column(
        Enum(RaceStatus, name="race_status_enum"),
        nullable=False,
        default=RaceStatus.VOTING,
    )
    custom_scoring: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_hidden: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    race_horses: Mapped[list["RaceHorse"]] = relationship(
        back_populates="race", cascade="all, delete-orphan"
    )
    votes: Mapped[list["Vote"]] = relationship(
        back_populates="race", cascade="all, delete-orphan"
    )


class RaceHorse(Base):
    __tablename__ = "race_horses"

    id: Mapped[int] = mapped_column(primary_key=True)
    race_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("races.id", ondelete="CASCADE"), nullable=False
    )
    horse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("horses.id", ondelete="CASCADE"), nullable=False
    )
    snapshot_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gate: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Per-race weight and jockey (race-specific, not from Horse library)
    weight: Mapped[str | None] = mapped_column(String(20), nullable=True)
    jockey: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    race: Mapped["Race"] = relationship(back_populates="race_horses")
    votes: Mapped[list["Vote"]] = relationship(
        back_populates="race_horse_rel", cascade="all, delete-orphan"
    )
