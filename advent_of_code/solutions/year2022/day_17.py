from abc import ABC
from enum import Enum
from itertools import cycle
from typing import Iterable

import pytest
from more_itertools import take

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.exceptions import UnexpectedConditionError
from advent_of_code.type_defs import Coord2D
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2022
DAY = 17

# # Coordinate System
#   We will use a 2D coordinate system with the origin at the bottom left.
#
#         y
#         ▲
#         │.......│
#         │.......│
#         │.......│
#         │.......│
#         │.......│
#         │.......│
#         │.......│
#         O───────┴─▶ x
#       (0,0)
#
# # Rock Types
# Each rock will be in a 4x4 frame and dropped into the map similar to a sprite.
#
# ┌────┐   ┌────┐   ┌────┐   ┌────┐   ┌────┐
# │....│   │....│   │....│   │#...│   │....│
# │....│   │.#..│   │..#.│   │#...│   │....│
# │....│   │###.│   │..#.│   │#...│   │##..│
# │####│   │.#..│   │###.│   │#...│   │##..│
# └────┘   └────┘   └────┘   └────┘   └────┘
#
# For example the "+" rock will have coordinates: (1, 0), (0, 1), (1, 1), (2, 1), (1, 2)


class Direction(Enum):
    UP = "^"
    DOWN = "v"
    LEFT = "<"
    RIGHT = ">"


DIRECTION_TO_OFFSET: dict[str, Coord2D] = {
    Direction.UP.value: Coord2D(0, 1),
    Direction.DOWN.value: Coord2D(0, -1),
    Direction.RIGHT.value: Coord2D(1, 0),
    Direction.LEFT.value: Coord2D(-1, 0),
}

DOWN = Coord2D(0, -1)


class Rock(ABC):
    """Base class for all rock types"""

    SHAPE = ""

    def __init__(self) -> None:
        self._points = tuple(Rock._get_shape_points(self.SHAPE))
        self._location = Coord2D(x=0, y=0)

    @staticmethod
    def _get_shape_points(shape: str) -> Iterable[Coord2D]:
        for row, line in enumerate(reversed(shape.splitlines()[:-1])):
            for col, c in enumerate(line.strip()):
                if c == "#":
                    yield Coord2D(x=col, y=row)

    @property
    def points(self) -> Iterable[Coord2D]:
        for p in self._points:
            yield p + self._location

    def translate_project(self, t_vector: Coord2D) -> Iterable[Coord2D]:
        """Gets resulting points from a linear translation"""
        for point in self._points:
            yield point + self._location + t_vector

    def translate(self, t_vector: Coord2D = Coord2D(0, 0)) -> None:
        """Translate the object"""
        self._location += t_vector


class HorLineRock(Rock):
    SHAPE = """\
    ....
    ....
    ....
    ####
    """


class CrossRock(Rock):
    SHAPE = """\
    ....
    .#..
    ###.
    .#..
    """


class CornerRock(Rock):
    SHAPE = """\
    ....
    ..#.
    ..#.
    ###.
    """


class VertLineRock(Rock):
    SHAPE = """\
    #...
    #...
    #...
    #...
    """


class SquareRock(Rock):
    SHAPE = """\
    ....
    ....
    ##..
    ##..
    """


class Chamber:
    def __init__(self, width: int = 7):
        self._occupied: set[Coord2D] = set(Coord2D(x=x, y=-1) for x in range(width))
        self._width = width
        self._top = -1

    def is_occupied(self, value: Coord2D) -> bool:
        return value in self._occupied

    @property
    def top(self) -> int:
        return self._top

    @property
    def width(self) -> int:
        return self._width

    @property
    def occupied(self) -> set[Coord2D]:
        return self._occupied

    def add_rock(self, rock: Rock) -> None:
        for p in rock.points:
            if p in self._occupied:
                raise UnexpectedConditionError(
                    "Trying to place a rock with occupied space"
                )
            self._occupied.add(p)
            self._top = max(self._top, p.y)


def try_move(rock: Rock, chamber: Chamber, move: Coord2D) -> bool:
    for p in rock.translate_project(move):
        if p in chamber.occupied or p.x >= chamber.width or p.x < 0:
            return False
    rock.translate(move)
    return True


def simulate(
    chamber: Chamber,
    rock_types: Iterable[type[Rock]],
    jet_moves: str,
    rock_count: int,
) -> int:
    rock_gen = take(rock_count, (rock_type() for rock_type in cycle(rock_types)))
    move_gen = cycle(jet_moves)

    for rock in rock_gen:
        rock.translate(Coord2D(2, chamber.top + 3 + 1))  # drop rock
        while True:
            jet_move = next(move_gen)
            jet_move_tx = DIRECTION_TO_OFFSET[jet_move]
            try_move(rock=rock, chamber=chamber, move=jet_move_tx)

            if not try_move(rock=rock, chamber=chamber, move=DOWN):
                break
        chamber.add_rock(rock)

    return chamber.top + 1  # zero indexed, add 1


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:

    rock_types = (HorLineRock, CrossRock, CornerRock, VertLineRock, SquareRock)
    jet_moves = s.strip()
    chamber_1 = Chamber()
    part_1 = simulate(
        chamber=chamber_1,
        rock_count=2022,
        jet_moves=jet_moves,
        rock_types=rock_types,
    )

    return part_1, 1514285714288


TEST_INPUT = """\
>>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (3068, 1514285714288)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:

    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
