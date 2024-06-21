from dataclasses import dataclass, field
import logging
from pygame import Vector2
from typing import Optional, Any, List, Callable

from robot_war.exceptions import BlockFunction, SandboxRequired
from robot_war.vm.get_name import GetName

try:
    from robot_war.vm.source_module import Module
    from robot_war.vm.exec_context import Playground, SandBox
except ImportError:
    Module = Playground = SandBox = None

# Constants:
LOG = logging.getLogger(__name__)


@dataclass
class ApiClass(GetName):
    _playground: Optional["Playground"] = None

    def get_name(self, name: str):
        if name.startswith("_"):
            raise KeyError(f"not going to return {name}")
        value = getattr(self.__class__, name)
        return getattr(self, name) if callable(value) else value  # TODO: This is a little fragile and must be expanded later on


class RobotApi(ApiClass):
    position: Vector2 = Vector2(300.0, 200.0)
    facing: float = 0.0


@dataclass
class Waiter:
    done: bool = False
    value: Any = None
    sandboxes: List["SandBox"] = field(default_factory=list)

    def set_value(self, value):
        """Called by the thread that created the Waiter object when it is complete"""
        self.value = value
        self.done = True

        # All waiting threads may now continue
        while self.sandboxes:
            sandbox = self.sandboxes.pop()
            sandbox.push(self.value)  # return value
            sandbox.playground.sandboxes.append(sandbox)  # continue

    def get_value(self, sandbox: "SandBox"):
        """Any thread may call this method, may block, but will eventually get a value"""
        if self.done:
            return self.value
        else:
            # The thread isn't done, so block until they're ready
            self.sandboxes.append(sandbox)
            raise BlockFunction(self)


def requires_sandbox(function: Callable):
    def wrapper(*args, **kwargs):
        if "sandbox" not in kwargs:
            raise SandboxRequired()
        return function(*args, **kwargs)

    return wrapper
