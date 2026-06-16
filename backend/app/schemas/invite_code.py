"""Invite code Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, field_validator


class InviteCodeCreate(BaseModel):
    qq: str

    @field_validator("qq")
    @classmethod
    def validate_qq(cls, v: str) -> str:
        if len(v) < 5 or len(v) > 20:
            raise ValueError("QQ 号长度需在 5-20 个字符之间")
        return v


class InviteCodeResponse(BaseModel):
    code: str
    status: str
    bound_username: str | None = None
    bound_qq: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class InviteCodeListResponse(BaseModel):
    data: list[InviteCodeResponse]
