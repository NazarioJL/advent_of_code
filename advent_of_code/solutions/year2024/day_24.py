import operator

from enum import Enum
from functools import cache
from functools import reduce
from typing import Callable
from typing import TypeAlias

import networkx as nx

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2024
DAY = 24


class Op(Enum):
    XOR = "XOR"
    AND = "AND"
    OR = "OR"


Circuit: TypeAlias = (
    str
    | tuple[str, Op, str]
    | tuple[str, Op, "Circuit"]  # Probably not needed
    | tuple["Circuit", Op, "Circuit"]
)


def is_simple(circuit: Circuit) -> bool:
    """Tests if circuit is in the form (str, Op, str)"""
    if isinstance(circuit, str):
        return False
    left, op, right = circuit
    return isinstance(left, str) and isinstance(right, str) and isinstance(op, Op)


def normalize(circuit: Circuit) -> Circuit:
    """Attempts to normalize a circuit for comparisons"""
    if isinstance(circuit, str):
        return circuit
    left, op, right = circuit
    if isinstance(left, str) and isinstance(right, str):
        return min(left, right), op, max(left, right)

    left_simple = is_simple(left)
    right_simple = is_simple(right)

    if left_simple and right_simple:
        # This should only be the case for "z01" -> (x01 XOR y01) XOR (x00 AND y00)
        if left[1] == Op.XOR:
            return normalize(left), op, normalize(right)
        return normalize(right), op, normalize(left)
    if right_simple:  # Vertical flip about operator
        return normalize(right), op, normalize(left)
    return normalize(left), op, normalize(right)


def expander(lookup: dict[str, Circuit]) -> Callable[[str], Circuit]:
    @cache
    def _expand(n: str) -> Circuit:
        if n[0] == "y" or n[0] == "x":
            return n
        lh, o, rh = lookup[n]  # type: ignore
        lh, rh = min(lh, rh), max(lh, rh)
        return _expand(lh), o, _expand(rh)

    return _expand


def label_var(var: str, level: int) -> str:
    return f"{var}{level:02}"


def label_x(level: int) -> str:
    return label_var("x", level)


def label_y(level: int) -> str:
    return label_var("y", level)


def label_z(level: int) -> str:
    return label_var("z", level)


OPERATOR_TO_OP = {
    "XOR": operator.xor,
    "AND": operator.and_,
    "OR": operator.or_,
}


def build_half_adder(level: int) -> Circuit:
    return label_x(level), Op.XOR, label_y(level)


def build_carry(level: int) -> Circuit:
    left = label_x(level), Op.AND, label_y(level)
    if level == 0:
        return left
    return (
        left,
        Op.OR,
        (build_half_adder(level), Op.AND, build_carry(level - 1)),
    )


def build_full_adder(level: int) -> Circuit:
    left = build_half_adder(level)
    if level == 0:
        return left
    return (
        left,
        Op.XOR,
        (build_carry(level - 1)),
    )


@aoc.partial(1)
def part_1(s: str) -> int:
    init, stmts = s.split("\n\n")
    graph = nx.DiGraph()
    statements = {}
    values = {}

    for stmt in init.splitlines():
        var, val = stmt.split(":")
        values[var] = int(val.strip())

    for stmt in stmts.splitlines():
        lhs, op, rhs, _, res = stmt.split(" ")
        graph.add_edge(lhs, res)
        graph.add_edge(rhs, res)
        statements[res] = lhs, op, rhs

    for item in nx.topological_sort(graph):
        if item in values:
            continue
        lhs, op, rhs = statements[item]
        values[item] = OPERATOR_TO_OP[op](values[lhs], values[rhs])

    zs = sorted(((var, values[var]) for var in values if var[0] == "z"), reverse=True)

    return reduce(lambda a, e: a * 2 + e, (n for _, n in zs))


@aoc.partial(2)
def part_2(s: str) -> str:
    _, stmts = s.split("\n\n")
    expressions = {}

    for stmt in stmts.splitlines():
        lhs, op, rhs, _, res = stmt.split(" ")
        ll = min(lhs, rhs)
        rr = max(lhs, rhs)
        expressions[res] = (ll, Op(op), rr)

    swaps = []

    zs = [label_z(i) for i in range(45)]
    full_adders = {z: build_full_adder(i) for i, z in enumerate(zs)}
    exp_fun = expander(expressions)
    expanded_expressions = {
        node: normalize(exp_fun(node)) for node in expressions.keys()
    }

    circuit_to_label_lookup = {v: k for k, v in expanded_expressions.items()}

    for z in zs:
        # TODO: We are doing extra work by re-calculating the whole dependency graph
        expected = full_adders[z]
        actual = expanded_expressions[z]

        if expected != actual:
            # either the whole expression is wrong, or one of the parts is
            # This makes the assumption that the incorrect parts will have a proper
            # replacement
            if expected in circuit_to_label_lookup:
                to_swap_1 = circuit_to_label_lookup[expected]
                to_swap_2 = z
            else:
                left_expected, op_expected, right_expected = expected
                left_actual, op_actual, right_actual = actual

                if left_expected != left_actual:
                    to_swap_1 = circuit_to_label_lookup[left_expected]
                    to_swap_2 = circuit_to_label_lookup[left_actual]
                else:
                    to_swap_1 = circuit_to_label_lookup[right_expected]
                    to_swap_2 = circuit_to_label_lookup[right_actual]
            expressions[to_swap_1], expressions[to_swap_2] = (
                expressions[to_swap_2],
                expressions[to_swap_1],
            )
            swaps.append((to_swap_1, to_swap_2))

            # There was a swap, re-calculate dependency graph
            exp_fun = expander(expressions)

            expanded_expressions = {
                node: normalize(exp_fun(node)) for node in expressions.keys()
            }

            circuit_to_label_lookup = {v: k for k, v in expanded_expressions.items()}

    return ",".join(sorted(e for swap in swaps for e in swap))


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    return part_1(s), part_2(s)


TEST_INPUT = """\
x00: 1
x01: 0
x02: 1
x03: 1
x04: 0
y00: 1
y01: 1
y02: 1
y03: 1
y04: 1

ntg XOR fgs -> mjb
y02 OR x01 -> tnw
kwq OR kpj -> z05
x00 OR x03 -> fst
tgd XOR rvg -> z01
vdt OR tnw -> bfw
bfw AND frj -> z10
ffh OR nrd -> bqk
y00 AND y03 -> djm
y03 OR y00 -> psh
bqk OR frj -> z08
tnw OR fst -> frj
gnj AND tgd -> z11
bfw XOR mjb -> z00
x03 OR x00 -> vdt
gnj AND wpb -> z02
x04 AND y00 -> kjc
djm OR pbm -> qhw
nrd AND vdt -> hwm
kjc AND fst -> rvg
y04 OR y02 -> fgs
y01 AND x02 -> pbm
ntg OR kjc -> kwq
psh XOR fgs -> tgd
qhw XOR tgd -> z09
pbm OR djm -> kpj
x03 XOR y03 -> ffh
x00 XOR y04 -> ntg
bfw OR bqk -> z06
nrd XOR fgs -> wpb
frj XOR qhw -> z04
bqk OR frj -> z07
y03 OR x01 -> nrd
hwm AND bqk -> z03
tgd XOR rvg -> z12
tnw OR pbm -> gnj
"""


def test_solve() -> None:
    assert part_1(TEST_INPUT).value == 2024


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
