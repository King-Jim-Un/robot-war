import logging

from robot_war.exceptions import ReturnException
from robot_war.instructions import CodeLine

try:
    from robot_war.exec_context import SandBox
except ImportError:
    SandBox = None

# Constants:
LOG = logging.getLogger(__name__)


class CallFunction(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        rev_args = [sandbox.pop() for _ in range(self.operand)]
        sandbox.call_function(sandbox.pop(), *reversed(rev_args))


class CallMethod(CodeLine):
    def exec(self, sandbox: SandBox):
        args = []
        for _ in range(self.operand):
            args.insert(0, sandbox.pop())
        obj = sandbox.pop()
        method = sandbox.pop()
        LOG.error("TODO: CallFunction %r %s%r", obj, method, args)
        sandbox.push(None)
        sandbox.next()


class PopJumpIfFalse(CodeLine):
    def exec(self, sandbox: SandBox):
        value = sandbox.pop()
        if not value:
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
