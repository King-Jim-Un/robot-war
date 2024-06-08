from dis import dis
from inspect import getsource
import logging
import re
from typing import Optional, List

from robot_war.exceptions import ReturnException
from robot_war.vm.built_ins import BUILT_INS
from robot_war.vm.exec_context import SandBox
from robot_war.vm.source_functions import Function
from robot_war.vm.source_module import Module

# Constants:
LOG = logging.getLogger(__name__)
SEARCH_DECORATOR = re.compile(r"^@compare_in_vm.*?def", re.DOTALL | re.MULTILINE)


def compare_in_vm(function1, functions: Optional[List] = None):
    module = Module("module", name_dict=dict(BUILT_INS))
    sandbox = SandBox(None)  # noqa
    if functions is None:
        functions = []

    def execute(function2: Function):
        sandbox.call_function(function2)
        try:
            sandbox.exec_through()
        except ReturnException as ret:
            return ret.value

    def wrapper():
        execute(module.add_standard_python_function(function1, *functions,
                                                    replace=(SEARCH_DECORATOR, "def")))
        vm_return = execute(module.get_name(function1.__name__))
        standard_return = function1()
        assert standard_return == vm_return

    if isinstance(function1, list):
        return lambda function3: compare_in_vm(function3, function1)
    else:
        return wrapper


def dump_func(function):
    if isinstance(function, list):
        for func in function:
            dis(getsource(func))
        return lambda f: dump_func(f)
    else:
        dis(getsource(function))
    assert False
