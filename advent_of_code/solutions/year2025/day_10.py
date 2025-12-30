from heapq import heappop
from heapq import heappush
from typing import Iterator
from typing import NamedTuple
from typing import TypeAlias

import pytest

from z3 import Ints
from z3 import Optimize
from z3 import Sum
from z3 import sat

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2025
DAY = 10

State: TypeAlias = int
ButtonConfig: TypeAlias = list[int]


class MachineConfig(NamedTuple):
    end_state: State
    buttons: list[ButtonConfig]
    joltages: list[int]


def parse_input(s: str) -> Iterator[MachineConfig]:
    """Very ghetto way of parsing input"""

    def _parse_state(state_data: str) -> State:
        """Parses the state string from the input _e.g._ [#.#..] -> 101"""
        result = 0

        state_data = state_data.replace("[", "").replace("]", "")
        for idx, val in enumerate(state_data):
            if val == "#":
                result |= 1 << idx

        return result

    def _parse_button_config(config: str) -> ButtonConfig:
        """Parses the button configuration _e.g._ (1,3) --> 01010
        Makes assumption each number is < 10
        """
        config = config.replace("(", "").replace(")", "")

        return [int(num) for num in config.split(",")]

    def _parse_joltages(config: str) -> list[int]:
        config = config.replace("{", "").replace("}", "")
        return [int(num) for num in config.split(",")]

    for line in s.splitlines():
        parts = line.split()
        if len(parts) < 3:
            raise ValueError("Not enough parts: {}".format(line))
        end_state = _parse_state(parts[0])
        button_configs = [_parse_button_config(c) for c in parts[1:-1]]
        yield MachineConfig(end_state, button_configs, _parse_joltages(parts[-1]))


def get_minimum_presses_part_1(config: MachineConfig) -> int:
    heap: list[tuple[int, State]] = [(0, 0)]
    visited = {0}

    def _button_to_state(button_config: ButtonConfig) -> int:
        result = 0
        for button_id in button_config:
            result |= 1 << button_id
        return result

    buttons = [_button_to_state(b) for b in config.buttons]

    while heap:
        cnt, state = heappop(heap)
        if state == config.end_state:
            return cnt
        for button in buttons:
            new_state = state ^ button
            if new_state not in visited:
                heappush(heap, (cnt + 1, new_state))
            visited.add(new_state)

    raise ValueError("No solution found")


def get_minimum_presses_part_2(machine_config: MachineConfig) -> int:
    button_vars = Ints(f"b{idx}" for idx in range(len(machine_config.buttons)))
    solver = Optimize()

    for j_idx, joltage in enumerate(machine_config.joltages):
        included = []
        for button_idx, button in enumerate(machine_config.buttons):
            if j_idx in button:
                included.append(button_idx)
        solver.add(Sum(button_vars[idx] for idx in included) == joltage)

    for var in button_vars:
        # Add positive result constraint
        solver.add(var >= 0)
    solver.minimize(Sum(button_vars))

    if solver.check() == sat:
        model = solver.model()
        return sum(model[var].as_long() for var in button_vars)
    raise ValueError("Unable to solve")


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    machine_configs = list(parse_input(s))
    part_1 = sum(get_minimum_presses_part_1(config) for config in machine_configs)
    part_2 = sum(get_minimum_presses_part_2(config) for config in machine_configs)

    return part_1, part_2


TEST_INPUT = """\
[.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}
[...#.] (0,2,3,4) (2,3) (0,4) (0,1,2) (1,2,3,4) {7,5,12,7,2}
[.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    [
        (TEST_INPUT, (7, 33)),
    ],
)
def test_solve(input_s: str, expected: tuple[int, int]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
