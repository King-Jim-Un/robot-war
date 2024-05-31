import logging
from pathlib import Path

from robot_war.run_program import run_program, exec_through

# Constants:
LOG = logging.getLogger(__name__)
PATH = Path(__file__).parent / "test-script.py"


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    exec_through(run_program(PATH))
