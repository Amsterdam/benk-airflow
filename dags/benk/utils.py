from typing import Any


def flatten_list(lst: list[list[Any]]):
    """Flatten a list of lists."""
    return [item for sublist in lst for item in sublist]
