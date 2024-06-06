"""Parse a source file into a module"""

import logging
from pathlib import Path

from robot_war.vm.instructions import classes, data, flow_control, imports, math, misc
from robot_war.vm.exec_context import SandBox
from robot_war.vm.source_functions import CodeBlock

# Constants:
LOG = logging.getLogger(__name__)
OP_CODE_CLASSES = {
    "BINARY_ADD": math.BinaryAdd,
    "BINARY_MULTIPLY": math.BinaryMultiply,
    "BINARY_SUBTRACT": math.BinarySubtract,
    "BINARY_FLOOR_DIVIDE": math.BinaryFloorDivide,
    "BINARY_TRUE_DIVIDE": math.BinaryTrueDivide,
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


def parse_source_file(sandbox: SandBox, module_dot_name: str, file_path: Path) -> CodeBlock:
    # Load source file
    with file_path.open("rt") as file_obj:
        source = file_obj.read()

    # Compile the source
    return code_to_codeblock(file_path, compile(source, str(file_obj), "exec"), sandbox, module_dot_name)
