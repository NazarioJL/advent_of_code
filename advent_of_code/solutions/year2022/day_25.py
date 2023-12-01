from math import log

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2022
DAY = 25


def stoi(s: str) -> int:
    result = 0
    power = 1

    for c in reversed(s):
        match c:
            case "-":
                result -= 1 * power
            case "=":
                result -= 2 * power
            case _:
                result += int(c) * power
        power *= 5

    return result


def itos(num: int) -> str:
    """
    Converts an integer to SNAFU. This is a base5 number that has coefficients that can
    be in [-2, -1, 0, 1, 2] as described by the day 25 🎄Advent of Code 2022 problem.

    Remarks:
        This code makes some assumptions I haven't formally proved 🤞. These are:
          1. Numbers consumed by `itos` have a perfect representation in SNAFU
          2. There is a unique solution to any number coming into `itos`
    :param num: an integer
    :return: the SNAFU representation
    """
    coeff_to_sym = {
        -2: "=",
        -1: "-",
        0: "0",
        1: "1",
        2: "2",
    }

    curr_power = int(log(num, 5))
    curr_sum = int((1 - 5 ** (curr_power + 1)) / (1 - 5) * 2)  # Geometric series
    curr_base = 5**curr_power
    coefficients = []

    while curr_power > 0:
        curr_sum = curr_sum - (curr_base << 1)
        for cf in (-2, -1, 0, 1, 2):
            candidate = num - cf * curr_base

            if abs(candidate) < curr_sum:
                coefficients.append(cf)
                num = candidate
                break
        curr_power -= 1
        curr_base //= 5

    # get what is left over, can only be -2, -1, 0, 1 or 2
    assert num in (-2, -1, 0, 1, 2)
    coefficients.append(num)

    return "".join(coeff_to_sym[c] for c in coefficients)


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    sum_of_n = sum(stoi(line) for line in s.splitlines())
    snafu = itos(sum_of_n)

    return snafu, None


TEST_INPUT = """\
1=-0-2
12111
2=0=
21
2=01
111
20012
112
1=-1=
1-12
12
1=
122
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, ("2=-1=0", None)),),
)
def test_solve(input_s: str, expected: str) -> None:
    assert solve(input_s).as_tuple() == expected


@pytest.mark.parametrize(
    ("s", "expected"),
    (
        ("1=-0-2", 1747),
        ("12111", 906),
        ("2=0=", 198),
        ("21", 11),
        ("2=01", 201),
        ("111", 31),
        ("20012", 1257),
        ("112", 32),
        ("1=-1=", 353),
        ("1-12", 107),
        ("12", 7),
        ("1=", 3),
        ("122", 37),
    ),
)
def test_stoi(s: str, expected: int) -> None:
    assert stoi(s) == expected


@pytest.mark.parametrize(
    ("n", "expected"),
    (
        (4890, "2=-1=0"),
        (35677038780996, "2-2--02=1---1200=0-1"),
    ),
)
def test_itos(n: int, expected: str) -> None:
    assert itos(n) == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
