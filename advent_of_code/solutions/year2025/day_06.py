import operator
from collections import defaultdict
from functools import reduce

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2025
DAY = 6


def get_nums_part_1(data: list[str]) -> list[list[int]]:
    num_rows = [[int(num) for num in line.split()] for line in data]
    rows = len(num_rows)
    cols = len(num_rows[0])
    return [[num_rows[row][col] for row in range(rows)] for col in range(cols)]


def get_nums_part_2(data: list[str]) -> list[list[int]]:
    group = 0
    group_nums: dict[int, list[int]] = defaultdict(list)
    # makes assumption all lines have same number of chars
    cols = len(data[0])
    rows = len(data)

    for col in range(cols):
        curr_num = 0
        found_num = False
        for row in range(rows):
            if (cell := data[row][col]).isdigit():
                curr_num *= 10
                curr_num += int(cell)
                found_num = True
        if found_num:
            group_nums[group].append(curr_num)
        else:
            group += 1

    return [v for v in group_nums.values()]


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    lines = s.splitlines()
    num_data = lines[:-1]
    ops = [op for op in lines[-1].split()]

    nums_part_1 = get_nums_part_1(num_data)
    nums_part_2 = get_nums_part_2(num_data)

    op_lookup = {"*": operator.mul, "+": operator.add}
    init_lookup = {"*": 1, "+": 0}
    return tuple(
        sum(
            reduce(
                op_lookup[op],
                num_group,
                init_lookup[op],
            )
            for op, num_group in zip(ops, nums)
        )
        for nums in (nums_part_1, nums_part_2)
    )


TEST_INPUT = """\
123 328  51 64
 45 64  387 23
  6 98  215 314
*   +   *   +
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    [
        (TEST_INPUT, (4277556, 3263827)),
    ],
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
