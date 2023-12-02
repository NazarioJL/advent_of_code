from functools import reduce
from operator import mul
from typing import TypedDict

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2023
DAY = 2


class CubeSet(TypedDict, total=False):
    green: int
    blue: int
    red: int


COLORS: list[str] = ["green", "blue", "red"]


def parse_input(s: str) -> dict[int, list[CubeSet]]:
    games: dict[int, list[CubeSet]] = {}
    for line in s.splitlines():
        game_part, games_part = line.split(":")
        _, game_id_str = game_part.split()
        game_id = int(game_id_str)

        games[game_id] = []

        games_str = games_part.split(";")
        for game_part in games_str:
            game: CubeSet = {}
            for piece in game_part.split(","):
                count, color = piece.split()
                game[color] = int(count)

            games[game_id].append(game)

    return games


def is_game_valid(total: CubeSet, game: CubeSet) -> bool:
    total_total = sum(total.get(color, 0) for color in COLORS)
    total_game = sum(game.get(color, 0) for color in COLORS)

    if total_total < total_game:
        return False

    for color in COLORS:
        if total.get(color, 0) < game.get(color, 0):
            return False

    return True


def get_min_required(game: list[CubeSet]) -> int:
    return reduce(mul, [max(game.get(color, 0) for game in game) for color in COLORS])


def part_1(games: dict[int, list[CubeSet]]) -> int:
    total: CubeSet = {
        "red": 12,
        "green": 13,
        "blue": 14,
    }
    return sum(
        game_id
        for game_id, game_sets in games.items()
        if all(is_game_valid(total, g) for g in game_sets)
    )


def part_2(games: dict[int, list[CubeSet]]) -> int:
    return sum(get_min_required(game) for game in games.values())


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    games = parse_input(s)

    return part_1(games), part_2(games)


TEST_INPUT = """\
Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (8, 2286)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
