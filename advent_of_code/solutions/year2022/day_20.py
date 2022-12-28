from itertools import pairwise

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.parsers import parse_ints
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2022
DAY = 20


class Node:
    def __init__(self, val: int, mixer: int = 1) -> None:
        self.val = val * mixer
        self.next: Node | None = None
        self.prev: Node | None = None

    def __repr__(self) -> str:
        next_s = "None" if self.next is None else str(self.next.val)
        prev_s = "None" if self.prev is None else str(self.prev.val)
        return f"Node(val={self.val}, prev={prev_s}, next={next_s})"

    def __str__(self) -> str:
        next_s = "None" if self.next is None else str(self.next.val)
        prev_s = "None" if self.prev is None else str(self.prev.val)
        return f"Node(val={self.val}, prev={prev_s}, next={next_s})"


def print_list(node: Node) -> None:
    tmp = []
    stop = id(node)
    tmp.append(node.val)
    node = node.next

    while id(node) != stop:
        tmp.append(node.val)
        node = node.next

    print(",".join(str(n) for n in tmp))


def mix(node_list: list[Node]) -> None:
    total = len(node_list)
    for node in node_list:
        if node.val == 0:
            continue

        # Need to take into account removed node
        count = abs(node.val) % (total - 1)

        # remove node
        node.prev.next = node.next
        node.next.prev = node.prev

        tmp = node
        if node.val > 0:
            for _ in range(count):
                tmp = tmp.next
            node.next = tmp.next
            node.prev = tmp
            tmp.next = node
            node.next.prev = node
        elif node.val < 0:
            for _ in range(count):
                tmp = tmp.prev
            node.next = tmp
            node.prev = tmp.prev
            node.next.prev = node
            node.prev.next = node
        else:
            pass


def get_password(zero: Node, length: int) -> int:
    stops = [1000 % length, 2000 % length, 3000 % length]
    vals = []
    for j in stops:
        tmp = zero
        for _ in range(j):
            tmp = tmp.next
        vals.append(tmp.val)

    print(vals)

    return sum(vals)


def create_node_list(nums: list[int], mixer: int) -> tuple[list[Node], Node]:
    zero: Node | None = None
    result = []
    for num in nums:
        n = Node(val=num, mixer=mixer)
        if num == 0:
            zero = n
        result.append(n)
    assert zero is not None
    for p, n in pairwise(result):
        p.next = n
        n.prev = p

    # Make this circular
    last = result[-1]
    first = result[0]

    last.next = first
    first.prev = last

    return result, zero


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    nums = parse_ints(s)

    node_list_1, zero_1 = create_node_list(nums, mixer=1)
    mix(node_list_1)
    part_1 = get_password(zero_1, len(node_list_1))

    node_list_2, zero_2 = create_node_list(nums, mixer=811589153)

    print_list(zero_2)
    for i in range(10):
        mix(node_list_2)
        print_list(zero_2)

    part_2 = get_password(zero_2, len(node_list_2))

    return part_1, part_2


TEST_INPUT = """\
1
2
-3
3
-2
0
4
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (3, 1623178306)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
