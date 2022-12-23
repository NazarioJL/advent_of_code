from typing import TypeAlias
from typing import Union


NoAns: TypeAlias = type[None]
AnsType: TypeAlias = Union[int, str]
TimedAns: TypeAlias = tuple[AnsType, float]
Ans: TypeAlias = Union[AnsType, TimedAns]
Solution: TypeAlias = Union[tuple[Ans, Ans], tuple[Ans, Ans, float]]
