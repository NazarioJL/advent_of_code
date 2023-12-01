import re
from collections import defaultdict
from functools import cache
from itertools import pairwise
from typing import Iterable
from typing import NamedTuple
from typing import Optional

import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2022
DAY = 16


class ValveInfo(NamedTuple):
    name: str
    flow_rate: int
    adjacent: list[str]


def create_valve_graph(valve_infos: Iterable[ValveInfo]) -> dict[str, set[str]]:
    graph = defaultdict(set)
    for valve_info in valve_infos:
        for adj in valve_info.adjacent:
            graph[valve_info.name].add(adj)

    return graph


def create_path_cost(valve_graph: dict[str, set[str]]) -> dict[tuple[str, str], int]:
    visited: dict[tuple[str, str], int] = {(v, v): 0 for v in valve_graph.keys()}
    all_valves = [k for k in valve_graph.keys()]
    for valve in all_valves:
        q: list[tuple[tuple[str, str], int]] = [((valve, valve), 0)]
        while q:
            (start, curr), cost = q.pop()
            for neighbor in valve_graph[curr]:
                cost_to_neighbor = cost + 1
                if (start, neighbor) in visited:
                    if cost_to_neighbor < visited[(start, neighbor)]:
                        visited[(start, neighbor)] = cost_to_neighbor
                        q.append(((start, neighbor), cost_to_neighbor))
                else:
                    # We do not have a start -> neighbor cost yet
                    visited[(start, neighbor)] = cost_to_neighbor
                    q.append(((start, neighbor), cost_to_neighbor))
    return visited


class ValveStateManager:
    """Class the helps with state operations"""

    def __init__(self, valve_infos: Iterable[ValveInfo]) -> None:
        # Create a stable index -> valve map
        self._valve_index_map = {
            name: index
            for index, name in enumerate(sorted(v.name for v in valve_infos))
        }
        # Valves and immediate neighbors _e.g._ AA -> {BB, CC}, BB -> {AA, DD} ...
        self._valve_graph = create_valve_graph(valve_infos=valve_infos)

        # Cost from one valve to another _e.g._ (AA, CC) -> 2
        self._valve_path_cost = create_path_cost(self._valve_graph)

        # Valve to bit mask _e.g._ AA -> 0b0001, BB -> 0b0010, ...
        self._bit_mask = {name: 1 << idx for name, idx in self._valve_index_map.items()}

        # Per valve flow rate
        self._flow_rate = {v.name: v.flow_rate for v in valve_infos}

        # Maximum pressure output
        self._max_pressure = sum(self._flow_rate.values())

        # All working valves on
        self._optimized_valve_state = sum(
            mask for valve, mask in self._bit_mask.items() if self._flow_rate[valve] > 0
        )

    @property
    def max_pressure(self) -> int:
        """The maximum pressure output per step for this configuration"""
        return self._max_pressure

    @property
    def optimized_valve_state(self) -> int:
        """Valve state where all important valves are on"""
        return self._optimized_valve_state

    def is_closed(self, valve: str, state: int) -> bool:
        """True if valve is closed, False otherwise"""
        return state & self._bit_mask[valve] == 0

    def should_open(self, valve: str, state: int) -> bool:
        """True if working valve and is closed"""
        return self._flow_rate[valve] > 0 and state & self._bit_mask[valve] == 0

    def get_open_valves(self, state: int) -> Iterable[str]:
        """Get all open valves"""
        for valve, idx in self._valve_index_map.items():
            if (state & self._bit_mask[valve]) != 0:
                yield valve

    def get_closed_working_valves(self, state: int) -> Iterable[str]:
        """ "Gets all working valves that are closed"""
        for valve, idx in self._valve_index_map.items():
            if (state & self._bit_mask[valve]) == 0 and self._flow_rate[valve] > 0:
                yield valve

    def open_valve(self, valve: str, state: int) -> int:
        """Returns a new state when opening a valve, this operation is idempotent"""
        return state | self._bit_mask[valve]

    def get_pressure(self, state: int) -> int:
        """Gets the pressure released for this configuration"""
        result = 0
        for valve, mask in self._bit_mask.items():
            if mask & state != 0:
                result += self._flow_rate[valve]

        return result

    def get_neighbors(self, valve: str) -> Iterable[str]:
        """Gets adjacent neighbors"""
        for neighbour in self._valve_graph[valve]:
            yield neighbour

    def get_flow_rate(self, valve: str) -> int:
        """Gets flow rate for valve"""
        return self._flow_rate[valve]

    def get_cost(self, source: str, dest: str) -> int:
        """Gets the required steps to go from source valve to destination valve

        raises: KeyError if there is no path
        """
        return self._valve_path_cost[(source, dest)]


