from itertools import pairwise
from typing import Iterable
from typing import TypeAlias

import pytest

from advent_of_code.algorithms.dykstra import dykstra
from advent_of_code.algorithms.dykstra import get_path
from advent_of_code.algorithms.grids import get_diamond
from advent_of_code.algorithms.grids import grid_get_neighbors
from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2024
DAY = 20


Location: TypeAlias = tuple[int, int]


def visualize(walls: Iterable[tuple[int, int]], path: list[tuple[int, int]]) -> None:
    import matplotlib.pyplot as plt

    plt.gca().invert_yaxis()

    x, y = zip(*walls)
    plt.plot(x, y, "bs")
    plt.plot(path[0][0], path[0][1], "ro")
    plt.plot(path[-1][0], path[-1][1], "go")

    for (x_1, y_1), (x_2, y_2) in pairwise(path):
        plt.quiver(
            x_1, y_1, (x_2 - x_1), (y_2 - y_1), angles="xy", scale_units="xy", scale=1
        )

    plt.show()


def get_neighbors_with_cost(
    location: tuple[int, int], item: str
) -> tuple[tuple[int, int], int]:
    return location, 1


def manhattan(loc_1: Location, loc_2: Location) -> int:
    x_1, y_1 = loc_1
    x_2, y_2 = loc_2

    return abs(x_1 - x_2) + abs(y_1 - y_2)


def count_cheats(
    path: list[tuple[int, int]],
    max_breaks: int,
    cost_from_start: dict[Location, int],
    cost_from_end: dict[Location, int],
    best_score: int,
) -> int:
    all_cheats: set[tuple[Location, Location]] = set()
    #  Use to compare with problem explanation
    #  e.g. - There are x cheats that save y picoseconds ...
    #  all_scores = defaultdict(int)
    path_as_set = set(path)

    for p in path:
        x, y = p
        break_in_locations = get_diamond(size=max_breaks)
        for loc_x, loc_y in break_in_locations:
            break_in = x + loc_x, y + loc_y
            if break_in in path_as_set:
                score = (
                    cost_from_start[p]
                    + manhattan(p, break_in)
                    + cost_from_end[break_in]
                )
                if score < best_score:
                    all_cheats.add((p, break_in))
                    # all_scores[score] += 1

    return len(all_cheats)


@aoc.solution(year=YEAR, day=DAY)
def solve(
    s: str, beat_best_by_part_1: int = 100, beat_best_by_part_2: int = 100
) -> Solution:
    lines = s.splitlines()
    positions = {
        item: (col, row)
        for row, line in enumerate(lines)
        for col, item in enumerate(line)
        if item in ("S", "E")
    }
    start = positions["S"]
    end = positions["E"]

    get_neighbors_dykstra = grid_get_neighbors(
        lines, invalid={"#"}, out_fun=get_neighbors_with_cost
    )
    cost_from_start_to_end, predecessors_start_to_end = dykstra(
        start, get_neighbors_dykstra
    )
    path_from_start_to_end = get_path(end, predecessors_start_to_end)

    # visualize(walls, path_from_start)

    cost_from_end_to_start, predecessors_end_to_start = dykstra(
        end, get_neighbors_dykstra
    )

    best_score = len(path_from_start_to_end)

    part_1 = count_cheats(
        path_from_start_to_end,
        2,
        cost_from_start_to_end,
        cost_from_end_to_start,
        best_score=best_score - beat_best_by_part_1,
    )
    part_2 = count_cheats(
        path_from_start_to_end,
        20,
        cost_from_start_to_end,
        cost_from_end_to_start,
        best_score=best_score - beat_best_by_part_2,
    )

    return part_1, part_2


TEST_INPUT = """\
###############
#...#...#.....#
#.#.#.#.#.###.#
#S#...#.#.#...#
#######.#.#.###
#######.#.#...#
#######.#.###.#
###..E#...#...#
###.#######.###
#...###...#...#
#.#####.#.###.#
#.#...#.#.#...#
#.#.#.#.#.#.###
#...#...#...###
###############
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    [
        (TEST_INPUT, (44, 285)),
    ],
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s, 1, 50).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
