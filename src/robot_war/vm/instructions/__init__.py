from dataclasses import dataclass
import logging
from typing import Optional

try:
    from robot_war.vm.exec_context import SandBox
except ImportError:
    SandBox = None

# Constants:
LOG = logging.getLogger(__name__)


@dataclass(repr=False)
class CodeLine:
    line_number: Optional[int]
    offset: int
    op_code: str
    operand: Optional[int]
    note: Optional[str]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.operand}, {self.note})"

    def exec(self, sandbox: SandBox):
        LOG.debug("%r", self)
        sandbox.next()
