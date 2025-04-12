from typing import Optional
from pydantic import BaseModel

from models.users import RoleEnum


class UserCreateReq(BaseModel):
  username: str
  email: str
  password: str
  full_name: str

class UserCreateAdminReq(UserCreateReq):
  role: RoleEnum = RoleEnum.USER

class UserUpdateReq(BaseModel):
  email: Optional[str] = None
  full_name: Optional[str] = None

class UserUpdateAdminReq(UserUpdateReq):
  role: RoleEnum = RoleEnum.USER