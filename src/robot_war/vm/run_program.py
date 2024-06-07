from pathlib import Path
from typing import Optional

from robot_war.exceptions import RobotWarSystemExit
from robot_war.vm.built_ins import BUILT_INS
from robot_war.vm.exec_context import SandBox, Playground
from robot_war.vm.instructions.classes import LoadName
from robot_war.vm.instructions.data import BuildList, LoadConstant, BuildTuple, LoadFast, PopTop
from robot_war.vm.instructions.flow_control import CallFunction, RaiseVarArgs
from robot_war.vm.instructions.imports import LoadModuleFile1
from robot_war.vm.source_functions import Function, CodeBlock
from robot_war.vm.source_module import Module


def run_program(source_file: Path, sandbox: Optional[SandBox] = None) -> Optional[Playground]:
    # If a sandbox is provided, run_program() returns None. If sandbox=None, run_program() will create one and return a
    # Playground object containing it.
    with Function("__main_launcher", ["source_file"]) as launcher:
        # LOAD_MODULE_FILE_1 wants two parameters: and empty module list, and a tuple of (module_name, source_path)
        launcher.BUILD_LIST()
        launcher.LOAD_CONST("__main__")
        launcher.LOAD_FAST("source_file"),
        launcher.BUILD_TUPLE(2)
        # Load module
        launcher.LOAD_MODULE_FILE_1()  # Load module (opcode that compile won't generate)
        # Discard module list
        launcher.POP_TOP()  # Discard list of modules
        # Instantiate a SystemExit(0) exception
        launcher.LOAD_NAME("SystemExit")
        launcher.LOAD_CONST("0"),
        launcher.CALL_FUNC(1)
        # Raise exception
        launcher.RAISE_VARARGS(1)  # Raise exception
    code_block.module = Module("__main_launcher__", code_block, name_dict=dict(BUILT_INS))
    playground = None
    if sandbox is None:
        playground = Playground(source_file.parent)
        sandbox = SandBox(playground)
        playground.sandboxes = [sandbox]
    module = Module("__main__")
    sandbox.call_function(Function("__run_program__", code_block=code_block), source_file)  # DO NOT SAVE FUNCTION IN NAMES
    return playground


def exec_through(sandbox: SandBox) -> int:
    try:
        while True:
            sandbox.step()
    except RobotWarSystemExit as rc:
        return rc.return_code
