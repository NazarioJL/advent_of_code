from collections import defaultdict
from heapq import heappop
from heapq import heappush
from typing import TypeAlias

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.exceptions import UnexpectedConditionError
from advent_of_code.type_defs import Coord2D
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2022
DAY = 24


Element: TypeAlias = str


class MapInfo:
    def __init__(
        self, width: int, height: int, elements: dict[Coord2D, Element]
    ) -> None:
        self._width = width
        self._height = height
        self._elements = elements

        self._up: dict[int, set[Coord2D]] = defaultdict(set)
        self._down: dict[int, set[Coord2D]] = defaultdict(set)
        self._left: dict[int, set[Coord2D]] = defaultdict(set)
        self._right: dict[int, set[Coord2D]] = defaultdict(set)

        for (x, y), e in self._elements.items():
            match e:
                case "^":  # Origin is at top left; `y` increases downward
                    for i in range(self._height):
                        new_y = (y - i) % self._height
                        self._up[i].add(Coord2D(x=x, y=new_y))
                case "v":
                    for i in range(self._height):
                        new_y = (y + i) % self._height
                        self._down[i].add(Coord2D(x=x, y=new_y))
                case ">":
                    for i in range(self._width):
                        new_x = (x + i) % self._width
                        self._right[i].add(Coord2D(x=new_x, y=y))
                case "<":
                    for i in range(self._width):
                        new_x = (x - i) % self._width
                        self._left[i].add(Coord2D(x=new_x, y=y))
                case _:
                    raise UnexpectedConditionError(f"Unexpected value of {e}")

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def get_indexes(self, period: int) -> tuple[int, int]:
        return period % self._width, period % self._height

    def get_map(self, period: int = 0) -> dict[Coord2D, Element]:
        horizontal_index, vertical_index = self.get_indexes(period=period)

        element_bit_map = {
            "^": 0b0001,
            "v": 0b0010,
            ">": 0b0100,
            "<": 0b1000,
        }

        result: dict[Coord2D, Element] = {}

        for sym, items, index in (
            ("^", self._up, vertical_index),
            ("v", self._down, vertical_index),
            (">", self._right, horizontal_index),
            ("<", self._left, horizontal_index),
        ):
            for coord in items[index]:
                if coord in result:  # there is at least 1 item already in this position
                    existing = result[coord]
                    current = element_bit_map[sym]

                    if existing in element_bit_map:
                        result[coord] = f"{(current | element_bit_map[existing]):x}"
                    else:
                        result[coord] = f"{(current | int(existing)):x}"
                else:
                    result[coord] = sym

        return result

    def is_occupied(self, coord: Coord2D, period: int) -> bool:
        h_idx, v_idx = self.get_indexes(period=period)

        return (
            coord in self._up[v_idx]
            or coord in self._down[v_idx]
            or coord in self._left[h_idx]
            or coord in self._right[h_idx]
        )


def find_shortest_path(
    map_info: MapInfo,
    start: Coord2D,
    end: Coord2D,
    period: int = 0,
) -> int:
    offsets = [(1, 0), (0, 1), (0, 0), (0, -1), (-1, 0)]
    found = False
    pq: list[tuple[int, Coord2D, tuple[int, int]]] = [
        (period, start, map_info.get_indexes(period=period))
    ]
    visited: dict[tuple[Coord2D, tuple[int, int]], int] = {}
    total_periods = -1

    while not found:
        period, coord, period_info = heappop(pq)
        next_period = period + 1
        next_period_info = map_info.get_indexes(next_period)

        # get next locations
        for next_coord in [coord + offset for offset in offsets]:
            if next_coord == end:
                found = True
                total_periods = next_period
                break
            else:
                next_x, next_y = next_coord
                if (
                    next_x < 0
                    or next_x >= map_info.width
                    or next_y < 0
                    or next_y >= map_info.height
                ) and (next_coord != start):
                    continue
                else:
                    state = (next_coord, next_period_info)
                    if state in visited:
                        continue
                    elif map_info.is_occupied(coord=next_coord, period=next_period):
                        continue
                    else:
                        visited[state] = next_period
                        heappush(pq, (next_period, state[0], state[1]))

    return total_periods


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    lines = s.splitlines()
    cols = len(lines[0]) - 2
    rows = len(lines) - 2

    elements: dict[Coord2D, Element] = {}

    for row, line in enumerate(lines):
        for col, char in enumerate(line):
            if char in "><^v":
                elements[Coord2D(x=col - 1, y=row - 1)] = char

    map_info = MapInfo(width=cols, height=rows, elements=elements)

    start = Coord2D(x=0, y=-1)
    end = Coord2D(x=map_info.width - 1, y=map_info.height)

    shortest_1 = find_shortest_path(map_info=map_info, start=start, end=end)
    shortest_2 = find_shortest_path(
        map_info=map_info,
        start=end,
        end=start,
        period=shortest_1,
    )
    shortest_3 = find_shortest_path(
        map_info=map_info, start=start, end=end, period=shortest_2
    )

    return shortest_1, shortest_3


TEST_INPUT = """\
#E######
#>>.<^<#
#.<..<<#
#>v.><>#
#<^v^^>#
######.#
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (18, 54)),),
)
def test_solve(input_s: str, expected: str) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
