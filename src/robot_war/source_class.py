from dataclasses import dataclass, field, asdict
import logging
from typing import Dict, Any, Optional

from robot_war.source_functions import Function

try:
    from robot_war.exec_context import NameDict
except ImportError:
    NameDict = None


# Constants:
LOG = logging.getLogger(__name__)


# Creating a class:
#   * Use MakeFunction to turn the constructor's code object into a function
#   * Call build_class to turn the function into a class
# Instantiating a class:
#   * Call the class, which must
#     * Create an instance
#     * Execute the constructor
#     * Execute the __init__ function
#     * Return the instance


@dataclass
class Constructor(Function):
    name_dict: NameDict = field(default_factory=dict)


def build_class(function: Function, name: str):
    return SourceClass(function)


@dataclass
class SourceClass:
    function: Function


@dataclass
class SourceInstance:
    source_class: SourceClass
    name_dict: NameDict = field(default_factory=dict)
    values: Dict[str, Any] = field(default_factory=dict)

    def set_attr(self, name: str, value: Any):
        self.values[name] = value

    def get_attr(self, name: str):
        if name in self.values:
            return self.values[name]
        else:
            obj = self.name_dict[name]
            return BoundMethod(instance=self, **obj.__dict__)if isinstance(obj, Function) else obj

    def get_method(self, name: str):
        return self.name_dict[name]


@dataclass
class BoundMethod(Function):
    instance: Optional[SourceInstance] = None
