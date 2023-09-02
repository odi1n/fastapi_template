from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from src.settings import setting

BaseModel = declarative_base()


class Database:
    def __init__(self) -> None:
        self._engine = create_async_engine(setting.DB_DSN, echo=setting.DEBUG)
        self._async_session = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    def create_database(self) -> None:
        BaseModel.metadata.create_all(self._engine)

    @asynccontextmanager
    async def get_session(
        self,
    ) -> AsyncIterator[AsyncSession]:
        async with self._async_session() as session:
            yield session
