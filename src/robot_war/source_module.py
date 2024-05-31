from dataclasses import dataclass, field
import logging

from robot_war.source_functions import Function

try:
    from robot_war.exec_context import NameDict
except ImportError:
    NameDict = None

# Constants:
LOG = logging.getLogger(__name__)


@dataclass(repr=False)
class Module(Function):
    name_dict: NameDict = field(default_factory=dict)

    def __repr__(self):
        return f"Module({self.name}, {len(self.name_dict)} names)"
