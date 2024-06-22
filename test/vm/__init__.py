from contextlib import contextmanager
from dis import dis
from inspect import getsource
from io import StringIO
import logging
import re
from subprocess import check_output
import sys
from typing import Optional, List, Callable, Dict, Any

from robot_war.constants import CONSTANTS
from robot_war.exceptions import ReturnException
from robot_war.vm.built_ins import BUILT_INS
from robot_war.vm.exec_context import SandBox, Playground
from robot_war.vm.source_functions import Function
from robot_war.vm.source_module import Module
from test import conftest

# Constants:
LOG = logging.getLogger(__name__)
SEARCH_DECORATOR1 = re.compile(r"^@compare_in_vm.*?def", re.DOTALL | re.MULTILINE)
SEARCH_DECORATOR2 = re.compile(r"^@run_in_vm.*?def", re.DOTALL | re.MULTILINE)


@contextmanager
def capture_stdout():
    old_stdout = sys.stdout
    try:
        capture = StringIO()
        sys.stdout = capture
        yield capture
    finally:
        sys.stdout = old_stdout


def compare_in_vm(function1=None, functions: Optional[List[Callable]] = None, global_vars: Optional[Dict[str, Any]] = None):
    module = Module("module", name_dict=dict(BUILT_INS))
    if global_vars:
        module.name_dict.update(global_vars)
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
                                                    replace=(SEARCH_DECORATOR1, "def")))
        with capture_stdout() as vm_io:
            vm_return = execute(module.get_name(function1.__name__))
        with capture_stdout() as standard_io:
            standard_return = function1()
        assert standard_return == vm_return
        LOG.debug("s=%r", standard_io.getvalue())
        LOG.debug("v=%r", vm_io.getvalue())
        assert standard_io.getvalue() == vm_io.getvalue()
        if not conftest.G_CALLED_FROM_TEST:
            sys.stdout.write(vm_io.getvalue())

    if isinstance(function1, list):
        return lambda function3: compare_in_vm(function3, function1)
    elif function1 is None:
        return lambda function4: compare_in_vm(function4, global_vars=global_vars)
    else:
        return wrapper


def run_in_vm(function1, functions: Optional[List[Callable]] = None):
    module = Module("module", name_dict=dict(BUILT_INS))
    sandbox = SandBox(None)  # noqa
    if functions is None:
        functions = []

    def wrapper():
        module.add_standard_python_function(
            function1, *functions, replace=(SEARCH_DECORATOR2, "def"))
        sandbox.call_function(module.get_name(function1.__name__))

        try:
            sandbox.exec_through()
        except ReturnException as ret:
            return ret.value

    if isinstance(function1, list):
        return lambda function3: run_in_vm(function3, function1)
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


def compare_external(base_module: str, args: List[str]):
    base_path = CONSTANTS.PATHS.TEST.EXTERNALS / f"{base_module}.py"
    playground = Playground(CONSTANTS.PATHS.TEST.EXTERNALS)
    sys_mod = Module("sys", name_dict={"argv": [None] + args})
    module = Module("__main__", name_dict=dict(BUILT_INS), path=base_path)
    playground.all_modules = {"__main__": module, "sys": sys_mod}
    sandbox = SandBox(playground)
    playground.sandboxes = [sandbox]
    sandbox.call_function(module.read_source_file(base_path))
    try:
        with capture_stdout() as vm_io:
            sandbox.exec_through()
    except ReturnException:
        pass
    standard_io = check_output([sys.executable, base_path] + args, text=True)
    assert standard_io == vm_io.getvalue()
    if not conftest.G_CALLED_FROM_TEST:
        sys.stdout.write(vm_io.getvalue())
