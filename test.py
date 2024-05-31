import logging

from robot_war.exec_context import ExecContext, SandBox
from robot_war.parse_source_file import parse_source_file, IMMEDIATE

# Constants:
LOG = logging.getLogger(__name__)
PATH = r"C:\git\robot-war\test-script.py"


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sandbox = SandBox()
    module = parse_source_file(sandbox, "__main__", PATH)
    context = ExecContext(sandbox, module.code_blocks_by_name[IMMEDIATE])
    while True:
        context.step()
