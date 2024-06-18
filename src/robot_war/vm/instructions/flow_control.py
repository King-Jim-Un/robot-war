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
        rev_args = [sandbox.pop() for _ in range(self.operand)]
        sandbox.call_function(sandbox.pop(), *reversed(rev_args))


class ForIter(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        try:
            sandbox.push(next(sandbox.peek(-1)))
        except StopIteration:
            sandbox.pop()
            sandbox.context.pc += self.operand


class GetIter(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push(iter(sandbox.pop()))


class JumpAbsolute(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.context.pc = self.operand


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
        super().exec(sandbox)
        value = sandbox.pop()
        if not value:
            sandbox.context.pc = self.operand


class PopJumpIfNone(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        value = sandbox.pop()
        if value is None:
            sandbox.context.pc = self.operand


class PopJumpIfNotNone(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        value = sandbox.pop()
        if value is not None:
            sandbox.context.pc = self.operand


class PopJumpIfTrue(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        value = sandbox.pop()
        if value:
            sandbox.context.pc = self.operand


class ReturnValue(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        raise ReturnException(sandbox.pop())
