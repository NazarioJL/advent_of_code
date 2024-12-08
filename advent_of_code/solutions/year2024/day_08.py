from collections import defaultdict
from typing import Iterable

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2024
DAY = 8


def rotate_vector(
    pair: tuple[tuple[int, int], tuple[int, int]],
) -> tuple[tuple[int, int], tuple[int, int]]:
    """
    Poor man's function to rotates a vector 180 degrees about the first point in the
    pair
    """
    (a_x, a_y), (b_x, b_y) = pair
    # move vector to origin
    n_y = b_y - a_y
    n_x = b_x - a_x

    # Rotate about the origin by using 180 1/2τ or π
    # | -1  0 || n_x |
    # |  0 -1 || n_y |

    r_x = -1 * n_x + 0 * n_y
    r_y = 0 * n_x + -1 * n_y

    # move vector back to origin
    new_x = r_x + a_x
    new_y = r_y + a_y

    return (a_x, a_y), (new_x, new_y)


def generate_antinodes(
    pair: tuple[tuple[int, int], tuple[int, int]],
) -> Iterable[tuple[int, int]]:
    """
    Yield antinodes that form from a pair opposite to the given pair
    """
    (a_y, a_x), (b_y, b_x) = pair  # original pair
    _, (n_x, n_y) = rotate_vector(((a_x, a_y), (b_x, b_y)))
    d_x, d_y = n_x - a_x, n_y - a_y

    while True:
        yield n_y, n_x
        n_x += d_x
        n_y += d_y


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    grid = [line for line in s.splitlines()]
    rows = len(grid)
    cols = len(grid[0])

    antennas: dict[str, set[tuple[int, int]]] = defaultdict(set)
    for col in range(cols):
        for row in range(rows):
            tile = grid[row][col]
            if tile == ".":
                continue
            antennas[tile].add((row, col))

    antinodes_part_1: set[tuple[int, int]] = set()
    antinodes_part_2: set[tuple[int, int]] = set()

    def in_grid(node: tuple[int, int]) -> bool:
        y_, x_ = node
        if y_ < 0 or y_ >= rows or x_ < 0 or x_ >= cols:
            return False
        return True

    def add_antinodes(pair: tuple[tuple[int, int], tuple[int, int]]) -> None:
        count = 0
        ant_a, ant_b = pair
        for antinode in generate_antinodes((ant_a, ant_b)):
            if in_grid(antinode):
                if count == 0:
                    # in part only add one from each side
                    antinodes_part_1.add(antinode)
                    count += 1
                antinodes_part_2.add(antinode)
            else:
                break

    for antenna, locations in antennas.items():
        lst = list(locations)
        for i in range(len(lst) - 1):
            for j in range(i + 1, len(lst)):
                #
                antinodes_part_2.add(lst[i])
                antinodes_part_2.add(lst[j])

                add_antinodes((lst[i], lst[j]))
                add_antinodes((lst[j], lst[i]))

    part_1 = len(antinodes_part_1)
    part_2 = len(antinodes_part_2)

    # Uncomment to render to screen
    # screen = Screen(start_x=0, start_y=0, end_x=cols, end_y=rows, default_pixel=".")
    #
    # for antenna, locations in antennas.items():
    #     for y, x in locations:
    #         screen.draw(antenna, x, y)
    # screen.render()
    #
    # for y, x in antinodes_part_2:
    #     screen.draw("#", x, y)
    #
    # screen.render()

    return part_1, part_2


TEST_INPUT = """\
............
........0...
.....0......
.......0....
....0.......
......A.....
............
............
........A...
.........A..
............
............
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (14, 34)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
