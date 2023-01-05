from collections.abc import Callable
from typing import NamedTuple

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import AnswerType
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2022
DAY = 5


Cargo = dict[str, list[str]]


class Operation(NamedTuple):
    count: int
    origin: str
    destination: str


def parse_input(s: str) -> tuple[Cargo, list[Operation]]:
    lines = s.splitlines()

    cargo: Cargo = {}
    operations = []

    index_to_label: dict[int, str] = {}
    index_to_crate_list: dict[int, list[str]] = {}

    is_parsing_cargo = True
    for line in lines:
        if not line:
            is_parsing_cargo = False
            continue

        if is_parsing_cargo:
            for idx, c in enumerate(line):
                if c.isalpha():
                    if idx not in index_to_crate_list:
                        index_to_crate_list[idx] = []
                    index_to_crate_list[idx].append(c)
                elif c.isdigit():
                    index_to_label[idx] = c
                else:
                    continue
        else:
            [_, count, _, origin, _, dest] = line.split()
            operations.append(
                Operation(count=int(count), origin=origin, destination=dest)
            )

    for idx, crates in index_to_crate_list.items():
        crates.reverse()
        cargo[index_to_label[idx]] = crates

    return cargo, operations


OpExecuteFuncTypeDef = Callable[[Cargo, Operation], None]


def execute_9000(cargo: Cargo, operation: Operation) -> None:
    for _ in range(operation.count):
        popped = cargo[operation.origin].pop()
        cargo[operation.destination].append(popped)


def execute_9001(cargo: Cargo, operation: Operation) -> None:
    new_stack = []
    for _ in range(operation.count):
        new_stack.append(cargo[operation.origin].pop())

    for crate in reversed(new_stack):
        cargo[operation.destination].append(crate)


def predict_arrangement(
    cargo: Cargo, operations: list[Operation], op_exec: OpExecuteFuncTypeDef
) -> str:
    for op in operations:
        op_exec(cargo, op)

    top = []
    for lbl, cargo_stack in cargo.items():
        top.append((lbl, cargo_stack.pop()))

    result = []
    for _, crate in sorted(top):
        result.append(crate)

    return "".join(result)


def part_1(s: str) -> AnswerType:
    cargo, operations = parse_input(s)
    return predict_arrangement(cargo, operations, execute_9000)


def part_2(s: str) -> AnswerType:
    cargo, operations = parse_input(s)
    return predict_arrangement(cargo, operations, execute_9001)


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    return part_1(s), part_2(s)


TEST_INPUT = """\
    [D]
[N] [C]
[Z] [M] [P]
 1   2   3

move 1 from 2 to 1
move 3 from 1 to 3
move 2 from 2 to 1
move 1 from 1 to 2
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, ("CMZ", "MCD")),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
