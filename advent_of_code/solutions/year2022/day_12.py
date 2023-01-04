from itertools import pairwise
from typing import Iterable

import pytest

from advent_of_code.algorithms.astar import a_star_search
from advent_of_code.algorithms.astar import PathNotFoundError
from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Coord2D
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2022
DAY = 12


def parse_input(s: str) -> tuple[list[list[int]], Coord2D, Coord2D]:
    def get_height(char: str) -> int:
        if char == "S":
            return get_height("a")
        elif char == "E":
            return get_height("z")
        else:
            return ord(char) - ord("a")

    grid: list[list[int]] = []
    start: Coord2D | None = None
    end: Coord2D | None = None

    for row, line in enumerate(s.splitlines()):
        grid.append([])
        for col, c in enumerate(line):
            grid[row].append(get_height(c))
            if c == "S":
                start = Coord2D(x=col, y=row)
            if c == "E":
                end = Coord2D(x=col, y=row)
    assert start is not None
    assert end is not None
    return grid, start, end


def visualize(
    grid: list[list[int]],
    start: Coord2D,
    end: Coord2D,
    path: Iterable[Coord2D],
) -> None:
    from matplotlib import pyplot as plt
    from matplotlib.patches import FancyArrowPatch
    from mpl_toolkits.mplot3d.proj3d import proj_transform

    import numpy as np

    class Arrow3D(FancyArrowPatch):  # type: ignore
        def __init__(  # type: ignore
            self, x, y, z, dx, dy, dz, *args, **kwargs
        ) -> None:
            super().__init__((0, 0), (0, 0), *args, **kwargs)
            self._xyz = (x, y, z)
            self._dxdydz = (dx, dy, dz)

        def draw(self, renderer) -> None:  # type: ignore
            x1, y1, z1 = self._xyz
            dx, dy, dz = self._dxdydz
            x2, y2, z2 = (x1 + dx, y1 + dy, z1 + dz)

            xs, ys, zs = proj_transform((x1, x2), (y1, y2), (z1, z2), self.axes.M)
            self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
            super().draw(renderer)

        def do_3d_projection(self, renderer=None) -> int:  # type: ignore
            x1, y1, z1 = self._xyz
            dx, dy, dz = self._dxdydz
            x2, y2, z2 = (x1 + dx, y1 + dy, z1 + dz)

            xs, ys, zs = proj_transform((x1, x2), (y1, y2), (z1, z2), self.axes.M)
            self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))

            return np.min(zs)  # type: ignore

    plt.figure()
    ax = plt.axes(projection="3d")

    x_values, y_values, z_values = [], [], []

    rows = len(grid)
    cols = len(grid[0])

    for x in range(cols):
        for y in range(rows):
            x_values.append(x)
            y_values.append(y)
            z_values.append(grid[y][x])

    ax.plot_trisurf(
        np.array(x_values),
        np.array(y_values),
        np.array(z_values),
        # alpha=0.8,
        color="yellow",
        linewidth=0,
        antialiased=False,
    )

    s_x, s_y, s_z = (start.x, start.y, grid[start.y][start.x])
    e_x, e_y, e_z = (end.x, end.y, grid[end.y][end.x])

    ax.scatter([s_x], [s_y], [s_z], c="blue")
    ax.scatter([e_x], [e_y], [e_z], c="red")

    for p1, p2 in pairwise(path):
        z_1 = grid[p1.y][p1.x]
        z_2 = grid[p2.y][p2.x]
        arrow = Arrow3D(
            p1.x,
            p1.y,
            z_1,
            p2.x - p1.x,
            p2.y - p1.y,
            z_2 - z_1,
            mutation_scale=20,
            ec="green",
            fc="red",
        )
        ax.add_artist(arrow)

    plt.show()


def find_shortest_path(
    grid: list[list[int]],
    start: Coord2D,
    goal: Coord2D,
    max_cost: int | None = None,
) -> Iterable[tuple[Coord2D, int]]:
    height = len(grid)
    width = len(grid[0])

    def get_adjacent(location: Coord2D) -> Iterable[tuple[Coord2D, int]]:
        offsets = ((1, 0), (-1, 0), (0, 1), (0, -1))
        current_height = grid[location.y][location.x]
        for offset in offsets:
            new_location = location + offset
            if (
                new_location.x < 0
                or new_location.x >= width
                or new_location.y < 0
                or new_location.y >= height
            ):
                continue
            new_height = grid[new_location.y][new_location.x]
            diff = new_height - current_height
            if diff > 1:
                continue
            yield new_location, 1

    def heuristic(a: Coord2D, b: Coord2D) -> int:
        return abs(b.y - a.y) + abs(b.x - a.x)

    result = a_star_search(
        start=start,
        goal=goal,
        get_adjacent=get_adjacent,
        heuristic=heuristic,
        max_cost=max_cost,
    )

    return result


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    grid, start, end = parse_input(s)

    path_1 = find_shortest_path(grid=grid, start=start, goal=end)
    part_1 = len(list(path_1)) - 1

    # Get all start locations with height = "a" (0)
    start_locations: list[Coord2D] = []
    for row, line in enumerate(grid):
        for col, h in enumerate(line):
            if h == 0:
                start_locations.append(Coord2D(x=col, y=row))

    max_cost: int | None = None
    for start in start_locations:
        try:
            path_2 = find_shortest_path(
                grid=grid, start=start, goal=end, max_cost=max_cost
            )
            current_cost = len(list(path_2))
            max_cost = min(max_cost or current_cost, current_cost)
        except PathNotFoundError:
            pass

    assert max_cost is not None

    return part_1, max_cost - 1


TEST_INPUT = """\
Sabqponm
abcryxxl
accszExk
acctuvwj
abdefghi
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (31, 29)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
