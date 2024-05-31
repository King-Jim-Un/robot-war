import logging
from dataclasses import dataclass, field
from typing import List, Any, Dict

from robot_war.user_functions import CodeBlock, ReturnException, Function

# Types:
NameDict = Dict[int, Any]

# Constants:
LOG = logging.getLogger(__name__)
CODE_STEP = 2


@dataclass
class SandBox:
    name_dict_by_module_name: Dict[str, NameDict] = field(default_factory=dict)


@dataclass
class CodeBlockContext:
    sandbox: SandBox
    code_block: CodeBlock
    exec_context: "ExecContext"
    data_stack: List[Any] = field(default_factory=list)
    fast_stack: Dict[int, Any] = field(default_factory=dict)
    pc: int = 0

    def step(self):
        instruction = self.code_block.code_lines[self.pc]
        instruction.exec(self, self.code_block)

    def next(self):
        self.pc += CODE_STEP

    def peek(self, offset: int):
        return self.data_stack[offset]

    def pop(self):
        return self.data_stack.pop()

    def push(self, value):
        return self.data_stack.append(value)


class ExecContext:
    sandbox: SandBox
    call_stack: List[CodeBlockContext]

    def __init__(self, sandbox: SandBox, code_block):
        self.sandbox = sandbox
        self.call_stack = [CodeBlockContext(sandbox, code_block, self)]

    def call_function(self, function, *args, **kwargs):
        if isinstance(function, Function):
            assert not kwargs
            code_block = function.code_block
            name_dict: NameDict
            if code_block.module.name in self.sandbox.name_dict_by_module_name:
                name_dict = self.sandbox.name_dict_by_module_name[code_block.module.name]
            else:
                name_dict = {}
                self.sandbox.name_dict_by_module_name[code_block.module.name] = name_dict
            name_to_index_dict = code_block.init_name_to_index_dict(name_dict)
            if "__annotations__" in name_to_index_dict:
                name_dict[name_to_index_dict["__annotations__"]] = {}
            context = CodeBlockContext(self.sandbox, code_block, self)
            context.fast_stack = args
            self.call_stack.append(context)
        else:
            self.call_stack[-1].push(function(*args, **kwargs))




    def step(self):
        try:
            self.call_stack[-1].step()
        except ReturnException as rc:
            logging.debug("stack depth = %d", len(self.call_stack.pop().data_stack))
            if self.call_stack:
                self.call_stack[-1].push(rc.value)
            else:
                raise
