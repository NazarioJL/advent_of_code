import operator
import re
from collections import deque
from functools import reduce
from re import RegexFlag
from typing import Callable
from typing import cast
from typing import Deque
from typing import Iterable
from typing import NamedTuple
from typing import TypeAlias

import pytest
from more_itertools import one
from more_itertools import take

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2022
DAY = 11


OpFuncTypeDef: TypeAlias = Callable[[int], int]
WorryReliefFuncTypeDef: TypeAlias = Callable[[int], int]


def make_fun(exp: str) -> OpFuncTypeDef:
    lh, op, rh = exp.split()
    ops = {
        "+": operator.add,
        "*": operator.mul,
    }
    op_func = ops[op]

    match (lh, rh):
        case ("old", "old"):
            return cast(OpFuncTypeDef, lambda x: op_func(x, x))
        case ("old", value):
            return cast(OpFuncTypeDef, lambda x: op_func(x, int(value)))
        case (value, "old"):
            return cast(OpFuncTypeDef, lambda x: op_func(int(value), x))
        case _:
            raise ValueError(f"Unexpected 'exp': {exp}")


class Monkey(NamedTuple):
    monkey_id: int
    items: Deque
    operation: Callable[[int], int]
    test: int
    true_case: int
    false_case: int


def parse_input(s: str) -> Iterable[Monkey]:
    monkey_id_re = r"Monkey (\d+):$\n"
    items_re = r"^\s+Starting items: (?P<items>[\d+,?\s?]+)$"
    expression_re = r"Operation: new = (.+)\n"
    test_div_re = r"Test: divisible by (\d+)\n"
    true_case_re = r"^\s+If true: throw to monkey (\d+)$"
    false_case_re = r"^\s+If false: throw to monkey (\d+)$"

    for monkey_text in s.split("\n\n"):
        monkey_id = int(one(re.findall(monkey_id_re, monkey_text, RegexFlag.MULTILINE)))
        items = (
            int(e)
            for e in one(re.findall(items_re, monkey_text, RegexFlag.MULTILINE)).split(
                ","
            )
        )
        expression = one(re.findall(expression_re, monkey_text, RegexFlag.MULTILINE))
        test_div = int(one(re.findall(test_div_re, monkey_text, RegexFlag.MULTILINE)))
        true_case = int(one(re.findall(true_case_re, monkey_text, RegexFlag.MULTILINE)))
        false_case = int(
            one(re.findall(false_case_re, monkey_text, RegexFlag.MULTILINE))
        )

        yield Monkey(
            monkey_id=monkey_id,
            items=deque(items),
            operation=make_fun(expression),
            test=test_div,
            true_case=true_case,
            false_case=false_case,
        )


def monkey_business(
    monkeys: Iterable[Monkey],
    total_rounds: int,
    worry_relief_func: WorryReliefFuncTypeDef,
    mod: int | None = None,
) -> int:
    monkeys_lookup = {m.monkey_id: m for m in monkeys}
    inspection_count = {m.monkey_id: 0 for m in monkeys}

    def step(
        monkey: Monkey,
    ) -> None:
        while monkey.items:
            item = monkey.items.popleft()
            new_item = monkey.operation(item)
            if mod:
                new_item %= mod
            inspection_count[monkey.monkey_id] += 1
            new_item = worry_relief_func(new_item)

            remainder = new_item % monkey.test

            thrown_to = monkey.true_case if remainder == 0 else monkey.false_case
            monkeys_lookup[thrown_to].items.append(new_item)

    for _ in range(total_rounds):
        for m in monkeys:
            step(monkey=m)

    return reduce(
        operator.mul, take(2, sorted(inspection_count.values(), reverse=True)), 1
    )


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    monkeys_1 = list(parse_input(s))

    def worry_relief_func_1(x: int) -> int:
        return x // 3

    part_1 = monkey_business(
        monkeys=monkeys_1,
        total_rounds=20,
        worry_relief_func=worry_relief_func_1,
    )

    prod = reduce(operator.mul, (m.test for m in monkeys_1))

    monkeys_2 = list(parse_input(s))

    def worry_relief_func_2(x: int) -> int:
        return x

    part_2 = monkey_business(
        monkeys=monkeys_2,
        total_rounds=10000,
        worry_relief_func=worry_relief_func_2,
        mod=prod,
    )

    return part_1, part_2


TEST_INPUT = """\
Monkey 0:
  Starting items: 79, 98
  Operation: new = old * 19
  Test: divisible by 23
    If true: throw to monkey 2
    If false: throw to monkey 3

Monkey 1:
  Starting items: 54, 65, 75, 74
  Operation: new = old + 6
  Test: divisible by 19
    If true: throw to monkey 2
    If false: throw to monkey 0

Monkey 2:
  Starting items: 79, 60, 97
  Operation: new = old * old
  Test: divisible by 13
    If true: throw to monkey 1
    If false: throw to monkey 3

Monkey 3:
  Starting items: 74
  Operation: new = old + 3
  Test: divisible by 17
    If true: throw to monkey 0
    If false: throw to monkey 1
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (10605, 2713310158)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
