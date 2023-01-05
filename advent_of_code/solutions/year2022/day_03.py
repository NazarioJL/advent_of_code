import pytest
from more_itertools import chunked

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2022
DAY = 3


PRIORITY_LOWER = {chr(i): i - ord("a") + 1 for i in range(ord("a"), ord("a") + 26)}


PRIORITY_UPPER = {
    chr(i): i - ord("A") + PRIORITY_LOWER["z"] + 1
    for i in range(ord("A"), ord("A") + 26)
}

PRIORITY = {
    **PRIORITY_LOWER,
    **PRIORITY_UPPER,
}


def get_common_item_priority(rucksack: str) -> int:
    middle = len(rucksack) // 2
    first_half = set(rucksack[:middle])
    second_half = set(rucksack[middle:])

    common = first_half & second_half

    assert len(common) == 1

    return PRIORITY[common.pop()]


def get_common_item(r1: str, r2: str, r3: str) -> int:
    common = set(r1) & set(r2) & set(r3)

    assert len(common) == 1

    return PRIORITY[common.pop()]


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    rucksacks = s.splitlines()

    part_1 = sum(get_common_item_priority(rucksack=rucksack) for rucksack in rucksacks)
    part_2 = sum(
        get_common_item(*chunk) for chunk in chunked(rucksacks, 3, strict=True)
    )

    return part_1, part_2


TEST_INPUT = """\
vJrwpWtwJgWrhcsFMMfFFhFp
jqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL
PmmdzqPrVvPwwTWBwg
wMqvLMZHhHMvwLHjbvcjnnSBnvTQFn
ttgJtRGJQctTZtZT
CrZsJsPPZsGzwwsLwLmpwMDw
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (157, 70)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
