import logging

from robot_war.vm.instructions import CodeLine

try:
    from robot_war.vm.exec_context import SandBox
except ImportError:
    SandBox = None

# Constants:
LOG = logging.getLogger(__name__)


class BinaryAdd(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        arg2 = sandbox.pop()
        arg1 = sandbox.pop()
        sandbox.push(arg1 + arg2)


class BinaryMultiply(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        arg2 = sandbox.pop()
        arg1 = sandbox.pop()
        sandbox.push(arg1 * arg2)


class BinarySubtract(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        arg2 = sandbox.pop()
        arg1 = sandbox.pop()
        sandbox.push(arg1 - arg2)


class BinaryFloorDivide(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        arg2 = sandbox.pop()
        arg1 = sandbox.pop()
        sandbox.push(arg1 // arg2)


class BinaryTrueDivide(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        arg2 = sandbox.pop()
        arg1 = sandbox.pop()
        sandbox.push(arg1 / arg2)


class ContainsOperand(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        arg2 = sandbox.pop()
        arg1 = sandbox.pop()
        sandbox.push((arg1 not in arg2) if self.operand else (arg1 in arg2))


class IsOperand(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        arg2 = sandbox.pop()
        arg1 = sandbox.pop()
        sandbox.push((arg1 is not arg2) if self.operand else (arg1 is arg2))


class UnaryInvert(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push(~sandbox.pop())


class UnaryNegative(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push(-sandbox.pop())


class UnaryNot(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push(not sandbox.pop())