def parse_input(s: str) -> Iterable[ValveInfo]:
    valve_names = r"(?P<valve>[A-Z]{2})"
    flow_rate = r"(?P<num>\d+)"

    for line in s.splitlines():
        source_valve, *adjacent = re.findall(valve_names, line)
        rate = re.findall(flow_rate, line)
        yield ValveInfo(name=source_valve, flow_rate=int(rate[0]), adjacent=[*adjacent])


class State(NamedTuple):
    valve: str  # Valve we are standing in
    valve_status: int  # Which valves are on?


class StateList(NamedTuple):
    """List of states for visualization"""

    state: State
    parent: Optional["StateList"]
    early_exit: bool = False


def calc_max_pressure(
    max_steps: int,
    valve_infos: Iterable[ValveInfo],
) -> int:
    valve_manager = ValveStateManager(valve_infos=valve_infos)

    @cache
    def calc_max_pressure_rec(
        valve: str, valve_status: int, remaining_steps: int
    ) -> int:
        if remaining_steps == 0:
            return 0

        if valve_status == valve_manager.optimized_valve_state:
            return remaining_steps * valve_manager.max_pressure

        # TODO: Add optimizations here, some possible are:
        #       - We can calculate an upper bound based on the path costs from this
        #       valve to other working valves that are closed, we can exit early
        #       - For the second part we can superimpose the activity that happens by
        #       the elephant and the human.
        #       - Calculate the global max at every step and exit early if will not meet

        result = 0

        if valve_manager.should_open(valve, valve_status):
            result = max(
                result,
                calc_max_pressure_rec(
                    valve=valve,
                    valve_status=valve_manager.open_valve(valve, valve_status),
                    remaining_steps=remaining_steps - 1,
                ),
            )

        for neighbor in valve_manager.get_neighbors(valve):
            result = max(
                result,
                calc_max_pressure_rec(
                    valve=neighbor,
                    valve_status=valve_status,
                    remaining_steps=remaining_steps - 1,
                ),
            )
        return result + valve_manager.get_pressure(valve_status)

    return calc_max_pressure_rec(valve="AA", valve_status=0, remaining_steps=max_steps)


def calc_max_pressure_with_visualization(
    max_steps: int, valve_infos: Iterable[ValveInfo]
) -> int:
    """Calculates the maximum pressure release.
    Remarks:
        Does *NOT* work with problem input, only sample input
    """
    valve_manager = ValveStateManager(valve_infos=valve_infos)
    start = State(valve="AA", valve_status=0)  # Always start at AA, all valves off

    # Keep max states for pruning
    max_pressure = 0
    max_pressure_state: Optional[State] = None
    max_state_list: Optional[StateList] = None

    visited: dict[State, tuple[int, int]] = {}

    def search(
        state: State,
        pressure: int,
        step_count: int,
        state_list: StateList,
    ) -> None:
        """Depth first search"""
        nonlocal max_steps
        nonlocal max_pressure
        nonlocal max_pressure_state
        nonlocal max_state_list

        # Stop if we reached max iterations allowed
        if step_count == max_steps:
            if pressure > max_pressure:
                max_pressure = pressure
                max_pressure_state = state
                max_state_list = state_list
            return

        # If all valves that contribute are on, we can calculate how much pressure will
        # have been released all the way to the end
        if state.valve_status == valve_manager.optimized_valve_state:
            remaining_steps = max_steps - step_count
            total_pressure = pressure + remaining_steps * valve_manager.max_pressure
            if total_pressure > max_pressure:
                max_pressure_state = state
                max_pressure = total_pressure
                max_state_list = StateList(
                    state=state,
                    parent=state_list,
                    early_exit=True,
                )
            return

        if max_pressure > 0:
            remaining_steps = max_steps - step_count
            upper_bound = pressure + valve_manager.max_pressure * remaining_steps
            if upper_bound < max_pressure:
                return

        # What is a theoretical limit of total pressure we can release by the end
        if max_pressure > 0:
            # Theoretical pressure:
            # 1. Pressure released so far
            # 2. Pressure rate (current pressure release per step * remaining steps)
            # 3. Pressure contributed by currently closed valves in the future

            remaining_steps = max_steps - step_count

            upper_bound = pressure  # pressure so far

            pressure_per_step = valve_manager.get_pressure(state.valve_status)
            upper_bound += pressure_per_step * remaining_steps  # pressure per step

            for closed_valve in valve_manager.get_closed_working_valves(
                state=state.valve_status
            ):
                closed_valve_flow_rate = valve_manager.get_flow_rate(closed_valve)
                # Cost to reach such valve
                steps_to_valve = valve_manager.get_cost(state.valve, closed_valve)
                # How long will this valve be open?
                steps_open = max(0, remaining_steps - steps_to_valve)
                # How much will this one contribute
                upper_bound += steps_open * closed_valve_flow_rate

            if upper_bound < max_pressure:
                return

        if state in visited:
            # We have been here before, was the previous state better than us?
            other_pressure, other_step_count = visited[state]
            if step_count >= other_step_count and other_pressure >= pressure:
                # We are further along, but worse, exit early!
                return

        visited[state] = (pressure, step_count)
        current_valve, current_valve_status = state
        # Get total pressure from this iteration
        current_pressure = valve_manager.get_pressure(current_valve_status)

        if valve_manager.is_closed(current_valve, current_valve_status):
            # Only turn on valves that are off and have flow rate > 0
            if valve_manager.get_flow_rate(current_valve) > 0:
                new_valve_status = valve_manager.open_valve(
                    current_valve, current_valve_status
                )
                next_state = State(
                    valve=current_valve,
                    valve_status=new_valve_status,
                )
                search(
                    state=next_state,
                    pressure=pressure + current_pressure,
                    step_count=step_count + 1,
                    state_list=StateList(state=next_state, parent=state_list),
                )

        for neighbour in valve_manager.get_neighbors(current_valve):
            if valve_manager.is_closed(neighbour, current_valve_status):
                next_state = State(
                    valve=neighbour,
                    valve_status=current_valve_status,
                )
                search(
                    state=next_state,
                    pressure=pressure + current_pressure,
                    step_count=step_count + 1,
                    state_list=StateList(state=next_state, parent=state_list),
                )

        for neighbour in valve_manager.get_neighbors(current_valve):
            if not valve_manager.is_closed(neighbour, current_valve_status):
                next_state = State(
                    valve=neighbour,
                    valve_status=current_valve_status,
                )
                search(
                    state=State(valve=neighbour, valve_status=current_valve_status),
                    pressure=pressure + current_pressure,
                    step_count=step_count + 1,
                    state_list=StateList(state=next_state, parent=state_list),
                )

    search(
        state=start,
        step_count=0,
        pressure=0,
        state_list=StateList(state=start, parent=None),
    )

    print(f"{max_pressure_state}")

    assert max_state_list is not None

    print_steps(valve_manager=valve_manager, state_list=max_state_list)

    return max_pressure


