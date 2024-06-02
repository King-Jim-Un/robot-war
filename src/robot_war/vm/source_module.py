from dataclasses import dataclass, field
import logging
from pathlib import Path
from typing import Optional, List

from robot_war.vm.get_name import GetName
from robot_war.vm.source_functions import Function

# Constants:
LOG = logging.getLogger(__name__)


@dataclass(repr=False)
class Module(GetName, Function):
    path: Optional[Path] = None
    dot_path: List[str] = field(default_factory=list)  # ["animal", "feline", "cat"] means: import animal.feline.cat

    def __repr__(self):
        return f"Module({self.name}, {len(self.name_dict)} names)"

    def get_method(self, name: str):
        return self.get_name(name)
