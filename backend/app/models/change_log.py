"""ScoreChangeLog model — audit trail for score modifications on re-settlement."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class ScoreChangeLog(Base):
    """Records each score change when a settled race's results are modified.

    Captures old_points (before modification) and new_points (after),
    along with the admin who performed the change and the timestamp.

    For first-time settlements: old_points=NULL, new_points=calculated score.
    For re-settlements: both old and new points are recorded.
    Only entries where old_points != new_points are stored.
    """

    __tablename__ = "score_change_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    race_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("races.id", ondelete="CASCADE"), nullable=False, index=True
    )
    vote_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("votes.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    admin_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    old_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    new_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    vote_rel: Mapped["Vote"] = relationship(
        back_populates="score_change_logs", foreign_keys=[vote_id]
    )
    user_rel: Mapped["User"] = relationship(
        foreign_keys=[user_id],
        back_populates="score_change_logs_as_voter",
    )
    admin_user_rel: Mapped["User"] = relationship(
        foreign_keys=[admin_user_id],
        back_populates="score_change_logs_as_admin",
    )
