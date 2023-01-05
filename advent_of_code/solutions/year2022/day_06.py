from collections import Counter

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2022
DAY = 6


def get_start_of_message(msg: str, length: int) -> int:
    fst = 0
    snd = 0

    buffer: Counter[str] = Counter()

    while snd < length:
        buffer.update(msg[snd])
        snd += 1

    while snd < len(msg):
        if len(buffer) == length:
            return snd
        else:
            buffer.update(msg[snd])
            buffer.subtract(msg[fst])
            fst += 1
            snd += 1
            # remove 0s
            to_remove = []
            for key in buffer.keys():
                if buffer[key] <= 0:
                    to_remove.append(key)

            for key in to_remove:
                buffer.pop(key)

    raise ValueError(f"No sequence of {length} distinct characters found")


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    return get_start_of_message(s, 4), get_start_of_message(s, 14)


TEST_INPUT = """\
"""


@pytest.mark.parametrize(
    ("input_s", "length", "expected"),
    (
        ("mjqjpqmgbljsphdztnvjfqwrcgsmlb", 4, 7),
        ("bvwbjplbgvbhsrlpgdmjqwftvncz", 4, 5),
        ("nppdvjthqldpwncqszvftbrmjlhg", 4, 6),
        ("nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg", 4, 10),
        ("zcfzfwzzqfrljwzlrfnpqdbhtmscgvjw", 4, 11),
        ("mjqjpqmgbljsphdztnvjfqwrcgsmlb", 14, 19),
        ("bvwbjplbgvbhsrlpgdmjqwftvncz", 14, 23),
        ("nppdvjthqldpwncqszvftbrmjlhg", 14, 23),
        ("nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg", 14, 29),
        ("zcfzfwzzqfrljwzlrfnpqdbhtmscgvjw", 14, 26),
    ),
)
def test_solve(input_s: str, length: int, expected: int) -> None:
    assert get_start_of_message(input_s, length) == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
