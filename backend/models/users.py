from sqlalchemy import UUID, Boolean, Column, DateTime, Enum, String, func
from .base import CommonBase
from enum import Enum as PyEnum

class RoleEnum(str, PyEnum):
  USER = "user"
  ADMIN = "admin"
  SUPER_ADMIN = "super_admin"
  AUTHOR = "author"
 
class UserModel(CommonBase):
  __tablename__ = "users"
  id = Column(UUID, primary_key=True)
  username = Column(String(50), unique=True)
  full_name = Column(String(50), nullable=True)
  email = Column(String(100), unique=True)
  password = Column(String(200))
  role = Column(Enum(RoleEnum), default=RoleEnum.USER , nullable=False)
  created_at = Column(DateTime, server_default=func.now())
  updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
  is_verified = Column(Boolean, default=False)
