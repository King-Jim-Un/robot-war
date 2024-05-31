"""Parse a source file into a module"""

from dis import dis
from io import StringIO
import logging
import os
from pathlib import Path
import re

from robot_war.built_ins import BUILT_INS
from robot_war.source_functions import CodeBlock
from robot_war.source_module import Module
from robot_war.instructions import classes, data, flow_control, imports
from robot_war.exec_context import SandBox

# Constants:
LOG = logging.getLogger(__name__)
IMMEDIATE = "IMMEDIATE"
LINE_SEARCH = re.compile(r"(\d*)\s+(\d+)\s(\w+)\s*(\d*)\s*(.*)")
DISASSEMBLY_SEARCH = re.compile("Disassembly of (<.*>):")
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


def parse_source_file(sandbox: SandBox, module_name: str, file_path: Path) -> CodeBlock:
    # Load source file
    with file_path.open("rt") as file_obj:
        source = file_obj.read()

    # Disassemble source
    string_file = StringIO()
    dis(source, file=string_file)
    print(string_file.getvalue())  # TODO: remove
    string_file.seek(os.SEEK_SET, 0)

    # Create a module
    initial_code_block = current_code_block = CodeBlock()
    module = Module(module_name, current_code_block, name_dict=dict(BUILT_INS))
    current_code_block.module = module
    module.name_dict["__name__"] = module_name
    sandbox.all_modules[module_name] = module

    # Extract code blocks
    for line in string_file.readlines():
        # Look for a new block marker
        match = DISASSEMBLY_SEARCH.search(line)
        if match:
            # Found a new code block
            block_name = match.group(1)
            current_code_block = CodeBlock(module=module)
            sandbox.code_blocks_by_name[block_name] = current_code_block
        else:
            # Look for an executable instruction
            match = LINE_SEARCH.search(line)
            if match:
                # Found an instruction
                line_number, offset, op_code, operand, note = match.groups()
                line_class = OpCodeClasses[op_code]
                code_line = line_class(int(line_number) if line_number else None, int(offset), op_code,
                                       int(operand) if operand else None, note[1:-1] if note else None)
                current_code_block.code_lines[int(offset)] = code_line

    return initial_code_block
