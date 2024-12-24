from collections import defaultdict
from functools import cache
from itertools import pairwise
from itertools import product
from typing import Iterable

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2024
DAY = 21


def sign(x: int) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


# Layouts from problem

NUMPAD_LAYOUT = """\
789
456
123
 0A
"""

DPAD_LAYOUT = """\
 ^A
<v>
"""


class Keypad:
    def __init__(self, keys: Iterable[tuple[str, tuple[int, int]]]):
        self._key_to_pos = dict(keys)
        self._pos_to_key = {pos: key for key, pos in self._key_to_pos.items()}
        self._make_paths()

    def _make_paths(self) -> None:
        self._paths: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
        for key_from, key_to in product(
            self._key_to_pos.keys(), self._key_to_pos.keys()
        ):
            if key_from == key_to or key_from == " " or key_to == " ":
                continue

            from_x, from_y = self._key_to_pos[key_from]
            to_x, to_y = self._key_to_pos[key_to]

            d_x = to_x - from_x
            d_y = to_y - from_y

            if d_x == 0 and d_y == 0:
                continue  # This should never happen because of top statement

            x_sign = sign(d_x)
            dir_x = ">" if d_x > 0 else "<"
            x_path = "".join([dir_x] * abs(d_x))

            y_sign = sign(d_y)
            dir_y = "v" if d_y > 0 else "^"
            y_path = "".join([dir_y] * abs(d_y))

            if d_x == 0 or d_y == 0:
                self._paths[key_from][key_to].append(x_path + y_path)
                continue

            # There can be 2 orthogonal paths from source to target
            # Do horizontal first if possible
            if not any(
                self._pos_to_key[(from_x + (i + 1) * x_sign, from_y)] == " "
                for i in range(abs(d_x))
            ):
                if not any(
                    self._pos_to_key[to_x, from_y + (i + 1) * y_sign] == " "
                    for i in range(abs(d_y))
                ):
                    self._paths[key_from][key_to].append(x_path + y_path)

            # Now try vertical then horizontal
            if not any(
                self._pos_to_key[(from_x, from_y + (i + 1) * y_sign)] == " "
                for i in range(abs(d_y))
            ):
                if not any(
                    self._pos_to_key[from_x + (i + 1) * x_sign, to_y] == " "
                    for i in range(abs(d_x))
                ):
                    self._paths[key_from][key_to].append(y_path + x_path)

    def get_paths(self, from_key: str, to_key: str) -> Iterable[str]:
        return self._paths[from_key][to_key]

    @staticmethod
    def from_data(data: str) -> "Keypad":
        return Keypad(
            keys=(
                (key, (col, row))
                for row, line in enumerate(data.splitlines())
                for col, key in enumerate(line)
            )
        )


DPAD = Keypad.from_data(DPAD_LAYOUT)
NUMPAD = Keypad.from_data(NUMPAD_LAYOUT)


def count_presses(
    code: str, layers: int, num_pad: Keypad = NUMPAD, d_pad: Keypad = DPAD
) -> int:
    @cache
    def move(layer: int, keys: str) -> int:
        if layer == layers:
            return len(keys)
        keypad = num_pad if layer == 0 else d_pad

        result = 0
        for f, t in pairwise(["A", *keys]):
            paths = keypad.get_paths(f, t) or [""]
            result += min(move(layer + 1, path + "A") for path in paths)

        return result

    return move(0, code)


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    part_1 = sum(count_presses(code, 3) * int(code[:-1]) for code in s.splitlines())
    part_2 = sum(count_presses(code, 26) * int(code[:-1]) for code in s.splitlines())

    return part_1, part_2


TEST_INPUT = """\
029A
980A
179A
456A
379A
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    [
        (TEST_INPUT, (126384, 337744744231414)),
    ],
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


@pytest.mark.parametrize(
    ("pad_layout", "from_", "to", "expected"),
    [
        (DPAD_LAYOUT, "^", "A", [">"]),
        (DPAD_LAYOUT, "^", "<", ["v<"]),
        (DPAD_LAYOUT, "^", ">", [">v", "v>"]),
        (DPAD_LAYOUT, "<", "A", [">>^"]),
        (NUMPAD_LAYOUT, "7", "A", [">>vvv"]),
        (NUMPAD_LAYOUT, "7", "3", [">>vv", "vv>>"]),
    ],
)
def test_build_paths(pad_layout: str, from_: str, to: str, expected: list[str]) -> None:
    keypad = Keypad.from_data(pad_layout)
    actual = keypad.get_paths(from_, to)

    assert len(list(actual)) == len(expected)
    assert set(actual) == set(expected)


def test_count_presses() -> None:
    assert count_presses("029A", 3) == 68


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
