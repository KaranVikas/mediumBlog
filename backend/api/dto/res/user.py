from enum import Enum
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from models.users import RoleEnum

class UserOutRes(BaseModel):
    id: UUID
    username: str
    email: str
    full_name: str | None = None
    role: RoleEnum
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True