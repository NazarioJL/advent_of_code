SOLUTION_JINJA_TEMPLATE = """\
import pytest

from support import get_input_data
from support import print_solution
from support import Solution
from support import time_solve

YEAR = {{ year }}
DAY = {{ day }}


@time_solve
def solve(s: str) -> Solution:
    raise NotImplementedError


TEST_INPUT = \"\"\"\\
\"\"\"


@pytest.mark.parametrize(
    ("input_s", "expected"),
    (
        (TEST_INPUT, ""),
    ),
)
def test_solve(input_s: str, expected: str):
    assert solve(input_s) == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
"""
