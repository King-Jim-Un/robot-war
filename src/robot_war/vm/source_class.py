from dataclasses import dataclass, field
import logging
from typing import Dict, Any, Optional, List

from robot_war.vm.get_name import GetName
from robot_war.vm.source_functions import Function

try:
    from robot_war.vm.source_module import Module
except ImportError:
    Module = None  # type: ignore

# Constants:
LOG = logging.getLogger(__name__)


# Creating a class:
#   * Use MakeFunction to turn the creation code object into a function
#   * Call build_class to turn the function into a class
#   * Execute the creation code to initialize name_dict
# Calling a class:
#   * Create an instance
#   * Execute the __init__ function
#   * Return the instance

@dataclass
class SourceClass(GetName):
    parent_classes: List["SourceClass"] = field(default_factory=list)
    module: Optional[Module] = None

    def get_name(self, name: str):
        # Do we have the name?
        if name in self.name_dict:
            return self.name_dict[name]

        # No, do any of our parents?
        for parent in self.parent_classes:
            try:
                return parent.get_name(name)
            except KeyError:
                pass

        # Try the module's namespace
        if self.module:
            return self.module.get_name(name)
        else:
            raise KeyError(f"{name} not found")


@dataclass
class Constructor(Function):
    source_class: Optional[SourceClass] = None


@dataclass
class SourceInstance(GetName):
    source_class: Optional[SourceClass] = None
    values: Dict[str, Any] = field(default_factory=dict)

    def __getattr__(self, item):
        return self.get_name(item)

    def set_attr(self, name: str, value: Any):
        self.values[name] = value

    def get_attr(self, name: str):
        if name in self.values:
            return self.values[name]
        else:
            obj = self.get_name(name)
            return BoundMethod(instance=self, **obj.__dict__) if isinstance(obj, Function) else obj

    def get_method(self, name: str):
        attr = self.get_name(name)
        return attr if callable(attr) else BoundMethod(instance=self, **attr.__dict__)

    def get_name(self, name: str):
        assert self.source_class
        return self.name_dict[name] if name in self.name_dict else self.source_class.get_name(name)


@dataclass
class BoundMethod(Function):
    instance: Optional[SourceInstance] = None
