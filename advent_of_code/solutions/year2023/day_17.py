from typing import Iterable
from typing import TypeAlias

import pytest

from advent_of_code.algorithms.astar import a_star_search
from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.grids import Coord2D
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2023
DAY = 17


State: TypeAlias = tuple[Coord2D, str]


class LavaPoolAStarSearch:
    _DIRECTIONS = {
        "<": (-1, 0),  # left
        ">": (1, 0),  # right
        "^": (0, -1),  # up
        "v": (0, 1),  # down
    }

    _OPPOSITES = {
        ">": "<",
        "^": "v",
        "<": ">",
        "v": "^",
    }

    def __init__(self, values: list[list[int]]) -> None:
        self._values = values
        self._width = len(values[0])
        self._height = len(values)

    def get_adjacent_1(self, state: State) -> Iterable[tuple[State, int]]:
        coord, dirs = state

        for dir_, offset in self._DIRECTIONS.items():
            new_cord = coord + offset
            if 0 <= new_cord.x < self._width and 0 <= new_cord.y < self._height:
                if self._OPPOSITES[dir_] in dirs:
                    continue
                cost_to_node = self._values[new_cord.y][new_cord.x]
                if dir_ in dirs:
                    # Can only move in same direction until 3 consecutive
                    if len(dirs) < 3:
                        yield (new_cord, dirs + dir_), cost_to_node
                else:
                    # Just ignore old direction memory _e.g._ ">>" -> "v"
                    yield (new_cord, dir_), cost_to_node

    def get_adjacent_2(self, state: State) -> Iterable[tuple[State, int]]:
        coord, dirs = state

        for dir_, offset in self._DIRECTIONS.items():
            new_cord = coord + offset
            if 0 <= new_cord.x < self._width and 0 <= new_cord.y < self._height:
                cost_to_node = self._values[new_cord.y][new_cord.x]
                opp = self._OPPOSITES[dir_]
                if opp in dirs:
                    continue

                if dir_ in dirs or len(dirs) == 0:
                    if len(dirs) < 10:
                        yield (new_cord, dirs + dir_), cost_to_node
                else:
                    if len(dirs) >= 4:  # Only turn if it's current path is 4 or more
                        yield (new_cord, dir_), cost_to_node

    def heuristic(self, state_1: State, state_2: State) -> int:
        # Manhattan distance should be fine
        return abs(state_1[0].x - (self._width - 1)) + abs(
            state_1[0].y - (self._height - 1)
        )

    @property
    def start(self) -> Coord2D:
        return Coord2D(x=0, y=0)

    def goal_1(self, state: State) -> bool:
        coord, _ = state
        return coord.x == (self._width - 1) and coord.y == (self._height - 1)

    def goal_2(self, state: State) -> bool:
        coord, dirs = state
        return (
            coord.x == (self._width - 1)
            and coord.y == (self._height - 1)
            and len(dirs) >= 4
        )

    @staticmethod
    def from_str(s: str) -> "LavaPoolAStarSearch":
        values: list[list[int]] = []

        for row in s.splitlines():
            curr_row = [int(c) for c in row]
            values.append(curr_row)

        return LavaPoolAStarSearch(values=values)


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    lava_pool = LavaPoolAStarSearch.from_str(s)

    path_1 = a_star_search(
        start=(lava_pool.start, ""),
        goal=lava_pool.goal_1,
        heuristic=lava_pool.heuristic,
        get_adjacent=lava_pool.get_adjacent_1,
    )

    path_2 = a_star_search(
        start=(lava_pool.start, ""),
        goal=lava_pool.goal_2,
        heuristic=lava_pool.heuristic,
        get_adjacent=lava_pool.get_adjacent_2,
    )

    return path_1[-1][1], path_2[-1][1]


TEST_INPUT_1 = """\
2413432311323
3215453535623
3255245654254
3446585845452
4546657867536
1438598798454
4457876987766
3637877979653
4654967986887
4564679986453
1224686865563
2546548887735
4322674655533
"""

TEST_INPUT_2 = """\
111111111111
999999999991
999999999991
999999999991
999999999991
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    (
        (TEST_INPUT_1, (102, 94)),
        (TEST_INPUT_2, (59, 71)),
    ),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
