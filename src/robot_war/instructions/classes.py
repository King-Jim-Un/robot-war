import logging

from robot_war.instructions import CodeLine

try:
    from robot_war.exec_context import SandBox
except ImportError:
    SandBox = None

# Constants:
LOG = logging.getLogger(__name__)


def build_class(function: Function, name: str):
    return SourceClass(name, function.code_block)


class LoadAttr(CodeLine):
    def exec(self, sandbox: SandBox):
        sandbox.push(sandbox.pop().getattr(self.note))
        super().exec(sandbox)


class LoadBuildClass(CodeLine):
    def exec(self, sandbox: SandBox):
        sandbox.push(build_class)
        super().exec(sandbox)


class LoadMethod(CodeLine):
    def exec(self, sandbox: SandBox):
        obj = sandbox.pop()
        LOG.error("TODO: LoadMethod(%r.%s)", obj, self.note)
        sandbox.push(None)
        sandbox.push(obj)
        sandbox.next()


class LoadName(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        name_dict = sandbox.name_dict_by_module_name[sandbox.module.name]
        sandbox.push(name_dict[self.note])


class MakeFunction(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        if self.operand & 0x01:
            LOG.error("TODO: Handle default values")
            sandbox.pop()
        if self.operand & 0x02:
            LOG.error("TODO: Handle keyword values")
            sandbox.pop()
        if self.operand & 0x04:
            # Ignore annotations
            sandbox.pop()
        if self.operand & 0x08:
            sandbox.context.function.closure = sandbox.pop()
        name = sandbox.pop()
        code_block = sandbox.pop()
        sandbox.push(Function(name, code_block))


class SetupAnnotations(CodeLine):
    pass


class StoreAttr(CodeLine):
    def exec(self, sandbox: SandBox):
        obj = sandbox.pop()
        value = sandbox.pop()
        obj.set_attr(obj, self.note, value)
        super().exec(sandbox)


class StoreName(CodeLine):
    def exec(self, sandbox: SandBox):
        name_dict = sandbox.sandbox.name_dict_by_module_name[sandbox.module.name]
        name_dict[self.note] = sandbox.pop()
        super().exec(sandbox)
