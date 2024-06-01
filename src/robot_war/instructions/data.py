import logging

from robot_war.instructions import CodeLine

try:
    from robot_war.exec_context import SandBox
except ImportError:
    SandBox = None

# Constants:
LOG = logging.getLogger(__name__)


class BinaryAdd(CodeLine):
    def exec(self, sandbox: SandBox):
        arg2 = sandbox.pop()
        arg1 = sandbox.pop()
        sandbox.push(arg1 + arg2)
        super().exec(sandbox)


class BinaryMultiply(CodeLine):
    def exec(self, sandbox: SandBox):
        arg2 = sandbox.pop()
        arg1 = sandbox.pop()
        sandbox.push(arg1 * arg2)
        super().exec(sandbox)


class BuildConstKeyMap(CodeLine):
    def exec(self, sandbox: SandBox):
        sandbox.push({key: sandbox.pop() for key in reversed(sandbox.pop())})
        super().exec(sandbox)


class BuildList(CodeLine):
    def exec(self, sandbox: SandBox):
        data_stack = sandbox.context.data_stack
        sandbox.context.data_stack, values = data_stack[:-self.operand], data_stack[-self.operand:]
        sandbox.push(values)
        super().exec(sandbox)


class BuildTuple(CodeLine):
    def exec(self, sandbox: SandBox):
        data_stack = sandbox.context.data_stack
        sandbox.context.data_stack, values = data_stack[:-self.operand], data_stack[-self.operand:]
        sandbox.push(tuple(values))
        super().exec(sandbox)


class CompareOp(CodeLine):
    def exec(self, sandbox: SandBox):
        arg2 = sandbox.pop()
        arg1 = sandbox.pop()
        sandbox.push(eval(f"{repr(arg1)} {self.note} {repr(arg2)}"))
        super().exec(sandbox)


class LoadClosure(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push(sandbox.context.fast_stack[sandbox.context.function.code_block.num_params + self.operand])


class LoadDeref(LoadClosure):
    pass


class LoadConst(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        constants = sandbox.context.function.code_block.constants

        # We don't preprocess the constants, just deal with them the first time they pop up. Have we done this one yet?
        if self.operand not in constants:
            # Not yet. Is it a code block?
            if self.note.startswith("<"):
                # Yes, grab the code
                constants[self.operand] = sandbox.code_blocks_by_name[self.note]
            else:
                # Something simple, just eval it
                constants[self.operand] = eval(self.note)

        sandbox.push(constants[self.operand])


class LoadFast(CodeLine):
    def exec(self, sandbox: SandBox):
        sandbox.push(sandbox.context.fast_stack[self.operand])
        super().exec(sandbox)


class LoadGlobal(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        name_dict = sandbox.context.function.code_block.module.name_dict
        sandbox.push(name_dict[self.note])


class LoadSubscript(CodeLine):
    def exec(self, sandbox: SandBox):
        key = sandbox.pop()
        container = sandbox.pop()
        sandbox.push(container[key])
        super().exec(sandbox)


class PopTop(CodeLine):
    def exec(self, sandbox: SandBox):
        sandbox.pop()
        super().exec(sandbox)


class StoreFast(CodeLine):
    def exec(self, sandbox: SandBox):
        sandbox.context.fast_stack[self.operand] = sandbox.pop()
        super().exec(sandbox)


class StoreSubscript(CodeLine):
    def exec(self, sandbox: SandBox):
        index = sandbox.pop()
        obj = sandbox.pop()
        obj[index] = sandbox.pop()
        super().exec(sandbox)


class StoreDeref(CodeLine):
    def exec(self, sandbox: SandBox):
        sandbox.context.fast_stack[sandbox.context.function.code_block.num_params + self.operand] = sandbox.pop()
        super().exec(sandbox)
