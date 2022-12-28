import pytest

from advent_of_code.recipes import trace_points


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        ((-2, -6), [-2, -3, -4, -5, -6]),
        ((1, 1), [1]),
        ((1, 2), [1, 2]),
        ((1, 3), [1, 2, 3]),
    ),
)
def test_trace_points(value, expected):
    assert list(trace_points(*value)) == expected
    # assert list(trace_points(1, 1)) == [1]
    # assert list(trace_points(1, 2)) == [1, 2]
    # assert list(trace_points(1, 3)) == [1, 2, 3]
