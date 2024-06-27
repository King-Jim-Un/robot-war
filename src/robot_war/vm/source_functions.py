from dataclasses import dataclass, field
import logging
from typing import Dict, Any, Optional, List, Callable, Tuple

from robot_war.vm.instructions import CodeLine

try:
    from robot_war.vm.exec_context import FunctionContext, SandBox
    from robot_war.vm.source_module import Module
except ImportError:
    Module = FunctionContext = Sandbox = None  # type: ignore

# Types:
CodeDict = Dict[str, "CodeBlock"]

# Constants:
LOG = logging.getLogger(__name__)


@dataclass(repr=False)
class CodeBlock:
    code_lines: Dict[int, CodeLine] = field(default_factory=dict)
    module: Optional[Module] = None
    num_params: int = 0
    param_names: List[str] = field(default_factory=list)
    constants: Dict[int, Any] = field(default_factory=dict)

    def __repr__(self):
        module_name = None if self.module is None else self.module.name
        return f"CodeBlock(module={module_name}, {len(self.code_lines)} lines, {len(self.constants)} constants)"


# The following code gives us a fancy way to create a function from byte codes on-the-fly. It works like this:
#
# with Function("foo", ["arg1", "arg2"]) as foo:
#     foo.LOAD_CONSTANT("bar")
#     foo.LOAD_FAST("arg1")
#     foo.LOAD_FAST("arg2")
#     foo.CALL_FUNCTION(2)
#     foo.RETURN_VALUE()
#
# That makes function foo which will accept arg1 and arg2, and will call function bas with them before returning the
# result.

@dataclass
class ConstMember:
    """Used below to add LOAD_CONST to the function creator"""
    function: "Function"
    name: str

    def __call__(self, note: str, label: Optional[str] = None) -> int:
        from robot_war.vm.exec_context import CODE_STEP
        from robot_war.vm.instructions.op_code_dict import OP_CODE_CLASSES
        code_lines = self.function.code_block.code_lines
        offset = len(code_lines) * CODE_STEP
        if note not in self.function.constants:
            self.function.constants.append(note)
        instr_class = OP_CODE_CLASSES[self.name]
        code_lines[offset] = instr_class(None, offset, self.name, self.function.constants.index(note), note)
        if label:
            self.function.labels[label] = offset
        return offset


@dataclass
class FastMember:
    """Used below to add LOAD_FAST to the function creator"""
    function: "Function"
    name: str

    def __call__(self, fast: str, label: Optional[str] = None) -> int:
        from robot_war.vm.exec_context import CODE_STEP
        from robot_war.vm.instructions.op_code_dict import OP_CODE_CLASSES
        code_lines = self.function.code_block.code_lines
        offset = len(code_lines) * CODE_STEP
        if fast not in self.function.arg_names:
            self.function.arg_names.append(fast)
        instr_class = OP_CODE_CLASSES[self.name]
        code_lines[offset] = instr_class(None, offset, self.name, self.function.arg_names.index(fast), fast)
        if label:
            self.function.labels[label] = offset
        return offset


@dataclass
class NoteMember:
    """Used below to add LOAD_NAME and LOAD_MODULE_FILE_3 to the function creator"""
    function: "Function"
    name: str

    def __call__(self, note: str, label: Optional[str] = None) -> int:
        from robot_war.vm.exec_context import CODE_STEP
        from robot_war.vm.instructions.op_code_dict import OP_CODE_CLASSES
        code_lines = self.function.code_block.code_lines
        offset = len(code_lines) * CODE_STEP
        instr_class = OP_CODE_CLASSES[self.name]
        code_lines[offset] = instr_class(None, offset, self.name, 0, note)
        if label:
            self.function.labels[label] = offset
        return offset


@dataclass
class RelativeMember:
    """Used below to add POP_JUMP_IF_FALSE to the function creator"""
    function: "Function"
    name: str

    def __call__(self, target: str, label: Optional[str] = None, offset: Optional[int] = None) -> int:
        from robot_war.vm.exec_context import CODE_STEP
        from robot_war.vm.instructions.op_code_dict import OP_CODE_CLASSES
        code_lines = self.function.code_block.code_lines
        if offset is None:
            offset = len(code_lines) * CODE_STEP
        instr_class = OP_CODE_CLASSES[self.name]
        code_lines[offset] = instr_class(None, offset, self.name, self.function.labels.get(target, 0), target)
        if target not in self.function.labels:
            self.function.redo.append((offset, self, target))
        if label:
            self.function.labels[label] = offset
        return offset


