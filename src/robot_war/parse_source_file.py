"""Parse a source file into a module"""

from dis import get_instructions, code_info
import logging
from pathlib import Path
import re
from typing import Optional, Tuple

from robot_war.built_ins import BUILT_INS
from robot_war.source_functions import CodeBlock
from robot_war.source_module import Module
from robot_war.instructions import classes, data, flow_control, imports
from robot_war.exec_context import SandBox

# Constants:
LOG = logging.getLogger(__name__)
CodeClass = compile("0", "", "eval").__class__  # There's gotta be a better way!
SearchNumArgs = re.compile(r"^Argument count:\s+(\d+)", re.MULTILINE)
SearchVarNames1 = re.compile(r"^Variable names:(.*)", re.MULTILINE | re.DOTALL)
SearchVarNames2 = re.compile(r"(.*?)^\S", re.MULTILINE | re.DOTALL)
SearchVarNames3 = re.compile(r"(\d+): (\w+)")
OpCodeClasses = {
    "BINARY_ADD": data.BinaryAdd,
    "BINARY_MULTIPLY": data.BinaryMultiply,
    "BUILD_CONST_KEY_MAP": data.BuildConstKeyMap,
    "BUILD_LIST": data.BuildList,
    "BUILD_TUPLE": data.BuildTuple,
    "CALL_FUNCTION": flow_control.CallFunction,
    "CALL_FUNCTION_KW": flow_control.CallFunctionKW,
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


def code_to_codeblock(code: CodeClass, sandbox: SandBox, module_name: str,
                      module: Optional[Module] = None) -> CodeBlock:
    code_block = CodeBlock()
    sandbox.code_blocks_by_name[str(code)] = code_block
    if module is None:
        module = Module(module_name, code_block, name_dict=dict(BUILT_INS))
        module.name_dict["__name__"] = module_name
        sandbox.all_modules[module_name] = module
    code_block.module = module

    # Add instructions
    for instr in get_instructions(code):
        line_class = OpCodeClasses[instr.opname]
        instr_obj = line_class(instr.starts_line, instr.offset, instr.opname, instr.arg, instr.argrepr)
        code_block.code_lines[instr.offset] = instr_obj

    # Number of arguments
    info_str = code_info(code)
    match = SearchNumArgs.search(info_str)
    assert match
    code_block.num_params = int(match.group(1))

    # Argument names
    match = SearchVarNames1.search(info_str)
    if match:
        var_name_str = match.group(1)
        match = SearchVarNames2.search(var_name_str)
        if match:
            var_name_str = match.group(1)
        var_name_dict = {int(index): name for index, name in SearchVarNames3.findall(var_name_str)}
        code_block.param_names = [var_name_dict[index] for index in range(code_block.num_params)]

    # Grab other code blocks
    for constant in code.co_consts:
        if isinstance(constant, CodeClass):
            code_to_codeblock(constant, sandbox, module_name, module)

    return code_block


def parse_source_file(sandbox: SandBox, module_name: str, file_path: Path) -> CodeBlock:
    # Load source file
    with file_path.open("rt") as file_obj:
        source = file_obj.read()


    from dis import dis  # TODO: remove
    dis(source)


    # Compile the source
    return code_to_codeblock(compile(source, str(file_obj), "exec"), sandbox, module_name)
