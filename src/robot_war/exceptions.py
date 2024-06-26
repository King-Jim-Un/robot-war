from dataclasses import dataclass
from typing import Any, Generator, Optional

try:
    from robot_war.vm.api_class import Waiter
    from robot_war.vm.exec_context import SandBox
except ImportError:
    Waiter = SandBox = None  # type: ignore


@dataclass
class ReturnException(Exception):
    value: Any


@dataclass
class RobotWarSystemExit(Exception):
    return_code: int


class DontPushReturnValue(Exception):
    """Thrown to indicate that the function will push its own return value"""


class TerminalError(BaseException):
    """Thrown when user code cannot recover"""


class BlockBase(Exception):
    pass


@dataclass
class BlockGenerator(BlockBase):
    generator: Generator
    sandbox: Optional["SandBox"] = None


@dataclass
class BlockFunction(BlockBase):
    waiter: "Waiter"


class SandboxRequired(Exception):
    """Thrown when an API function requires a sandbox parameter"""
