"""Parse a source file into a module"""

from dis import dis
from io import StringIO
import logging
import re

from robot_war.source_module import Module
import robot_war.user_functions as uf
from robot_war.exec_context import SandBox, NameDict

# Constants:
LOG = logging.getLogger(__name__)
IMMEDIATE = "IMMEDIATE"
LINE_SEARCH = re.compile(r"(\d*)\s+(\d+)\s(\w+)\s*(\d*)\s*(.*)")
DISASSEMBLY_SEARCH = re.compile("Disassembly of (<.*>):")
OpCodeClasses = {
    "BUILD_CONST_KEY_MAP": uf.BuildConstKeyMap, "CALL_FUNCTION": uf.CallFunction, "CALL_METHOD": uf.CallMethod,
    "COMPARE_OP": uf.CompareOp, "IMPORT_FROM": uf.ImportFrom, "IMPORT_NAME": uf.ImportName, "LOAD_ATTR": uf.LoadAttr,
    "LOAD_BUILD_CLASS": uf.LoadBuildClass, "LOAD_CONST": uf.LoadConst, "LOAD_FAST": uf.LoadFast,
    "LOAD_METHOD": uf.LoadMethod, "LOAD_NAME": uf.LoadName, "MAKE_FUNCTION": uf.MakeFunction,
    "POP_JUMP_IF_FALSE": uf.PopJumpIfFalse, "POP_TOP": uf.PopTop, "RETURN_VALUE": uf.ReturnValue,
    "SETUP_ANNOTATIONS": uf.SetupAnnotations, "STORE_ATTR": uf.StoreAttr, "STORE_NAME": uf.StoreName,
    "STORE_SUBSCR": uf.StoreSubscript
}


def parse_source_file(sandbox: SandBox, name: str, filename: str) -> Module:
    # Load source file
    with open(filename, "rt") as file_obj:
        source = file_obj.read()

    # Disassemble source
    temp = StringIO()
    dis(source, file=temp)
    print(temp.getvalue())

    # Extract code blocks
    module = Module(name)
    Module.all_modules[name] = module
    module.code_blocks_by_name[IMMEDIATE] = uf.CodeBlock(module)
    current_code_block = module.code_blocks_by_name[IMMEDIATE]
    for line in temp.getvalue().split("\n"):
        match = DISASSEMBLY_SEARCH.search(line)
        if match:
            # New code block
            block_name = match.group(1)
            module.code_blocks_by_name[block_name] = uf.CodeBlock(module)
            current_code_block = module.code_blocks_by_name[block_name]
        else:
            match = LINE_SEARCH.search(line)
            if match:
                # Code line
                line_number, offset, op_code, operand, note = match.groups()
                line_class = OpCodeClasses[op_code]
                code_line = line_class(int(line_number) if line_number else None, int(offset), op_code,
                                       int(operand) if operand else None, note[1:-1] if note else None)
                current_code_block.code_lines[int(offset)] = code_line

    # Populate some built-ins
    name_dict: NameDict = {}
    sandbox.name_dict_by_module_name[name] = name_dict
    name_to_index_dict = module.code_blocks_by_name[IMMEDIATE].init_name_to_index_dict(name_dict)
    if "__name__" in name_to_index_dict:
        # Yes, save it
        name_dict[name_to_index_dict["__name__"]] = name

    return module
