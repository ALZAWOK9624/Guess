"""HorseAutoUpdateLog model — change traceability for auto-updates."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class HorseAutoUpdateLog(Base):
    """Records each field-level change made by the auto-update framework.

    Tracks what changed (field_name), the before/after values, and
    what triggered the update (trigger_source).
    """

    __tablename__ = "horse_auto_update_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    horse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("horses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    race_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("races.id", ondelete="SET NULL"), nullable=True, index=True
    )
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    trigger_source: Mapped[str] = mapped_column(
        String(50), nullable=False, default="settlement"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
