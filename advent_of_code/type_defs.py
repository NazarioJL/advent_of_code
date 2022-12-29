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

    def __mul__(self, other: object) -> "Coord2D":
        if not isinstance(other, int):
            raise TypeError("Can only scale by an `int` value")
        return Coord2D(x=self.x * other, y=self.y * other)


class Coord3D(NamedTuple):
    x: int
    y: int
    z: int

    def __add__(self, other: object) -> "Coord3D":
        if not isinstance(other, tuple):
            raise ValueError("expected a tuple object")
        x_, y_, z_ = other
        return Coord3D(x=self.x + x_, y=self.y + y_, z=self.z + z_)

    def __mul__(self, other: object) -> "Coord3D":
        if not isinstance(other, int):
            raise TypeError("Can only scale by an `int` value")
        return Coord3D(x=self.x * other, y=self.y * other, z=self.z * other)


class CardinalPoints(Enum):
    NORTH = auto()
    SOUTH = auto()
    EAST = auto()
    WEST = auto()
    CENTER = auto()
