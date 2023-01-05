from enum import Enum
from typing import Iterable

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2022
DAY = 2


class Item(Enum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3


LEFT_MAP = {
    "A": Item.ROCK,
    "B": Item.PAPER,
    "C": Item.SCISSORS,
}

RIGHT_MAP = {
    "X": Item.ROCK,
    "Y": Item.PAPER,
    "Z": Item.SCISSORS,
}

LOSES_TO = {
    Item.ROCK: Item.SCISSORS,
    Item.PAPER: Item.ROCK,
    Item.SCISSORS: Item.PAPER,
}

BEATS = {v: k for k, v in LOSES_TO.items()}


def score_round_part_1(them: Item, me: Item) -> int:
    score = me.value
    if them == me:
        return score + 3  # draw
    if them == LOSES_TO[me]:
        return score + 6  # me wins
    return score  # me loses


def score_round_part_2(left: str, right: str) -> int:
    them = LEFT_MAP[left]
    match right:
        case "X":  # me must lose
            me = LOSES_TO[them]
        case "Y":  # draw
            me = them
        case "Z":  # me must win
            me = BEATS[them]
        case _:
            raise ValueError

    return score_round_part_1(them, me)


def parse_input(s: str) -> Iterable[tuple[str, str]]:
    for line in s.splitlines():
        left, right = line.split()
        yield left, right


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    part_1 = sum(
        score_round_part_1(LEFT_MAP[left], RIGHT_MAP[right])
        for left, right in parse_input(s)
    )
    part_2 = sum(score_round_part_2(left, right) for left, right in parse_input(s))

    return part_1, part_2


TEST_INPUT = """\
A Y
B X
C Z
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (15, 12)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
