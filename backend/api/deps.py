from fastapi import Depends, HTTPException, status
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from api.security import oauth2_scheme
from models.users import RoleEnum
from core.settings import settings
from ops.user_ops import get_user_by_id
from core.db import async_db


async def get_db():
    """Dependency that provides a database session for each request"""
    async with async_db.get_session() as session:
        yield session


async def _get_user_from_token(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Helper function to extract user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value() if settings.SECRET_KEY else None,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        if payload.get("type") != "access":
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception

    user = await get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
        
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Dependency to get current authenticated user"""
    return await _get_user_from_token(token, db)


async def get_current_super_admin(
    user = Depends(get_current_user)
):
    """Dependency to get current authenticated super admin"""
    if user.role != RoleEnum.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges required",
        )
    return user


async def get_current_admin(
    user = Depends(get_current_user)
):
    """Dependency to get current authenticated admin or super admin"""
    if user.role not in [RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user


async def get_current_author(
    user = Depends(get_current_user)
):
    """Dependency to get current authenticated author, admin or super admin"""
    if user.role not in [RoleEnum.AUTHOR, RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Author privileges required",
        )
    return user


# Role verification helpers (for more granular control)
def has_role(required_role: RoleEnum):
    """Factory function to create role verification dependencies"""
    async def role_verifier(user = Depends(get_current_user)):
        if user.role == RoleEnum.SUPER_ADMIN:
            return user
            
        # For SUPER_ADMIN, we already returned, so now check other roles
        role_hierarchy = {
            RoleEnum.ADMIN: [RoleEnum.ADMIN],
            RoleEnum.AUTHOR: [RoleEnum.AUTHOR, RoleEnum.ADMIN],
            RoleEnum.USER: [RoleEnum.USER, RoleEnum.AUTHOR, RoleEnum.ADMIN]
        }
        
        if user.role not in role_hierarchy.get(required_role, []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires at least {required_role.value} privileges",
            )
        return user
    return role_verifier