import logging
from pathlib import Path
import re
from typing import Optional, List, Callable

from robot_war.vm.built_ins import BUILT_INS
from robot_war.vm.exec_context import SandBox, Playground
from robot_war.vm.source_module import Module

# Constants:
LOG = logging.getLogger(__name__)
SEARCH_DECORATOR1 = re.compile(r"^@run_in_vm.*?def", re.DOTALL | re.MULTILINE)


def run_in_vm(function1, functions: Optional[List[Callable]] = None):
    module = Module("module", name_dict=dict(BUILT_INS))
    playground = Playground(Path("."))
    sandbox = SandBox(playground)
    playground.sandboxes = [sandbox]
    if functions is None:
        functions = []

    def wrapper():
        module.add_standard_python_function(
            function1, *functions, replace=(SEARCH_DECORATOR1, "def"))
        sandbox.call_function(module.get_name(function1.__name__))

        # while not sandbox.done:
        while playground.sandboxes or playground.workers:
            playground.step_all()

    if isinstance(function1, list):
        return lambda function2: run_in_vm(function2, function1)
    else:
        return wrapper
