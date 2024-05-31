from dataclasses import dataclass, field
import logging
from typing import Dict, Any, Optional

from robot_war.instructions import CodeLine

try:
    from robot_war.source_module import Module
    from robot_war.exec_context import SandBox
except ImportError:
    Module = CodeBlockContext = NameDict = SandBox = None

# Types:
CodeDict = Dict[str, "CodeBlock"]

# Constants:
LOG = logging.getLogger(__name__)


@dataclass(repr=False)
class CodeBlock:
    code_lines: Dict[int, CodeLine] = field(default_factory=dict)
    module: Optional["Module"] = None
    constants: Dict[int, Any] = field(default_factory=dict)

    def __repr__(self):
        return f"CodeBlock(module={self.module.name}, {len(self.code_lines)} lines, {len(self.constants)} constants)"


@dataclass
class Function:
    name: str
    code_block: CodeBlock
    num_params: int = 0
    closure: tuple = ()
