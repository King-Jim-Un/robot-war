import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Any, Dict, Optional

from robot_war.instructions.flow_control import ReturnException
from robot_war.source_functions import CodeDict, Function
from robot_war.source_module import Module

# Types:
NameDict = Dict[str, Any]

# Constants:
LOG = logging.getLogger(__name__)
CODE_STEP = 2


@dataclass
class FunctionContext:
    function: Function
    fast_stack: Dict[int, Any] = field(default_factory=dict)
    data_stack: List[Any] = field(default_factory=list)
    pc: int = 0


@dataclass
class SandBox:
    root_path: Path
    all_modules: Dict[str, Module] = field(default_factory=dict)
    code_blocks_by_name: CodeDict = field(default_factory=dict)
    call_stack: List[FunctionContext] = field(default_factory=list)
    api: Optional[Module] = None

    @property
    def context(self) -> FunctionContext:
        return self.call_stack[-1]

    def call_function(self, function, *args, **kwargs):
        if isinstance(function, Function):
            assert not kwargs, "TODO: kwargs"
            fast_stack = {index: value for index, value in enumerate(args + function.closure)}
            self.call_stack.append(FunctionContext(function, fast_stack))
        else:
            self.push(function(*args, **kwargs))

    def step(self):
        try:
            context = self.context
            context.function.code_block.code_lines[context.pc].exec(self)
        except ReturnException as rc:
            logging.debug("stack depth = %d", len(self.call_stack.pop().data_stack))
            if self.call_stack:
                self.push(rc.value)
            else:
                raise

    def next(self):
        self.context.pc += CODE_STEP

    def peek(self, offset: int):
        return self.context.data_stack[offset]

    def pop(self):
        return self.context.data_stack.pop()

    def push(self, value):
        return self.context.data_stack.append(value)
