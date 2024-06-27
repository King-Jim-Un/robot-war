from dataclasses import dataclass, field
from typing import Optional

from robot_war.vm.api_class import Waiter, ApiClass, requires_sandbox
from robot_war.vm.source_class import SourceInstance
from robot_war.vm.source_module import Module

try:
    from robot_war.vm.exec_context import SandBox
    from robot_war.vm.source_functions import Function
except ImportError:
    SandBox = Function = None  # type: ignore


@dataclass
class Thread(ApiClass, SourceInstance):
    _sandbox: Optional["SandBox"] = None
    _running: bool = False
    _waiter: Waiter = field(default_factory=Waiter)

    def __post_init__(self):
        self.name_dict = {"join": self.join, "start": self.start}

    @property
    def running(self):
        return self._running

    @requires_sandbox
    def join(self, sandbox: Optional[SandBox] = None):
        assert sandbox
        return self._waiter.get_value(sandbox)

    def start(self, function: "Function", *args, **kwargs) -> "Thread":
        assert self._playground and not self._running
        self._running = True

        arguments = {"_set_value": self._waiter.set_value, "_func": function}
        for index, arg in enumerate(args):
            arguments[f"_arg{index}"] = arg
        arguments.update(kwargs)
        from robot_war.vm.source_functions import Function
        with Function("thread_wrapper", arguments=arguments) as wrapper:
            wrapper.LOAD_FAST("_set_value")
            wrapper.LOAD_FAST("_func")
            for index in range(len(args)):
                wrapper.LOAD_FAST(f"_arg{index}")
            named_args = []
            for name, value in kwargs.items():
                wrapper.LOAD_FAST(name)
                named_args.append(name)
            wrapper.LOAD_CONST(repr(tuple(named_args)))
            wrapper.CALL_FUNCTION_KW(len(args) + len(named_args))  # Call thread function
            wrapper.CALL_FUNCTION(1)  # Call set_value() with the result
            wrapper.RETURN_VALUE()
        self._sandbox = self._playground.new_sandbox(wrapper)

        return self


THREAD_MODULE = Module("thread", name_dict={"Thread": Thread})
