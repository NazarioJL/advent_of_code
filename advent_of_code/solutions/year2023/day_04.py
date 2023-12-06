from typing import FrozenSet
from typing import Iterable
from typing import NamedTuple

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2023
DAY = 4


class ScratchCard(NamedTuple):
    card_id: int
    winning_nums: FrozenSet[int]
    owned_nums: FrozenSet[int]


def parse_input(s: str) -> Iterable[ScratchCard]:
    for line in s.splitlines():
        card_info, rest = line.split(": ", maxsplit=1)
        card_id = int(card_info.split()[-1])
        winning_nums, owned_nums = rest.split("|")

        yield ScratchCard(
            card_id=card_id,
            winning_nums=frozenset(int(n) for n in winning_nums.split()),
            owned_nums=frozenset(int(n) for n in owned_nums.split()),
        )


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    scratch_cards = list(parse_input(s))

    # Matches won at each card
    matches = [len(card.owned_nums & card.winning_nums) for card in scratch_cards]

    part_1 = sum(1 << (match_count - 1) for match_count in matches if match_count > 0)

    total_cards = [1] * len(matches)

    for card_id, match_count in enumerate(matches):
        contrib = total_cards[card_id]
        for i in range(match_count):
            total_cards[card_id + 1 + i] += contrib

    return part_1, sum(total_cards)


TEST_INPUT = """\
Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19
Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1
Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83
Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36
Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (13, 30)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
