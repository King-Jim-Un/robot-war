import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Any, Dict, Optional

from robot_war.built_ins import BUILT_INS
from robot_war.instructions.classes import LoadName
from robot_war.instructions.data import LoadFast, PopTop
from robot_war.instructions.flow_control import ReturnException, CallFunction, ReturnValue
from robot_war.source_class import SourceClass, SourceInstance, Constructor
from robot_war.source_functions import CodeDict, Function, CodeBlock
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
    name_dict: NameDict = field(default_factory=dict)
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

    @staticmethod
    def args_to_fast(function: Function, *args, **kwargs) -> Dict[int, Any]:
        # Initial placeholders
        arg_list = [None] * function.code_block.num_params

        # Default values
        arg_list = arg_list[:-len(function.default_args)] + list(function.default_args)

        # Specified values & closure
        arg_list = list(args) + arg_list[len(args):] + list(function.closure)

        # Keyword arguments
        for index, param_name in enumerate(function.code_block.param_names):
            if param_name in kwargs:
                arg_list[index] = kwargs[param_name]

        return {index: value for index, value in enumerate(arg_list)}

    def call_function(self, function, *args, **kwargs):
        if isinstance(function, SourceClass):
            # Calling a class as a function instantiates an object
            name_dict = {"__name__": function.function.code_block.module.name}
            name_dict.update(BUILT_INS)
            instance = SourceInstance(function, name_dict=name_dict)

            # But we can't just run the code associated with the class. Both the constructor and any __init__ function
            # will return None, but we need to return the instance, so we create a little wrapper function to fix that
            # up.

            # We pass in the constructor function, our instance, and all the arguments that the caller wanted. So, note
            # that the number of __init__ arguments is the number of total arguments minus 1: we added in constructor
            # and instance, but the __init__ function expects the instance in addition to the regular arguments!

            # Also note that the constructor function packages up the instance's name_dict.
            constructor = Constructor(**function.function.__dict__)
            constructor.name_dict = instance.name_dict
            fast_stack = self.args_to_fast(function.function, constructor, instance, *args, **kwargs)
            num_args = len(fast_stack) - 1

            # Create the wrapper function
            code_block = CodeBlock()
            wrapper = Function("__wrapper__", code_block)
            ip = 0

            def add(instruction):
                code_block.code_lines[instruction.offset] = instruction
                return instruction.offset + CODE_STEP

            # Call the constructor
            ip = add(LoadFast(None, ip, "LOAD_FAST", 0, "constructor"))
            ip = add(CallFunction(None, ip, "CALL_FUNCTION", 0, None))

            # Discard the constructor's return value
            ip = add(PopTop(None, ip, "POP_TOP", 0, None))

            # Load the parameters and call the __init__
            ip = add(LoadName(None, ip, "LOAD_NAME", 0, "__init__"))
            for index in range(num_args):
                ip = add(LoadFast(None, ip, "LOAD_FAST", index + 1, f"arg[{index}]"))
            ip = add(CallFunction(None, ip, "CALL_FUNCTION", num_args, None))

            # Discard __init__'s return value
            ip = add(PopTop(None, ip, "POP_TOP", 0, None))

            # Return our instance
            ip = add(LoadFast(None, ip, "LOAD_FAST", 1, "instance"))
            add(ReturnValue(None, ip, "RETURN_VALUE", 0, None))

            self.call_stack.append(FunctionContext(wrapper, fast_stack, instance.name_dict))

        elif isinstance(function, Constructor):
            fast_stack = self.args_to_fast(function, *args, **kwargs)
            self.call_stack.append(FunctionContext(function, fast_stack, function.name_dict))

        elif isinstance(function, Function):
            fast_stack = self.args_to_fast(function, *args, **kwargs)
            module = function.code_block.module
            name_dict = module.name_dict if module else {}  # TODO: when running a member function, we need to use the class's name_dict
            self.call_stack.append(FunctionContext(function, fast_stack, name_dict))

        else:
            self.push(function(*args, **kwargs))

    def step(self):
        try:
            context = self.context
            instruction = context.function.code_block.code_lines[context.pc]
            instruction.exec(self)
            # context.function.code_block.code_lines[context.pc].exec(self)
        except ReturnException as rc:
            assert not self.call_stack.pop().data_stack, "Data stack wasn't empty"
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
