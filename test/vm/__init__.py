from dis import dis
import logging

from robot_war.exceptions import ReturnException
from robot_war.vm.exec_context import SandBox
from robot_war.vm.run_program import exec_through
from robot_war.vm.source_functions import CodeBlock, Function
from robot_war.vm.source_module import Module

# Constants:
LOG = logging.getLogger(__name__)


def compare_in_vm(function, module=None):
    def wrapper():
        standard_return = function()
        LOG.warning("return value in standard python: %r", standard_return)
        code_block = CodeBlock(module=module)
        code_block.set_function(function)
        sandbox = SandBox(None)
        sandbox.call_function(Function(function.__name__, code_block=code_block))
        try:
            exec_through(sandbox)
        except ReturnException as ret:
            vm_return = ret.value
        assert standard_return == vm_return

    if isinstance(function, list):
        module = Module("module")
        for func in function:
            code_block = CodeBlock(module=module)
            code_block.set_function(func)
            module.set_name(func.__name__, Function(func.__name__, code_block=code_block))
        return lambda f: compare_in_vm(f, module)
    else:
        return wrapper


def dump_func(function):
    dis(function)
    assert False
