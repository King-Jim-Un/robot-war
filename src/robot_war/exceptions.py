from dataclasses import dataclass
from typing import Any


@dataclass
class ReturnException(Exception):
    value: Any


@dataclass
class RobotWarSystemExit(Exception):
    return_code: int


class DontPushReturnValue(Exception):
    """Thrown to indicate that the function will push its own return value"""
