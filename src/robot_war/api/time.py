import logging
from time import monotonic

from robot_war.exceptions import BlockGenerator
from robot_war.vm.source_module import Module

# Constants:
LOG = logging.getLogger(__name__)


def sleep(delay: float):
    wake_at = monotonic() + delay

    def poll_time():
        while monotonic() < wake_at:
            yield

    raise BlockGenerator(poll_time())


TIME_MODULE = Module("time", name_dict={"monotonic": monotonic, "sleep": sleep})
