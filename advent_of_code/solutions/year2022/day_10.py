from enum import Enum
from itertools import cycle
from typing import cast
from typing import Iterable
from typing import TypeAlias
from typing import Union

import pytest
from more_itertools import chunked

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2022
DAY = 10


class OpCode(Enum):
    NOOP = "noop"
    ADDX = "addx"


Instruction: TypeAlias = Union[OpCode, tuple[OpCode, int]]


def instr_str(inst: Instruction) -> str:
    if isinstance(inst, tuple):
        return f"{inst[0].value} {inst[1]}"
    else:
        return f"{inst.value}"


class CPU:
    """Extremely over-engineered class for the problem at hand"""

    OPCODE_CYCLES = {
        OpCode.NOOP: 1,
        OpCode.ADDX: 2,
    }

    def __init__(self, program: Iterable[Instruction], x: int = 1) -> None:
        self._program = cycle(program)
        self._x = x
        self._cycle = 0
        self._current_instruction: tuple[Instruction, int] | None = None

    def fetch(self) -> tuple[Instruction, int]:
        if self._current_instruction is not None:
            return self._current_instruction
        else:
            result = next(self._program)
            cycles = self.get_cycles(result)
            return result, cycles

    def step(self) -> tuple[int, int]:
        next_instruction, cycles_left = self.fetch()
        cycles_left = cycles_left - 1

        curr_x = self._x
        if cycles_left == 0:
            self._execute(next_instruction)
            self._current_instruction = None
        else:
            self._current_instruction = next_instruction, cycles_left
        curr_cycle = self._cycle
        self._cycle += 1
        return curr_x, curr_cycle

    def get_cycles(self, instruction: Instruction) -> int:
        opcode = self.get_opcode(instruction)
        return CPU.OPCODE_CYCLES[opcode]

    def get_opcode(self, instruction: Instruction) -> OpCode:
        if isinstance(instruction, tuple):
            return instruction[0]
        else:
            return instruction

    def _execute(self, instruction: Instruction) -> None:
        match instruction:
            case OpCode.NOOP:
                pass
            case (OpCode.ADDX, val):
                val = cast(int, val)
                self._x += val
            case _:
                raise ValueError

    @property
    def x(self) -> int:
        return self._x


def parse_input(s: str) -> list[Instruction]:
    parsed: list[Instruction] = []
    for line in s.splitlines():
        match line.split():
            case ["noop"]:
                parsed.append(OpCode.NOOP)
            case ["addx", val]:
                parsed.append((OpCode.ADDX, int(val)))
            case _:
                raise ValueError

    return parsed


def visualize(data: list[tuple[int, int]]) -> None:
    from matplotlib import pyplot as plt

    x = [e[0] for e in data]
    y = [e[1] for e in data]

    # This is interesting, there is a repeating cycle after some time.
    # Past 1000 iterations the pattern becomes apparent.
    plt.plot(x, y)
    plt.show()


def draw(data: list[tuple[int, int]]) -> str:
    if len(data) != 240:
        raise ValueError("data must have exactly 220 chars")

    result: list[str] = []

    for clock, x in data:
        hor = clock % 40
        sprite = (x - 1, x, x + 1)
        if hor in sprite:
            result.append("#")
        else:
            result.append(".")

    assert len(result) == 240

    return "\n".join("".join(c) for c in chunked(result, 40, strict=True))


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    instructions = parse_input(s)
    cpu = CPU(program=instructions)

    data = []
    signal = 0

    for _ in range(240):
        x, clock = cpu.step()
        data.append((clock, x))
        mod = (clock - 20 + 1) % 40
        if mod == 0:
            signal += x * (clock + 1)
        else:
            pass

    return signal, draw(data)


TEST_INPUT_SMALL = """\
noop
addx 3
addx -5
"""

TEST_INPUT = """\
addx 15
addx -11
addx 6
addx -3
addx 5
addx -1
addx -8
addx 13
addx 4
noop
addx -1
addx 5
addx -1
addx 5
addx -1
addx 5
addx -1
addx 5
addx -1
addx -35
addx 1
addx 24
addx -19
addx 1
addx 16
addx -11
noop
noop
addx 21
addx -15
noop
noop
addx -3
addx 9
addx 1
addx -3
addx 8
addx 1
addx 5
noop
noop
noop
noop
noop
addx -36
noop
addx 1
addx 7
noop
noop
noop
addx 2
addx 6
noop
noop
noop
noop
noop
addx 1
noop
noop
addx 7
addx 1
noop
addx -13
addx 13
addx 7
noop
addx 1
addx -33
noop
noop
noop
addx 2
noop
noop
noop
addx 8
noop
addx -1
addx 2
addx 1
noop
addx 17
addx -9
addx 1
addx 1
addx -3
addx 11
noop
noop
addx 1
noop
addx 1
noop
noop
addx -13
addx -19
addx 1
addx 3
addx 26
addx -30
addx 12
addx -1
addx 3
addx 1
noop
noop
noop
addx -9
addx 18
addx 1
addx 2
noop
noop
addx 9
noop
noop
noop
addx -1
addx 2
addx -37
addx 1
addx 3
noop
addx 15
addx -21
addx 22
addx -6
addx 1
noop
addx 2
addx 1
noop
addx -10
noop
noop
addx 20
addx 1
addx 2
addx 2
addx -6
addx -11
noop
noop
noop
"""


EXPECTED = """\
##..##..##..##..##..##..##..##..##..##..
###...###...###...###...###...###...###.
####....####....####....####....####....
#####.....#####.....#####.....#####.....
######......######......######......####
#######.......#######.......#######....."""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (13140, EXPECTED)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)), multiline_block=True)
