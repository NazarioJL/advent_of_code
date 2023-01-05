from enum import auto
from enum import Enum
from typing import Iterable

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import AnswerType
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2022
DAY = 8

Grid = list[list[int]]
Coord = tuple[int, int]


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    CENTER = auto()


DIRECTION_OFFSET = {
    Direction.UP: (-1, 0),
    Direction.DOWN: (1, 0),
    Direction.RIGHT: (0, 1),
    Direction.LEFT: (0, -1),
    Direction.CENTER: (0, 0),
}


def parse_input(s: str) -> Grid:
    result: list[list[int]] = []
    for row in s.splitlines():
        result.append([int(c) for c in row])

    return result


def print_grid(grid: Grid) -> None:
    for row in grid:
        print("".join(str(r) for r in row))


def get_visible(grid: Grid, coords: Iterable[Coord]) -> Iterable[Coord]:
    prev: int | None = None
    for r, c in coords:
        curr = grid[r][c]
        if prev is None:
            prev = curr
            yield r, c
        else:
            if curr > prev:
                prev = curr
                yield r, c


def generate_grid_paths(rows: int, cols: int) -> Iterable[Iterable[Coord]]:
    # Generates all straight paths in a grid
    yield from (((r, c) for r in range(rows)) for c in range(cols))  # down
    yield from (((r, c) for r in reversed(range(rows))) for c in range(cols))  # up
    yield from (((r, c) for c in range(cols)) for r in range(rows))  # right
    yield from (
        ((r, c) for c in reversed(range(cols))) for r in reversed(range(rows))
    )  # left


@aoc.partial(part=1)
def part_1(grid: Grid) -> AnswerType:
    rows = len(grid)
    cols = len(grid[0])
    visible: set[Coord] = set()

    for path in generate_grid_paths(rows=rows, cols=cols):
        visible.update(get_visible(grid, path))

    return len(visible)


def calc_visibility_score_for_direction(grid: Grid, direction: Direction) -> Grid:
    len(grid)
    len(grid[0])

    return grid


def calc_visibility_score(grid: Grid, coord: Coord) -> int:
    dirs = (Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT)
    rows = len(grid)
    cols = len(grid[0])
    row, col = coord

    if row == 0 or col == 0:
        return 0

    curr_height = grid[row][col]

    score = 1

    for dir_ in dirs:
        row, col = coord

        row_off, col_off = DIRECTION_OFFSET[dir_]
        tmp_score = 0
        while True:
            row += row_off
            col += col_off

            if row < 0 or row >= rows or col < 0 or col >= cols:
                break

            new_val = grid[row][col]

            tmp_score += 1
            if new_val >= curr_height:
                break

        score *= tmp_score

    return score


@aoc.partial(part=2)
def part_2(grid: Grid) -> AnswerType:
    rows = len(grid)
    cols = len(grid[0])

    max_score = -1

    for row in range(rows):
        for col in range(cols):
            max_score = max(max_score, calc_visibility_score(grid, (row, col)))

    return max_score


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    grid = parse_input(s)
    return part_1(grid), part_2(grid)


TEST_INPUT = """\
30373
25512
65332
33549
35390
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (21, 8)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
