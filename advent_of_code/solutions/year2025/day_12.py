from typing import NamedTuple

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2025
DAY = 12


Shape = tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]


class Space(NamedTuple):
    height: int
    width: int


class Requirement(NamedTuple):
    shape_id: int
    quantity: int


class Configuration(NamedTuple):
    space: Space
    requirements: list[Requirement]


class PuzzleInput(NamedTuple):
    shapes: dict[int, Shape]
    configurations: list[Configuration]


def parse_input(s: str) -> PuzzleInput:
    chunks = s.split("\n\n")

    def _cell_to_num(cell: str) -> int:
        if cell == "#":
            return 1
        return 0

    def _parse_shape(shape_data: str) -> tuple[int, Shape]:
        lines = shape_data.splitlines()
        num = int(lines[0].split(":")[0])
        rows = []
        for row in lines[1:]:
            rows.append([_cell_to_num(c) for c in row])

        return num, tuple(rows)

    configurations = []

    for line in chunks[-1].splitlines():
        ss, reqs = line.split(":")
        w, h = ss.split("x")
        configurations.append(
            Configuration(
                space=Space(int(w), int(h)),
                requirements=[
                    Requirement(idx, int(qty))
                    for idx, qty in enumerate(reqs.strip().split(" "))
                ],
            )
        )

    return PuzzleInput(
        shapes=dict([_parse_shape(data) for data in chunks[1:-1]]),
        configurations=configurations,
    )


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    data = parse_input(s)
    maybe_fits = 0
    does_not_fit = 0
    for configuration in data.configurations:
        available_area = configuration.space.width * configuration.space.height
        required = sum(req.quantity for req in configuration.requirements) * 8
        if available_area >= required:
            maybe_fits += 1
        else:
            does_not_fit += 1

    return maybe_fits, 0


TEST_INPUT = """\
0:
###
##.
##.

1:
###
##.
.##

2:
.##
###
##.

3:
##.
###
##.

4:
###
#..
###

5:
###
.#.
###

4x4: 0 0 0 0 2 0
12x5: 1 0 1 0 2 2
12x5: 1 0 1 0 3 2
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    [
        (TEST_INPUT, (2, 0)),
    ],
)
def test_solve(input_s: str, expected: tuple[int, int]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
