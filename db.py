from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/game2"

meta = MetaData()


class Base(AsyncAttrs, DeclarativeBase):
    pass


engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

async_session = async_sessionmaker(bind=engine,
                                   class_=AsyncSession,
                                   expire_on_commit=False)
