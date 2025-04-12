from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from api.deps import get_db
from ops.user_ops import (
    get_user_by_email,
    get_user_by_username,
    create_user
)
from api.dto.req.user import UserCreateReq
from api.dto.res.user import UserOutRes

from api.security import create_access_token, get_password_hash, verify_password

router = APIRouter(tags=["auth"])

@router.post("/register", response_model=UserOutRes)
async def register(user_data: UserCreateReq, db: AsyncSession = Depends(get_db)):
    if await get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    if await get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    password = get_password_hash(user_data.password)
    
    user = await create_user(
        db,
        username=user_data.username,
        email=user_data.email,
        password=password,
        full_name=user_data.full_name
    )
    return user

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }