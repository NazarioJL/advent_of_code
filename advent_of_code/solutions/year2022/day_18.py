from collections import Counter
from typing import Iterable
from typing import TypeAlias
from typing import Union

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Coord3D
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2022
DAY = 18


SideItem: TypeAlias = Union[tuple[int, int] | int]
Side: TypeAlias = tuple[SideItem, SideItem, SideItem]


def parse_input(s: str) -> Iterable[Coord3D]:
    for line in s.splitlines():
        x, y, z = line.split(",", maxsplit=2)
        yield Coord3D(x=int(x), y=int(y), z=int(z))


def get_sides(coord: Coord3D) -> Iterable[Side]:
    # Gets uniquely encoded sides for any 1x1x1 cube
    def ranged(a: int, b: int) -> SideItem:
        return min(a, b), max(a, b)

    x, y, z = coord
    # xy plane, z varies
    yield x, y, ranged(z, z + 1)
    yield x, y, ranged(z, z - 1)
    # yz plane, x varies
    yield ranged(x, x + 1), y, z
    yield ranged(x, x - 1), y, z
    # xz plane, y varies
    yield x, ranged(y, y + 1), z
    yield x, ranged(y, y - 1), z


def get_adjacent(cube: Coord3D) -> Iterable[Coord3D]:
    # Gets orthogonally adjacent cubes
    offsets = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
    for offset in offsets:
        yield cube + offset


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:  # noqa: C901
    cubes = set(parse_input(s))
    side_counts = Counter(side for cube in cubes for side in get_sides(cube))
    surface_sides = {side for side, count in side_counts.items() if count == 1}
    part_1 = len(surface_sides)

    # Get bounding box for limiting the outside flooding
    max_x, min_x, max_y, min_y, max_z, min_z = (None, None, None, None, None, None)
    for x, y, z in cubes:
        max_x = max(max_x or x, x)
        min_x = min(min_x or x, x)
        max_y = max(max_y or y, y)
        min_y = min(min_y or y, y)
        max_z = max(max_z or z, z)
        min_z = min(min_z or z, z)

    outside: set[Coord3D] = set()
    inside: set[Coord3D] = set()

    for cube in cubes:
        if cube in outside or cube in inside:
            continue

        # Find adjacent cube that is in the outside or inside
        try:
            not_solid = next(filter(lambda c: c not in cubes, get_adjacent(cube)))
        except StopIteration:
            continue

        # Have we seen this empty space already?
        if not_solid in outside or not_solid in inside:
            continue

        # Flood from not solid
        q = [not_solid]
        curr_flood = set()
        is_outside = False
        while q:
            curr = q.pop()
            if curr in curr_flood:
                continue
            if curr in cubes:
                continue
            if (
                curr.x > max_x  # type: ignore
                or curr.x < min_x  # type: ignore
                or curr.y > max_y  # type: ignore
                or curr.y < min_y  # type: ignore
                or curr.z > max_z  # type: ignore
                or curr.z < min_z  # type: ignore
            ):
                # This flood is adjacent to the outside, do not enqueue
                is_outside = True
                continue
            else:
                # curr is _visited_
                curr_flood.add(curr)
                for adj in get_adjacent(curr):
                    q.append(adj)
        if is_outside:
            outside.update(curr_flood)
        else:
            inside.update(curr_flood)

    # For part 2, find the intersection of inside sides with all surface sides
    inside_sides = set(side for cube in inside for side in get_sides(cube))
    part_2 = part_1 - len(inside_sides.intersection(surface_sides))

    return part_1, part_2


TEST_INPUT = """\
2,2,2
1,2,2
3,2,2
2,1,2
2,3,2
2,2,1
2,2,3
2,2,4
2,2,6
1,2,5
3,2,5
2,1,5
2,3,5
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (64, 58)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
