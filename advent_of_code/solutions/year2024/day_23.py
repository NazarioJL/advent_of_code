from collections import defaultdict
from typing import cast

import networkx as nx
import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2024
DAY = 23


def find_cycles_size_3(graph: dict[str, set[str]]) -> set[tuple[str, str, str]]:
    # I know I will be severely punished for writing this aberration of code. Sorry mom!

    # This was a clear mistake that happened to work for _cliques_ of 3. A cycle of
    # size 3; Happens to be the same as a clique of 3! Oh, well, in this case 2 errors
    # made it right... C'est la vie.

    result = set()

    def dfs(first: str, second: str | None = None, third: str | None = None) -> None:
        if second is None:
            for neighbor in graph[first]:
                if neighbor == first:
                    continue
                dfs(first, neighbor)
        elif third is None:
            for neighbor in graph[second]:
                if neighbor == second:
                    continue
                dfs(first, second, neighbor)
        else:
            for neighbor in graph[third]:
                if neighbor == first:
                    unique = sorted([first, second, third])
                    result.add(tuple(unique))

    for node in graph.keys():
        dfs(node)

    return cast(set[tuple[str, str, str]], result)


def visualize(graph: nx.Graph) -> None:
    import matplotlib.pyplot as plt

    nx.draw(graph, with_labels=True)
    plt.show()


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    nx_graph = nx.Graph()
    graph = defaultdict(set)  # Used for ghetto implementation
    for line in s.splitlines():
        a, b = line.split("-")
        graph[a].add(b)
        graph[b].add(a)
        nx_graph.add_edge(a, b)

    # visualize(nx_graph)
    part_1 = sum(
        1
        for group in find_cycles_size_3(graph)
        if any(item[0] == "t" for item in group)
    )

    _, biggest_clique = max(  # Is this cheating?
        (len(clique), clique) for clique in nx.clique.find_cliques(nx_graph)
    )

    part_2 = ",".join(sorted(biggest_clique))

    return part_1, part_2


TEST_INPUT = """\
kh-tc
qp-kh
de-cg
ka-co
yn-aq
qp-ub
cg-tb
vc-aq
tb-ka
wh-tc
yn-cg
kh-ub
ta-co
de-co
tc-td
tb-wq
wh-td
ta-ka
td-qp
aq-cg
wq-ub
ub-vc
de-ta
wq-aq
wq-vc
wh-yn
ka-de
kh-ta
co-tc
wh-qp
tb-vc
td-yn
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    [
        (TEST_INPUT, (7, "co,de,ka,ta")),
    ],
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
