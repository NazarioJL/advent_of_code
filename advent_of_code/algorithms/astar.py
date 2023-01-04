from fractions import Fraction
from heapq import heappop
from heapq import heappush
from typing import Callable
from typing import cast
from typing import Hashable
from typing import Iterable
from typing import Protocol
from typing import TypeVar


class PathNotFoundError(Exception):
    pass


class InconsistentStateError(Exception):
    pass


class CostType(Protocol):
    def __add__(self, other: "CostType") -> "CostType":
        pass

    def __lt__(self, other: "CostType") -> bool:
        pass


AStarState = TypeVar("AStarState", bound=Hashable)
AStarCostType = TypeVar("AStarCostType", int, float, Fraction)

GetAdjacentFuncTypeDef = Callable[
    [AStarState], Iterable[tuple[AStarState, AStarCostType]]
]
HeuristicFuncTypeDef = Callable[[AStarState, AStarState], AStarCostType]


def a_star_search(
    start: AStarState,
    goal: AStarState,
    get_adjacent: GetAdjacentFuncTypeDef,
    heuristic: HeuristicFuncTypeDef,
    max_cost: AStarCostType | None = None,
) -> Iterable[tuple[AStarState, AStarCostType]]:
    came_from: dict[AStarState, AStarState | None] = {}
    cost_so_far: dict[AStarState, AStarCostType] = {}

    _zero_cost = cast(AStarCostType, 0)
    came_from[start] = None
    cost_so_far[start] = _zero_cost
    pq: list[tuple[AStarCostType, AStarState]] = [(_zero_cost, start)]

    found = False

    while pq:
        priority, current = heappop(pq)
        # current is the highest priority

        if max_cost is not None:
            if priority > max_cost:
                raise PathNotFoundError(
                    f"Cannot do better than {max_cost}, lowest cost at: {priority}"
                )

        if current == goal:
            found = True
            break
        for adj, cost_to_adj in get_adjacent(current):
            new_cost = cost_so_far[current] + cost_to_adj
            if adj not in cost_so_far or new_cost < cost_so_far[adj]:
                cost_so_far[adj] = new_cost
                priority = new_cost + heuristic(adj, goal)
                heappush(pq, (priority, adj))
                came_from[adj] = current

    if not found:
        raise PathNotFoundError

    path = []
    node: AStarState | None = goal

    while node != start:
        if node is None:
            raise InconsistentStateError("Expected node in path to be not `None`")
        path.append((node, cost_so_far[node]))
        node = came_from[node]

    path.append((start, _zero_cost))

    path.reverse()

    return path
