from functools import cache
from typing import cast

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2025
DAY = 3


def largest_right(nums: list[int]) -> list[int]:
    """Memoize the largest value to the right of any index"""
    result = [-1] * len(nums)
    result[-1] = float("-inf")  # type: ignore
    for i in reversed(range(len(nums) - 1)):
        result[i] = max(result[i + 1], nums[+1])

    return result


def find_largest_part_1(num: str) -> int:
    nums = [int(n) for n in num]
    right = largest_right(nums)
    candidate = cast(int, float("-inf"))  # just lie to mypy
    for n, r in zip(nums[:-1], right[:-1]):
        # n is current number, and r is largest possible to the right
        tmp = n * 10 + r
        candidate = max(tmp, candidate)

    return candidate


def find_largest_part_2(num: str, size: int = 12) -> int:
    nums = [int(n) for n in num]

    # TODO: potential optimization, prune intermediate values that will never become
    #       larger than a previous candidate result

    @cache
    def search(total_digits: int, pos: int = 0) -> int:
        if total_digits == size:
            return 0
        # do we have enough digits left
        nums_remaining = len(nums) - pos
        nums_required = size - total_digits
        if nums_remaining < nums_required:
            return 0
        # take current number
        num_at_pos = nums[pos]
        take_current = num_at_pos * (10 ** (size - total_digits - 1)) + search(
            total_digits + 1, pos + 1
        )
        skip_current = search(total_digits, pos + 1)
        return max(take_current, skip_current)

    return search(0, 0)


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    part_1 = sum(find_largest_part_1(line) for line in s.splitlines())
    part_2 = sum(find_largest_part_2(line) for line in s.splitlines())
    return part_1, part_2


TEST_INPUT = """\
987654321111111
811111111111119
234234234234278
818181911112111
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    [
        (TEST_INPUT, (357, 3121910778619)),
    ],
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
