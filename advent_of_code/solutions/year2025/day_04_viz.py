# mypy: ignore-errors
import time

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console(force_terminal=True)


TEST_INPUT = """\
..@@.@@@@.
@@@.@.@.@@
@@@@@.@.@@
@.@@@@..@.
@@.@@@@.@@
.@@@@@@@.@
.@.@.@.@@@
@.@@@.@@@@
.@@@@@@@@.
@.@.@@@.@.
"""


def remove_rolls(
    paper_rolls: list[list[str]], threshold: int = 4, remove: bool = False
) -> list[tuple[int, int]]:
    """Counts how many rolls can be removed from the grid

    :param paper_rolls: the paper roll list as a grid '@' = paper roll, '.' empty
    :param threshold: if a roll has less than the given threshold, it can be removed
    :param remove: remove the rolls from the input
    :return: the number of rolls that can be removed
    """
    rows = len(paper_rolls)
    cols = len(paper_rolls[0])

    # fmt: off
    directions = (
        (-1, -1), ( 0, -1), ( 1, -1),
        (-1,  0),           ( 1,  0),
        (-1,  1), ( 0,  1), ( 1,  1),
    )

    to_remove = []

    for row, col in ((row, col) for col in range(cols) for row in range(rows) if paper_rolls[row][col] == "@"):
        roll_count = 0
        for d_row, d_col in directions:
            new_row = row + d_row
            new_col = col + d_col
            if 0 <= new_row < rows and 0 <= new_col < cols and paper_rolls[new_row][new_col] == "@":
                roll_count += 1
        if roll_count < threshold:
            to_remove.append((row, col))

    if remove:
        for row, col in to_remove:
            paper_rolls[row][col] = "."

    return to_remove


class PaperRollsGrid:
    def __init__(
        self,
        rows: int,
        cols: int,
        rolls: set[tuple[int, int]],
        marked: set[tuple[int, int]],
    ) -> None:
        self._rows = rows
        self._cols = cols
        self._marked = marked
        self._rolls = rolls
        self._table = Table(
            box=box.DOUBLE_EDGE, show_header=False, padding=0, show_lines=True
        )
        self.update_props()

    def update_props(self):
        self._table = Table(
            box=box.DOUBLE_EDGE,
            style="cyan",
            show_header=False,
            padding=0,
            show_lines=True,
        )
        for row in range(self._rows):
            columns = []
            for col in range(self._cols):
                if (row, col) in self._rolls:
                    if (row, col) in self._marked:
                        columns.append(Text("@", style="red italic"))
                    else:
                        columns.append(Text("@", style="bold green"))
                else:
                    columns.append(Text(" ", style="blue"))
            self._table.add_row(*columns)

    def mark_for_removal(self, row, col):
        self._marked.add((row, col))
        self.update_props()

    def remove(self, row, col):
        self._rolls.discard((row, col))
        self._marked.discard((row, col))
        self.update_props()

    def __rich__(self) -> Table:
        return self._table


class RemovedRolls:
    def __init__(self) -> None:
        self._removed = 0
        self._text = Text()
        self._final = False
        self._panel = Panel(self._text, title=f"Removed ({self._removed})", style="red")

    def add_removed(self):
        self._removed += 1
        self.update()

    def finalize(self):
        self._final = True
        self.update()

    def update(self):
        self._panel = Panel(self._text, title=f"Removed ({self._removed})", style="red")
        self._text = Text("@" * self._removed)
        if self._final:
            self._text.stylize("blink red")
        else:
            self._text.stylize("orange")

    def __rich__(self) -> Panel:
        return self._panel


class PaperRollsViewModel:
    def __init__(
        self, rows: int, cols: int, paper_rolls: list[tuple[int, int]]
    ) -> None:
        self._rows = rows
        self._cols = cols
        self._paper_rolls = set(paper_rolls)
        self._marked_for_removal = set()
        self._removed_count = 0
        self._layout = Layout(name="root")

        self._paper_roll_grid = PaperRollsGrid(
            rows, cols, self._paper_rolls, self._marked_for_removal
        )
        self._removed_panel = RemovedRolls()
        self._panel_1 = Panel(
            self._paper_roll_grid, title="🎄2025 Day 4 -- Paper Rolls"
        )
        self._panel_2 = Panel(self._removed_panel, title="Removed")
        self._layout.split_row(
            Layout(name="main", ratio=1),
            Layout(name="side"),
        )

        self._layout["main"].update(self._panel_1)
        self._layout["side"].update(self._panel_2)

    def set_action(self, action):
        self._panel_1.subtitle = action

    def mark_for_removal(self, row, col) -> None:
        self._paper_roll_grid.mark_for_removal(row, col)

    def remove(self, row, col):
        self._paper_roll_grid.remove(row, col)
        self._removed_panel.add_removed()

    def finalize(self):
        self._removed_panel.finalize()

    def __rich__(self) -> Layout:
        return self._layout


def main():
    paper_rolls = [[c for c in line] for line in TEST_INPUT.splitlines()]
    rows = len(paper_rolls)
    cols = len(paper_rolls[0])

    rolls_cords = []
    for row, line in enumerate(paper_rolls):
        for col, char in enumerate(line):
            if char == "@":
                rolls_cords.append((row, col))

    paper_rolls_view_model = PaperRollsViewModel(rows, cols, rolls_cords)

    with Live(paper_rolls_view_model, console=console, auto_refresh=True) as live:
        live.update(paper_rolls_view_model)
        while removed := remove_rolls(paper_rolls, remove=True):
            paper_rolls_view_model.set_action("Identifying...")
            for row, col in removed:
                paper_rolls_view_model.mark_for_removal(row, col)
                time.sleep(0.1)
            time.sleep(0.5)
            paper_rolls_view_model.set_action("Removing...")
            for row, col in removed:
                paper_rolls_view_model.remove(row, col)
                live.update(paper_rolls_view_model)
                time.sleep(0.05)
            time.sleep(0.5)

        paper_rolls_view_model.finalize()
        paper_rolls_view_model.set_action("Done!")


if __name__ == "__main__":
    main()
