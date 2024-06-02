import logging
from pathlib import Path

from robot_war.vm.run_program import run_program, exec_through

# Constants:
LOG = logging.getLogger(__name__)
PATH = Path(__file__).parent / "test-script.py"


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("robot_war.vm.instructions").setLevel(logging.WARNING)
    exec_through(run_program(PATH))
