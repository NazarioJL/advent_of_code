from abc import ABC
from abc import abstractmethod
from enum import Enum
from enum import auto
from heapq import heappush, heappop
from typing import Generic, Union, Protocol, Iterable, Callable, Optional
from typing import Iterator
from typing import TypeVar

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2024
DAY = 3


class FiniteStateMachineError(Exception):
    pass


class FiniteStateNodeStatus(Enum):
    """Status a FSN can be in"""

    NotStarted = auto()
    Consuming = auto()
    Complete = auto()
    Error = auto()


class ConsumeResultType(Enum):
    """Types of a consume operation result"""

    Okay = auto()
    Complete = auto()
    Mismatch = auto()
    Error = auto()


class ConsumeResult(ABC, Iterable):
    """Represents the result of a consume operation"""

    pass

    @abstractmethod
    def __iter__(self) -> Iterator:
        pass


class Okay(ConsumeResult):
    """Represents an ok result of consuming a character"""

    def __iter__(self) -> Iterator[ConsumeResultType]:
        yield from [ConsumeResultType.Okay]


class Error(ConsumeResult):
    """Represents an error state of consuming a character"""

    def __iter__(self) -> Iterator[ConsumeResultType]:
        yield from [ConsumeResultType.Error]


class Complete(ConsumeResult):
    """Represents when an FSN has completed consuming characters"""

    def __init__(self, consumed: bool = False) -> None:
        self._consumed = consumed

    @property
    def consumed(self) -> bool:
        """Whether the token was consumed on completion"""
        return self._consumed

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ConsumeResult):
            raise TypeError()
        return isinstance(other, Complete) and other.consumed == self.consumed

    def __iter__(self) -> Iterator[Union[ConsumeResultType, bool]]:
        yield ConsumeResultType.Complete
        yield self._consumed


class Mismatch(ConsumeResult):
    """Represents an error state of consuming a character specific to a mismatch of an
    expected character"""

    def __init__(self, expected: str, given: str) -> None:
        self._expected = expected
        self._given = given

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ConsumeResult):
            raise TypeError()
        return (
            isinstance(other, Mismatch)
            and other.expected == self._expected
            and other.given == self._given
        )

    @property
    def expected(self) -> str:
        return self._expected

    @property
    def given(self) -> str:
        return self._given

    def __iter__(self) -> Iterator[Union[ConsumeResultType, str]]:
        yield ConsumeResultType.Mismatch
        yield self.expected
        yield self.given


class Operation(Enum):
    MULT = auto()


class Symbols(Enum):
    OPEN_PAREN = auto()
    CLOSE_PAREN = auto()
    COMMA = auto()


TToken = TypeVar("TToken", int, str, Operation, Symbols)


class FiniteStateNode(ABC, Generic[TToken]):
    """Base type for any finite state node"""

    def __init__(self) -> None:
        self._status: FiniteStateNodeStatus = FiniteStateNodeStatus.NotStarted

    @abstractmethod
    def consume(self, char: str) -> ConsumeResult:
        pass

    def _validate_for_token(self) -> None:
        if self._status != FiniteStateNodeStatus.Complete:
            raise FiniteStateMachineError(
                "Only a node which has completed can return a token value"
            )

    @property
    def status(self) -> FiniteStateNodeStatus:
        return self._status

    @property
    @abstractmethod
    def token(self) -> TToken:
        pass


class SupportsStringMatchMixin(Protocol):
    """Mixin for supporting string matching nodes"""

    _index: int
    _to_match: str
    _status: FiniteStateNodeStatus

    @property
    def status(self) -> FiniteStateNodeStatus:
        pass


class StringMatchMixin:
    def __init__(self, to_match: str) -> None:
        self._to_match = to_match
        self._index = 0
        super().__init__()

    def consume(self: SupportsStringMatchMixin, char: str) -> ConsumeResult:
        if not char or len(char) > 1:
            return Error()
        if self.status in (FiniteStateNodeStatus.Complete, FiniteStateNodeStatus.Error):
            return Error()
        if char == self._to_match[self._index]:
            self._index += 1
            if self._index == len(self._to_match):
                self._status = FiniteStateNodeStatus.Complete
                return Complete(True)
            else:
                self._status = FiniteStateNodeStatus.Consuming
                return Okay()
        else:
            self._status = FiniteStateNodeStatus.Error
            return Mismatch(self._to_match[self._index], char)

    def __str__(self) -> str:
        return f"StringMatch({self._to_match})"


