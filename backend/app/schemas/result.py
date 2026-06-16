"""Result entry schemas — for drag-sort result submission and settlement."""

from pydantic import BaseModel, field_validator


class ResultPosition(BaseModel):
    """A single horse's finishing position."""
    race_horse_id: int
    position: int  # 0 = DNF, 1+ = finishing order


class ResultEntry(BaseModel):
    """Request body for submitting race results."""
    positions: list[ResultPosition]

    @field_validator("positions")
    @classmethod
    def validate_positions(cls, v: list[ResultPosition]) -> list[ResultPosition]:
        if not v:
            raise ValueError("positions must not be empty")
        # Validate no duplicate positive positions
        positive_positions = [p.position for p in v if p.position > 0]
        if len(positive_positions) != len(set(positive_positions)):
            raise ValueError("Duplicate positive positions are not allowed")
        # Validate all positions are non-negative
        for p in v:
            if p.position < 0:
                raise ValueError(f"Position must be >= 0, got {p.position}")
        # Validate positions are contiguous (1, 2, 3, ... no gaps)
        if positive_positions:
            sorted_pos = sorted(positive_positions)
            if sorted_pos != list(range(1, len(sorted_pos) + 1)):
                raise ValueError(
                    "Positions must be contiguous starting from 1"
                )
        return v


class UserScoreItem(BaseModel):
    """A single user's score for a race."""
    user_id: int
    username: str
    points: int


class ResultEntryResponse(BaseModel):
    """Response after submitting race results."""
    race_id: int
    status: str
    scores: list[UserScoreItem]
