import math
import re
from functools import reduce
from operator import mul

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2023
DAY = 6


def quad_solve(a: float, b: float, c: float) -> tuple[float, float]:
    """
    Solve quadratic equation ax^2 + bx + c = 0. Makes the assumption that all solutions
    are real.

    :param a: coefficient of x^2
    :param b: coefficient of x
    :param c: constant term
    :return: tuple of solutions to the equation.
    """

    d = math.sqrt(b * b - 4 * a * c)
    sol_1 = (-b + d) / (2 * a)
    sol_2 = (-b - d) / (2 * a)

    return sol_1, sol_2


def get_ways_to_break_record(max_time: int, current_record: int) -> int:
    """
    Finds all integer ways to beat the current record.

    Summary:

        Based on the rules, we can derive the following equations:

        Given:
          - t_t: The total time allowed
          - t_a: The time spent accelerating
          - t_r: Time spent running
          - v: The velocity achieved
          - d_m: The current max distance, or record
          - d_t: The total distance traveled

        Then:

            t_t = t_a + t_r
            v = t_a
            d_t = v * t_a = t_a * t_r = (t_t - t_a) * t_a

        This results in the quadratic equation:

            (-1) * t_a ^ 2 + t_t * t_a

        Finding the intersection with the horizontal d_m line, we get:

            (-1) * t_a ^ 2 + t_t * t_a - d_m = 0

        All is left, is to find all the integer values bounded by the solutions to the
        previous quadratic equation.

    :param max_time: The time allowed to race
    :param current_record: The record to beat
    :return: The total ways that the record can be beaten.
    """

    sol = quad_solve(a=-1, b=max_time, c=-current_record)
    left, right = math.ceil(min(sol)), math.floor(max(sol))

    result = 0

    # Check if integer solutions exists, this means the record is matched, not exceeded
    if int(left * (max_time - left)) == current_record:
        result -= 1

    if int(right * (max_time - right)) == current_record:
        result -= 1

    return result + math.floor(right) - math.ceil(left) + 1


def parse_nums(s: str) -> list[str]:
    _, *nums = re.split(r"\s+| : ", s)
    return nums


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    lines = s.splitlines()

    times_str = parse_nums(lines[0])
    dists_str = parse_nums(lines[1])

    times_1 = [int(t) for t in times_str]
    distances_1 = [int(d) for d in dists_str]

    part_1 = reduce(
        mul, (get_ways_to_break_record(t, d) for t, d in zip(times_1, distances_1))
    )

    time_2 = int("".join(times_str))
    dist_2 = int("".join(dists_str))

    part_2 = get_ways_to_break_record(time_2, dist_2)

    return part_1, part_2


TEST_INPUT = """\
Time:      7  15   30
Distance:  9  40  200
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (288, 71503)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
