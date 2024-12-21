from heapq import heapify
from heapq import heappop
from heapq import heappush
from typing import Callable
from typing import Hashable
from typing import Iterable
from typing import NamedTuple
from typing import Protocol
from typing import Self
from typing import TypeAlias
from typing import cast


class SupportsCost(Protocol):
    def __lt__(self, other: Self) -> bool:
        pass

    def __add__(self, other: Self) -> Self:
        pass


TNode: TypeAlias = Hashable
TCost: TypeAlias = SupportsCost

GetNeighborsFuncTypeDef = Callable[[TNode], Iterable[TNode]]
GetNeighborsWithCostFuncTypeDef = Callable[[TNode], Iterable[tuple[TNode, TCost]]]
GetCostFuncTypeDef = Callable[[TNode, TNode], TCost]


_zero_cost: SupportsCost = cast(TCost, 0)
_default_cost: SupportsCost = cast(TCost, 1)


class DykstraSearchResult(NamedTuple):
    costs: dict[Hashable, TCost]
    predecessors: dict[TNode, TNode | None]


def _default_get_cost(a: TNode, b: TNode) -> TCost:
    return _default_cost


def dykstra(
    start: TNode,
    get_neighbors: GetNeighborsFuncTypeDef | GetNeighborsWithCostFuncTypeDef,
    get_cost: GetCostFuncTypeDef = _default_get_cost,
    zero_cost: TCost = _zero_cost,
) -> DykstraSearchResult:
    """
    Performs the dykstra algorithm on an implicit graph. The edges of a node are
    described by the get_neighbors function, and associated

    :param start: starting node
    :param get_neighbors: function returning neighboring nodes along with cost for each node
    :param get_cost: function returning cost for each node
    :param zero_cost: cost of zero

    :returns: a tuple of the cost to reach node from start, and the predecessors of each node
    """

    costs: dict[TNode, TCost] = {}
    pq = [(zero_cost, start)]
    heapify(pq)
    visited = set()
    costs[start] = zero_cost

    while pq:
        distance, node = heappop(pq)
        if node in visited:
            continue
        visited.add(node)

        # get neighbors
        for neighbor in get_neighbors(node):
            if isinstance(neighbor, tuple):
                neighbor, cost = neighbor
            else:
                cost = get_cost(node, neighbor)
            new_cost = distance + cost
            if neighbor not in costs or new_cost < costs[neighbor]:
                costs[neighbor] = new_cost
                heappush(pq, (new_cost, neighbor))

    predecessors: dict[TNode, TNode | None] = {start: None}

    for node, distance in costs.items():
        for neighbor in get_neighbors(node):
            if isinstance(neighbor, tuple):
                neighbor, cost = neighbor
            else:
                cost = get_cost(node, neighbor)
            if costs[neighbor] == distance + cost:
                assert neighbor
                predecessors[neighbor] = node

    return DykstraSearchResult(costs=costs, predecessors=predecessors)


def get_path(target: TNode, predecessors: dict[TNode, TNode]) -> list[TNode]:
    path = []
    curr = target
    while curr:
        path.append(curr)
        curr = predecessors[curr]
    path.reverse()
    return path
