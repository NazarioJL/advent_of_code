from functools import reduce
from typing import Literal
from typing import NamedTuple
from typing import TypeAlias

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2025
DAY = 1

Rotation: TypeAlias = Literal["L", "R"]


class State(NamedTuple):
    position: int
    total_lands_on_origin: int
    total_rotations_over_origin: int


class RotateResult(NamedTuple):
    position: int
    rotations_over_origin: int


def rotate(current: int, size: int, direction: Rotation, n: int) -> RotateResult:
    """
    Rotates a dial and returns a result that represents the position the dial landed in
    and how many times we've rotated over the origin

    :param current: The current position of the dial
    :param size: The size of the dial
    :param direction: The direction to rotate the dial in one of ('L', 'R')
    :param n: How many position to rotate
    :return: The new position and the number of times we've rotated over the origin
    """
    full_rotations, n = divmod(n, size)
    over_zero = 0

    match direction:
        case "R":
            if current > 0 and n >= 100 - current:
                over_zero += 1
            next_pos = current + n
        case "L":
            if n > current > 0:
                over_zero += 1
            next_pos = current - n

    over_zero += full_rotations
    return RotateResult(next_pos % 100, over_zero)


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    start_state: State = State(50, 0, 0)

    def acc_func(state: State, e: tuple[Rotation, int]) -> State:
        res = rotate(state.position, 100, e[0], e[1])
        return State(
            res.position,
            state.total_lands_on_origin + (1 if res.position == 0 else 0),
            state.total_rotations_over_origin + res.rotations_over_origin,
        )

    end_state = reduce(
        acc_func, ((line[0], int(line[1:])) for line in s.splitlines()), start_state
    )

    return end_state[1], end_state[2]


TEST_INPUT = """\
L68
L30
R48
L5
R60
L55
L1
L99
R14
L82
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    [
        (TEST_INPUT, (3, 6)),
    ],
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))


@pytest.mark.parametrize(
    ("current", "direction", "qty", "expected"),
    [
        (50, "R", 1000, (50, 10)),
        (0, "R", 100, (0, 1)),
        (0, "R", 101, (1, 1)),
        (0, "L", 100, (0, 1)),
        (0, "L", 101, (99, 1)),
        (1, "L", 2, (99, 1)),
        (1, "L", 102, (99, 2)),
        (0, "R", 200, (0, 2)),
        (0, "R", 199, (99, 1)),
    ],
)
def test_rotate(current, direction, qty, expected):
    assert rotate(current, 100, direction, qty) == expected
