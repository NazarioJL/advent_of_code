import pytest

from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data

YEAR = 2022
DAY = 7


TFileObject = dict[str, dict[str, "TFileObject"] | int]


def is_dir(fo: TFileObject) -> bool:
    return isinstance(fo, dict)


def print_directory(fo: TFileObject) -> None:
    def _print(f: TFileObject, level: int = 0) -> None:
        for k, v in f.items():
            space = "    " * level
            if isinstance(v, int):
                print(f"{space}- {k} (file, size={v})")
            else:
                print(f"{space}- {k}  (dir)")
                _print(v, level + 1)

    if isinstance(fo, int):
        print(fo)
    else:
        _print(fo)


def build_directory(commands: list[str]) -> TFileObject:
    directory: TFileObject = {"/": {}}
    stack: list[TFileObject] = [directory["/"]]

    for command in commands:
        match command.split():
            case ["$", "cd", dir_name]:
                if dir_name == "..":
                    if not stack:
                        raise ValueError("Cannot 'cd ..' as it is already at root")
                    stack.pop()
                else:
                    if dir_name == "/":
                        # special case
                        pass
                    else:
                        if not stack:
                            raise ValueError(
                                f"No current dir to point to: {command}, stack is empty"
                            )
                        if dir_name not in stack[-1]:
                            stack[-1][dir_name] = {}
                        stack.append(stack[-1][dir_name])
            case ["$", "ls"]:
                # This means next items will be file entries
                pass
            case ["dir", dir_name]:
                if dir_name not in stack[-1]:
                    stack[-1][dir_name] = {}
            case [size, file_name]:
                stack[-1][file_name] = int(size)
            case _:
                raise ValueError(f"Cannot understand statement: {command}")

    return directory


def get_dir_sizes(root: TFileObject) -> dict[str, int]:
    result = {}

    def _get_size_rec(fo: TFileObject, path: str) -> int:
        size = 0
        for k, v in fo.items():
            if is_dir(v):
                path = path + "." + k
                dir_size = _get_size_rec(v, path)
                result[path] = dir_size
                size += dir_size
            else:
                size += v

        return size

    result["/"] = _get_size_rec(root["/"], "/")

    return result


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    directory = build_directory(s.splitlines())
    sizes = get_dir_sizes(directory)
    part_1 = sum([size for size in sizes.values() if size <= 100000])

    total_disk = 70000000
    required = 30000000
    limit = total_disk - required

    total_used_space = sizes["/"]

    found = False
    min_diff = total_disk
    folder_result = None

    # find folder that deleted minimizes the diff between used and limit
    for folder, size in sizes.items():
        new_unused_space = total_used_space - size
        if new_unused_space <= limit:
            diff = limit - new_unused_space
            if diff < min_diff:
                min_diff = diff
                folder_result = folder
                found = True

    if not found:
        raise ValueError("Unable to find a suitable folder for part 2")

    part_2 = sizes[folder_result]

    return part_1, part_2


TEST_INPUT = """\
$ cd /
$ ls
dir a
14848514 b.txt
8504156 c.dat
dir d
$ cd a
$ ls
dir e
29116 f
2557 g
62596 h.lst
$ cd e
$ ls
584 i
$ cd ..
$ cd ..
$ cd d
$ ls
4060174 j
8033020 d.log
5626152 d.ext
7214296 k
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((TEST_INPUT, (95437, 24933642)),),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
