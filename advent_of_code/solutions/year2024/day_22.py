from collections import defaultdict
from collections import deque
from itertools import pairwise
from unittest.mock import ANY

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2024
DAY = 22


def mix(secret: int, num: int) -> int:
    return secret ^ num


def prune(secret: int) -> int:
    return secret % 16777216


def evolve(secret: int) -> int:
    x_1 = secret * 64
    secret = mix(secret, x_1)
    secret = prune(secret)

    x_2 = secret // 32
    secret = mix(secret, x_2)
    secret = prune(secret)

    x_3 = secret * 2048
    secret = mix(secret, x_3)
    secret = prune(secret)
    return secret


def find_max_bananas(sellers: list[list[int]]) -> int:
    changes_to_sum: dict[tuple[int, int, int, int], int] = defaultdict(int)

    for seller, secrets in enumerate(sellers):
        queue: deque[int] = deque()
        for p, n in pairwise(secrets[0:5]):
            queue.append((n - p))

        seen = {tuple(queue)}
        assert len(queue) == 4
        changes_to_sum[tuple(queue)] += secrets[4] % 10  # type: ignore

        for p, n in pairwise(secrets[4:]):
            queue.append((n - p))
            queue.popleft()
            assert len(queue) == 4
            diff_id = tuple(queue)
            if tuple(diff_id) in seen:
                continue

            seen.add(diff_id)
            changes_to_sum[diff_id] += n  # type: ignore

    return max(changes_to_sum.values())


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    starters = [int(ns.strip()) for ns in s.splitlines()]

    sellers: list[list[int]] = []
    sellers_tens: list[list[int]] = []  # Get digit in tens

    for index, starter in enumerate(starters):
        lst = []
        lst_tens = []
        for _ in range(2001):
            lst.append(starter)
            lst_tens.append(starter % 10)
            starter = evolve(starter)
        sellers.append(lst)
        sellers_tens.append(lst_tens)

    part_1 = sum(lst[-1] for lst in sellers)
    part_2 = find_max_bananas(sellers_tens)

    return part_1, part_2


TEST_INPUT = """\
1
10
100
2024
"""


TEST_INPUT_2 = """\
1
2
3
2024
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    (
        (TEST_INPUT, (37327623, ANY)),
        (TEST_INPUT_2, (ANY, 23)),
    ),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


def test_mix() -> None:
    assert mix(42, 15) == 37


def test_prune() -> None:
    assert prune(100000000) == 16113920


def test_evolve() -> None:
    evolved = [
        15887950,
        16495136,
        527345,
        704524,
        1553684,
        12683156,
        11100544,
        12249484,
        7753432,
        5908254,
    ]

    num = 123

    for e in evolved:
        assert evolve(num) == e
        num = e


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
