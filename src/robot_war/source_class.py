from dataclasses import dataclass
import logging

from robot_war.source_functions import Function

# Constants:
LOG = logging.getLogger(__name__)


@dataclass
class SourceClass(Function):
    pass
