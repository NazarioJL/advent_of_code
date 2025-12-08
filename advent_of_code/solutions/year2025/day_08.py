import operator
from functools import reduce
from heapq import heappop
from heapq import heappush

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2025
DAY = 8

type Point3D = tuple[int, int, int]


class FindUnion:
    def __init__(self, n: int) -> None:
        self._parents = list(range(n))
        self._sizes = [1 for _ in range(n)]

    def find(self, element: int) -> int:
        curr = element
        while self._parents[curr] != curr:
            curr = self._parents[curr]
        # flatten element to parent as well
        self._parents[element] = curr

        return curr

    def union(self, element_1: int, element_2: int) -> bool:
        parent_1 = self.find(element_1)
        parent_2 = self.find(element_2)

        if parent_1 == parent_2:
            return False

        if self._sizes[parent_1] < self._sizes[parent_2]:
            # set 1 is smaller
            smaller = parent_1
            larger = parent_2
        else:
            smaller = parent_2
            larger = parent_1

        self._parents[smaller] = larger
        self._sizes[larger] += self._sizes[smaller]
        self._sizes[smaller] = 0

        self._parents[element_1] = larger
        self._parents[element_2] = larger

        return True

    @property
    def sizes(self) -> list[int]:
        return self._sizes


def dist(p1: Point3D, p2: Point3D) -> int:
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    return (x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str, first_part_iterations: int = 1000) -> Solution:
    points = []
    for line in s.splitlines():
        x, y, z = line.split(",")
        points.append((int(x), int(y), int(z)))

    distances: list[tuple[int, tuple[int, int]]] = []

    for i in range(len(points) - 1):
        for j in range(i + 1, len(points)):
            d = dist(points[i], points[j])
            heappush(distances, (d, (i, j)))

    disjoint_set = FindUnion(len(distances))

    unique_sets = len(points)

    for _ in range(first_part_iterations):
        _, (idx1, idx2) = heappop(distances)
        if disjoint_set.union(idx1, idx2):
            unique_sets -= 1

    part_1 = reduce(operator.mul, sorted(disjoint_set.sizes, reverse=True)[0:3], 1)

    while True:
        d, (idx1, idx2) = heappop(distances)
        if disjoint_set.union(idx1, idx2):
            unique_sets -= 1
        if unique_sets == 1:
            # This is the merge of the last two sets remaining
            fx_1 = points[idx1][0]
            fx_2 = points[idx2][0]
            break

    return part_1, fx_1 * fx_2


TEST_INPUT = """\
162,817,812
57,618,57
906,360,560
592,479,940
352,342,300
466,668,158
542,29,236
431,825,988
739,650,466
52,470,668
216,146,977
819,987,18
117,168,530
805,96,715
346,949,466
970,615,88
941,993,340
862,61,35
984,92,344
425,690,689
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    [
        (TEST_INPUT, (40, 25272)),
    ],
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s, 10).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
