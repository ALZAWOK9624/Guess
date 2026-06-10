"""Invite code Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel


class InviteCodeResponse(BaseModel):
    code: str
    status: str
    bound_username: str | None = None
    bound_qq: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class InviteCodeListResponse(BaseModel):
    data: list[InviteCodeResponse]
