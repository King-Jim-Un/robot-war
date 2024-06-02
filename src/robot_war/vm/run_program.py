from pathlib import Path

from robot_war.exceptions import RobotWarSystemExit
from robot_war.vm.built_ins import BUILT_INS
from robot_war.vm.exec_context import SandBox
from robot_war.vm.instructions.classes import LoadName
from robot_war.vm.instructions.data import BuildList, LoadConst, BuildTuple, LoadFast, PopTop
from robot_war.vm.instructions.flow_control import CallFunction, RaiseVarArgs
from robot_war.vm.instructions.imports import LoadModuleFile1
from robot_war.vm.source_functions import Function, CodeBlock
from robot_war.vm.source_module import Module


def run_program(source_file: Path) -> SandBox:
    code_block = CodeBlock({
        # LOAD_MODULE_FILE_1 wants two parameters: and empty module list, and a tuple of (module_name, source_path)
        0: BuildList(None, 0, "BUILD_LIST", 0, None),
        2: LoadConst(None, 2, "LOAD_CONST", 0, "'__main__'"),
        4: LoadFast(None, 4, "LOAD_FAST", 0, "source_file"),
        6: BuildTuple(None, 6, "BUILD_TUPLE", 2, None),
        # Load module
        8: LoadModuleFile1(None, 8, "LOAD_MODULE_FILE_1", 0, None),  # Load module (opcode that compile won't generate)
        # Discard module list
        10: PopTop(None, 10, "POP_TOP", 0, None),  # Discard list of modules
        # Instantiate a SystemExit(0) exception
        12: LoadName(None, 12, "LOAD_NAME", 0, "SystemExit"),
        14: LoadConst(None, 14, "LOAD_CONST", 1, "0"),
        16: CallFunction(None, 16, "CALL_FUNCTION", 1, None),
        # Raise exception
        18: RaiseVarArgs(None, 18, "RAISE_VARARGS", 1, None)  # Raise exception
    }, num_params=1)
    code_block.module = Module("__main_launcher__", code_block, name_dict=dict(BUILT_INS))
    sandbox = SandBox(source_file.parent)
    sandbox.call_function(Function("__run_program__", code_block), source_file)  # DO NOT SAVE FUNCTION IN NAMES
    return sandbox


def exec_through(sandbox: SandBox) -> int:
    try:
        while True:
            sandbox.step()
    except RobotWarSystemExit as rc:
        return rc.return_code
