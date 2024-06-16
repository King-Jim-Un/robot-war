from dataclasses import dataclass
import logging
from pygame import Vector2
from typing import Optional

from robot_war.vm.get_name import GetName

try:
    from robot_war.vm.source_module import Module
    from robot_war.vm.exec_context import Playground
except ImportError:
    Module = Playground = None

# Constants:
LOG = logging.getLogger(__name__)


@dataclass
class ApiClass(GetName):
    _playground: Optional["Playground"] = None
    position: Vector2 = Vector2(300.0, 200.0)
    facing: float = 0.0

    def get_name(self, name: str):
        if name.startswith("_"):
            raise KeyError(f"not going to return {name}")
        value = getattr(self.__class__, name)
        return getattr(self, name) if callable(value) else value  # TODO: This is a little fragile and must be expanded later on
