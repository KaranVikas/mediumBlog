from fastapi import APIRouter

# Import all your routers here
from api.endpoints.users import router as users_router
from api.endpoints.auth import router as auth_router

api_router = APIRouter()

# Include all your routers
api_router.include_router(users_router, prefix="/users")
api_router.include_router(auth_router, prefix="/auth")
