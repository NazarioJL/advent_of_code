import os
import time
import urllib.error
import urllib.request
from typing import cast

import click
from jinja2 import Template

from advent_of_code import settings
from advent_of_code.utilities import download_input_data
from advent_of_code.utilities import get_project_root


@click.group()
def main() -> None:
    pass


@main.command(name="getinfo")
def get_info() -> None:
    click.secho(f"{get_project_root()}", fg="cyan", bg="red")


@main.command(name="create-solution")
@click.option(
    "-y",
    "--year",
    type=int,
    required=True,
    help="Advent of Code year to generate the template for",
)
@click.option(
    "-d",
    "--day",
    "day",
    type=int,
    required=True,
    help="Advent of Code day to generate the template for",
)
@click.option(
    "-ip",
    "--input-path",
    "input_path",
    type=str,
    required=False,
    help="Base directory to save input file to",
)
@click.option(
    "-sp",
    "--solution-path",
    "solution_path",
    type=str,
    required=False,
    help="Base directory to save solution template to",
)
@click.option(
    "-t",
    "--template",
    "template_path",
    type=str,
    required=False,
    help="Jinja template file path to use for solution",
)
@click.option(
    "-f",
    "--force",
    "force",
    type=bool,
    required=False,
    help="Will overwrite files if they exist",
)
def create_solution(
    year: int,
    day: int,
    force: bool,
    input_path: str = None,
    solution_path: str = None,
    template_path: str = None,
) -> None:

    click.echo()
    click.secho(
        f"Creating the solution skeleton for Year: [{year}] - Day: [{day}]",
        fg="green",
        bold=True,
    )

    input_path = input_path or str(get_project_root())
    input_base_path = os.path.join(input_path, "inputs", f"{year}")
    input_file_name = f"day{day:02}.txt"
    input_file_path = os.path.join(input_base_path, input_file_name)

    click.secho(
        f"Will attempt to create input file: {click.format_filename(input_file_path)} ",
        fg="green",
    )

    if os.path.exists(input_file_path):
        click.secho(f"Found file at: {input_file_path}", fg="yellow")
        file_exists = True
    else:
        file_exists = False

    if (file_exists and force) or not file_exists:
        click.secho(f"Downloading file to {input_file_path}", fg="green")

        cookie_location = os.path.join(get_project_root(), ".env")

        with open(cookie_location) as f:
            cookie = f.read().strip()
        for i in range(5):
            try:
                s = download_input_data(year=year, day=day, cookie=cookie)
            except urllib.error.URLError as e:
                print(f"zzz: not ready yet: {e}")
                time.sleep(1)
            else:
                break
        else:
            raise SystemExit("timed out after attempting many times")

        os.makedirs(input_base_path, exist_ok=True)

        with open(file=input_file_path, mode="w") as f:
            f.write(s)
    else:
        click.secho("Skipping file download...", fg="yellow")

    module_path = solution_path or os.path.join(
        get_project_root(), f"advent_of_code/solutions/year{year}"
    )
    solution_path = os.path.join(module_path, f"day_{day:02}.py")
    init_path = os.path.join(module_path, "__init__.py")

    os.makedirs(module_path, exist_ok=True)

    click.secho(
        f"Will attempt to create solution file: "
        f"{click.format_filename(solution_path)} ",
        fg="green",
    )

    solution_exists = os.path.exists(solution_path)

    if solution_exists:
        click.secho(
            f"Solution file: {click.format_filename(solution_path)} already exists!",
            fg="yellow",
        )

    if (solution_exists and force) or not solution_exists:
        with open(solution_path, "w") as fw:
            click.secho(
                f"Writing solution file: {click.format_filename(solution_path)}",
                fg="green",
            )
            fw.write(
                render_template(
                    year=year, day=day, template_source=settings.SOLUTION_JINJA_TEMPLATE
                )
            )

        with open(init_path, "w"):
            click.secho(
                f"Writing init file: {click.format_filename(init_path)}", fg="green"
            )
    else:
        click.secho("Skipping solution file creation...", fg="yellow")

    raise SystemExit(0)


@main.command(name="create-template")
@click.option(
    "-y",
    "--year",
    type=int,
    required=True,
    help="Advent of Code year to generate the template for",
)
@click.option(
    "-d",
    "--day",
    "day",
    type=int,
    required=True,
    help="Advent of Code day to generate the template for",
)
def create_template(year: int, day: int) -> None:
    print(
        render_template(
            year=year, day=day, template_source=settings.SOLUTION_JINJA_TEMPLATE
        )
    )


def render_template(year: int, day: int, template_source: str) -> str:
    template = Template(source=template_source, keep_trailing_newline=True)
    result = cast(str, template.render(year=year, day=day))
    return result


if __name__ == "__main__":
    main()
