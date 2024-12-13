import re
from typing import Iterable, Optional
import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data
from fractions import Fraction


YEAR = 2024
DAY = 13


def parse_input(s: str, add_prize: int = 0) -> Iterable[tuple[int, int]]:
    for line in s.splitlines():
        a, b = re.findall(r"\d+", line)
        to_add = add_prize if line.startswith("Prize") else 0
        yield int(a) + to_add, int(b) + to_add


def solve_eq(equation: list[tuple[int, int]]) -> Optional[tuple[int, int]]:
    assert len(equation) == 3
    [(coeff_a_x, coeff_a_y), (coeff_b_x, coeff_b_y), (X, Y)] = equation

    # Derived a and b by hand :)
    a = (Fraction(X * coeff_b_y) - Fraction(Y * coeff_b_x)) / (
        coeff_a_x * coeff_b_y - coeff_a_y * coeff_b_x
    )
    b = (Y - a * coeff_a_y) / coeff_b_y

    if a.is_integer() and b.is_integer():
        return a.numerator, b.numerator
    else:
        return 0, 0


def get_cost(equations: list[list[tuple[int, int]]]) -> int:
    return sum(3 * a + b for a, b in [solve_eq(equation) for equation in equations])


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    equations = [list(parse_input(line)) for line in s.split("\n\n")]
    part_1 = get_cost(equations)
    equations_2 = [
        list(parse_input(line, add_prize=10000000000000)) for line in s.split("\n\n")
    ]
    part_2 = get_cost(equations_2)

    return part_1, part_2


TEST_INPUT = """\
Button A: X+94, Y+34
Button B: X+22, Y+67
Prize: X=8400, Y=5400

Button A: X+26, Y+66
Button B: X+67, Y+21
Prize: X=12748, Y=12176

Button A: X+17, Y+86
Button B: X+84, Y+37
Prize: X=7870, Y=6450

Button A: X+69, Y+23
Button B: X+27, Y+71
Prize: X=18641, Y=10279
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (480, 0)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
