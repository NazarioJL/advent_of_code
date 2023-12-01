from enum import auto
from enum import Enum
from itertools import pairwise
from typing import Iterable
from typing import NamedTuple
from typing import Union

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2022
DAY = 9


class Point2D(NamedTuple):
    x: int
    y: int

    def __add__(self, other: Union["Point2D", tuple]) -> "Point2D":
        if isinstance(other, Point2D):
            return Point2D(x=self.x + other.x, y=self.y + other.y)
        elif isinstance(other, tuple) and len(other) == 2:
            return Point2D(x=(self.x + other[0]), y=(self.y + other[1]))
        else:
            raise TypeError(f"{other} is not valid")

    @staticmethod
    def origin() -> "Point2D":
        return Point2D(x=0, y=0)


def sign(n: int) -> int:
    if n > 0:
        return 1
    elif n < 0:
        return -1
    else:
        return 0


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    CENTER = auto()


DIRECTION_OFFSET = {
    Direction.UP: (0, 1),
    Direction.DOWN: (0, -1),
    Direction.RIGHT: (1, 0),
    Direction.LEFT: (-1, 0),
    Direction.CENTER: (0, 0),
}

KEY_DIRECTION = {
    "R": Direction.RIGHT,
    "L": Direction.LEFT,
    "U": Direction.UP,
    "D": Direction.DOWN,
}


class Operation(NamedTuple):
    direction: Direction
    count: int


def print_rope(rope: list[Point2D]) -> None:
    rope_spots = {}
    min_x, max_x, min_y, max_y = None, None, None, None

    def update(val: int, cmp: int, func) -> int:  # type: ignore
        return cmp if val is None else func(val, cmp)

    for idx, p in enumerate(rope):
        min_x = update(min_x, p.x, min)
        max_x = update(max_x, p.x, max)
        min_y = update(min_y, p.y, min)
        max_y = update(max_y, p.y, max)

        if p in rope_spots:
            continue
        char = "H" if idx == 0 else str(idx)
        rope_spots[p] = char

    for row in reversed(range(min_y - 1, max_y + 1)):
        buff = []
        for col in range(min_x - 1, max_x + 1):
            buff.append(rope_spots.get(Point2D(x=col, y=row), "."))
        print("".join(buff))


def move_head(point: Point2D, direction: Direction) -> Point2D:
    return point + DIRECTION_OFFSET[direction]


def follow(leader: Point2D, follower: Point2D) -> Point2D:
    delta_x = leader.x - follower.x
    delta_y = leader.y - follower.y

    sum_sqr = delta_y * delta_y + delta_x * delta_x

    # Sum of squares from (0, 0) (bottom-left)
    # XXXX
    # 458X
    # 125X
    # 014X
    # [0, 1, 2] -> Touching, no need to move
    # [4, 5, 8] -> Move (orthogonally for 4, diagonal for 5 and 8)
    # [X] -> Too far, ERROR!

    assert sum_sqr >= 0

    if sum_sqr > 8:
        raise ValueError(
            f"'follower' [{follower}] is way to behind 'leader' [{leader}]"
        )

    if sum_sqr in (0, 1, 2):
        return follower
    elif sum_sqr in (4, 5, 8):
        return Point2D(x=follower.x + sign(delta_x), y=follower.y + sign(delta_y))
    else:
        raise ValueError(f"Unexpected sum of square value {sum_sqr}!")


def move(rope: list[Point2D], direction: Direction) -> None:
    rope[0] += DIRECTION_OFFSET[direction]

    for leader_idx, follower_idx in pairwise(range(len(rope))):
        leader = rope[leader_idx]
        follower = rope[follower_idx]
        rope[follower_idx] = follow(leader=leader, follower=follower)


def find_total_tail_visited(ops: Iterable[Operation], rope_size: int) -> int:
    rope = [Point2D(x=0, y=0) for _ in range(rope_size)]
    tail_visited = {rope[-1]}

    for op in ops:
        for _ in range(op.count):
            move(rope=rope, direction=op.direction)
            tail_visited.add(rope[-1])

    return len(tail_visited)


def parse_input(s: str) -> Iterable[Operation]:
    for line in s.splitlines():
        dir_, cnt = line.split(maxsplit=1)
        yield Operation(direction=KEY_DIRECTION[dir_], count=int(cnt))


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    ops = list(parse_input(s))
    return (
        find_total_tail_visited(ops=ops, rope_size=2),
        find_total_tail_visited(ops=ops, rope_size=10),
    )


TEST_INPUT = """\
R 4
U 4
L 3
D 1
R 4
D 1
L 5
R 2
"""

TEST_INPUT_2 = """\
R 5
U 8
L 8
D 3
R 17
D 10
L 25
U 20
"""


@pytest.mark.parametrize(
    ("input_s", "rope_size", "expected"),
    ((TEST_INPUT, 2, 13), (TEST_INPUT, 10, 1), (TEST_INPUT_2, 10, 36)),
)
def test_solve(input_s: str, rope_size: int, expected: tuple[int, int]) -> None:
    ops = parse_input(input_s)
    assert find_total_tail_visited(ops=ops, rope_size=rope_size) == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
