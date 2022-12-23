from typing import Generic
from typing import TypeVar

from advent_of_code.parsers import parse_lines


def test_parse_lines_no_func():
    test_input = """\
one
two
three
"""

    assert list(parse_lines(input_s=test_input)) == ["one", "two", "three"]


def test_parse_lines_func():
    test_input = """\
1
2
3
"""

    assert list(parse_lines(input_s=test_input, tx_func=int)) == [1, 2, 3]


T = TypeVar("T")


class ValueWithDuration(Generic[T]):
    def __init__(self, value: T, duration_ns: int):
        self._value = value
        self._duration_ns = duration_ns

    @property
    def value(self):
        return self._value

    @property
    def duration_ns(self):
        return self._duration_ns

    def __len__(self):
        return 2

    def __getitem__(self, index):
        if index == "value":
            return self._value
        elif index == "duration_ns":
            return self._duration_ns
        else:
            raise KeyError(f"object has no such key: {index}")

    def __iter__(self):
        yield self._value
        yield self._duration_ns

    def keys(self):
        return ["value", "duration_ns"]


def test_value():
    v = ValueWithDuration(value="foo", duration_ns=10)
    x = [*v]
    assert len(x) == 2
    assert {**v} == {"value": "foo", "duration_ns": 10}