class StringMatchNode(StringMatchMixin, FiniteStateNode[str]):
    """Matches any string"""

    def __init__(self, to_match: str) -> None:
        super().__init__(to_match=to_match)

    @property
    def token(self) -> str:
        self._validate_for_token()
        return self._to_match


class OpenParenNode(StringMatchMixin, FiniteStateNode[Symbols]):
    """Matches an open parenthesis symbol"""

    def __init__(self) -> None:
        super().__init__(to_match="(")

    @property
    def token(self) -> Symbols:
        self._validate_for_token()
        return Symbols.OPEN_PAREN

    def __str__(self) -> str:
        return "OpenParenNode['(']"


class CloseParenNode(StringMatchMixin, FiniteStateNode[Symbols]):
    """Matches a closing parenthesis symbol"""

    def __init__(self) -> None:
        super().__init__(to_match=")")

    @property
    def token(self) -> Symbols:
        self._validate_for_token()
        return Symbols.CLOSE_PAREN

    def __str__(self) -> str:
        return "CloseParenNode[')']"


class CommaNode(StringMatchMixin, FiniteStateNode[Symbols]):
    def __init__(self) -> None:
        super().__init__(to_match=",")

    @property
    def token(self) -> Symbols:
        self._validate_for_token()
        return Symbols.COMMA

    def __str__(self) -> str:
        return "CommaNode[',']"


class MultOperatorNode(StringMatchMixin, FiniteStateNode[Operation]):
    def __init__(self) -> None:
        super().__init__(to_match="mul")

    @property
    def token(self) -> Operation:
        self._validate_for_token()
        return Operation.MULT

    def __str__(self) -> str:
        return "MultOperatorNode"


class NumberNode(FiniteStateNode[int]):
    def __init__(self) -> None:
        super().__init__()
        self._num = 0

    def consume(self, num: str) -> ConsumeResult:
        if num == "":
            self._status = FiniteStateNodeStatus.Complete
            return Complete(consumed=True)
        if num.isdigit():
            self._num *= 10
            self._num += int(num)
            return Okay()
        else:
            self._status = FiniteStateNodeStatus.Complete
            return Complete(consumed=False)  # We did not consume this character

    @property
    def token(self) -> int:
        self._validate_for_token()
        return self._num

    def __str__(self) -> str:
        return f"NumberNode('{self._num}')"


class ProcessResultType:
    SUCCESS = auto()
    FAILED = auto()
    ERROR = auto()


class ProcessResult(ABC):
    pass


class ProcessSuccess(ProcessResult):
    def __init__(
        self, end: int, tokens: list[Union[str, int, Symbols, Operation]]
    ) -> None:
        super().__init__()
        self._end = end
        self._tokens = tokens

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProcessResult):
            raise TypeError()
        return isinstance(other, ProcessSuccess) and self._end == other._end

    def __iter__(self) -> Iterator[Union[ProcessResultType, int]]:
        yield ProcessResultType.SUCCESS
        yield self._end

    @property
    def tokens(self) -> list[Union[str, int, Symbols, Operation]]:
        return self._tokens

    @property
    def end(self) -> int:
        return self._end


class ProcessFailed(ProcessResult):
    def __init__(self, message: str) -> None:
        self._message = message
        super().__init__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProcessResult):
            raise TypeError()
        return isinstance(other, ProcessFailed)

    @property
    def message(self) -> str:
        return self._message


class ProcessError(ProcessResult):
    def __init__(self) -> None:
        super().__init__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProcessError):
            raise TypeError()
        return isinstance(other, ProcessError)


