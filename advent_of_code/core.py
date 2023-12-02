import time
from functools import wraps
from typing import Callable
from typing import ParamSpec
from typing import TypeAlias
from typing import TypeVar
from typing import Union

from attr import define
from attr import field

from advent_of_code.exceptions import IncorrectReturnTypeError
from advent_of_code.type_defs import Solution as Solution2

AnswerType: TypeAlias = int | float | str | None


@define(kw_only=True, frozen=True)
class Unsolved:
    pass


@define(kw_only=True, frozen=True)
class PartialAnswer:
    value: AnswerType
    duration_ns: int | None = field(default=None)


@define(kw_only=True, frozen=True)
class Solution:
    part_1: PartialAnswer | Unsolved = field(default=Unsolved())
    part_2: PartialAnswer | Unsolved = field(default=Unsolved())
    duration_ns: int | None = field(default=None)

    def as_tuple(self) -> tuple[AnswerType | None, AnswerType | None]:
        return (
            getattr(self.part_1, "value") if hasattr(self.part_1, "value") else None,
            getattr(self.part_2, "value") if hasattr(self.part_2, "value") else None,
        )


def print_solution(sol: Solution, multiline_block: bool = False) -> None:  # noqa: C901
    def fmt_time(duration_ns: int) -> str:
        duration = float(duration_ns)
        unit = "ns"
        if duration > 1000:
            duration /= 1000
            unit = "μs"
        if duration > 1000:
            duration /= 1000
            unit = "ms"
        if duration > 1000:
            duration /= 1000
            unit = "s"
        return f"{duration:.2f} {unit}"

    def fmt_ans(ans: PartialAnswer | Unsolved) -> str:
        if isinstance(ans, Unsolved):
            return "Not solved"
        else:
            if ans.duration_ns is None:
                if isinstance(ans.value, str) and "\n" in ans.value:
                    ans_str = ans.value

                    if multiline_block:
                        ans_str = ans_str.replace("#", "█").replace(".", " ")
                    # multi line answer
                    return f"\n{ans_str}"
                else:
                    return f": {ans.value}"
            else:
                if isinstance(ans.value, str) and "\n" in ans.value:
                    ans_str = ans.value
                    # multi line answer
                    if multiline_block:
                        ans_str = ans_str.replace("#", "█").replace(".", " ")
                    return f"({fmt_time(ans.duration_ns)})\n{ans_str}"
                else:
                    return f"({fmt_time(ans.duration_ns)}): {ans.value}"

    print(f"Solution part 1 {fmt_ans(sol.part_1)}")
    print(f"Solution part 2 {fmt_ans(sol.part_2)}")
    if sol.duration_ns is not None:
        print(f"Total Duration: {fmt_time(sol.duration_ns)}")


SolutionReturnTypeDef: TypeAlias = Union[
    Solution,
    Solution2,
    tuple[PartialAnswer, PartialAnswer],
    tuple[AnswerType, AnswerType],
]

SolutionFuncTypeDef: TypeAlias = Callable[[str], SolutionReturnTypeDef]
DecoratedSolutionFuncTypeDef: TypeAlias = Callable[[str], Solution]

P = ParamSpec("P")
T = TypeVar("T")

PartialSolutionFuncTypeDef: TypeAlias = Callable[[P.args, P.kwargs], AnswerType]
DecoratedPartialSolutionFuncTypeDef: TypeAlias = Callable[
    [P.args, P.kwargs], PartialAnswer
]


class AdventOfCode:
    def __init__(self) -> None:
        self._solutions: dict[tuple[int, int], DecoratedSolutionFuncTypeDef] = {}

    def solution(
        self, year: int, day: int
    ) -> Callable[[SolutionFuncTypeDef], DecoratedSolutionFuncTypeDef]:
        _original_func: SolutionFuncTypeDef | None = None

        def inner(func: SolutionFuncTypeDef) -> DecoratedSolutionFuncTypeDef:
            nonlocal _original_func
            _original_func = func

            @wraps(func)
            def wrapper(s: str) -> Solution:
                before = time.perf_counter_ns()
                result = func(s)
                after = time.perf_counter_ns()
                dur = after - before

                if isinstance(result, Solution):
                    return Solution(
                        # This overwrites any duration information from prev solution
                        part_1=result.part_1,
                        part_2=result.part_2,
                        duration_ns=dur,
                    )
                elif isinstance(result, tuple):
                    if len(result) != 2:
                        raise IncorrectReturnTypeError(
                            "The solution function must return a tuple of either 2 "
                            "`PartialAnswer` or 2 answer types (int | str | float)"
                        )
                    p1, p2 = result

                    part_1 = (
                        p1 if isinstance(p1, PartialAnswer) else PartialAnswer(value=p1)
                    )
                    part_2 = (
                        p2 if isinstance(p2, PartialAnswer) else PartialAnswer(value=p2)
                    )
                    return Solution(part_1=part_1, part_2=part_2, duration_ns=dur)

            return wrapper

        if _original_func is not None:
            self._solutions[(year, day)] = inner(_original_func)
        return inner

    def partial(
        self, part: int
    ) -> Callable[[PartialSolutionFuncTypeDef], DecoratedPartialSolutionFuncTypeDef]:
        def inner(
            func: PartialSolutionFuncTypeDef,
        ) -> DecoratedPartialSolutionFuncTypeDef:
            @wraps(func)  # type: ignore
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> PartialAnswer:
                before = time.perf_counter_ns()
                result = func(*args, **kwargs)
                after = time.perf_counter_ns()
                dur = after - before

                return PartialAnswer(value=result, duration_ns=dur)

            return wrapper

        return inner

    def count_solutions(self) -> int:
        return len(self._solutions)


aoc = AdventOfCode()
