import logging

from robot_war.exceptions import ReturnException
from robot_war.vm.instructions import CodeLine

try:
    from robot_war.vm.exec_context import SandBox
except ImportError:
    SandBox = None

# Constants:
LOG = logging.getLogger(__name__)


class CallFunction(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        rev_args = [sandbox.pop() for _ in range(self.operand)]
        sandbox.call_function(sandbox.pop(), *reversed(rev_args))


class CallFunctionKW(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        tuple_kw_params = sandbox.pop()
        kwargs = {}
        for key in reversed(tuple_kw_params):
            kwargs[key] = sandbox.pop()
        rev_args = [sandbox.pop() for _ in range(self.operand - len(kwargs))]
        sandbox.call_function(sandbox.pop(), *reversed(rev_args), **kwargs)


class CallMethod(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        rev_args = [sandbox.pop() for _ in range(self.operand + 1)]  # include self
        sandbox.call_function(sandbox.pop(), *reversed(rev_args))


class JumpBackward(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.context.pc -= self.operand


class JumpForward(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.context.pc += self.operand


class PopJumpIfFalse(CodeLine):
    def exec(self, sandbox: SandBox):
        value = sandbox.pop()
        if not value:
            sandbox.pc = self.operand
        super().exec(sandbox)


class PopJumpIfNone(CodeLine):
    def exec(self, sandbox: SandBox):
        value = sandbox.pop()
        if value is None:
            sandbox.pc = self.operand
        super().exec(sandbox)


class PopJumpIfNotNone(CodeLine):
    def exec(self, sandbox: SandBox):
        value = sandbox.pop()
        if value is not None:
            sandbox.pc = self.operand
        super().exec(sandbox)


class PopJumpIfTrue(CodeLine):
    def exec(self, sandbox: SandBox):
        value = sandbox.pop()
        if value:
            sandbox.pc = self.operand
        super().exec(sandbox)


class RaiseVarArgs(CodeLine):
    def exec(self, sandbox: SandBox):
        assert self.operand != 0, "TODO: re-raise"
        assert self.operand != 2, "TODO: raise with cause"
        raise sandbox.pop()


class ReturnValue(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        raise ReturnException(sandbox.pop())
