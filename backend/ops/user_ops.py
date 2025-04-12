from typing import Optional
from uuid import UUID
import uuid
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models import UserModel

async def get_user_by_id(db: AsyncSession, user_id: UUID):
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(UserModel).where(UserModel.email == email))
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(UserModel).where(UserModel.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, username: str, email: str, password: str, full_name: Optional[str] = None):
    user = UserModel(
        id=uuid.uuid4(),
        username=username,
        email=email,
        password=password,
        full_name=full_name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def create_admin_user(db: AsyncSession, username: str, email: str, password: str, role: str, full_name: Optional[str] = None):
    user = UserModel(
        username=username,
        email=email,
        password=password,
        role=role,
        full_name=full_name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def update_user(db: AsyncSession, user_id: UUID, **kwargs):
    stmt = (
        update(UserModel)
        .where(UserModel.id == user_id)
        .values(**kwargs)
        .returning(UserModel)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalars().first()

async def delete_user(db: AsyncSession, user_id: UUID):
    stmt = delete(UserModel).where(UserModel.id == user_id).returning(UserModel)
    result = await db.execute(stmt)
    await db.commit()
    return result.scalars().first()