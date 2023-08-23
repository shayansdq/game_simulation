from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from enums import PlayerActionEnum


class PlayerActionData(BaseModel):
    action: PlayerActionEnum
    player_id: int = Field(ge=1)
    robot_id: int = Field(ge=1, le=10)


class ObjectModel(BaseModel):
    id: int
    x_position: int
    y_position: int


class BoardGameModel(BaseModel):
    id: int
    finished: bool
    created: datetime

    class Config:
        orm_mode = True


class PlayerModel(BaseModel):
    id: int
    point: int
