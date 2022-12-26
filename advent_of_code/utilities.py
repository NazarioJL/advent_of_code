import os
import urllib.error
import urllib.request
from pathlib import Path


def get_input_data(year: int, day: int, relative_dir: str | None = None) -> str:
    file_name = f"day{day:02}.txt"
    file_dir = f"{year}"

    if relative_dir is None:
        relative_dir = os.path.join(get_project_root(), "inputs")

    file_path = os.path.join(relative_dir, file_dir, file_name)

    with open(file_path) as f:
        return f.read()


def download_input_data(year: int, day: int, cookie: str) -> str:
    url = f"https://adventofcode.com/{year}/day/{day}/input"
    req = urllib.request.Request(url, headers={"Cookie": cookie})
    return urllib.request.urlopen(req).read().decode()  # type: ignore


def get_project_root() -> Path:
    current = Path(os.getcwd())
    found = False

    while not found:
        if current == "/":
            SystemExit(
                "Could not find the project root, make sure you're inside the "
                "'advent_of_code' project"
            )
        if os.path.isfile(os.path.join(current, "pyproject.toml")):
            found = True
        else:
            current = current.parent
    return current
