from enum import Enum
from itertools import cycle
from typing import NamedTuple, Protocol, TypeVar, Self

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.grids import Coord2D
from advent_of_code.solutions.year2024.tmp import InfiniteLoop
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2024
DAY = 6


class Directions(Enum):
    UP = "^"
    DOWN = "v"
    LEFT = "<"
    RIGHT = ">"


DIRECTION_TO_OFFSET: dict[Directions, Coord2D] = {
    Directions.UP: Coord2D(y=-1, x=0),
    Directions.RIGHT: Coord2D(y=0, x=1),
    Directions.DOWN: Coord2D(y=1, x=0),
    Directions.LEFT: Coord2D(y=0, x=-1),
}


class Guard(NamedTuple):
    """A player that has a direction and a 2D location"""

    location: Coord2D
    direction: Directions


class PatrolResult(NamedTuple):
    type_: str = "PatrolResult"


class InfiniteLoop(NamedTuple):
    type_: str = "InfiniteLoop"


class Exited(NamedTuple):
    path: list[Guard]
    type_: str = "Exited"


class Comparable(Protocol):
    def __eq__(self: Self, other: object) -> bool:
        pass

    def __lt__(self: Self, other: Self) -> bool:
        pass

    def __gt__(self: Self, other: Self) -> bool:
        pass

    def __ge__(self: Self, other: Self) -> bool:
        pass

    def __le__(self: Self, other: Self) -> bool:
        pass


TCmp = TypeVar("TCmp", bound=Comparable)


def in_bounds(x: Comparable, a: Comparable, b: Comparable) -> bool:
    min_ = min(a, b)
    max_ = max(a, b)
    return min_ <= x <= max_


def patrol_grid(
    grid: list[str], guard: Guard, extra_obstacle: Coord2D | None
) -> Exited | InfiniteLoop:
    rows = len(grid)
    cols = len(grid[0])
    current = guard
    next_direction = cycle(DIRECTION_TO_OFFSET.keys())
    next(next_direction)

    path = [guard]
    visited = set()

    while True:
        next_loc = current.location + DIRECTION_TO_OFFSET[current.direction]
        if in_bounds(next_loc.x, 0, cols - 1) and in_bounds(next_loc.y, 0, rows - 1):
            next_tile = (
                "#"
                if extra_obstacle and next_loc == extra_obstacle
                else grid[next_loc.y][next_loc.x]
            )
            match next_tile:
                case "." | "^":
                    current = Guard(next_loc, current.direction)
                    if current in visited:
                        return InfiniteLoop()
                    path.append(current)
                    visited.add(current)
                case "#":  # rotate
                    rotated = next(next_direction)
                    current = Guard(current.location, rotated)
                case "_":
                    raise ValueError
        else:
            return Exited(path=path)


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    puzzle_map = [line for line in s.splitlines()]
    cols = len(puzzle_map[0])
    rows = len(puzzle_map)
    start: Guard | None = None
    for col in range(cols):
        for row in range(rows):
            if puzzle_map[row][col] == "^":
                start = Guard(direction=Directions.UP, location=Coord2D(y=row, x=col))
                break
    assert start, "Could not find initial position"

    result = patrol_grid(puzzle_map, start, None)

    assert isinstance(result, Exited)
    unique_locs = set(p.location for p in result.path)
    part_1 = len(unique_locs)

    # Uncomment to make visualization
    # visualize(grid=puzzle_map, path=result.path, start=start, end=result.path[-1])

    # Add an obstacle on every path possible
    # TODO: please optimize this
    # Consider using last 3 points to see if a valid loop can form

    unique_locs.discard(start.location)
    part_2 = 0
    for loc in unique_locs:
        result = patrol_grid(puzzle_map, start, loc)
        if isinstance(result, Exited):
            pass
        elif isinstance(result, InfiniteLoop):
            part_2 += 1
        else:
            raise ValueError("Unexpected result")

    return part_1, part_2


# 5023 4883
def visualize(
    grid: list[str],
    path: list[Guard],
    start: Guard,
    end: Guard,
) -> None:
    from PIL import Image, ImageDraw, ImageColor

    def guard_to_xy(player: Guard) -> tuple[int, int]:
        return player.location.x, player.location.y

    cols = len(grid[0])
    rows = len(grid)

    image = Image.new("RGBA", (cols, rows), color="black")
    draw = ImageDraw.Draw(image, "RGBA")

    for idx, guard in enumerate(path):
        percent = 100.0 - int((idx / len(path)) * 1000) / 10
        new_color = f"hsl(0, 100%, {percent}%)"
        color = ImageColor.getrgb(new_color)
        draw.point((guard_to_xy(guard)), fill=color)

    draw.point((guard_to_xy(start)), fill="yellow")

    for col in range(cols):
        for row in range(rows):
            if grid[row][col] == "#":
                draw.point((col, row), fill="blue")

    draw.point((0, 0), fill="green")
    draw.point(guard_to_xy(end), fill="cyan")

    print(end)

    image.show()


TEST_INPUT = """\
....#.....
.........#
..........
..#.......
.......#..
..........
.#..^.....
........#.
#.........
......#...
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (41, 6)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
