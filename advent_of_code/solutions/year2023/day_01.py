from typing import Sequence

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2023
DAY = 1


DIGIT_TO_NUM = {str(v): v for v in range(1, 10)}

STRING_TO_NUM = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
}

COMBINED_LOOKUP = {**DIGIT_TO_NUM, **STRING_TO_NUM}  # Used in part 2


def find_occurrences(val: str, sub: str) -> Sequence[int]:
    """
    Find all occurrences of sub in val.

    :param val: The string to search in.
    :param sub: The string to search for.
    :return: A list of indices where sub occurs in val.
    """
    return [i for i in range(len(val)) if val.startswith(sub, i)]


def get_calibration_value(code: str, lookup: dict[str, int]) -> int:
    """
    Get the calibration value from the input data. This is done by concatenating the
    first occurrence of a number with the last to produce a 2-digit integer.

    Remarks:
        This currently is unnecessarily slow. It can be reduced from n * log(n) to n.

    :param code: The code to get calibration value from
    :param lookup: A lookup of string values to their associated integer value
    :return: A 2-digit number
    """

    nums_with_pos = sorted(
        (pos, val)
        for word, val in lookup.items()
        for pos in find_occurrences(code, word)
    )

    if not nums_with_pos:
        raise ValueError(f"Unexpected code: '{code}'")

    return nums_with_pos[0][1] * 10 + nums_with_pos[-1][1]  # Slow version


def get_calibration_sum(codes: list[str], lookup: dict[str, int]) -> int:
    """
    Get the sum of the calibration values from the input data.

    :param codes: The codes to get calibration value from
    :param lookup: A lookup of string values to their associated integer value
    :return: The sum of the calibration values
    """
    return sum(get_calibration_value(code, lookup) for code in codes)


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    codes = s.splitlines()
    part_1 = get_calibration_sum(codes, DIGIT_TO_NUM)
    part_2 = get_calibration_sum(codes, COMBINED_LOOKUP)
    return part_1, part_2


TEST_INPUT_1 = """\
1abc2
pqr3stu8vwx
a1b2c3d4e5f
treb7uchet
"""


TEST_INPUT_2 = """\
two1nine
eightwothree
abcone2threexyz
xtwone3four
4nineeightseven2
zoneight234
7pqrstsixteen
"""


@pytest.mark.parametrize(
    ("input_s", "lookup", "expected"),
    (
        (TEST_INPUT_1, DIGIT_TO_NUM, 142),
        (TEST_INPUT_2, COMBINED_LOOKUP, 281),
    ),
)
def test_get_calibration_sum(
    input_s: str, lookup: dict[str, int], expected: int
) -> None:
    print()
    assert get_calibration_sum(input_s.splitlines(), lookup) == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
