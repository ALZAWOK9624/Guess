"""Race-related Pydantic schemas."""

from datetime import date as date_type, datetime

from pydantic import BaseModel, field_validator, field_serializer
from sqlalchemy.orm import InstrumentedAttribute


class HorseSnapshot(BaseModel):
    name: str
    sex: str | None = None
    birth_year: int | None = None
    origin: str | None = None
    hemisphere: str | None = None
    location: str | None = None
    sire: str | None = None
    damsire: str | None = None
    previous_result: str | None = None
    previous_result_date: str | None = None
    previous_result_position: int | None = None
    best_win: str | None = None
    best_win_date: str | None = None


class PenaltyRule(BaseModel):
    position: int  # negative, e.g. -1 for last place
    points: int    # negative, e.g. -5


class CustomScoring(BaseModel):
    positive_scores: list[int]
    penalty_rules: list[PenaltyRule] | None = None


class RaceCreate(BaseModel):
    name: str
    date: date_type
    grade: str  # "G1" | "G2_JPN1" | "YOUNG_G1" | "CUSTOM"
    horse_ids: list[int] | None = None
    horse_weights: dict[int, str] | None = None  # horse_id → weight
    horse_jockeys: dict[int, str] | None = None  # horse_id → jockey
    custom_scoring: CustomScoring | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v) < 1 or len(v) > 200:
            raise ValueError("比赛名称长度需在 1-200 个字符之间")
        return v.strip()

    @field_validator("grade")
    @classmethod
    def validate_grade(cls, v: str) -> str:
        allowed = {"G1", "G2_JPN1", "YOUNG_G1", "CUSTOM"}
        if v not in allowed:
            raise ValueError(f"无效的比赛等级，允许的值: {', '.join(sorted(allowed))}")
        return v

    @field_validator("horse_ids")
    @classmethod
    def validate_horse_ids(cls, v: list[int] | None) -> list[int] | None:
        if v is not None:
            if len(v) > 0 and len(v) < 2:
                raise ValueError("至少需要 2 匹参赛马")
            if len(v) != len(set(v)):
                raise ValueError("参赛马匹不能重复")
        return v


class RaceUpdate(BaseModel):
    name: str | None = None
    date: date_type | None = None
    grade: str | None = None
    horse_ids: list[int] | None = None
    horse_weights: dict[int, str] | None = None  # race_horse_id → weight
    horse_jockeys: dict[int, str] | None = None  # race_horse_id → jockey
    custom_scoring: CustomScoring | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None:
            if len(v) < 1 or len(v) > 200:
                raise ValueError("比赛名称长度需在 1-200 个字符之间")
            return v.strip()
        return v

    @field_validator("grade")
    @classmethod
    def validate_grade(cls, v: str | None) -> str | None:
        if v is not None:
            allowed = {"G1", "G2_JPN1", "YOUNG_G1", "CUSTOM"}
            if v not in allowed:
                raise ValueError(f"无效的比赛等级，允许的值: {', '.join(sorted(allowed))}")
        return v

    @field_validator("horse_ids")
    @classmethod
    def validate_horse_ids(cls, v: list[int] | None) -> list[int] | None:
        if v is not None:
            if len(v) < 2:
                raise ValueError("至少需要 2 匹参赛马")
            if len(v) != len(set(v)):
                raise ValueError("参赛马匹不能重复")
        return v


class RaceHorseUpdate(BaseModel):
    weight: str | None = None
    jockey: str | None = None


class AddRaceHorseRequest(BaseModel):
    horse_id: int
    weight: str | None = None
    jockey: str | None = None


class GateOrderUpdate(BaseModel):
    order: list[int]

    @field_validator("order")
    @classmethod
    def validate_order(cls, v: list[int]) -> list[int]:
        if len(v) != len(set(v)):
            raise ValueError("闸位排序不能包含重复马匹")
        return v


class RaceHorseResponse(BaseModel):
    race_horse_id: int
    horse_id: int
    snapshot_data: HorseSnapshot
    position: int | None = None
    gate: int | None = None
    weight: str | None = None
    jockey: str | None = None

    model_config = {"from_attributes": True}


class RaceListResponse(BaseModel):
    id: int
    name: str
    date: date_type
    grade: str
    status: str
    custom_scoring: CustomScoring | None = None
    is_hidden: bool = False
    horse_count: int
    vote_count: int
    has_voted: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class RaceDetailResponse(BaseModel):
    id: int
    name: str
    date: date_type
    grade: str
    status: str
    custom_scoring: CustomScoring | None = None
    is_hidden: bool = False
    horses: list[RaceHorseResponse]
    horse_votes: dict | None = None  # populated for settled races
    vote_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
