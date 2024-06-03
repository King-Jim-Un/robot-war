from dataclasses import dataclass
import logging
from typing import Optional, Callable

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
    playground: Optional["Playground"] = None

    def get_name(self, name: str):
        if name == "__init__":
            raise KeyError(f"not going to return {name}")
        value = getattr(self.__class__, name)
        return ApiMethod(value) if callable(value) else value  # TODO: This is a little fragile and must be expanded later on


@dataclass
class ApiMethod:
    function: Callable = None
