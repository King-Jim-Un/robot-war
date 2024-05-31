from dataclasses import dataclass
from typing import Any


@dataclass
class ReturnException(Exception):
    value: Any


@dataclass
class RobotWarSystemExit(Exception):
    return_code: int
