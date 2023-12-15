import re
from collections import OrderedDict
from typing import cast
from typing import Literal
from typing import NamedTuple

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2023
DAY = 15


Operation = Literal["=", "-"]


class Step(NamedTuple):
    label: str
    operation: Operation
    focal_length: int | None


def parse_input(s: str) -> list[str]:
    return s.strip().split(",")


def parse_steps(steps: list[str]) -> list[Step]:
    result = []
    for step in steps:
        match = re.match(
            r"^(?P<label>[a-z]+)(?P<op>[=|-])(?P<focal_length>\d*)$", step
        ).groupdict()  # type: ignore
        result.append(
            Step(
                match["label"],
                cast(Operation, match["op"]),
                int(match["focal_length"]) if match["focal_length"] else None,
            )
        )

    return result


def get_hash(value: str) -> int:
    result = 0
    for char in value:
        result += ord(char)  # ASCII value
        result *= 17
        _, rem = divmod(result, 256)
        result = rem

    return result


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    steps_1 = parse_input(s)
    part_1 = sum(get_hash(step) for step in steps_1)

    steps_2 = parse_steps(steps_1)
    label_to_box = {step.label: get_hash(step.label) for step in steps_2}
    boxes: list[dict[str, int]] = [OrderedDict() for _ in range(256)]  # 256 boxes* 256

    for label, op, focal_length in steps_2:
        box = label_to_box[label]
        if op == "-":
            if label in boxes[box]:
                boxes[box].pop(label)
        elif op == "=":
            assert focal_length is not None
            if label in boxes[box]:
                boxes[box][label] = focal_length
            else:
                boxes[box][label] = focal_length
        else:
            raise ValueError(f"Unexpected op: '{op}'")

    part_2 = sum(
        sum((idx + 1) * value * (pos + 1) for pos, value in enumerate(box.values()))
        for idx, box in enumerate(boxes)
    )

    return part_1, part_2


TEST_INPUT = """\
rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (1320, 145)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
