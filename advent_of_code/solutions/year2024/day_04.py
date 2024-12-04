from typing import Iterable

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2024
DAY = 4

XMAS_OFFSETS_PART_1 = [
    [((dir_x * sign * offset), (dir_y * sign * offset)) for offset in range(4)]
    for (dir_y, dir_x) in ((0, 1), (1, 0), (1, 1), (1, -1))
    for sign in (1, -1)
]


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    lines = s.splitlines()
    cols = len(lines[0])  # makes assumption grid is square
    rows = len(lines)
    all_cells = [(row, col) for col in range(cols) for row in range(rows)]

    def is_path_in_bounds(p: Iterable[tuple[int, int]]) -> bool:
        return all(0 <= y < rows and 0 <= x < cols for (y, x) in p)

    def get_word_count_part_1(r: int, c: int) -> int:
        total = 0
        for offset in XMAS_OFFSETS_PART_1:
            path = [(r + y, c + x) for x, y in offset]
            if not is_path_in_bounds(path):
                continue
            if [lines[y][x] for y, x in path] == ["X", "M", "A", "S"]:
                total += 1
        return total

    def get_word_count_part_2(r: int, c: int) -> int:
        tl = (r - 1, c - 1)
        tr = (r - 1, c + 1)
        bl = (r + 1, c - 1)
        br = (r + 1, c + 1)
        if not is_path_in_bounds((bl, br, tl, tr)):
            return False
        diag_1: tuple[str, str] = (lines[tl[0]][tl[1]], lines[br[0]][br[1]])
        diag_2: tuple[str, str] = (lines[tr[0]][tr[1]], lines[bl[0]][bl[1]])
        return int(all(diag in (("M", "S"), ("S", "M")) for diag in [diag_1, diag_2]))

    part_1 = sum(
        get_word_count_part_1(row, col)
        for (row, col) in all_cells
        if lines[row][col] == "X"
    )
    part_2 = sum(
        get_word_count_part_2(row, col)
        for (row, col) in all_cells
        if lines[row][col] == "A"
    )
    return part_1, part_2


TEST_INPUT = """\
MMMSXXMASM
MSAMXMSMSA
AMXSXMAAMM
MSAMASMSMX
XMASAMXAMM
XXAMMXXAMA
SMSMSASXSS
SAXAMASAAA
MAMMMXMMMM
MXMXAXMASX
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (18, 9)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
