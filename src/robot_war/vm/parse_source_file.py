"""Parse a source file into a module"""

from dis import get_instructions, code_info
import logging
from pathlib import Path
import re
from typing import Optional

from robot_war.vm.built_ins import BUILT_INS
from robot_war.vm.instructions import classes, data, flow_control, imports, math, misc
from robot_war.vm.exec_context import SandBox
from robot_war.vm.source_functions import CodeBlock
from robot_war.vm.source_module import Module

# Constants:
LOG = logging.getLogger(__name__)
CODE_CLASS = compile("0", "", "eval").__class__  # There's gotta be a better way!
SEARCH_NUM_ARGS = re.compile(r"^Argument count:\s+(\d+)", re.MULTILINE)
SEARCH_VAR_NAMES1 = re.compile(r"^Variable names:(.*)", re.MULTILINE | re.DOTALL)
SEARCH_VAR_NAMES2 = re.compile(r"(.*?)^\S", re.MULTILINE | re.DOTALL)
SEARCH_VAR_NAMES3 = re.compile(r"(\d+): (\w+)")
OP_CODE_CLASSES = {
    "BINARY_ADD": math.BinaryAdd,
    "BINARY_MULTIPLY": math.BinaryMultiply,
    "BINARY_SLICE": data.BinarySlice,
    "BINARY_SUBSCR": data.BinarySubscript,
    "BUILD_CONST_KEY_MAP": data.BuildConstKeyMap,
    "BUILD_LIST": data.BuildList,
    "BUILD_SET": data.BuildSet,
    "BUILD_STRING": data.BuildString,
    "BUILD_TUPLE": data.BuildTuple,
    "CALL_FUNCTION": flow_control.CallFunction,
    "CALL_FUNCTION_KW": flow_control.CallFunctionKW,
    "CALL_METHOD": flow_control.CallMethod,
    "COMPARE_OP": data.CompareOperand,
    "CONTAINS_OP": math.ContainsOperand,
    "COPY": data.Copy,
    "DELETE_FAST": data.DeleteFast,
    "DELETE_GLOBAL": data.DeleteGlobal,
    "DELETE_SUBSCR": data.DeleteSubscript,
    "IMPORT_FROM": imports.ImportFrom,
    "IMPORT_NAME": imports.ImportName,
    "IS_OP": math.IsOperand,
    "JUMP_BACKWARD": flow_control.JumpBackward,
    "JUMP_FORWARD": flow_control.JumpForward,
    "LOAD_ATTR": classes.LoadAttribute,
    "LOAD_BUILD_CLASS": classes.LoadBuildClass,
    "LOAD_CLOSURE": data.LoadClosure,
    "LOAD_CONST": data.LoadConstant,
    "LOAD_DEREF": data.LoadDeref,
    "LOAD_FAST": data.LoadFast,
    "LOAD_GLOBAL": data.LoadGlobal,
    "LOAD_METHOD": classes.LoadMethod,
    "LOAD_NAME": classes.LoadName,
    "LOAD_SUBSCR": data.LoadSubscript,
    "MAKE_FUNCTION": classes.MakeFunction,
    "NOP": misc.Nop,
    "POP_JUMP_IF_FALSE": flow_control.PopJumpIfFalse,
    "POP_JUMP_IF_NONE": flow_control.PopJumpIfNone,
    "POP_JUMP_IF_NOT_NONE": flow_control.PopJumpIfNotNone,
    "POP_JUMP_IF_TRUE": flow_control.PopJumpIfTrue,
    "POP_TOP": data.PopTop,
    "RAISE_VARARGS": flow_control.RaiseVarArgs,
    "RESUME": misc.Nop,
    "RETURN_VALUE": flow_control.ReturnValue,
    "SETUP_ANNOTATIONS": classes.SetupAnnotations,
    "STORE_ATTR": classes.StoreAttribute,
    "STORE_DEREF": data.StoreDeref,
    "STORE_FAST": data.StoreFast,
    "STORE_GLOBAL": data.StoreGlobal,
    "STORE_NAME": classes.StoreName,
    "STORE_SUBSCR": data.StoreSubscript,
    "SWAP": data.Swap,
    "UNARY_INVERT": math.UnaryInvert,
    "UNARY_NEGATIVE": math.UnaryNegative,
    "UNARY_NOT": math.UnaryNot
}


def code_to_codeblock(path: Path, code: CODE_CLASS, sandbox: SandBox, module_dot_name: str,
                      module: Optional[Module] = None) -> CodeBlock:
    code_block = CodeBlock()
    sandbox.playground.code_blocks_by_name[str(code)] = code_block
    if module is None:
        module = Module(module_dot_name, code_block, name_dict=dict(BUILT_INS), path=path,
                        dot_path=module_dot_name.split("."))
        module.name_dict["__name__"] = module_dot_name
        sandbox.playground.all_modules[module_dot_name] = module
    code_block.module = module

    # Add instructions
    for instr in get_instructions(code):
        line_class = OP_CODE_CLASSES[instr.opname]
        instr_obj = line_class(instr.starts_line, instr.offset, instr.opname, instr.arg, instr.argrepr)
        code_block.code_lines[instr.offset] = instr_obj

    # Number of arguments
    info_str = code_info(code)
    match = SEARCH_NUM_ARGS.search(info_str)
    assert match
    code_block.num_params = int(match.group(1))

    # Argument names
    match = SEARCH_VAR_NAMES1.search(info_str)
    if match:
        var_name_str = match.group(1)
        match = SEARCH_VAR_NAMES2.search(var_name_str)
        if match:
            var_name_str = match.group(1)
        var_name_dict = {int(index): name for index, name in SEARCH_VAR_NAMES3.findall(var_name_str)}
        code_block.param_names = [var_name_dict[index] for index in range(code_block.num_params)]

    # Grab other code blocks
    for constant in code.co_consts:
        if isinstance(constant, CODE_CLASS):
            code_to_codeblock(path, constant, sandbox, module_dot_name, module)

    return code_block


def parse_source_file(sandbox: SandBox, module_dot_name: str, file_path: Path) -> CodeBlock:
    # Load source file
    with file_path.open("rt") as file_obj:
        source = file_obj.read()

    # Compile the source
    return code_to_codeblock(file_path, compile(source, str(file_obj), "exec"), sandbox, module_dot_name)
