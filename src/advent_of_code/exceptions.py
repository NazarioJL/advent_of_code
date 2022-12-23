class SolutionNotImplementedError(Exception):
    """Raise this error when a solver method has not yet implemented the solution"""

    def __init__(self) -> None:
        super().__init__("You have not implemented this method as of yet.")


class UnexpectedConditionError(Exception):
    """Raise this error when an unexpected condition occurs in the code"""


class IncorrectReturnTypeError(TypeError):
    pass