def print_steps(valve_manager: ValveStateManager, state_list: StateList) -> None:
    """Prints the step activity similar to sample"""
    states = []
    curr = state_list
    while curr is not None:
        states.append((curr.state, curr.early_exit))
        curr = curr.parent  # type: ignore

    states.reverse()
    print()
    for idx, ((p, e1), (n, e2)) in enumerate(pairwise(states)):
        current_pressure = valve_manager.get_pressure(p.valve_status)
        open_valves = set(valve_manager.get_open_valves(p.valve_status))
        opened_valve = set(valve_manager.get_open_valves(n.valve_status)) - open_valves
        if len(open_valves) == 0:
            valve_message = "No valves are open"
        elif len(open_valves) == 1:
            open_valve = open_valves.pop()
            valve_message = (
                f"Valve {open_valve} is open, releasing {current_pressure} pressure"
            )
        else:
            valve_message = (
                f"Valves {' and '.join(sorted(open_valves))} are open, "
                f"releasing {current_pressure} pressure."
            )
        print(f"== Minute {idx + 1} ==")
        print(valve_message)
        if n.valve != p.valve:
            print(f"You move to valve {n.valve}")
        if opened_valve:
            print(f"You open valve: {opened_valve.pop()}")
        if e2:
            print("All working valves have been opened")


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    valve_infos = list(parse_input(s))
    # part_1 = maximise_pressure_release(total_steps=26, valve_infos=valve_infos)
    part_1 = calc_max_pressure(max_steps=30, valve_infos=valve_infos)

    return part_1, 0


TEST_INPUT = """\
Valve AA has flow rate=0; tunnels lead to valves DD, II, BB
Valve BB has flow rate=13; tunnels lead to valves CC, AA
Valve CC has flow rate=2; tunnels lead to valves DD, BB
Valve DD has flow rate=20; tunnels lead to valves CC, AA, EE
Valve EE has flow rate=3; tunnels lead to valves FF, DD
Valve FF has flow rate=0; tunnels lead to valves EE, GG
Valve GG has flow rate=0; tunnels lead to valves FF, HH
Valve HH has flow rate=22; tunnel leads to valve GG
Valve II has flow rate=0; tunnels lead to valves AA, JJ
Valve JJ has flow rate=21; tunnel leads to valve II
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (1651, 0)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
