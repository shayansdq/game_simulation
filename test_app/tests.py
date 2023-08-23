# tests.py
import asyncio
from sqlalchemy import NullPool
from .models_test import *
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from main import get_db

DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/game_test"
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    poolclass=NullPool,
)
TestingSessionLocal = async_sessionmaker(bind=engine,
                                         class_=AsyncSession,
                                         expire_on_commit=False)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()


asyncio.run(create_db())


async def override_get_db():
    async with AsyncSession(engine) as session:
        async with session.begin():
            yield session


app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)


def test_start_new_game():
    response = client.post(
        "/start_game/",
    )
    assert response.status_code == 201


def test_player_actions():
    response_1 = client.post(
        "/action/", json={
            'player_id': 1,
            'robot_id': 3,
            'action': 'u'
        }
    )
    response_2 = client.post(
        "/action/", json={
            'player_id': 2,
            'robot_id': 3,
            'action': 'u'
        }
    )
    response_3 = client.post(
        "/action/", json={
            'player_id': 2,
            'robot_id': 3,
            'action': 't'
        }
    )
    assert response_2.json()['detail'] == 'Your not a real player'
    assert response_3.status_code == 422
    assert response_1.status_code in [403, 202]


