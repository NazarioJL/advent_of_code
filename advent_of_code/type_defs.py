from typing import TypeAlias

NoAns: TypeAlias = None
AnswerType: TypeAlias = int | float | str | NoAns
Solution: TypeAlias = tuple[AnswerType, AnswerType]
