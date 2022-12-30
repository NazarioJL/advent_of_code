from abc import ABC
from enum import Enum
from itertools import cycle
from typing import Iterable
from typing import NamedTuple

import pytest
from more_itertools import peekable
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


def get_thumbprint(chamber: Chamber) -> int:
    """Create a hashable thumbprint of the chamber"""
    result = 0
    rows = 18
    for row in range(chamber.top, chamber.top - rows, -1):
        for i in (0, 1, 2, 3, 4, 5, 6):
            if (i, row) in chamber.occupied:
                result |= 1
            result <<= 1

    return result


class State(NamedTuple):
    rock_type: type[Rock]
    jet_move_index: int
    chamber_thumbprint: int


class PreCycleInfo(NamedTuple):
    rock_index: int
    height: int


class CycleResult(NamedTuple):
    end_index: int
    start_index: int
    cycle_height: int


def find_cycle(
    chamber: Chamber,
    rock_types: Iterable[type[Rock]],
    jet_moves: str,
) -> CycleResult:
    MAX_ROCKS = 100000
    rock_gen = take(MAX_ROCKS, (rock_type() for rock_type in cycle(rock_types)))
    move_gen = peekable(cycle(enumerate(jet_moves)))
    visited: dict[State, PreCycleInfo] = {}

    for rock_index, rock in enumerate(rock_gen):
        jet_index, _ = move_gen.peek()
        state = State(
            rock_type=type(rock),
            jet_move_index=jet_index,
            chamber_thumbprint=get_thumbprint(chamber),
        )

        if state in visited:
            cycle_start_state_value = visited[state]
            return CycleResult(
                start_index=cycle_start_state_value.rock_index,
                end_index=rock_index,
                cycle_height=chamber.top + 1 - cycle_start_state_value.height,
            )

        else:
            visited[state] = PreCycleInfo(rock_index=rock_index, height=chamber.top + 1)

        rock.translate(Coord2D(2, chamber.top + 3 + 1))  # drop rock
        while True:
            _, jet_move = next(move_gen)
            jet_move_tx = DIRECTION_TO_OFFSET[jet_move]
            try_move(rock=rock, chamber=chamber, move=jet_move_tx)
            if not try_move(rock=rock, chamber=chamber, move=DOWN):
                break
        chamber.add_rock(rock)

    raise UnexpectedConditionError("Unable to find a cycle")


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    rock_types = (HorLineRock, CrossRock, CornerRock, VertLineRock, SquareRock)
    jet_moves = s.strip()
    part_1 = simulate(
        chamber=Chamber(),
        jet_moves=jet_moves,
        rock_count=2022,
        rock_types=rock_types,
    )

    cycle_result = find_cycle(
        chamber=Chamber(), rock_types=rock_types, jet_moves=jet_moves
    )

    # We assume that there is a cyclic behavior in our simulation, each cycle
    # contributes to a specific height
    #
    # We will model a cycle like the following:
    #
    #    PRE      CYCLE0       CYCLE1  ... CYCLE_N-1    REM
    # └───────┴────────────┴────────────┴────────────┴───────┘
    # total = height(pre) + n * height(cycle) + height(rem)
    #
    # In our simulation we only need to do PRE, CYCLE0, REM as the rest is cyclic.
    #
    # Rearranging as:
    # total = height(pre + cycle + rem) + (n - 1) * height(cycle)
    #
    # We can then simulate the count for the first part

    TOTAL_ROCKS = 1000000000000

    pre_cycle_rock_count = cycle_result.start_index
    cycle_rock_count = cycle_result.end_index - cycle_result.start_index
    total_cycles, post_cycle_rock_count = divmod(
        TOTAL_ROCKS - pre_cycle_rock_count, cycle_rock_count
    )

    single_cycle_height = simulate(
        chamber=Chamber(),
        jet_moves=jet_moves,
        rock_count=pre_cycle_rock_count + cycle_rock_count + post_cycle_rock_count,
        rock_types=rock_types,
    )

    remaining_cycles_height = (total_cycles - 1) * cycle_result.cycle_height

    part_2 = single_cycle_height + remaining_cycles_height

    return part_1, part_2


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
