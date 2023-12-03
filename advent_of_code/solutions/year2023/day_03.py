import operator
from collections import defaultdict
from functools import reduce
from typing import TypeAlias

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


Coord: TypeAlias = tuple[int, int]

# NumberLocation uniquely identifies a number in the schematic
#     |<-length->|
#     123456789101
#     |
#   [x,y]: Coord

NumberLocation: TypeAlias = tuple[Coord, int]


YEAR = 2023
DAY = 3

ADJACENT_NODES = (
    (-1, 1),
    (0, 1),
    (1, 1),
    (-1, 0),
    (1, 0),
    (-1, -1),
    (0, -1),
    (1, -1),
)


def lft(coord: Coord) -> Coord:
    return coord[0] - 1, coord[1]


def rgt(coord: Coord) -> Coord:
    return coord[0] + 1, coord[1]


def get_number(schematic: dict[Coord, str], coord: Coord) -> tuple[NumberLocation, int]:
    # Go all the way to the beginning
    start_coord = coord

    while (left := lft(start_coord)) in schematic and schematic[left].isdigit():
        start_coord = left

    result_num = 0
    current = start_coord
    num_length = 0

    while current in schematic and schematic[current].isdigit():
        result_num = result_num * 10 + int(schematic[current])
        num_length += 1
        current = rgt(current)

    return (start_coord, num_length), result_num


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    schematic: dict[Coord, str] = {}
    symbols: list[Coord] = []

    for row, line in enumerate(s.splitlines()):
        for col, char in enumerate(line):
            if char == ".":  # ignore empty space
                continue

            current = col, row  # use (x,y)
            schematic[col, row] = char

            if not char.isdigit():
                symbols.append(current)

    numbers: dict[NumberLocation, int] = {}
    visited: set[Coord] = set()

    gears: dict[Coord, list[int]] = defaultdict(list)

    for col, row in symbols:
        for col_off, row_off in ADJACENT_NODES:
            adj_node = col + col_off, row + row_off
            if adj_node not in schematic or adj_node in visited:
                continue
            visited.add(adj_node)
            if schematic[adj_node].isdigit():
                num_loc, number = get_number(schematic, adj_node)
                if num_loc in numbers:
                    continue
                numbers[num_loc] = number
                if schematic[col, row] == "*":
                    gears[col, row].append(number)

    part_1 = sum(numbers.values())
    part_2 = sum(
        reduce(operator.mul, gear_lst)
        for gear_lst in gears.values()
        if len(gear_lst) == 2
    )

    return part_1, part_2


TEST_INPUT = """\
467..114..
...*......
..35..633.
......#...
617*......
.....+.58.
..592.....
......755.
...$.*....
.664.598..
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (4361, 467835)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
