from enum import auto, Enum
from typing import Optional, Generic, TypeVar, cast

import attrs
import pytest
from attrs import validators


from advent_of_code.core import aoc
from advent_of_code.core import print_solution
from advent_of_code.exceptions import UnexpectedConditionError
from advent_of_code.type_defs import Solution
from advent_of_code.utilities import get_input_data


YEAR = 2024
DAY = 9


T = TypeVar("T")


class ListNode(Generic[T]):
    """ListNode definition for a doubly linked list"""

    def __init__(
        self,
        value: T,
        next_: Optional["ListNode[T]"] = None,
        prev: Optional["ListNode[T]"] = None,
    ) -> None:
        self.value = value
        self.next = next_
        self.prev = prev

    def __repr__(self) -> str:
        prev = str(self.prev.value) if self.prev is not None else "None"
        next_ = str(self.next.value) if self.next is not None else "None"
        return f"ListNode({self.value}, next={next_}, prev={prev})"


def insert_after(node: ListNode, value: T) -> ListNode:
    """Inserts a new node with value 'value' after the given node 'node'"""

    new_node = ListNode(value=value)
    if node.next is None:
        node.next = new_node
        new_node.prev = node
    else:
        new_node.next = node.next
        node.next = new_node
        new_node.next.prev = node
        new_node.prev = node

    return new_node


class BlockType(Enum):
    FILE = auto()
    FREE = auto()


@attrs.define
class Block:
    block_id: Optional[int]
    size: int = attrs.field(validator=[validators.instance_of(int), validators.ge(0)])
    block_type: BlockType


def get_blocks(layout: str) -> list[Block]:
    blocks = []
    file_id = 0
    for idx, curr_length in enumerate(layout.strip()):
        size = int(curr_length)
        if size == 0:
            continue

        if idx % 2 == 0:  # even indexes are files
            blocks.append(Block(block_id=file_id, size=size, block_type=BlockType.FILE))
            file_id += 1
        else:
            blocks.append(Block(block_id=None, size=size, block_type=BlockType.FREE))

    return blocks


def blocks_to_string(blocks: list[Block]) -> str:
    buffer = ""
    for block in blocks:
        if block.block_id is None:
            buffer += "".join(["."] * block.size)
        else:
            buffer += "".join([str(block.block_id)] * block.size)

    return buffer


def checksum(blocks: list[Block]) -> int:
    result = 0
    start_index = 0
    prev_s = 0  # hold previous sum, so we don't re-calc every time
    for block in blocks:
        start_index += block.size
        s = ((start_index * start_index + start_index) // 2) - start_index
        result += (s - prev_s) * (block.block_id or 0)
        prev_s = s

    return result


def compress(blocks: list[Block]) -> list[Block]:
    """Compress the given blocks. ⚠️ This mutates the contents of 'blocks'!"""

    # TODO: Re-implement this in compress_part_2 so we don't have 2 functions doing the
    #       same thing. We would accept partial moves to pack the disk densely.
    compressed = []
    left, right = 0, len(blocks) - 1

    empty_block: Block | None = None
    file_block: Block | None = None

    while True:
        # Find next block that can be allocated to
        while left <= right:
            if empty_block:
                break
            tmp_free: Block = blocks[left]
            if tmp_free.block_type == BlockType.FREE:
                if tmp_free.size > 0:
                    empty_block = blocks[left]
                    break
                else:
                    left += 1
            else:  # BlockType.FILE
                if tmp_free.size > 0:
                    compressed.append(tmp_free)
                else:
                    # Discard and move to next
                    pass
                left += 1

        if not empty_block:
            break

        # Find next block that needs to be allocated

        while left <= right:
            if file_block:
                break
            tmp_file: Block = blocks[right]
            if tmp_file.block_type == BlockType.FILE:
                if tmp_file.size <= 0:
                    right -= 1
                else:
                    file_block = blocks[right]
                    break
            else:  # This is an empty block
                right -= 1

        if not file_block:
            break

        if empty_block.size > file_block.size:
            # The whole block is going in
            empty_block.size -= file_block.size
            compressed.append(file_block)
            right -= 1
            file_block = None
        elif empty_block.size == file_block.size:
            compressed.append(file_block)
            left += 1  # Find next empty block
            right -= 1
            file_block = None
            empty_block = None

        elif empty_block.size < file_block.size:
            # Can partially fit the file block
            left += 1
            file_block.size -= empty_block.size
            compressed.append(
                Block(
                    block_id=file_block.block_id,
                    size=empty_block.size,
                    block_type=BlockType.FILE,
                )
            )
            empty_block = None
        else:
            raise UnexpectedConditionError

    return compressed


def compress_part_2(blocks: list[Block]) -> list[Block]:
    """Compress the given blocks using rules from part 2 of puzzle"""
    dummy = ListNode(
        value=Block(block_id=None, size=0, block_type=BlockType.FREE),
        next_=None,
        prev=None,
    )
    curr: ListNode[Block] = dummy

    for block in blocks:
        curr = insert_after(curr, block)

    head: ListNode[Block] = cast(ListNode[Block], dummy.next)
    right: ListNode[Block] = curr

    # Move to first file that needs to be moved
    while right and right.value.block_type != BlockType.FILE:
        assert right.prev
        right = right.prev

    assert right.value.block_id
    block_id = (
        right.value.block_id + 1
    )  # keep track of block_id so we don't run over previously moved

    while True:
        if right.value.block_id == 0:
            break

        # Find next block to move by moving right pointer to the left
        while right != head:
            if (
                right.value.block_type == BlockType.FILE
                and right.value.block_id == block_id - 1
            ):
                block_id = right.value.block_id
                break
            else:
                assert right.prev
                right = right.prev

        # Find first block that can accommodate the file at 'right'
        left = head

        while left != right:
            if (
                left.value.block_type == BlockType.FREE
                and left.value.size >= right.value.size
            ):
                # we found a suitable block!
                if right.value.size == left.value.size:
                    # Let's swap for convenience
                    right.value, left.value = left.value, right.value
                elif left.value.size > right.value.size:
                    # We have to split the free block
                    empty_block = left.value  # Block to be split
                    left.value = right.value  # Place file in block
                    right.value = Block(
                        block_id=None, block_type=BlockType.FREE, size=right.value.size
                    )
                    insert_after(
                        left,
                        Block(
                            block_id=None,
                            size=empty_block.size - right.value.size,
                            block_type=BlockType.FREE,
                        ),
                    )
                else:
                    raise UnexpectedConditionError
                break
            else:
                assert left.next
                left = left.next

    compressed = []
    node: ListNode[Block] | None = head
    while node:
        compressed.append(node.value)
        node = node.next

    return compressed


@aoc.solution(year=YEAR, day=DAY)
def solve(s: str) -> Solution:
    part_1 = checksum(compress(get_blocks(s)))
    part_2 = checksum(compress_part_2(get_blocks(s)))

    return part_1, part_2


TEST_INPUT = """\
12345
"""

TEST_INPUT_2 = """\
2333133121414131402
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    (
        (TEST_INPUT, (60, 132)),
        (TEST_INPUT_2, (1928, 2858)),
    ),
)
def test_solve(input_s: str, expected: tuple[()]) -> None:
    assert solve(input_s).as_tuple() == expected


def test_checksum() -> None:
    blocks = [
        Block(block_id=int(e), size=1, block_type=BlockType.FILE)
        for e in "0099811188827773336446555566"
    ]
    assert checksum(blocks) == 1928


if __name__ == "__main__":
    print_solution(solve(get_input_data(YEAR, DAY)))
