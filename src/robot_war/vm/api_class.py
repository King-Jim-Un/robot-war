from dataclasses import dataclass
import logging

from robot_war.vm.get_name import GetName

try:
    from robot_war.vm.source_module import Module
except ImportError:
    Module = None

# Constants:
LOG = logging.getLogger(__name__)


@dataclass
class ApiClass(GetName):
    def get_name(self, name: str):
        if name == "__init__":
            raise KeyError(f"not going to return {name}")
        return getattr(self.__class__, name)  # TODO: This is a little fragile and must be expanded later on
