import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Any, Dict, Optional

from robot_war.api import API_CLASSES
from robot_war.exceptions import DontPushReturnValue, TerminalError, BlockThread
from robot_war.vm.api_class import ApiClass, ApiMethod
from robot_war.vm.get_name import GetName
from robot_war.vm.instructions.classes import LoadName
from robot_war.vm.instructions.data import LoadFast, PopTop
from robot_war.vm.instructions.flow_control import ReturnException, CallFunction, ReturnValue
from robot_war.vm.source_class import SourceClass, SourceInstance, BoundMethod, Constructor
from robot_war.vm.source_functions import CodeDict, Function, CodeBlock
from robot_war.vm.source_module import Module

# Types:
NameDict = Dict[str, Any]

# Constants:
LOG = logging.getLogger(__name__)
CODE_STEP = 2

# FunctionContext knows about execution through a single function. Sandbox knows about the execution of a single thread
# and all the nested function calls. A Playground knows all the threads for a given robot. If a player has multiple
# robots operating simultaneously, they will have multiple Playground objects


@dataclass
class FunctionContext:
    function: Function
    fast_stack: Dict[int, Any] = field(default_factory=dict)
    get_name_obj: Optional[GetName] = None
    data_stack: List[Any] = field(default_factory=list)
    pc: int = 0


@dataclass
class Playground:
    root_path: Path
    all_modules: Dict[str, Module] = field(default_factory=dict)
    code_blocks_by_name: CodeDict = field(default_factory=dict)
    sandboxes: List["SandBox"] = field(default_factory=list)
    robot: Optional[ApiClass] = None

    def set_robot(self, robot: ApiClass):
        self.robot = robot

    def unset_robot(self):
        self.robot = None


@dataclass
class SandBox:
    playground: Playground
    call_stack: List[FunctionContext] = field(default_factory=list)

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
            instance = SourceInstance({"__name__": function.module.name}, function)

            try:
                # But we can't just run the __init__ function as it will return None. We need to return the instance,
                # so we create a little wrapper function to fix that up. We'll pass in parameters __init__, instance,
                # and the arguments we received.
                init_func = function.get_name("__init__")
                fast_stack = self.args_to_fast(init_func, init_func, instance, *args, **kwargs)
                num_args = len(fast_stack) - 1  # Skipping __init__

                # Create the wrapper function
                code_block = CodeBlock(num_params=len(fast_stack))
                wrapper = Function("__wrapper__", code_block)
                ip = 0

                def add(instruction):
                    code_block.code_lines[instruction.offset] = instruction
                    return instruction.offset + CODE_STEP

                # Load the parameters and call the __init__
                ip = add(LoadName(None, ip, "LOAD_FAST", 0, "__init__"))
                for index in range(num_args):
                    ip = add(LoadFast(None, ip, "LOAD_FAST", index + 1, f"arg[{index}]"))
                ip = add(CallFunction(None, ip, "CALL_FUNCTION", num_args, None))

                # Discard __init__'s return value
                ip = add(PopTop(None, ip, "POP_TOP", 0, None))

                # Return our instance
                ip = add(LoadFast(None, ip, "LOAD_FAST", 1, "instance"))
                add(ReturnValue(None, ip, "RETURN_VALUE", 0, None))

                self.call_stack.append(FunctionContext(wrapper, fast_stack, instance))
            except KeyError:
                self.push(instance)  # No __init__()

        elif isinstance(function, Constructor):
            fast_stack = self.args_to_fast(function, *args, **kwargs)
            self.call_stack.append(FunctionContext(function, fast_stack, function.source_class))

        elif isinstance(function, BoundMethod):
            fast_stack = self.args_to_fast(function, function.instance, *args, **kwargs)
            self.call_stack.append(FunctionContext(function, fast_stack, function.instance))

        elif isinstance(function, Function):
            fast_stack = self.args_to_fast(function, *args, **kwargs)
            self.call_stack.append(FunctionContext(function, fast_stack, function.code_block.module))

        else:
            assert function not in API_CLASSES, "API classes must be subclassed, do not instantiate as-is"
            if isinstance(function, ApiMethod) and args and isinstance(args[0], SourceInstance):
                function = function.function
                args = (self.playground.robot,) + args[1:]

            try:
                self.push(function(*args, **kwargs))
            except DontPushReturnValue:
                pass
            except BlockThread as block_thread:
                self.block_thread(block_thread)

    def step(self):
        try:
            # context = self.context
            # instruction = context.function.code_block.code_lines[context.pc]
            # instruction.exec(self)
            self.context.function.code_block.code_lines[self.context.pc].exec(self)
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

    def build_class(self, function: Function, name: str, *parent_classes):
        num_api_parents = len([cls for cls in parent_classes if cls in API_CLASSES])
        if num_api_parents == 0:
            class_list = list(parent_classes)
        elif num_api_parents == 1:
            assert self.playground.robot is None, "each VM can only instantiate a single robot"
            robot = [cls(_playground=self.playground) for cls in parent_classes if cls in API_CLASSES][0]
            class_list = [robot if cls in API_CLASSES else cls for cls in parent_classes]
            self.playground.set_robot(robot)
            LOG.debug("Instantiated robot %r", robot)
        else:
            raise TerminalError("Robots can only inherit from a single API class")
        source_class = SourceClass({"__name__": name}, class_list, function.code_block.module)

        # Run the creation code function to set up our new class. Of course, the creation code just returns None, and we
        # need to return the new class, so we'll need a little wrapper.

        # A second complication is function, which is just a regular function, so its namespace is module. We want to
        # use the class's namespace. To specify the right namespace, we'll create a temporary Constructor object.
        constructor = Constructor(source_class=source_class, **function.__dict__)
        wrapper = Function("__wrapper__", CodeBlock({
            # Call creation function
            0: LoadFast(None, 0, "LOAD_FAST", 0, "creation"),
            2: CallFunction(None, 2, "CALL_FUNCTION", 0, None),
            # Discard result
            4: PopTop(None, 4, "POP_TOP", 0, None),
            # Return class
            6: LoadFast(None, 6, "LOAD_FAST", 1, "source_class"),
            8: ReturnValue(None, 8, "RETURN_VALUE", 0, None)
        }, num_params=2))
        self.call_stack.append(FunctionContext(wrapper, {0: constructor, 1: source_class}, source_class))
        raise DontPushReturnValue()

    def block_thread(self, block_thread: BlockThread):
        raise NotImplementedError()
