from dataclasses import dataclass, field
import logging
from typing import Dict, Any, Optional, List

from robot_war.instructions import CodeLine

try:
    from robot_war.source_module import Module
except ImportError:
    Module = None

# Types:
CodeDict = Dict[str, "CodeBlock"]

# Constants:
LOG = logging.getLogger(__name__)


@dataclass(repr=False)
class CodeBlock:
    code_lines: Dict[int, CodeLine] = field(default_factory=dict)
    module: Optional[Module] = None
    num_params: int = 0
    param_names: List[str] = field(default_factory=list)
    constants: Dict[int, Any] = field(default_factory=dict)

    def __repr__(self):
        module_name = None if self.module is None else self.module.name
        return f"CodeBlock(module={module_name}, {len(self.code_lines)} lines, {len(self.constants)} constants)"


@dataclass
class Function:
    name: str
    code_block: CodeBlock
    closure: tuple = ()
    default_args: tuple = ()
