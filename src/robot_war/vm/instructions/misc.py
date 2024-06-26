import logging

from robot_war.vm.instructions import CodeLine

try:
    from robot_war.vm.exec_context import SandBox
except ImportError:
    SandBox = None  # type: ignore

# Constants:
LOG = logging.getLogger(__name__)


class Nop(CodeLine):
    pass
