from typing import Callable
from typing import Iterable
from typing import TypeVar

TItem = TypeVar("TItem")


TransformerFuncTypeDef = Callable[[str], TItem]


def parse_lines(
    input_s: str, tx_func: TransformerFuncTypeDef = lambda x: x
) -> Iterable[TItem]:
    for line in input_s.splitlines():
        yield tx_func(line)
