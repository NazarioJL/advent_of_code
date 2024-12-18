from typing import Callable
from typing import Iterable

import pytest

from advent_of_code.algorithms.astar import PathNotFoundError
from advent_of_code.algorithms.astar import a_star_search
from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.grids import Coord2D
from advent_of_code.screen import Screen
from advent_of_code.screen import ScreenOrigin
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2024
DAY = 18


State = tuple[int, int]


class Puzzle:
    def __init__(
        self, byte_locations: list[tuple[int, int]], cols: int = 71, rows: int = 71
    ) -> None:
        self._rows = rows
        self._cols = cols
        self._corrupted = set(byte_locations)
        self._start = (0, 0)
        self._end = (cols - 1, rows - 1)

    @property
    def start(self) -> State:
        return self._start

    @property
    def end(self) -> State:
        return self._end

    def goal(self) -> Callable[[State], bool]:
        def _goal(state: State) -> bool:
            return state == self._end

        return _goal

    def heuristic(self) -> Callable[[State, State], int]:
        def _heuristic(a: State, b: State) -> int:
            # get the manhattan distance
            (x_a, y_a) = a
            (x_b, y_b) = self._end

            d_x = x_b - x_a
            d_y = y_b - y_a

            if d_y == 0 and d_x == 0:
                return 0

            h = abs(d_x) + abs(d_y)

            return h

        return _heuristic

    def get_adjacent(self) -> Callable[[State], Iterable[tuple[State, int]]]:
        def _get_adjacent(state: State) -> Iterable[tuple[State, int]]:
            offsets = (
                (0, 1),
                (0, -1),
                (1, 0),
                (-1, 0),
            )
            x, y = state
            for off_x, off_y in offsets:
                new_x, new_y = x + off_x, y + off_y
                if (
                    (new_x, new_y) not in self._corrupted
                    and 0 <= new_x < self._cols
                    and 0 <= new_y < self._rows
                ):
                    yield (new_x, new_y), 1

        return _get_adjacent

    @property
    def corrupted(self) -> set[tuple[int, int]]:
        return self._corrupted

    @property
    def cols(self) -> int:
        return self._cols

    @property
    def rows(self) -> int:
        return self._rows


def print_puzzle(puzzle: Puzzle, path: list[Coord2D]) -> None:
    screen = Screen(
        start_x=0,
        start_y=0,
        end_x=puzzle.cols,
        end_y=puzzle.rows,
        screen_origin=ScreenOrigin.TOP_LEFT,
        default_pixel=".",
    )
    for corrupted in puzzle.corrupted:
        screen.draw(s="#", x=corrupted[0], y=corrupted[1])

    for p in path:
        screen.draw(s="O", x=p[0], y=p[1])

    screen.draw(s="S", x=puzzle.start[0], y=puzzle.start[1])
    screen.draw(s="E", x=puzzle.end[0], y=puzzle.end[1])

    screen.render()


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str, cols: int = 71, rows: int = 71, limit: int = 1024) -> Solution:
    byte_locations = []
    for line in s.splitlines():
        a, b = line.split(",")
        byte_locations.append((int(a), int(b)))

    puzzle = Puzzle(byte_locations[0:limit], cols, rows)

    path = a_star_search(
        start=puzzle.start,
        goal=puzzle.goal(),
        heuristic=puzzle.heuristic(),
        get_adjacent=puzzle.get_adjacent(),
    )

    part_1 = len(path) - 1
    part_2 = None

    for i in range(limit, len(byte_locations)):
        trimmed_bytes = byte_locations[0:i]
        puzzle = Puzzle(trimmed_bytes, cols, rows)
        try:
            a_star_search(
                start=puzzle.start,
                goal=puzzle.goal(),
                heuristic=puzzle.heuristic(),
                get_adjacent=puzzle.get_adjacent(),
            )
        except PathNotFoundError:
            part_2 = byte_locations[i - 1]
            break

    return part_1, str(part_2)


TEST_INPUT = """\
5,4
4,2
4,5
3,0
2,1
6,3
2,4
1,5
0,6
3,3
2,6
5,1
1,2
5,5
2,5
6,5
1,4
0,4
6,4
1,1
6,1
1,0
0,5
1,6
2,0
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (22, (6, 1))),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s, cols=7, rows=7, limit=12).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
