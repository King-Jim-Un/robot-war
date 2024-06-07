from dis import dis
import logging
from typing import Optional

from robot_war.exceptions import ReturnException
from robot_war.vm.exec_context import SandBox
from robot_war.vm.source_module import Module

# Constants:
LOG = logging.getLogger(__name__)


def compare_in_vm(function, module: Optional[Module] = None):
    if module is None:
        module = Module("module")

    def wrapper():
        module.add_standard_python_function(function)

        sandbox = SandBox(None)  # noqa
        sandbox.call_function(module.get_name(function.__name__))
        try:
            sandbox.exec_through()
        except ReturnException as ret:
            vm_return = ret.value
            standard_return = function()
            assert standard_return == vm_return

    if isinstance(function, list):
        for func in function:
            module.add_standard_python_function(func)
        return lambda f: compare_in_vm(f, module)
    else:
        return wrapper


def dump_func(function):
    dis(function)
    assert False
