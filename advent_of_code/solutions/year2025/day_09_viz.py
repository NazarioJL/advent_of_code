from itertools import pairwise

from matplotlib import patches
from matplotlib import pyplot as plt

from advent_of_code.solutions.year2025.day_09 import Point
from advent_of_code.solutions.year2025.day_09 import parse_input
from advent_of_code.solutions.year2025.day_09 import part_1
from advent_of_code.solutions.year2025.day_09 import part_2
from advent_of_code.utilities import get_input_data

TEST_INPUT = """\
7,1
11,1
11,7
9,7
9,5
2,5
2,3
7,3
"""


def make_rect(p1: Point, p2: Point, color: str = "green") -> patches.Rectangle:
    x1, y1 = p1
    x2, y2 = p2
    bottom_left_x = min(x1, x2)
    bottom_left_y = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)

    return patches.Rectangle(
        (bottom_left_x, bottom_left_y),
        width,
        height,
        linewidth=2,
        edgecolor="r",
        facecolor=color,
        alpha=0.5,
    )


def main():
    data = get_input_data(2025, 9)

    coords = parse_input(data)

    _, ax = plt.subplots()

    for (x1, y1), (x2, y2) in pairwise([coords[-1], *coords]):
        plt.plot([x1, x2], [y1, y2])

    part_1_p1, part_1_p2, _ = part_1(coords)
    part_2_p1, part_2_p2, _ = part_2(coords)

    rect_1 = make_rect(part_1_p1, part_1_p2, "blue")
    rect_2 = make_rect(part_2_p1, part_2_p2, "green")

    ax.add_patch(rect_1)
    ax.add_patch(rect_2)
    plt.show()


if __name__ == "__main__":
    main()
