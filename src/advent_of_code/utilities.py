import time
from functools import wraps
from typing import Any
from typing import Callable
from typing import cast
from typing import TypeVar

from advent_of_code.type_defs import Ans
from advent_of_code.type_defs import Solution


F = TypeVar("F", bound=Callable[..., Any])


def print_solution(sol: Solution) -> None:  # type: ignore
    def fmt_time(duration: float) -> str:
        unit = "ms"
        if duration < 100:
            duration *= 1000
            unit = "μs"
        return f"{int(duration)} {unit}"

    def fmt_ans(ans: Ans) -> str:  # type: ignore
        if ans is None:
            return "Not solved"
        if isinstance(ans, tuple):
            ans_val, ans_t = ans
            if isinstance(ans_val, str) and "\n" in ans_val:
                # multi line answer
                return f"({fmt_time(ans_t)})\n{ans_val}"
            else:
                return f"({fmt_time(ans_t)}): {ans_val} "
        else:
            if isinstance(ans, str) and "\n" in ans:
                # multi line answer
                return f"\n{ans}"
            else:
                return f": {ans}"

    if len(sol) == 3:
        part_1, part_2, dur = sol
        print(f"Solution part 1 {fmt_ans(part_1)}")
        print(f"Solution part 2 {fmt_ans(part_2)}")
        print(f"Total duration: {fmt_time(dur)}")
    else:
        part_1, part_2 = sol
        print(f"Solution part 1 {fmt_ans(part_1)}")
        print(f"Solution part 2 {fmt_ans(part_2)}")


def time_solve(func: F) -> F:
    @wraps(func)
    def wrapper(*args, **kwargs):  # type: ignore
        before = time.time()
        result = func(*args, **kwargs)
        after = time.time()
        dur = (after - before) * 1000
        if isinstance(result, tuple):
            return *result, dur
        else:
            return result, dur

    return cast(F, wrapper)
