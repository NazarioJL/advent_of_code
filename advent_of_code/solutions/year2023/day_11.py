import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.screen import Screen
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2023
DAY = 11

Coord = tuple[int, int]


def parse_input(s: str) -> dict[Coord, int]:
    result = {}
    index = 1
    for row, line in enumerate(s.splitlines()):
        for col, char in enumerate(line):
            if char == "#":
                result[(col, row)] = index
                index += 1

    return result


def expand_universe(
    universe: dict[Coord, int], expansion_factor: int = 2
) -> dict[Coord, int]:
    """
    Creates an expanded universe based on the inputs. The universe gets expanded by
    expanding empty columns and rows by the provided factor.

    :param universe: The universe to expand, a map of coordinates to galaxy id.
    :param expansion_factor: The factor by which to expand the universe.
    :return: An expanded universe.
    """
    # find columns w/o universes
    max_col = max(c[0] for c in universe)
    max_row = max(c[1] for c in universe)

    empty_cols = set(c for c in range(max_col + 1)) - set(c[0] for c in universe)
    empty_rows = set(r for r in range(max_row + 1)) - set(c[1] for c in universe)

    # create map all empty rows above, and all empty cols left
    expanded_cols_left = [0] * (max_col + 1)
    expanded_rows_above = [0] * (max_row + 1)

    # We could also just store the empty column/row positions with the expansion factor
    # and iterate the galaxies in order to calculate new locations.
    expanded_cols_seen = 0
    for idx in range(max_col + 1):
        expanded_cols_left[idx] = expanded_cols_seen
        if idx in empty_cols:
            expanded_cols_seen += expansion_factor - 1

    expanded_rows_seen = 0
    for idx in range(max_row + 1):
        expanded_rows_above[idx] = expanded_rows_seen
        if idx in empty_rows:
            expanded_rows_seen += expansion_factor - 1

    expanded = {}
    for (col, row), idx in universe.items():
        new_col, new_row = col + expanded_cols_left[col], row + expanded_rows_above[row]
        expanded[new_col, new_row] = idx

    return expanded


def get_distances(universe: dict[Coord, int]) -> dict[tuple[int, int], int]:
    """Gets the distance between of each galaxy pair"""
    result = {}
    for (col, row), gal in universe.items():
        for (other_col, other_row), other_gal in universe.items():
            if gal == other_gal:
                continue

            stable_id = min(gal, other_gal), max(gal, other_gal)
            if stable_id in result:
                continue

            distance = abs(col - other_col) + abs(row - other_row)
            result[stable_id] = distance

    return result


def draw_universe(universe: dict[Coord, int]) -> None:
    max_col = max(c[0] for c in universe)
    max_row = max(c[1] for c in universe)

    screen = Screen(0, 0, max_col + 1, max_row + 1)

    for (col, row), idx in universe.items():
        screen.draw(str(idx), col, row)

    screen.render()


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    universe = parse_input(s)
    # draw_universe(universe)
    expanded_1 = expand_universe(universe)
    # draw_universe(expanded_1)
    expanded_2 = expand_universe(universe, expansion_factor=1000000)

    part_1 = sum(get_distances(expanded_1).values())
    part_2 = sum(get_distances(expanded_2).values())

    return part_1, part_2


TEST_INPUT = """\
...#......
.......#..
#.........
..........
......#...
.#........
.........#
..........
.......#..
#...#.....
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (374, 82000210)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    print()
    assert solve(input_s).as_tuple() == expected


@pytest.mark.parametrize(
    ("input_s", "factor", "expected"),
    (
        (TEST_INPUT, 10, 1030),
        (TEST_INPUT, 100, 8410),
    ),
)
def test_get_distances(input_s: str, factor: int, expected: int) -> None:
    universe = parse_input(input_s)
    expanded = expand_universe(universe, factor)
    sum_of_distances = sum(get_distances(expanded).values())
    assert sum_of_distances == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