class FiniteStateMachine:
    def __init__(self, nodes: list[FiniteStateNode]) -> None:
        self._nodes = nodes

    def process(self, string: str) -> ProcessResult:
        """Process a string"""

        # TODO: reset FSM so it can be re-used
        str_idx = 0
        node_index = 0
        while True:
            # Check if all nodes processed
            if node_index == len(self._nodes):
                return ProcessSuccess(
                    end=str_idx, tokens=[t.token for t in self._nodes]
                )

            # Get next character
            if str_idx > len(string):
                return ProcessFailed("No more string characters to consume")
            elif str_idx == len(string):
                curr = ""
            else:
                curr = string[str_idx]

            curr_node = self._nodes[node_index]
            res = curr_node.consume(curr)

            match list(res):
                case [ConsumeResultType.Error]:
                    return ProcessError()
                case [ConsumeResultType.Complete, consumed]:
                    if consumed:
                        str_idx += 1
                    node_index += 1
                case [ConsumeResultType.Mismatch, a, b]:
                    return ProcessFailed(
                        f"Mismatched on: {curr_node} expected: {a} got {b}"
                    )
                case [ConsumeResultType.Okay]:
                    str_idx += 1
                case _:
                    raise FiniteStateMachineError("Inconsistent state")


TTransform = TypeVar("TTransform")
TransformFuncTypeDef = Callable[[ProcessSuccess], Optional[TTransform]]


def capture_tokens(
    string: str,
    fsm_definition: list[tuple[type[FiniteStateNode], tuple]],
    func: TransformFuncTypeDef,
) -> list[tuple[int, TTransform]]:
    result: list[tuple[int, TTransform]] = []
    start_at: int = 0
    while rem := string[start_at:]:
        fsm = FiniteStateMachine([n_type(*args) for n_type, args in fsm_definition])
        res = fsm.process(rem)
        if isinstance(res, ProcessSuccess):
            transformed = func(res)  # type: ignore
            assert isinstance(start_at, int)
            result.append((start_at, transformed))
            start_at += res.end
        else:
            start_at += 1
    return result


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    def to_expression(ps: ProcessSuccess) -> tuple[int, int]:
        a, b = [t for t in ps.tokens if isinstance(t, int)]
        return a, b

    expressions = capture_tokens(
        string=s,
        fsm_definition=[
            (MultOperatorNode, ()),
            (OpenParenNode, ()),
            (NumberNode, ()),
            (CommaNode, ()),
            (NumberNode, ()),
            (CloseParenNode, ()),
        ],
        func=to_expression,
    )

    enables: list[tuple[int, bool]] = capture_tokens(
        string=s,
        fsm_definition=[
            (StringMatchNode, ("do",)),
            (OpenParenNode, ()),
            (CloseParenNode, ()),
        ],
        func=lambda _: True,
    )

    disables: list[tuple[int, bool]] = capture_tokens(
        string=s,
        fsm_definition=[
            (StringMatchNode, ("don't",)),
            (OpenParenNode, ()),
            (CloseParenNode, ()),
        ],
        func=lambda _: False,
    )

    merged: list[Union[tuple[int, int], bool]] = []

    heap_: list[tuple[int, int, list[Union[tuple[int, int], bool]]]] = []

    if expressions:
        heappush(heap_, (expressions[0][0], 0, expressions))
    if enables:
        heappush(heap_, (enables[0][0], 0, enables))
    if disables:
        heappush(heap_, (disables[0][0], 0, disables))

    while heap_:
        pos, index, lst = heappop(heap_)
        merged.append(lst[index])
        if index + 1 < len(lst):
            heappush(heap_, (lst[index + 1][0], index + 1, lst))

    part_1 = sum(a * b for _, (a, b) in expressions)

    part_2 = 0

    enabled = True
    for _, item in merged:
        if isinstance(item, bool):
            enabled = item
        elif isinstance(item, tuple) and enabled:
            assert len(item) == 2
            a, b = item
            part_2 += a * b

    return part_1, part_2


TEST_INPUT = """\
xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]then(mul(11,8)mul(8,5))
"""

TEST_INPUT_2 = """\
xmul(2,4)&mul[3,7]!^don't()_mul(5,5)+mul(32,64](mul(11,8)undo()?mul(8,5))
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (161, 161)), (TEST_INPUT_2, (161, 48))),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
