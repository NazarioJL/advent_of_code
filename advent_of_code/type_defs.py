from enum import auto
from enum import Enum
from typing import NamedTuple
from typing import TypeAlias

NoAns: TypeAlias = None
AnswerType: TypeAlias = int | float | str | NoAns
Solution: TypeAlias = tuple[AnswerType, AnswerType]


class Coord2D(NamedTuple):
    x: int
    y: int

    def __add__(self, other: object) -> "Coord2D":
        if not isinstance(other, tuple):
            raise ValueError("expected a tuple object")
        x_, y_ = other
        return Coord2D(x=self.x + x_, y=self.y + y_)


class CardinalPoints(Enum):
    NORTH = auto()
    SOUTH = auto()
    EAST = auto()
    WEST = auto()
    CENTER = auto()
