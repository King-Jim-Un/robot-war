"""Parse a source file into a module"""

from dis import get_instructions, code_info
import logging
from pathlib import Path
import re

from robot_war.built_ins import BUILT_INS
from robot_war.source_functions import CodeBlock
from robot_war.source_module import Module
from robot_war.instructions import classes, data, flow_control, imports
from robot_war.exec_context import SandBox

# Constants:
LOG = logging.getLogger(__name__)
CodeClass = compile("0", "", "eval").__class__  # There's gotta be a better way!
SearchNumArgs = re.compile(r"^Argument count:\s+(\d+)", re.MULTILINE)
OpCodeClasses = {
    "BINARY_ADD": data.BinaryAdd,
    "BINARY_MULTIPLY": data.BinaryMultiply,
    "BUILD_CONST_KEY_MAP": data.BuildConstKeyMap,
    "BUILD_LIST": data.BuildList,
    "BUILD_TUPLE": data.BuildTuple,
    "CALL_FUNCTION": flow_control.CallFunction,
    "CALL_METHOD": flow_control.CallMethod,
    "COMPARE_OP": data.CompareOp,
    "IMPORT_FROM": imports.ImportFrom,
    "IMPORT_NAME": imports.ImportName,
    "LOAD_ATTR": classes.LoadAttr,
    "LOAD_BUILD_CLASS": classes.LoadBuildClass,
    "LOAD_CLOSURE": data.LoadClosure,
    "LOAD_CONST": data.LoadConst,
    "LOAD_DEREF": data.LoadDeref,
    "LOAD_FAST": data.LoadFast,
    "LOAD_GLOBAL": data.LoadGlobal,
    "LOAD_METHOD": classes.LoadMethod,
    "LOAD_NAME": classes.LoadName,
    "LOAD_SUBSCR": data.LoadSubscript,
    "MAKE_FUNCTION": classes.MakeFunction,
    "POP_JUMP_IF_FALSE": flow_control.PopJumpIfFalse,
    "POP_TOP": data.PopTop,
    "RAISE_VARARGS": flow_control.RaiseVarArgs,
    "RETURN_VALUE": flow_control.ReturnValue,
    "SETUP_ANNOTATIONS": classes.SetupAnnotations,
    "STORE_ATTR": classes.StoreAttr,
    "STORE_DEREF": data.StoreDeref,
    "STORE_FAST": data.StoreFast,
    "STORE_NAME": classes.StoreName,
    "STORE_SUBSCR": data.StoreSubscript
}


def code_to_codeblock(code: CodeClass) -> CodeBlock:
    code_block = CodeBlock()

    # Add instructions
    for instruction in get_instructions(code):
        line_class = OpCodeClasses[instruction.opname]
        code_block.code_lines[instruction.offset] = line_class(instruction.starts_line, instruction.offset,
                                                               instruction.opname, instruction.arg, instruction.argrepr)

    # Number of arguments
    match = SearchNumArgs.search(code_info(code))
    assert match
    code_block.num_params = int(match.group(1))

    return code_block


def parse_source_file(sandbox: SandBox, module_name: str, file_path: Path) -> CodeBlock:
    # Load source file
    with file_path.open("rt") as file_obj:
        source = file_obj.read()

    # Compile the source
    compiled = compile(source, str(file_obj), "exec")
    initial_code_block = code_to_codeblock(compiled)
    module = Module(module_name, initial_code_block, name_dict=dict(BUILT_INS))
    initial_code_block.module = module
    module.name_dict["__name__"] = module_name
    sandbox.all_modules[module_name] = module

    # Grab other code blocks
    for constant in compiled.co_consts:
        if isinstance(constant, CodeClass):
            code_block = code_to_codeblock(constant)
            code_block.module = module
            sandbox.code_blocks_by_name[str(constant)] = code_block

    return initial_code_block
