import re
from enum import Enum
from math import prod
from typing import Iterable
from typing import NamedTuple

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.exceptions import UnexpectedConditionError
from advent_of_code.recipes import batched
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2022
DAY = 19

SUM_OF_ELEMENTS = {i: (i * i + i) // 2 for i in range(33)}


class Mineral(Enum):
    ORE = "ore"
    CLAY = "clay"
    OBSIDIAN = "obsidian"
    GEODE = "geode"


MINERAL_ATTR_MAP = {e: f"total_{e.value}" for e in Mineral}

ROBOT_ATTR_MAP = {e: f"total_{e.value}_robots" for e in Mineral}

ROBOT_TO_ARGS = {
    Mineral.ORE: (1, 0, 0, 0),
    Mineral.CLAY: (0, 1, 0, 0),
    Mineral.OBSIDIAN: (0, 0, 1, 0),
    Mineral.GEODE: (0, 0, 0, 1),
}


class MineralInventory(NamedTuple):
    ore: int = 0
    clay: int = 0
    obsidian: int = 0
    geode: int = 0


class Blueprint(NamedTuple):
    blueprint_id: int
    robot_cost: dict[Mineral, MineralInventory]


class State(NamedTuple):
    total_ore: int = 0
    total_clay: int = 0
    total_obsidian: int = 0
    total_geode: int = 0
    total_ore_robots: int = 0
    total_clay_robots: int = 0
    total_obsidian_robots: int = 0
    total_geode_robots: int = 0

    def as_heap_tuple(self) -> tuple:
        # heapq only supports a min heap, we need a max heap instead
        return (
            -self.total_geode,
            -self.total_geode_robots,
            -self.total_obsidian,
            -self.total_obsidian_robots,
            -self.total_clay,
            -self.total_clay_robots,
            -self.total_ore,
            -self.total_ore_robots,
        )

    @staticmethod
    def from_heap_tuple(
        heap_tuple: tuple[int, int, int, int, int, int, int, int]
    ) -> "State":
        tg, tgr, tob, tobr, tc, tcr, to, tor = heap_tuple
        return State(
            total_geode=-tg,
            total_geode_robots=-tgr,
            total_obsidian=-tob,
            total_obsidian_robots=-tobr,
            total_clay=-tc,
            total_clay_robots=-tcr,
            total_ore=-to,
            total_ore_robots=-tor,
        )

    def get_mineral_count(self, mineral: Mineral) -> int:
        return getattr(self, MINERAL_ATTR_MAP[mineral])  # type: ignore

    def get_robot_count(self, mineral: Mineral) -> int:
        return getattr(self, ROBOT_ATTR_MAP[mineral])  # type: ignore

    def __str__(self) -> str:
        return (
            f"State(m={self.total_ore:03}"
            f"|{self.total_clay:03}"
            f"|{self.total_obsidian:03}"
            f"|{self.total_geode:03}, "
            f"r={self.total_ore_robots:02}"
            f"|{self.total_clay_robots:02}"
            f"|{self.total_obsidian_robots:02}"
            f"|{self.total_geode_robots:02}))"
        )

    def __repr__(self) -> str:
        return str(self)


def parse_input(s: str) -> Iterable[Blueprint]:
    for batch in batched(re.findall(r"(\d+)", s), n=7):
        (
            bp_id,
            ore_robot_cost_ore,
            clay_robot_cost_ore,
            obs_ore_cost,
            obs_clay_cost,
            geode_ore_cost,
            geode_obs_cost,
        ) = batch

        yield Blueprint(
            blueprint_id=int(bp_id),
            robot_cost={
                Mineral.ORE: MineralInventory(ore=int(ore_robot_cost_ore)),
                Mineral.CLAY: MineralInventory(ore=int(clay_robot_cost_ore)),
                Mineral.OBSIDIAN: MineralInventory(
                    ore=int(obs_ore_cost),
                    clay=int(obs_clay_cost),
                ),
                Mineral.GEODE: MineralInventory(
                    ore=int(geode_ore_cost),
                    obsidian=int(geode_obs_cost),
                ),
            },
        )


def print_blueprint(blueprint: Blueprint) -> None:
    print(f"Blueprint {blueprint.blueprint_id}:")
    for robot_type, costs in blueprint.robot_cost.items():
        cost_lst = [(m, c) for m, c in zip(Mineral, costs) if c != 0]
        bom = " and ".join(f"{c} {m.value}" for m, c in cost_lst)
        print(f"\tEach {robot_type.value} robot costs {bom}.")


def add_minerals(
    state: State, ore: int = 0, clay: int = 0, obsidian: int = 0, geode: int = 0
) -> State:
    return State(
        total_clay=state.total_clay + clay,
        total_ore=state.total_ore + ore,
        total_obsidian=state.total_obsidian + obsidian,
        total_geode=state.total_geode + geode,
        total_ore_robots=state.total_ore_robots,
        total_clay_robots=state.total_clay_robots,
        total_obsidian_robots=state.total_obsidian_robots,
        total_geode_robots=state.total_geode_robots,
    )


def remove_minerals(
    state: State, ore: int = 0, clay: int = 0, obsidian: int = 0, geode: int = 0
) -> State:
    return State(
        total_clay=state.total_clay - clay,
        total_ore=state.total_ore - ore,
        total_obsidian=state.total_obsidian - obsidian,
        total_geode=state.total_geode - geode,
        total_ore_robots=state.total_ore_robots,
        total_clay_robots=state.total_clay_robots,
        total_obsidian_robots=state.total_obsidian_robots,
        total_geode_robots=state.total_geode_robots,
    )


def add_robots(
    state: State, ore: int = 0, clay: int = 0, obsidian: int = 0, geode: int = 0
) -> State:
    return State(
        total_clay=state.total_clay,
        total_ore=state.total_ore,
        total_obsidian=state.total_obsidian,
        total_geode=state.total_geode,
        total_ore_robots=state.total_ore_robots + ore,
        total_clay_robots=state.total_clay_robots + clay,
        total_obsidian_robots=state.total_obsidian_robots + obsidian,
        total_geode_robots=state.total_geode_robots + geode,
    )


def collect_resources(state: State) -> State:
    # Returns the state after all resources have been collected
    return State(
        total_ore_robots=state.total_ore_robots,
        total_clay_robots=state.total_clay_robots,
        total_obsidian_robots=state.total_obsidian_robots,
        total_geode_robots=state.total_geode_robots,
        total_ore=state.total_ore + state.total_ore_robots,
        total_clay=state.total_clay + state.total_clay_robots,
        total_obsidian=state.total_obsidian + state.total_obsidian_robots,
        total_geode=state.total_geode + state.total_geode_robots,
    )


def buy_robot(robot_type: Mineral, blueprint: Blueprint, state: State) -> State:
    costs = blueprint.robot_cost[robot_type]
    robots = ROBOT_TO_ARGS[robot_type]
    return State(
        total_ore=state.total_ore - costs.ore,
        total_clay=state.total_clay - costs.clay,
        total_obsidian=state.total_obsidian - costs.obsidian,
        total_geode=state.total_geode - costs.geode,
        total_ore_robots=state.total_ore_robots + robots[0],
        total_clay_robots=state.total_clay_robots + robots[1],
        total_obsidian_robots=state.total_obsidian_robots + robots[2],
        total_geode_robots=state.total_geode_robots + robots[3],
    )


def can_buy(robot_type: Mineral, blueprint: Blueprint, state: State) -> bool:
    costs = blueprint.robot_cost[robot_type]
    return (
        costs.ore <= state.total_ore
        and costs.clay <= state.total_clay
        and costs.obsidian <= state.total_obsidian
        # or costs.geode <= state.total_geode
    )


def estimate_geode(state: State, remaining_steps: int, blueprint: Blueprint) -> int:
    """Creates an upper bound estimate of produce geode"""
    total = 0
    # Add current total geode
    total += state.total_geode + state.total_geode_robots
    # Add total geode that can be produced by geode robots
    total += remaining_steps * state.total_geode_robots
    effective_steps = remaining_steps - 1

    # Naively Assume we can make a geode robot every day
    if effective_steps > 0:
        total += SUM_OF_ELEMENTS[effective_steps]

    return total


def should_prune(state: State, remaining_steps: int, blueprint: Blueprint) -> bool:
    # This is the max element we can produce if we build one robot every step from now
    # TODO: Analyze why this is not working
    effective_steps = remaining_steps - 1
    next_element_total = SUM_OF_ELEMENTS[effective_steps]

    if state.total_clay_robots == 0:
        # Can we make clay robots
        if effective_steps < 3:
            return True  # we can't create the other types of robots anyways
        required_ore = blueprint.robot_cost[Mineral.CLAY].ore
        total_ore = next_element_total
        total_ore += state.total_ore
        if total_ore < required_ore:
            return True

    if state.total_obsidian_robots == 0:
        if effective_steps < 2:
            return True
        # Can we even create an obsidian robot, clay requirement is always > ore
        required_clay = blueprint.robot_cost[Mineral.OBSIDIAN].clay
        total_clay = next_element_total
        total_clay += state.total_clay
        if total_clay < required_clay:
            return True

    if state.total_geode_robots == 0:
        if effective_steps < 1:
            return True
        # Can we even crate a geode robot, obsidian requirement is always > clay
        required_obsidian = blueprint.robot_cost[Mineral.GEODE].obsidian
        total_obsidian = next_element_total
        total_obsidian += state.total_obsidian
        if total_obsidian < required_obsidian:
            return True

    return False


def get_max_robot_counts(blueprint: Blueprint) -> dict[Mineral, int]:
    robot_types = (Mineral.ORE, Mineral.CLAY, Mineral.OBSIDIAN)
    return {
        robot_type: count
        for (robot_type, count) in zip(
            robot_types,
            (
                max(getattr(e, str(et.value)) for e in blueprint.robot_cost.values())
                for et in robot_types
            ),
        )
    }


def maximize(blueprint: Blueprint, max_steps: int) -> int:
    start = State(total_ore_robots=1)
    max_geodes = 0
    visited = set()
    max_robot_counts = get_max_robot_counts(blueprint)

    def step(state: State, current_step: int) -> None:
        if (state, current_step) in visited:
            return
        else:
            visited.add((state, current_step))

        nonlocal max_steps
        nonlocal max_geodes

        if current_step > max_steps:
            raise UnexpectedConditionError("Running more steps than should!")
        elif current_step == max_steps:
            max_geodes = max(max_geodes, state.total_geode)
        else:
            remaining_steps = max_steps - current_step
            estimated_geode = estimate_geode(
                state=state, remaining_steps=remaining_steps, blueprint=blueprint
            )
            if estimated_geode < max_geodes:
                return
            # if should_prune(
            #     state=state, remaining_steps=remaining_steps, blueprint=blueprint
            # ):
            #     return

            for robot_type in (
                Mineral.GEODE,
                Mineral.OBSIDIAN,
                Mineral.CLAY,
                Mineral.ORE,
            ):
                # No need to make a robot if element production is at max
                if robot_type in max_robot_counts:
                    assert robot_type != Mineral.GEODE
                    if (
                        state.get_robot_count(robot_type)
                        >= max_robot_counts[robot_type]
                    ):
                        continue

                if can_buy(robot_type=robot_type, blueprint=blueprint, state=state):
                    collected = collect_resources(state)
                    with_robot = buy_robot(
                        robot_type=robot_type, state=collected, blueprint=blueprint
                    )
                    step(state=with_robot, current_step=current_step + 1)
            step(state=collect_resources(state), current_step=current_step + 1)

    step(start, 0)

    return max_geodes


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    blueprints = list(parse_input(s))

    results_1 = {}

    for blueprint in blueprints:
        max_geodes = maximize(blueprint=blueprint, max_steps=24)
        results_1[blueprint.blueprint_id] = max_geodes

    part_1 = sum(bpid * mg for bpid, mg in results_1.items())

    results_2 = []
    for blueprint in blueprints[:3]:  # take only first 3
        max_geodes = maximize(blueprint=blueprint, max_steps=32)
        print(f"{blueprint.blueprint_id} -> {max_geodes}")
        results_2.append(max_geodes)

    part_2 = prod(results_2)

    return part_1, part_2


TEST_INPUT = """\
Blueprint 1:
  Each ore robot costs 4 ore.
  Each clay robot costs 2 ore.
  Each obsidian robot costs 3 ore and 14 clay.
  Each geode robot costs 2 ore and 7 obsidian.

Blueprint 2:
  Each ore robot costs 2 ore.
  Each clay robot costs 3 ore.
  Each obsidian robot costs 3 ore and 8 clay.
  Each geode robot costs 3 ore and 12 obsidian.
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (33, 3472)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
