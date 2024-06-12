from enum import auto
from enum import Enum
from typing import Iterator
from typing import NamedTuple
from typing import Union


class Coord2D:
    """
    Represents a 2D coordinate
    """

    __slots__ = ("_x", "_y")

    def __init__(self, x: int, y: int) -> None:
        self._x = x
        self._y = y

    def __iter__(self) -> Iterator[int]:
        return iter([self._x, self._y])

    def __mul__(self, other: int) -> "Coord2D":
        if isinstance(other, int):
            return Coord2D(self.x * other, self.y * other)
        else:
            raise NotImplementedError

    def __add__(self, other: Union["Coord2D", tuple[int, int]]) -> "Coord2D":
        if isinstance(other, tuple):
            if len(other) != 2:
                raise ValueError("If adding a tuple, it must have length of 2")
            return Coord2D(
                self.x + other[0],
                self.y + other[1],
            )
        elif isinstance(other, Coord2D):
            return Coord2D(self.x + other.x, self.y + other.y)
        else:
            raise ValueError

    def __sub__(self, other: Union["Coord2D", tuple[int, int]]) -> "Coord2D":
        return (self * -1) + other

    def __hash__(self) -> int:
        return hash((self._x, self._y))

    def __str__(self) -> str:
        return f"Coord(x={self.x}, y={self.y})"

    def __repr__(self) -> str:
        return f"Coord(x={self.x}, y={self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Coord2D):
            return NotImplemented
        else:
            return self.x == other.x and self.y == other.y

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def as_tuple(self) -> tuple[int, int]:
        return self.x, self.y

    @staticmethod
    def from_tuple(val: tuple[int, int]) -> "Coord2D":
        return Coord2D(*val)

    def __lt__(self, other: "Coord2D") -> bool:
        return abs(self) < abs(other)

    def __abs__(self) -> int:
        return abs(self.x) + abs(self.y)


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
