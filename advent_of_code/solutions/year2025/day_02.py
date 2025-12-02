import pytest
from more_itertools.more import chunked

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.exceptions import SolutionNotImplementedError
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2025
DAY = 2


def brute_force_part_1(lower: int, upper: int) -> int:
    result = 0
    for i in range(lower, upper + 1):
        str_val = str(i)
        size = len(str_val)
        if size % 2 != 0:
            continue
        mid = size // 2
        if str_val[0: mid] == str_val[mid : size]:
            result += i

    return result

def brute_force_part_2(lower: int, upper: int, factors: dict[int, set[int]]) -> int:
    invalid_ids = set()
    for i in range(lower, upper + 1):
        if i < 10:
            continue
        str_val = str(i)
        for factor in factors[len(str_val)]:
            it = chunked(str_val, factor)
            first = next(it)
            if all(first == chunk for chunk in it):
                invalid_ids.add(i)
                break
    return sum(invalid_ids)


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    range_values = []
    for ranges in s.split(","):
        lower, upper = ranges.split("-")
        range_values.append((int(lower), int(upper)))

    part_1 = sum(brute_force_part_1(lower, upper) for lower, upper in range_values)

    max_length = max(max(len(str(lower)), len(str(upper))) for lower, upper in range_values)

    factors = {i: {1} for i in range(1, max_length + 1)}
    for i in range(1, max_length + 1):
        for j in range(1, i):
            if i % j == 0:
                factors[i].add(j)

    print(factors)

    part_2 = sum(brute_force_part_2(lower, upper, factors) for lower, upper in range_values)

    return part_1, part_2


TEST_INPUT = """\
11-22,95-115,998-1012,1188511880-1188511890,222220-222224,1698522-1698528,446443-446449,38593856-38593862,565653-565659,824824821-824824827,2121212118-2121212124
"""

@pytest.mark.parametrize(
    ("input_s", "expected"),
    [
        (TEST_INPUT, (1227775554, 4174379265)),
    ],
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))