@dataclass
class OperandMember:
    """
    Used below to add the following to the function creator:
        BUILD_LIST, BUILD_TUPLE, CALL_FUNCTION, CALL_FUNCTION_KW, LOAD_MODULE_FILE_1, LOAD_MODULE_FILE_2, LOAD_SUBSCR,
        POP_TOP, RAISE_VARARGS, and RETURN_VALUE
    """
    function: "Function"
    name: str

    def __call__(self, operand: int = 0, label: Optional[str] = None) -> int:
        from robot_war.vm.exec_context import CODE_STEP
        from robot_war.vm.instructions.op_code_dict import OP_CODE_CLASSES
        code_lines = self.function.code_block.code_lines
        offset = len(code_lines) * CODE_STEP
        instr_class = OP_CODE_CLASSES[self.name]
        code_lines[offset] = instr_class(None, offset, self.name, operand, None)
        return offset


@dataclass
class Function:
    name: str
    arg_names: List[str] = field(default_factory=list)
    code_block: CodeBlock = field(default_factory=CodeBlock)
    default_args: tuple = ()
    closure: tuple = ()
    constants: List[str] = field(default_factory=list)
    labels: Dict[str, int] = field(default_factory=dict)
    redo: List[Tuple[int, Callable, str]] = field(default_factory=list)
    arguments: Dict[str, Any] = field(default_factory=dict)

    def add_const_member(self, name: str):
        """Used below to add LOAD_CONST to the function creator"""
        setattr(self, name, ConstMember(self, name))

    def add_fast_member(self, name: str):
        """Used below to add LOAD_FAST to the function creator"""
        setattr(self, name, FastMember(self, name))

    def add_note_member(self, name: str):
        """Used below to add LOAD_NAME and LOAD_MODULE_FILE_3 to the function creator"""
        setattr(self, name, NoteMember(self, name))

    def add_operand_member(self, name: str):
        """
        Used below to add the following to the function creator:
            BUILD_LIST, BUILD_TUPLE, CALL_FUNCTION, CALL_FUNCTION_KW, LOAD_MODULE_FILE_1, LOAD_MODULE_FILE_2,
            LOAD_SUBSCR, POP_TOP, RAISE_VARARGS, and RETURN_VALUE
        """
        setattr(self, name, OperandMember(self, name))

    def add_absolute_branch(self, name: str):
        """Used below to add POP_JUMP_IF_FALSE to the function creator"""
        setattr(self, name, RelativeMember(self, name))

    # Function creator gizmo
    def __enter__(self):
        self.add_const_member("LOAD_CONST")
        self.add_fast_member("LOAD_FAST")
        self.add_note_member("LOAD_NAME")
        self.add_note_member("LOAD_MODULE_FILE_3")
        self.add_absolute_branch("POP_JUMP_IF_FALSE")
        for name in ["BUILD_LIST", "BUILD_TUPLE", "CALL_FUNCTION", "CALL_FUNCTION_KW", "LOAD_MODULE_FILE_1",
                     "LOAD_MODULE_FILE_2", "LOAD_SUBSCR", "POP_TOP", "RAISE_VARARGS", "RETURN_VALUE"]:
            self.add_operand_member(name)
        self.code_block.num_params = len(self.arg_names)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for offset, func, target in self.redo:
            func(target, offset=offset)

    def function_context(self, source_class, *args) -> FunctionContext:
        """Create a context for executing this function"""
        from robot_war.vm.exec_context import FunctionContext
        return FunctionContext(self, {index: arg for index, arg in enumerate(args)}, source_class)

    def call_in_sandbox(self, sandbox: "SandBox"):
        self.arg_names = list(self.arguments.keys())
        sandbox.call_function(self, *tuple(self.arguments.values()))
