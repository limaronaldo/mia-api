import contextlib
from typing import Any, AsyncIterator

from decouple import config
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
)
from supabase import ClientOptions, create_client

supabase_vault = create_client(
    config("SUPABASE_URL"),
    config("SUPABASE_KEY"),
    options=ClientOptions(schema="vault"),
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class DatabaseSessionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, Any] = {}):
        self._engine = create_async_engine(
            host,
            pool_size=20,
            max_overflow=0,
            pool_pre_ping=True,
            connect_args={"prepare_threshold": float("inf")},
            **engine_kwargs,
        )
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine)

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config("DB_URI"), {"echo": False})


async def get_db_session():
    async with sessionmanager.session() as session:
        yield session
