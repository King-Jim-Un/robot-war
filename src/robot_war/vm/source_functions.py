from dataclasses import dataclass, field
import logging
from typing import Dict, Any, Optional, List

from robot_war.vm.instructions import CodeLine

try:
    from robot_war.vm.exec_context import FunctionContext
    from robot_war.vm.source_module import Module
except ImportError:
    Module = FunctionContext = None

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


@dataclass
class ConstMember:
    function: "Function"
    name: str

    def __call__(self, note: str):
        from robot_war.vm.exec_context import CODE_STEP
        from robot_war.vm.parse_source_file import OP_CODE_CLASSES
        code_lines = self.function.code_block.code_lines
        offset = len(code_lines) * CODE_STEP
        if note not in self.function.constants:
            self.function.constants.append(note)
        instr_class = OP_CODE_CLASSES[self.name]
        code_lines[offset] = instr_class(None, offset, self.name, self.function.constants.index(note), note)
        return offset


@dataclass
class FastMember:
    function: "Function"
    name: str

    def __call__(self, fast: str) -> int:
        from robot_war.vm.exec_context import CODE_STEP
        from robot_war.vm.parse_source_file import OP_CODE_CLASSES
        code_lines = self.function.code_block.code_lines
        offset = len(code_lines) * CODE_STEP
        if fast not in self.function.arg_names:
            self.function.arg_names.append(fast)
        instr_class = OP_CODE_CLASSES[self.name]
        code_lines[offset] = instr_class(None, offset, self.name, self.function.arg_names.index(fast), fast)
        return offset


@dataclass
class NoteMember:
    function: "Function"
    name: str

    def __call__(self, note: str) -> int:
        from robot_war.vm.exec_context import CODE_STEP
        from robot_war.vm.parse_source_file import OP_CODE_CLASSES
        code_lines = self.function.code_block.code_lines
        offset = len(code_lines) * CODE_STEP
        instr_class = OP_CODE_CLASSES[self.name]
        code_lines[offset] = instr_class(None, offset, self.name, 0, note)
        return offset


@dataclass
class OperandMember:
    function: "Function"
    name: str

    def __call__(self, operand: int = 0) -> int:
        from robot_war.vm.exec_context import CODE_STEP
        from robot_war.vm.parse_source_file import OP_CODE_CLASSES
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
    closure: tuple = ()
    default_args: tuple = ()
    constants: List[str] = field(default_factory=list)

    def add_const_member(self, name: str):
        setattr(self, name, ConstMember(self, name))

    def add_fast_member(self, name: str):
        setattr(self, name, FastMember(self, name))

    def add_note_member(self, name: str):
        setattr(self, name, NoteMember(self, name))

    def add_operand_member(self, name: str):
        setattr(self, name, OperandMember(self, name))

    def __enter__(self):
        self.add_const_member("LOAD_CONST")
        self.add_fast_member("LOAD_FAST")
        self.add_note_member("LOAD_NAME")
        for name in ["BUILD_LIST", "BUILD_TUPLE", "CALL_FUNCTION", "LOAD_MODULE_FILE_1", "LOAD_MODULE_FILE_2",
                     "LOAD_SUBSCR", "POP_TOP", "RAISE_VARARGS", "RETURN_VALUE"]:
            self.add_operand_member(name)
        self.code_block.num_params = len(self.arg_names)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def function_context(self, source_class, *args) -> FunctionContext:
        from robot_war.vm.exec_context import FunctionContext
        return FunctionContext(self, {index: arg for index, arg in enumerate(args)}, source_class)
