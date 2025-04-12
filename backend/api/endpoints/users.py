from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from api.deps import get_current_admin, get_current_super_admin, get_db
from ops.user_ops import (
    get_user_by_id,
    update_user,
    delete_user
)
from api.dto.req.user import UserUpdateReq
from api.dto.res.user import UserOutRes
from api.deps import get_current_user

router = APIRouter(tags=["users"])

@router.get("/me", response_model=UserOutRes)
async def read_current_user(
    current_user: UserOutRes = Depends(get_current_user)
):
    return current_user

@router.get("/{user_id}", response_model=UserOutRes)
async def read_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserOutRes = Depends(get_current_admin)
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.patch("/me", response_model=UserOutRes)
async def update_current_user(
    user_data: UserUpdateReq,
    db: AsyncSession = Depends(get_db),
    current_user: UserOutRes = Depends(get_current_user)
):
    update_data = user_data.model_dump(exclude_unset=True)
    print(update_data)
    return await update_user(db, current_user.id, **update_data)

@router.delete("/{user_id}")
async def delete_current_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserOutRes = Depends(get_current_super_admin)
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    await delete_user(db, user.id)
    return {"message": "User deleted successfully"}