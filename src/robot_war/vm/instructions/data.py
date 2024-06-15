import logging

from robot_war.vm.instructions import CodeLine

try:
    from robot_war.vm.exec_context import SandBox
except ImportError:
    SandBox = None

# Constants:
LOG = logging.getLogger(__name__)
COMPARE_DICT = {"<": lambda a, b: a < b, "<=": lambda a, b: a <= b, ">": lambda a, b: a > b, ">=": lambda a, b: a >= b,
                "==": lambda a, b: a == b, "!=": lambda a, b: a != b, }


class BinarySlice(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        end = sandbox.pop()
        start = sandbox.pop()
        container = sandbox.pop()
        sandbox.push(container[start:end])


class BinarySubscript(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        key = sandbox.pop()
        container = sandbox.pop()
        sandbox.push(container[key])


class BuildConstKeyMap(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push({key: sandbox.pop() for key in reversed(sandbox.pop())})


class BuildList(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        data_stack = sandbox.context.data_stack
        sandbox.context.data_stack, values = data_stack[:-self.operand], data_stack[-self.operand:]
        sandbox.push(values)


class BuildSet(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push({sandbox.pop() for _ in range(self.operand)})


class BuildString(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        value = ""
        for _ in range(self.operand):
            value = sandbox.pop() + value
        sandbox.push(value)


class BuildTuple(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        data_stack = sandbox.context.data_stack
        sandbox.context.data_stack, values = data_stack[:-self.operand], data_stack[-self.operand:]
        sandbox.push(tuple(values))


class CompareOperand(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        arg2 = sandbox.pop()
        arg1 = sandbox.pop()
        sandbox.push(COMPARE_DICT[self.note](arg1, arg2))


class Copy(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push(sandbox.peek(-self.operand))


class DeleteFast(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        del sandbox.context.fast_stack[self.operand]


class DeleteGlobal(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.context.function.code_block.module.del_name(self.note)


class DeleteSubscript(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        key = sandbox.pop()
        container = sandbox.pop()
        del container[key]


class GetLength(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push(len(sandbox.peek(-1)))


class LoadClosure(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push(sandbox.context.fast_stack[sandbox.context.function.code_block.num_params + self.operand])


class LoadDeref(LoadClosure):
    pass


class LoadConstant(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        constants = sandbox.context.function.code_block.constants

        # We don't preprocess the constants, just deal with them the first time they pop up. Have we done this one yet?
        if self.operand not in constants:
            # Not yet. Is it a code block?
            if self.note.startswith("<"):
                # Yes, grab the code
                constants[self.operand] = sandbox.context.function.code_block.module.get_name(self.note)
            else:
                # Something simple, just eval it
                from pathlib import WindowsPath  # Should allow us to eval a constant path
                constants[self.operand] = eval(self.note)

        sandbox.push(constants[self.operand])


class LoadFast(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push(sandbox.context.fast_stack[self.operand])


class LoadGlobal(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        name_dict = sandbox.context.function.code_block.module.name_dict
        sandbox.push(name_dict[self.note])


class LoadSubscript(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        key = sandbox.pop()
        container = sandbox.pop()
        LOG.warning("%r[%r]",container,key)
        sandbox.push(container[key])


class PopTop(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.pop()


class StoreFast(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.context.fast_stack[self.operand] = sandbox.pop()


class StoreGlobal(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.context.function.code_block.module.set_name(self.note, sandbox.pop())


class StoreSubscript(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        index = sandbox.pop()
        obj = sandbox.pop()
        obj[index] = sandbox.pop()


class StoreDeref(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.context.fast_stack[sandbox.context.function.code_block.num_params + self.operand] = sandbox.pop()


class StoreSlice(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        end = sandbox.pop()
        start = sandbox.pop()
        container = sandbox.pop()
        container[start:end] = sandbox.pop()


class Swap(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        data_stack = sandbox.context.data_stack
        data_stack[-self.operand], data_stack[-1] = data_stack[-1], data_stack[-self.operand]
