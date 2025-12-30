from collections import defaultdict
from functools import cache
from typing import Iterable

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2025
DAY = 11


type Graph = dict[str, list[str]]


def parse_input(s: str) -> Graph:
    graph: dict[str, list[str]] = defaultdict(list)
    for line in s.splitlines():
        parent, children = line.split(":")
        for child in children.lstrip().rstrip().split(" "):
            graph[parent].append(child)
    return graph


def count_paths(
    graph: Graph,
    start: str,
    end: str,
    required: Iterable[str] | None = None,
) -> int:
    mask_lookup = defaultdict(
        int, {k: 1 << idx for idx, k in enumerate(required or [])}
    )
    all_included = 2 ** len(mask_lookup) - 1

    @cache
    def count(n, mask: int = 0) -> int:
        nonlocal all_included
        if n == end and mask == all_included:
            return 1
        return sum(count(child, mask | mask_lookup[n]) for child in graph[n])

    return count(start)


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    graph = parse_input(s)
    part_1 = count_paths(graph, "you", "out")
    part_2 = count_paths(graph, "svr", "out", ["dac", "fft"])
    return part_1, part_2


TEST_INPUT = """\
aaa: you hhh
you: bbb ccc
bbb: ddd eee
ccc: ddd eee fff
ddd: ggg
eee: out
fff: out
ggg: out
hhh: ccc fff iii
iii: out
"""


TEST_INPUT_2 = """\
svr: aaa bbb
aaa: fft
fft: ccc
bbb: tty
tty: ccc
ccc: ddd eee
ddd: hub
hub: fff
eee: dac
dac: fff
fff: ggg hhh
ggg: out
hhh: out
"""


@pytest.mark.parametrize(
    ("test_input", "start", "end", "required", "expected"),
    [
        (TEST_INPUT, "you", "out", [], 5),
        (TEST_INPUT_2, "svr", "out", ["dac", "fft"], 2),
    ],
)
def test_count_paths(test_input, start, end, required, expected) -> None:
    graph = parse_input(test_input)
    assert count_paths(graph, start, end, required) == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
