import os
import time
import urllib.error
import urllib.request
from functools import wraps
from pathlib import Path
from typing import Any
from typing import Callable
from typing import cast
from typing import TypeVar

from advent_of_code.type_defs import Ans
from advent_of_code.type_defs import Solution


F = TypeVar("F", bound=Callable[..., Any])


def print_solution(sol: Solution) -> None:  # type: ignore # noqa: C901
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
    def wrapper(*args, **kwargs) -> tuple[..., int]:  # type: ignore
        before = time.perf_counter_ns()
        result = func(*args, **kwargs)
        after = time.perf_counter_ns()
        dur = after - before
        if isinstance(result, tuple):
            return *result, dur  # type: ignore
        else:
            return result, dur

    return cast(F, wrapper)


def get_input_data(year: int, day: int, relative_dir: str | None = None) -> str:
    file_name = f"day{day:02}.txt"
    file_dir = f"{year}"

    if relative_dir is None:
        relative_dir = os.path.join(get_project_root(), "inputs", file_dir, file_name)

    file_path = os.path.join(relative_dir, file_dir, file_name)

    with open(file_path) as f:
        return f.read()


def get_input(year: int, day: int, cookie: str) -> str:
    with open("./.env") as f:
        f.read()

    url = f"https://adventofcode.com/{year}/day/{day}/input"
    req = urllib.request.Request(url, headers={"Cookie": cookie})
    return urllib.request.urlopen(req).read().decode()  # type: ignore


def get_project_root() -> Path:
    iterations = 0

    current = Path(os.getcwd())
    found = False

    while not found:
        if iterations > 15:
            SystemExit(
                "Could not find the project root, make sure you're inside the "
                "'advent_of_code' project"
            )
        if os.path.isfile(os.path.join(current, "pyproject.toml")):
            found = True
        else:
            current = current.parent
    return current
