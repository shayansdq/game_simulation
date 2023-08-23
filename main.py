# from fastapi import FastAPI
# from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from asyncpg import transaction
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession
import db
from http import HTTPStatus
import models
from sqlalchemy import select

from app.schemas import PlayerActionData, BoardGameModel
from app.utils import do_action, start_game
from enums import PlayerActionEnum


async def get_db():
    async with AsyncSession(db.engine) as session:
        async with session.begin():
            yield session


app = FastAPI()


@app.post("/start_game/", status_code=HTTPStatus.CREATED)
async def start_new_game(db: AsyncSession = Depends(get_db)):
    try:
        board_game = await start_game(db)
        return board_game
    except InvalidRequestError as e:
        # Handle the closed transaction error
        raise HTTPException(status_code=500, detail="Failed to start game: Transaction already closed")


@app.post("/action/", status_code=HTTPStatus.ACCEPTED, )
async def do_action_api(data: PlayerActionData, db: AsyncSession = Depends(get_db)):
    try:
        # print('in req')
        res = await do_action(data, db)
        return res
    except InvalidRequestError as e:
        # Handle the closed transaction error
        raise HTTPException(status_code=500, detail="Failed to start game: Transaction already closed")
