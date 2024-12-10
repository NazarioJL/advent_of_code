import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2024
DAY = 10


DIRECTIONS = ((1, 0), (-1, 0), (0, -1), (0, 1))


def hike(
    start: tuple[int, int],
    topo_map: dict[tuple[int, int], int],
) -> list[tuple[int, int]]:
    """Hike ot summit from start position"""
    result = []

    def hike_rec(s: tuple[int, int]) -> None:
        curr_height = topo_map[s]
        if curr_height == 9:
            result.append(s)
        else:
            r, c = s
            for r_off, c_off in DIRECTIONS:
                new_s = r_off + r, c_off + c
                if new_s in topo_map and topo_map[new_s] == curr_height + 1:
                    hike_rec(new_s)

    hike_rec(start)
    return result


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    topo_map: dict[tuple[int, int], int] = {}
    trail_heads: list[tuple[int, int]] = []

    for row, line in enumerate(s.splitlines()):
        for col, char in enumerate(line):
            if char.isdigit():
                h = int(char)
                topo_map[(row, col)] = h
                if h == 0:
                    trail_heads.append((row, col))

    part_1 = 0
    part_2 = 0

    for head in trail_heads:
        summits = hike(head, topo_map)
        part_1 += len(set(summits))
        part_2 += len(summits)

    return part_1, part_2


TEST_INPUT = """\
89010123
78121874
87430965
96549874
45678903
32019012
01329801
10456732
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (36, 81)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
