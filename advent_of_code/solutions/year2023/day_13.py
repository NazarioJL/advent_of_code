import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.exceptions import SolutionNotImplementedError
from advent_of_code.screen import Screen
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2023
DAY = 13

SYMBOL_TO_INT = {
    ".": 0,
    "#": 1,
}


def parse_input(s: str) -> list[list[list[int]]]:
    result = []

    for pattern_str in s.split("\n\n"):
        pattern = []
        for line in pattern_str.splitlines():
            pattern.append([SYMBOL_TO_INT[c] for c in line])
        result.append(pattern)

    return result


def get_columns_signature(pattern: list[list[int]]) -> list[int]:
    rows = len(pattern)
    cols = len(pattern[0])
    result = [0] * cols

    for col in range(cols):
        col_val = 0
        for row in range(rows):
            col_val += pattern[row][col]
            col_val <<= 1
        result[col] = col_val

    return result


def get_rows_signature(pattern: list[list[int]]) -> list[int]:
    rows = len(pattern)
    cols = len(pattern[0])
    result = [0] * rows

    for row in range(rows):
        row_val = 0
        for col in range(cols):
            row_val += pattern[row][col]
            row_val <<= 1
        result[row] = row_val

    return result


def find_reflection(signature: list[int]) -> tuple[int, int]:
    max_reflected = -1
    best_index = -1

    for idx in range(1, len(signature)):
        # get right and left
        right = idx
        left = idx - 1
        count = 0
        while True:
            if right >= len(signature) or left < 0:
                return idx, 10
            if signature[right] != signature[left]:
                break
            count += 1
            right += 1
            left -= 1
    return best_index, max_reflected


def print_pattern(pattern: list[list[int]]) -> None:
    max_rows = len(pattern)
    max_cols = len(pattern[0])

    screen = Screen(
        start_x=0,
        end_x=max_cols,
        start_y=0,
        end_y=max_rows,
    )

    for row in range(max_rows):
        for col in range(max_cols):
            char = "#" if pattern[row][col] == 1 else "."
            screen.draw(char, col, row)

    screen.render()


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    patterns = parse_input(s)

    best_indexes = []

    for pattern in patterns:
        col_signature = get_columns_signature(pattern)
        row_signature = get_rows_signature(pattern)

        best_index_row, max_reflected_row = find_reflection(row_signature)
        best_index_col, max_reflected_col = find_reflection(col_signature)

        print_pattern(pattern)
        print(f"Row signature: {row_signature}")
        print(f"Col signature: {col_signature}")

        print(find_reflection(row_signature))
        print(find_reflection(col_signature))

        if max_reflected_row > max_reflected_col:
            print(f"Mirror at: {best_index_row} row")
            best_indexes.append(best_index_row * 100)
        else:
            print(f"Mirror at: {best_index_col} col")
            best_indexes.append(best_index_col)

        # print(f"Mirror at: {best_index_row} row")
        # best_indexes.append(best_index_row * 100)
        #
        # print(f"Mirror at: {best_index_col} col")
        # best_indexes.append(best_index_col)

    print(best_indexes)
    part_1 = sum(best_indexes)
    return part_1, 0


TEST_INPUT_1 = """\
#.##..##.
..#.##.#.
##......#
##......#
..#.##.#.
..##..##.
#.#.##.#.

#...##..#
#....#..#
..##..###
#####.##.
#####.##.
..##..###
#....#..#
"""


TEST_INPUT_2 = """\
#...##..#
#....#..#
..##..###
#####.##.
#####.##.
..##..###
#....#..#
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT_1, (405, 0)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
