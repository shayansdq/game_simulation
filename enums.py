from enum import Enum


class PlayerActionEnum(str, Enum):
    UP = 'u'
    DOWN = 'd'
    RIGHT = 'r'
    LEFT = 'l'
    KILL = 'k'
