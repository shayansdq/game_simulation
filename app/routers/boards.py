from fastapi import Depends
# from sqlalchemy import create_engine
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session
# from database import SessionLocal
from main import app
from app.utils import get_db



# @app.post('/start_game/')
# async def create_new_board_game(db: AsyncSession = Depends(get_db)):
#     async with db.begin():
#         query = models.BoardGame.insert().values(finish)
#         await db.execute(query)


@app.get('/start_game/')
def create_new_board_game(db: Session=Depends(get_db)):
    refresh_db