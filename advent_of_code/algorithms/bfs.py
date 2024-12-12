from typing import TypeVar, TypeAlias, Hashable, Callable, Iterable

TNode = TypeVar("TNode", bound=Hashable)
GetAdjacentNodesFuncTypeDef: TypeAlias = Callable[[TNode], Iterable[TNode]]


def bfs(start: TNode, get_nodes: GetAdjacentNodesFuncTypeDef) -> set[TNode]:
    """
    Performs a breadth first search on a graph-like structure.

    :param start: the starting node
    :param get_nodes: a function that takes a node as input and returns its adjacent nodes
    """
    queue = [start]
    result = {start}

    while queue:
        node = queue.pop()
        for neighbor in get_nodes(node):
            if neighbor not in result:
                queue.append(neighbor)
                result.add(neighbor)

    return result