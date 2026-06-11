"""Horse-related Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, field_validator


class HorseCreate(BaseModel):
    name: str
    sex: str | None = None
    age: int | None = None
    origin: str | None = None
    sire: str | None = None
    damsire: str | None = None
    weight: str | None = None
    jockey: str | None = None
    previous_result: str | None = None
    best_win: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v) < 1 or len(v) > 100:
            raise ValueError("马匹名称长度需在 1-100 个字符之间")
        return v.strip()


class HorseUpdate(BaseModel):
    name: str | None = None
    sex: str | None = None
    age: int | None = None
    origin: str | None = None
    sire: str | None = None
    damsire: str | None = None
    weight: str | None = None
    jockey: str | None = None
    previous_result: str | None = None
    best_win: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None:
            if len(v) < 1 or len(v) > 100:
                raise ValueError("马匹名称长度需在 1-100 个字符之间")
            return v.strip()
        return v


class HorseResponse(BaseModel):
    id: int
    name: str
    sex: str | None = None
    age: int | None = None
    origin: str | None = None
    sire: str | None = None
    damsire: str | None = None
    weight: str | None = None
    jockey: str | None = None
    previous_result: str | None = None
    best_win: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
