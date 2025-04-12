from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.settings import settings
from core.db import async_db
from api.routers import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    await async_db.init()
    yield
    # Shutdown code
    await async_db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    lifespan=lifespan
)

# Include all routers
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/")
def read_root():
    return {"message": "Hello World"}