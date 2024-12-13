import random
from collections import defaultdict, Counter
from itertools import product
from typing import TypeAlias, Optional, Iterable, Callable, TypeVar

import attrs
import pytest

from advent_of_code.algorithms.bfs import bfs
from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2024
DAY = 12


DIRECTIONS = ((1, 0), (-1, 0), (0, -1), (0, 1))


PlotId: TypeAlias = tuple[str, int]
Coord: TypeAlias = tuple[int, int]
T = TypeVar("T")


@attrs.define
class PlotCounts:
    area: int = 0
    perimeter: int = 0


GardenNode: TypeAlias = tuple[Coord, Optional[str]]
GetAdjacentGardenNodesFuncTypeDef: TypeAlias = Callable[
    [GardenNode], Iterable[GardenNode]
]


def all_same(seq: Iterable[T]) -> Optional[T]:
    it = iter(seq)
    item = next(it)
    try:
        while item == next(it):
            pass
    except StopIteration:
        return item

    return None


def safe_get(
    garden: list[str], default: Optional[str] = None
) -> Callable[[tuple[int, int]], Optional[str]]:
    rows = len(garden)
    cols = len(garden[0])

    def safe_get_func(coord: tuple[int, int]) -> Optional[str]:
        row, col = coord
        if row < 0 or row >= rows or col < 0 or col >= cols:
            return default
        else:
            return garden[row][col]

    return safe_get_func


def survey_garden(garden: list[str]) -> dict[PlotId, set[Coord]]:
    rows = len(garden)
    cols = len(garden[0])
    plots: dict[PlotId, set[Coord]] = defaultdict(set)

    get_neighbors_func = make_get_neighbors_func(garden)

    plot_idx = 0
    visited: set[Coord] = set()

    for row, col in product(range(rows), range(cols)):
        if (row, col) in visited:
            continue
        else:
            val = garden[row][col]
            plot_id = val, plot_idx
            items = bfs(start=((row, col), val), get_nodes=get_neighbors_func)
            plots[plot_id] = set(coord for coord, _ in items)
            visited |= plots[plot_id]
            plot_idx += 1

    return plots


def make_get_neighbors_func(
    garden: list[str], all_nodes: bool = False
) -> GetAdjacentGardenNodesFuncTypeDef:
    rows = len(garden)
    cols = len(garden[0])

    def get_neighbors_inner(node: GardenNode) -> Iterable[GardenNode]:
        (row, col), val = node
        for d_r, d_c in ((1, 0), (-1, 0), (0, -1), (0, 1)):
            new_row, new_col = row + d_r, col + d_c
            if new_row < 0 or new_row >= rows or new_col < 0 or new_col >= cols:
                if all_nodes:
                    yield (new_row, new_col), None
            else:
                new_val = garden[new_row][new_col]
                if new_val == val or all_nodes:
                    yield (new_row, new_col), garden[new_row][new_col]

    return get_neighbors_inner


def get_perimeters(
    plots: dict[PlotId, set[Coord]], get_nodes: GetAdjacentGardenNodesFuncTypeDef
) -> dict[PlotId, int]:
    result = {}
    for (letter, idx), items in plots.items():
        count = 0
        for item in items:
            for _, val in get_nodes((item, letter)):
                if not val or val != letter:
                    count += 1

        result[(letter, idx)] = count
    return result


def get_sides(plots: dict[PlotId, set[Coord]], garden: list[str]) -> dict[PlotId, int]:
    rows = len(garden)
    cols = len(garden[0])
    result: dict[PlotId, int] = defaultdict(int)

    coord_to_plot_id = {}
    for plot_id, items in plots.items():
        for coord in items:
            coord_to_plot_id[coord] = plot_id

    # Create 4x4 sliding window
    offsets = ((0, 0), (0, 1), (1, 0), (1, 1))

    for row, col in product(range(-1, rows + 1), range(-1, cols + 1)):
        coords = [(row + offset[0], col + offset[1]) for offset in offsets]
        counts = Counter(coord_to_plot_id.get(coord, None) for coord in coords)

        plot_id_: Optional[PlotId]
        for plot_id_, count in counts.items():
            if plot_id_ is not None and (count == 1 or count == 3):
                result[plot_id_] += 1

    return result


def visualize(garden: list[str]) -> None:
    from PIL import Image, ImageDraw

    cols = len(garden[0])
    rows = len(garden)

    image = Image.new("RGBA", (cols, rows), color="black")
    draw = ImageDraw.Draw(image, "RGBA")

    def get_rand_color() -> tuple[int, int, int]:
        return (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )

    colors: dict[str, tuple[int, int, int]] = defaultdict(get_rand_color)

    for col in range(cols):
        for row in range(rows):
            color = colors[garden[row][col]]
            draw.point((col, row), fill=color)

    ratio = 1200 // cols

    image = image.resize(
        size=(cols * ratio, rows * ratio), resample=Image.Resampling.BOX
    )
    image.show()


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    garden = s.strip().splitlines()
    plots = survey_garden(garden)
    perimeters = get_perimeters(plots, make_get_neighbors_func(garden, all_nodes=True))
    sides = get_sides(plots, garden)
    part_1 = sum(len(items) * perimeters[plot_id] for plot_id, items in plots.items())
    part_2 = sum(len(items) * sides[plot_id] for plot_id, items in plots.items())

    # visualize(garden)

    return part_1, part_2


TEST_INPUT = """\
AAAA
BBCD
BBCC
EEEC
"""


TEST_INPUT_2 = """\
OOOOO
OXOXO
OOOOO
OXOXO
OOOOO
"""

TEST_INPUT_3 = """\
RRRRIICCFF
RRRRIICCCF
VVRRRCCFFF
VVRCCCJFFF
VVVVCJJCFE
VVIVCCJJEE
VVIIICJJEE
MIIIIIJJEE
MIIISIJEEE
MMMISSJEEE
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    (
        (TEST_INPUT, (140, 80)),
        (TEST_INPUT_2, (772, 436)),
        (TEST_INPUT_3, (1930, 1206)),
    ),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
