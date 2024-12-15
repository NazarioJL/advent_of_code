import re
import time

from collections import defaultdict
from functools import reduce
from typing import NamedTuple
from typing import Optional

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.screen import Screen
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2024
DAY = 14


class Robot(NamedTuple):
    position: tuple[int, int]
    velocity: tuple[int, int]


def get_pos(
    pos: tuple[int, int], vel: tuple[int, int], secs: int, dims: tuple[int, int]
) -> tuple[int, int]:
    x, y = pos
    width, height = dims
    new_x, new_y = x + vel[0] * secs, y + vel[1] * secs

    _, new_x = divmod(new_x, width)
    _, new_y = divmod(new_y, height)
    return new_x, new_y


def get_quadrant(pos: tuple[int, int], dims: tuple[int, int]) -> Optional[int]:
    x, y = pos
    width, height = dims
    if x == width // 2 or y == height // 2:
        return None
    a, b = x > width // 2, y > height // 2
    return 1 * (1 if a else 0) + 2 * (1 if b else 0)


def visualize(robots: list[Robot], dims: tuple[int, int]) -> None:
    import matplotlib.pyplot as plt

    from matplotlib.animation import FuncAnimation

    width, height = dims
    start_at = 6400

    def animate(i) -> None:
        plt.cla()
        plt.gca().invert_yaxis()
        x = []
        y = []
        secs = i + start_at
        for robot in robots:
            r_x, r_y = robot.position
            r_v_x, r_v_y = robot.velocity
            new_x, new_y = r_x + r_v_x * secs, r_y + r_v_y * secs
            _, new_x = divmod(new_x, width)
            _, new_y = divmod(new_y, height)
            x.append(new_x)
            y.append(new_y)
        plt.plot(x, y, "ro")

        xmas_x = []
        xmas_y = []
        for x, y in zip(x, y):
            if x > 46 and x < 74 and y > 40 and y < 68:
                xmas_x.append(x)
                xmas_y.append(y)

        plt.plot(xmas_x, xmas_y, "go")

        plt.title(f"Seconds: {secs}")
        if secs == 6753:
            time.sleep(20)
        if secs == 6754:
            time.sleep(2)

    plt.gca().invert_yaxis()
    fig = plt.figure()
    ani = FuncAnimation(fig, animate, interval=20)
    plt.show()


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    width = 101
    height = 103
    total_secs = 6752
    final_positions = defaultdict(int)
    for line in s.splitlines():
        p1, p2, v1, v2 = (int(n) for n in re.findall(r"-?\d+", line))
        final_positions[get_pos((p1, p2), (v1, v2), total_secs, (width, height))] += 1

    screen = Screen(start_x=0, start_y=0, end_x=width, end_y=height, default_pixel=".")

    for (x, y), cnt in final_positions.items():
        screen.draw(str(cnt), x=x, y=y)

    for i in range(width):
        screen.draw(" ", x=i, y=height // 2)

    for i in range(height):
        screen.draw(" ", x=width // 2, y=i)

    # screen.render()

    # for x, y in product(range(width), range(height)):
    #     num = get_quadrant((x, y), (width, height))
    #
    #     screen.draw(str(num) if num is not None else " ", x=x, y=y)
    #
    # screen.render()

    quadrant_count = defaultdict(int)

    for pos, cnt in final_positions.items():
        quadrant = get_quadrant(pos, (width, height))
        if quadrant is not None:
            quadrant_count[quadrant] += cnt

    part_1 = reduce(lambda acc, e: acc * e, quadrant_count.values(), 1)
    part_1 = 0

    robots = []
    for line in s.splitlines():
        p1, p2, v1, v2 = (int(n) for n in re.findall(r"-?\d+", line))
        robots.append(Robot(position=(p1, p2), velocity=(v1, v2)))
    visualize(robots=robots, dims=(width, height))

    return part_1, 0


TEST_INPUT = """\
p=0,4 v=3,-3
p=6,3 v=-1,-3
p=10,3 v=-1,2
p=2,0 v=2,-1
p=0,0 v=1,3
p=3,0 v=-2,-2
p=7,6 v=-1,-3
p=3,0 v=-1,-2
p=9,3 v=2,3
p=7,3 v=-1,2
p=2,4 v=2,-3
p=9,5 v=-3,-3
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (12, 0)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
