"""Score change log schemas — for audit trail of result modifications."""

from datetime import datetime

from pydantic import BaseModel


class ScoreChangeEntry(BaseModel):
    """A single vote's score change entry in the audit log."""

    vote_id: int
    username: str
    race_id: int
    old_points: int | None
    new_points: int | None
    modified_at: str | None = None
    admin_username: str


class ScoreChangeLogResponse(BaseModel):
    """Response for the score change history query."""

    race_id: int
    race_name: str
    changes: list[ScoreChangeEntry]
