import logging

from robot_war.instructions import CodeLine

try:
    from robot_war.exec_context import SandBox
except ImportError:
    SandBox = None

# Constants:
LOG = logging.getLogger(__name__)


class LoadAttr(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push(sandbox.pop().get_attr(self.note))


class LoadBuildClass(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        from robot_war.source_class import build_class
        sandbox.push(build_class)


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
        sandbox.push(sandbox.context.name_dict[self.note])


class MakeFunction(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        name = sandbox.pop()
        code_block = sandbox.pop()
        from robot_war.source_functions import Function
        function = Function(name, code_block)
        if self.operand & 0x01:
            function.default_args = sandbox.pop()
        if self.operand & 0x02:
            LOG.error("TODO: Handle keyword values")
            sandbox.pop()
        if self.operand & 0x04:
            # Ignore annotations
            sandbox.pop()
        if self.operand & 0x08:
            function.closure = sandbox.pop()
        sandbox.push(function)


class SetupAnnotations(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.context.name_dict["__annotations__"] = {}


class StoreAttr(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        obj = sandbox.pop()
        value = sandbox.pop()
        obj.set_attr(self.note, value)


class StoreName(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.context.name_dict[self.note] = sandbox.pop()
