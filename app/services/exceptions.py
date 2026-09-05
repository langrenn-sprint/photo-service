"""Module for service exceptions."""


class IllegalValueError(Exception):
    """Class representing custom exception for create method."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""
        super().__init__(message)
