from collections import defaultdict
from functools import cmp_to_key
from itertools import pairwise
from typing import Iterable

import pytest
from more_itertools.recipes import partition

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2024
DAY = 5


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    page_ordering_rules, updates = s.split("\n\n")

    ordering_rules: list[tuple[str, str]] = [
        (split[0], split[1])
        for rule in page_ordering_rules.splitlines()
        if (split := rule.split("|", maxsplit=1))
    ]

    # Build graph of relative positions between pages
    # NOTE: I attempted to create a graph and topologically sort it. This works for the
    # sample data, but not for my input as it has cycles.
    rel = defaultdict(set)
    for p, n in ordering_rules:
        rel[p].add(n)

    def is_sorted(updates_: list[str]) -> bool:
        """Tests an update to verify they are all sorted"""
        for prev_page, next_page in pairwise(updates_):
            if next_page not in rel[prev_page]:
                return False
        return True

    page_updates = [update.split(",") for update in updates.splitlines()]
    bad_updates, good_updates = partition(is_sorted, page_updates)

    def page_compare(a: str, b: str) -> int:
        if b in rel[a]:  # b comes after a, b > a
            return -1
        elif a in rel[b]:  # a comes after b, a > b
            return 1
        else:
            return 0

    fixed_updates = []
    for bad_update in bad_updates:
        bad_update.sort(key=cmp_to_key(page_compare))
        fixed_updates.append(bad_update)

    def get_sum(updates_: Iterable[list[str]]) -> int:
        return sum(int(update_[len(update_) // 2]) for update_ in updates_)

    part_1 = get_sum(good_updates)
    part_2 = get_sum(fixed_updates)

    return part_1, part_2


TEST_INPUT = """\
47|53
97|13
97|61
97|47
75|29
61|13
75|53
29|13
97|29
53|29
61|53
97|53
61|29
47|13
75|47
97|75
47|61
75|61
47|29
75|13
53|13

75,47,61,53,29
97,61,53,29,13
75,29,13
75,97,47,61,53
61,13,29
97,13,75,29,47
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (143, 123)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    print()
    assert solve(TEST_INPUT).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
