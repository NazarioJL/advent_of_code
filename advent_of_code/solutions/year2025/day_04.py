import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2025
DAY = 4


def parse_input(s) -> list[list[str]]:
    result = [[r for r in line] for line in s.splitlines()]
    for row in result:
        print("".join(row))
    return result


def remove_rolls(
    paper_rolls: list[list[str]], threshold: int = 4, remove: bool = False
) -> int:
    """Counts how many rolls can be removed from the grid

    :param paper_rolls: the paper roll list as a grid '@' = paper roll, '.' empty
    :param threshold: if a roll has less than the given threshold, it can be removed
    :param remove: remove the rolls from the input
    :return: the number of rolls that can be removed
    """
    rows = len(paper_rolls)
    cols = len(paper_rolls[0])

    # fmt: off
    directions = (
        (-1, -1), ( 0, -1), ( 1, -1),
        (-1,  0),           ( 1,  0),
        (-1,  1), ( 0,  1), ( 1,  1),
    )
    # fmt: on

    to_remove = []

    for row, col in (
        (row, col)
        for col in range(cols)
        for row in range(rows)
        if paper_rolls[row][col] == "@"
    ):
        roll_count = 0
        for d_row, d_col in directions:
            new_row = row + d_row
            new_col = col + d_col
            if (
                0 <= new_row < rows
                and 0 <= new_col < cols
                and paper_rolls[new_row][new_col] == "@"
            ):
                roll_count += 1
        if roll_count < threshold:
            to_remove.append((row, col))

    if remove:
        for row, col in to_remove:
            paper_rolls[row][col] = "."

    return len(to_remove)


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    paper_rolls = parse_input(s)
    part_1 = remove_rolls(paper_rolls)

    part_2 = 0
    while removed := remove_rolls(paper_rolls, remove=True):
        part_2 += removed

    return part_1, part_2


TEST_INPUT = """\
..@@.@@@@.
@@@.@.@.@@
@@@@@.@.@@
@.@@@@..@.
@@.@@@@.@@
.@@@@@@@.@
.@.@.@.@@@
@.@@@.@@@@
.@@@@@@@@.
@.@.@@@.@.
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    [
        (TEST_INPUT, (13, 43)),
    ],
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
