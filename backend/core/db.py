from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from core.settings import settings

class AsyncDatabaseSession:
    def __init__(self):
        self._sessionmaker = None
        self._engine = None
        
    async def init(self):
        """Initialize the engine and sessionmaker (call this once at startup)"""
        if self._engine is None:
            db_url = str(settings.async_db_url)
            self._engine = create_async_engine(
                db_url,
                future=True,
                echo=True,
                pool_size=20,
                max_overflow=10,
                pool_timeout=30,
            )
            self._sessionmaker = sessionmaker(
                self._engine, expire_on_commit=False, class_=AsyncSession
            )
    
    @asynccontextmanager
    async def get_session(self):
        """Async context manager that yields a session"""
        if not self._sessionmaker:
            await self.init()
        session = self._sessionmaker()
        try:
            yield session
        finally:
            await session.close()
        
    async def close(self):
        """Close the engine (call this at shutdown)"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None

# Global instance
async_db = AsyncDatabaseSession()