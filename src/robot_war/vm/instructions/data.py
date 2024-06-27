from dataclasses import dataclass
import logging
from typing import Optional, Iterable

from robot_war.vm.instructions import CodeLine

try:
    from robot_war.vm.exec_context import SandBox
except ImportError:
    SandBox = None  # type: ignore

# Constants:
LOG = logging.getLogger(__name__)
COMPARE_DICT = {"<": lambda a, b: a < b, "<=": lambda a, b: a <= b, ">": lambda a, b: a > b, ">=": lambda a, b: a >= b,
                "==": lambda a, b: a == b, "!=": lambda a, b: a != b, }


@dataclass
class Slice:
    start: Optional[int]
    end: Optional[int]


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
        sandbox.push(container[key.start:key.end] if isinstance(key, Slice) else container[key])


class BuildConstKeyMap(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        keys = sandbox.pop()
        values = sandbox.context.data_stack[-len(keys):]
        sandbox.context.data_stack = sandbox.context.data_stack[:-len(keys)]
        sandbox.push({key: values[index] for index, key in enumerate(keys)})


class BuildList(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        data_stack = sandbox.context.data_stack
        if self.operand:
            sandbox.context.data_stack, values = data_stack[:-self.operand], data_stack[-self.operand:]
        else:
            values = []
        sandbox.push(values)


class BuildMap(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        context = sandbox.context
        num_items = self.operand * 2
        context.data_stack, values = context.data_stack[:-num_items], context.data_stack[-num_items:]
        sandbox.push({values[i]: values[i + 1] for i in range(0, num_items, 2)})


class BuildSet(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push({sandbox.pop() for _ in range(self.operand)})


class BuildSlice(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        end = sandbox.pop()
        start = sandbox.pop()
        sandbox.push(Slice(start, end))


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
        assert self.note
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
        module = sandbox.context.function.code_block.module
        assert module and self.note
        module.del_name(self.note)


class DeleteSubscript(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        key = sandbox.pop()
        container = sandbox.pop()
        del container[key]


class DupTop(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push(sandbox.peek(-1))


class FormatValue(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        format_str = sandbox.pop() if self.operand & 0x04 else None
        value = sandbox.pop()
        flags3 = self.operand & 0x03
        if flags3 == 0x01:
            value = str(value)
        elif flags3 == 0x02:
            value = repr(value)
        elif flags3 == 0x03:
            value = repr(value)  # Not real clear on converting to ascii
        sandbox.push(str(value) if format_str is None else f"{value:{format_str}}")


class GetLength(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push(len(sandbox.peek(-1)))


class ListAppend(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        item = sandbox.pop()
        the_list: list = sandbox.peek(-self.operand)
        the_list.append(item)


class ListExtend(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        extend: Iterable = sandbox.pop()
        the_list: list = sandbox.pop()
        for item in extend:
            the_list.append(item)
        sandbox.push(the_list)


class LoadClosure(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push(sandbox.context.deref[self.operand])


class LoadDeref(LoadClosure):
    pass


class LoadConstant(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        assert self.note
        constants = sandbox.context.function.code_block.constants

        # We don't preprocess the constants, just deal with them the first time they pop up. Have we done this one yet?
        if self.operand not in constants:
            # Not yet. Is it a code block?
            if self.note.startswith("<"):
                # Yes, grab the code
                module = sandbox.context.function.code_block.module
                assert module
                constants[self.operand] = module.get_name(self.note)
            else:
                # Something simple, just eval it
                from pathlib import WindowsPath  # noqa Should allow us to eval a constant path
                constants[self.operand] = eval(self.note)

        sandbox.push(constants[self.operand])


class LoadFast(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push(sandbox.context.fast_stack[self.operand])


class LoadGlobal(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        module = sandbox.context.function.code_block.module
        assert module and self.note
        sandbox.push(module.name_dict[self.note])


class LoadSubscript(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        key = sandbox.pop()
        container = sandbox.pop()
        sandbox.push(container[key])


class MapAdd(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        value = sandbox.pop()
        key = sandbox.pop()
        the_dict: dict = sandbox.peek(-self.operand)
        the_dict[key] = value


class PopTop(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.pop()


class SetAdd(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        item = sandbox.pop()
        the_set: set = sandbox.peek(-self.operand)
        the_set.add(item)


class SetUpdate(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        items: Iterable = sandbox.pop()
        the_set: set = sandbox.pop()
        sandbox.push(the_set.union(items))


class StoreFast(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.context.fast_stack[self.operand] = sandbox.pop()


class StoreGlobal(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        module = sandbox.context.function.code_block.module
        assert module and self.note
        module.set_name(self.note, sandbox.pop())


class StoreSubscript(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        index = sandbox.pop()
        obj = sandbox.pop()
        obj[index] = sandbox.pop()


class StoreDeref(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.context.deref[self.operand] = sandbox.pop()


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
        ctext = sandbox.context
        ctext.data_stack[-self.operand], ctext.data_stack[-1] = ctext.data_stack[-1], ctext.data_stack[-self.operand]
