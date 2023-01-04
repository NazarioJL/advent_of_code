from itertools import pairwise
from typing import Iterable

import pytest

from advent_of_code.algorithms.astar import a_star_search
from advent_of_code.algorithms.astar import PathNotFoundError


class SimpleAStarMap:
    def __init__(
        self,
        walls: set[tuple[int, int]],
        start: tuple[int, int],
        goal: tuple[int, int],
        width: int,
        height: int,
    ) -> None:
        self._walls = walls
        self._start = start
        self._goal = goal
        self._width = width
        self._height = height

    @property
    def start(self) -> tuple[int, int]:
        return self._start

    @property
    def goal(self) -> tuple[int, int]:
        return self._goal

    @property
    def walls(self) -> set[tuple[int, int]]:
        return self._walls

    @property
    def height(self) -> int:
        return self._height

    @property
    def width(self) -> int:
        return self._width

    def get_adjacent(
        self, location: tuple[int, int]
    ) -> Iterable[tuple[tuple[int, int], int]]:
        x, y = location
        offsets = ((1, 0), (-1, 0), (0, 1), (0, -1))
        for off_x, off_y in offsets:
            new_x, new_y = x + off_x, y + off_y
            if new_x < 0 or new_x >= 10 or new_y < 0 or new_y >= 10:
                continue
            if (new_x, new_y) in self._walls:
                continue
            yield (new_x, new_y), 1

    def heuristic(self, a: tuple[int, int], b: tuple[int, int]) -> int:
        # Return manhattan distance
        return abs(b[1] - a[1]) + abs(b[0] - a[0])

    @staticmethod
    def from_data(map_data: str) -> "SimpleAStarMap":
        walls = set()
        start: tuple[int, int] | None = None
        goal: tuple[int, int] | None = None

        lines = map_data.splitlines(keepends=False)
        height = len(lines)
        width = len(lines[0])
        for row, line in enumerate(lines):
            for col, c in enumerate(line.strip()):
                if c == "#":
                    walls.add((col, row))
                elif c == "S":
                    start = (col, row)
                elif c == "E":
                    goal = (col, row)
                else:
                    continue
        assert start is not None
        assert goal is not None

        return SimpleAStarMap(
            walls=walls,
            start=start,
            goal=goal,
            width=width,
            height=height,
        )


def print_path(a_star_map: SimpleAStarMap, path: Iterable[tuple[int, int]]) -> None:
    """Utility method to print a map with taken path"""
    output = []

    for _ in range(10):
        output.append(["."] * 10)

    for x, y in a_star_map.walls:
        output[y][x] = "#"

    for (x1, y1), (x2, y2) in pairwise(path):
        move_char = ""
        if x2 > x1:
            move_char = ">"
        if x2 < x1:
            move_char = "<"
        if y2 > y1:
            move_char = "v"
        if y2 < y1:
            move_char = "^"
        output[y1][x1] = move_char

    output[a_star_map.start[1]][a_star_map.start[0]] = "S"
    output[a_star_map.goal[1]][a_star_map.goal[0]] = "E"
    for row in output:
        print("".join(row))


def test_a_star_search():
    map_data = """\
    .........
    .S..#.....
    ....#.....
    #######.#.
    ..........
    ...###....
    .....##...
    ......##..
    ......E#..
    .......#..
    """

    a_star_map = SimpleAStarMap.from_data(map_data=map_data)

    result = a_star_search(
        start=a_star_map.start,
        goal=a_star_map.goal,
        get_adjacent=a_star_map.get_adjacent,
        heuristic=a_star_map.heuristic,
    )

    assert len(list(result)) == 25


def test_a_star_search_simple():
    map_data = """\
    ..........
    .S........
    ..........
    ..........
    ..........
    ..........
    ..........
    ..........
    ......E...
    ..........
    """

    a_star_map = SimpleAStarMap.from_data(map_data=map_data)

    result = a_star_search(
        start=a_star_map.start,
        goal=a_star_map.goal,
        get_adjacent=a_star_map.get_adjacent,
        heuristic=a_star_map.heuristic,
    )

    assert len(list(result)) - 1 == a_star_map.heuristic(
        a_star_map.start, a_star_map.goal
    )


def test_a_star_search_path_not_found():
    map_no_solution = """\
    .........
    .S..#.....
    ....#.....
    ####### ##
    ..........
    ...###....
    .....##...
    ....####..
    ....#.E#..
    ....#..#..
    """

    a_star_map = SimpleAStarMap.from_data(map_data=map_no_solution)

    with pytest.raises(PathNotFoundError):
        a_star_search(
            start=a_star_map.start,
            goal=a_star_map.goal,
            get_adjacent=a_star_map.get_adjacent,
            heuristic=a_star_map.heuristic,
        )
