from typing import List
# from sqlalchemy.ext.asyncio import AsyncSession
import databases
from sqlalchemy import Column, Integer, String, UniqueConstraint, Boolean
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
from db import Base


class ObjectPosition(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    x_position: Mapped[int] = mapped_column(nullable=False)
    y_position: Mapped[int] = mapped_column(nullable=False)
    __abstract__ = True


class Robot(ObjectPosition):
    __tablename__ = 'robots'
    __table_args__ = (
        UniqueConstraint("x_position",
                         "y_position",
                         name="exact_position_robots"),
    )

    def __repr__(self):
        return f"<Robot ({self.id})-> position: ({self.x_position},{self.y_position})"


class Dinosaur(ObjectPosition):
    __tablename__ = 'dinosaurs'
    killed: Mapped[bool] = mapped_column(default=False, nullable=False)
    __table_args__ = (
        UniqueConstraint("x_position",
                         "y_position",
                         name="exact_position_dinosaurs"),
    )

    def __repr__(self):
        return f"<Dinosaur ({self.id})-> position: ({self.x_position},{self.y_position})"


class BoardGame(Base):
    __tablename__ = 'boardgame'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    finished: Mapped[bool] = mapped_column(default=False)
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    def __repr__(self):
        return f"<BoardGame ({self.id})-> finished: {self.finished}, created: {self.created}"


class Player(Base):
    __tablename__ = 'players'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    point: Mapped[int] = mapped_column(default=0)

    def __repr__(self):
        return f"<Player ({self.id})-> point: {self.point}"
