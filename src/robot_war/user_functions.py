from dataclasses import dataclass, field
import logging
from typing import Optional, Dict, Any

from robot_war.built_ins import BUILT_INS

try:
    from robot_war.source_module import Module
    from robot_war.exec_context import CodeBlockContext, NameDict
except ImportError:
    Module = CodeBlockContext = NameDict = None

# Types:
CodeDict = Dict[str, "CodeBlock"]

# Constants:
LOG = logging.getLogger(__name__)


@dataclass(repr=False)
class CodeLine:
    line_number: Optional[int]
    offset: int
    op_code: str
    operand: Optional[int]
    note: Optional[str]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.operand}, {self.note})"

    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        LOG.debug("%r", self)
        context.next()


@dataclass(repr=False)
class CodeBlock:
    module: "Module"
    code_lines: Dict[int, "CodeLine"] = field(default_factory=dict)
    constants: Dict[int, Any] = field(default_factory=dict)

    def __repr__(self):
        return f"CodeBlock(module={self.module.name}, {len(self.code_lines)} lines, {len(self.constants)} constants)"

    def init_name_to_index_dict(self, name_dict: NameDict) -> Dict[str, int]:
        # Build the mapping
        name_to_index_dict: Dict[str, int] = {}
        for code_line in self.code_lines.values():
            if isinstance(code_line, StoreName) or isinstance(code_line, LoadName):
                name_to_index_dict[code_line.note] = code_line.operand

        # Initialize the built-ins
        for built_in, func in BUILT_INS.items():
            if built_in in name_to_index_dict:
                name_dict[name_to_index_dict[built_in]] = func

        return name_to_index_dict


@dataclass
class Function:
    name: str
    code_block: CodeBlock


@dataclass
class SourceClass(Function):
    pass


def build_class(function: Function, name: str):
    return SourceClass(name, function.code_block)


@dataclass
class ReturnException(Exception):
    value: Any


class BuildConstKeyMap(CodeLine):
    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        context.push({key: context.pop() for key in reversed(context.pop())})
        print(context.peek(-1))
        super().exec(context, code_block)


class CallFunction(CodeLine):
    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        super().exec(context, code_block)
        args = []
        for _ in range(self.operand):
            args.insert(0, context.pop())
        context.exec_context.call_function(context.pop(), *args)


class CallMethod(CodeLine):
    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        args = []
        for _ in range(self.operand):
            args.insert(0, context.pop())
        obj = context.pop()
        method = context.pop()
        LOG.error("TODO: CallFunction %r %s%r", obj, method, args)
        context.push(None)
        context.next()


class CompareOp(CodeLine):
    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        arg2 = context.pop()
        arg1 = context.pop()
        context.push(eval(f"{repr(arg1)} {self.note} {repr(arg2)}"))
        super().exec(context, code_block)


class ImportFrom(CodeLine):
    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        module = context.peek(-1)
        LOG.error("TODO: ImportFrom(module=%r, name=%s)", module, self.note)
        context.push(None)
        context.next()


class ImportName(CodeLine):
    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        from_list = context.pop()
        level = context.pop()
        LOG.error("TODO: ImportName(from_list=%s.%s, level=%d)", self.note, from_list, level)
        context.push(None)
        context.next()


class LoadBuildClass(CodeLine):
    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        context.push(build_class)
        super().exec(context, code_block)


class LoadConst(CodeLine):
    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        if self.operand not in code_block.constants:
            if self.note.startswith("<"):
                code_block.constants[self.operand] = code_block.module.code_blocks_by_name[self.note]
            else:
                code_block.constants[self.operand] = eval(self.note)
        context.push(code_block.constants[self.operand])
        super().exec(context, code_block)


class LoadAttr(CodeLine):
    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        context.push(context.pop().getattr(self.note))
        super().exec(context, code_block)


class LoadFast(CodeLine):
    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        context.push(context.fast_stack[self.operand])
        super().exec(context, code_block)


class LoadMethod(CodeLine):
    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        obj = context.pop()
        LOG.error("TODO: LoadMethod(%r.%s)", obj, self.note)
        context.push(None)
        context.push(obj)
        context.next()


class LoadName(CodeLine):
    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        super().exec(context, code_block)
        name_dict = context.sandbox.name_dict_by_module_name[code_block.module.name]
        context.push(name_dict[self.operand])


class MakeFunction(CodeLine):
    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        super().exec(context, code_block)
        if self.operand & 0x01:
            LOG.error("TODO: Handle default values")
            context.pop()
        if self.operand & 0x02:
            LOG.error("TODO: Handle keyword values")
            context.pop()
        if self.operand & 0x04:
            # Ignore annotations
            context.pop()
        if self.operand & 0x02:
            LOG.error("TODO: Handle closure")
            context.pop()
        name = context.pop()
        code_block = context.pop()
        context.push(Function(name, code_block))


class PopJumpIfFalse(CodeLine):
    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        value = context.pop()
        if not value:
            context.pc = self.operand
        super().exec(context, code_block)


class PopTop(CodeLine):
    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        context.pop()
        super().exec(context, code_block)


class ReturnValue(CodeLine):
    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        super().exec(context, code_block)
        raise ReturnException(context.pop())


class SetupAnnotations(CodeLine):
    pass


class StoreAttr(CodeLine):
    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        obj = context.pop()
        value = context.pop()
        obj.set_attr(obj, self.note, value)
        super().exec(context, code_block)


class StoreName(CodeLine):
    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        name_dict = context.sandbox.name_dict_by_module_name[code_block.module.name]
        name_dict[self.operand] = context.pop()
        super().exec(context, code_block)


class StoreSubscript(CodeLine):
    def exec(self, context: "CodeBlockContext", code_block: "CodeBlock"):
        index = context.pop()
        obj = context.pop()
        obj[index] = context.pop()
        super().exec(context, code_block)
