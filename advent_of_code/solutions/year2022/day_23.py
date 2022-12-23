from collections import defaultdict
from typing import Literal

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.exceptions import UnexpectedConditionError
from advent_of_code.screen import Screen
from advent_of_code.type_defs import CardinalPoints
from advent_of_code.type_defs import Coord2D
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2022
DAY = 23

DIRECTIONS = [
    CardinalPoints.NORTH,
    CardinalPoints.SOUTH,
    CardinalPoints.WEST,
    CardinalPoints.EAST,
]

Directions = Literal["N", "S", "W", "E", "NE", "NW", "SE", "SW"]
[N, S, W, E, NE, NW, SE, SW] = ["N", "S", "W", "E", "NE", "NW", "SE", "SW"]


N_OFFSET = Coord2D(0, 1)
S_OFFSET = Coord2D(0, -1)
E_OFFSET = Coord2D(1, 0)
W_OFFSET = Coord2D(-1, 0)
NE_OFFSET = N_OFFSET + E_OFFSET
NW_OFFSET = N_OFFSET + W_OFFSET
SE_OFFSET = S_OFFSET + E_OFFSET
SW_OFFSET = S_OFFSET + W_OFFSET


DIRECTIONS_OFFSET_MAP: dict[Directions, Coord2D] = {
    "N": N_OFFSET,
    "S": S_OFFSET,
    "W": W_OFFSET,
    "E": E_OFFSET,
}

DIRECTIONS_ORDER: list[Directions] = ["N", "S", "W", "E"]

DIRECTIONS_ADJ_MAP: dict[Directions, list[Coord2D]] = {
    "N": [N_OFFSET, NE_OFFSET, NW_OFFSET],
    "S": [S_OFFSET, SE_OFFSET, SW_OFFSET],
    "W": [W_OFFSET, NW_OFFSET, SW_OFFSET],
    "E": [E_OFFSET, NE_OFFSET, SE_OFFSET],
}


def step(elves: set[Coord2D], rnd: int) -> int:  # noqa: C901
    proposed_moves: dict[Coord2D, Coord2D] = {}  # Elf to square
    move_to_squares: dict[Coord2D, int] = defaultdict(int)  # Square to elves

    count = len(elves)

    for elf in elves:
        move = False
        any_occupied = False
        potential_move = None

        for idx in range(4):
            if move and any_occupied:
                break
            curr_dir = DIRECTIONS_ORDER[(idx + rnd) % 4]
            offset_occupied = False
            for offset in DIRECTIONS_ADJ_MAP[curr_dir]:
                adj_square = elf + offset
                offset_occupied = adj_square in elves
                if offset_occupied:
                    any_occupied = True
                    break
            if not offset_occupied and not move:
                potential_move = elf + DIRECTIONS_OFFSET_MAP[curr_dir]
                move = True

        if move and any_occupied and potential_move is not None:
            proposed_moves[elf] = potential_move
            move_to_squares[potential_move] += 1

    move_list = []

    for elf, proposed in proposed_moves.items():
        if move_to_squares[proposed] == 1:
            move_list.append((elf, proposed))
        else:
            continue

    for from_, to in move_list:
        elves.discard(from_)
        elves.add(to)

    if len(elves) != count:
        raise UnexpectedConditionError("Some elves have vanished!")

    return len(move_list)


def print_elves(elves: set[Coord2D], screen: Screen) -> None:
    for x, y in elves:
        screen.draw("#", x, y)
    screen.render()
    screen.clear()


def get_empty_area(elves: set[Coord2D]) -> int:
    top = elves.pop()
    [min_x, min_y, max_x, max_y] = [*top, *top]

    for elf in elves:
        min_x = min(min_x, elf.x)
        min_y = min(min_y, elf.y)
        max_x = max(max_x, elf.x)
        max_y = max(max_y, elf.y)

    # put elf back
    elves.add(top)

    return (abs(max_x - min_x) + 1) * (abs(max_y - min_y) + 1) - len(elves)


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    rounds = 10  # initial set of rounds
    elves: set[Coord2D] = set()

    for row, line in enumerate(reversed(s.splitlines())):
        for col, char in enumerate(line):
            if char == "#":
                elves.add(Coord2D(x=col, y=row))

    for rnd in range(rounds):
        step(elves=elves, rnd=rnd)

    part_1 = get_empty_area(elves)

    while (step(elves, rounds)) > 0:
        rounds += 1

    return part_1, rounds + 1


TEST_INPUT_SMALL = """\
.....
..##.
..#..
.....
..##.
.....
"""

TEST_INPUT = """\
..............
..............
.......#......
.....###.#....
...#...#.#....
....#...##....
...#.###......
...##.#.##....
....#..#......
..............
..............
..............
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (110, 20)), (TEST_INPUT_SMALL, (25, 11))),
)
def test_solve(input_s: str, expected: str) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
