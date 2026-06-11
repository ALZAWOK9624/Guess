"""Horse model — 10-attribute horse data library."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class Horse(Base):
    __tablename__ = "horses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    sex: Mapped[str | None] = mapped_column(String(10), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    origin: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sire: Mapped[str | None] = mapped_column(String(100), nullable=True)
    damsire: Mapped[str | None] = mapped_column(String(100), nullable=True)
    weight: Mapped[str | None] = mapped_column(String(20), nullable=True)
    jockey: Mapped[str | None] = mapped_column(String(50), nullable=True)
    previous_result: Mapped[str | None] = mapped_column(String(100), nullable=True)
    best_win: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
