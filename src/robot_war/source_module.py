from dataclasses import dataclass
import logging

from robot_war.get_name import GetName
from robot_war.source_functions import Function

# Constants:
LOG = logging.getLogger(__name__)


@dataclass(repr=False)
class Module(GetName, Function):

    def __repr__(self):
        return f"Module({self.name}, {len(self.name_dict)} names)"
