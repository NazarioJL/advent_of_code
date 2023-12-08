import math
import re

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2023
DAY = 8


def parse_input(s: str) -> tuple[list[str], dict[str, tuple[str, str]]]:
    commands, network_data = s.split("\n\n")

    network = {}
    for line in network_data.splitlines():
        node, left, right = re.findall(r"[A-Z0-9]{3,}", line)
        network[node] = (left, right)

    return [c for c in commands], network


def get_steps(
    commands: list[str],
    network: dict[str, tuple[str, str]],
    start_node: str,
    end_nodes: set[str],
) -> int:
    steps = 0
    current = start_node

    while True:
        for command in commands:
            if command == "L":
                current = network[current][0]
            else:  # command == "R"
                current = network[current][1]
            steps += 1
        if current in end_nodes:
            break

    return steps


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    commands, network = parse_input(s)

    steps_1 = get_steps(commands, network, "AAA", {"ZZZ"})

    ghost_start_nodes = {node: 0 for node in network.keys() if node.endswith("A")}
    ghost_end_nodes: set[str] = set(
        node for node in network.keys() if node.endswith("Z")
    )

    for start_node in ghost_start_nodes:
        steps = get_steps(commands, network, start_node, ghost_end_nodes)
        ghost_start_nodes[start_node] = steps

    steps_2 = math.lcm(*ghost_start_nodes.values())

    return steps_1, steps_2


TEST_INPUT = """\
RL

AAA = (BBB, CCC)
BBB = (DDD, EEE)
CCC = (ZZZ, GGG)
DDD = (DDD, DDD)
EEE = (EEE, EEE)
GGG = (GGG, GGG)
ZZZ = (ZZZ, ZZZ)
"""

TEST_INPUT_2 = """\
LLR

AAA = (BBB, BBB)
BBB = (AAA, ZZZ)
ZZZ = (ZZZ, ZZZ)
"""

TEST_INPUT_PART_2 = """\
LR

11A = (11B, XXX)
11B = (XXX, 11Z)
11Z = (11B, XXX)
22A = (22B, XXX)
22B = (22C, 22C)
22C = (22Z, 22Z)
22Z = (22B, 22B)
XXX = (XXX, XXX)
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    (
        (TEST_INPUT, (2, 2)),
        (TEST_INPUT_2, (6, 6)),
        (TEST_INPUT_2, (6, 6)),
    ),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
