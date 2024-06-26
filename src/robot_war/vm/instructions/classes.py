import logging

from robot_war.vm.instructions import CodeLine

try:
    from robot_war.vm.exec_context import SandBox
except ImportError:
    SandBox = None  # type: ignore

# Constants:
LOG = logging.getLogger(__name__)


class LoadAttribute(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push(sandbox.pop().get_attr(self.note))


class LoadBuildClass(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push(sandbox.build_class)


class LoadMethod(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        assert self.note
        obj = sandbox.pop()
        try:
            sandbox.push(obj.get_method(self.note))
        except AttributeError:
            sandbox.push(getattr(obj, self.note))


class LoadName(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        assert self.note
        get_name_obj = sandbox.context.get_name_obj
        assert get_name_obj
        sandbox.push(get_name_obj.get_name(self.note))


class MakeFunction(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        name = sandbox.pop()
        code_block = sandbox.pop()
        from robot_war.vm.source_functions import Function
        function = Function(name, code_block=code_block)
        if self.operand & 0x08:
            function.closure = sandbox.pop()
        if self.operand & 0x04:
            # Ignore annotations
            sandbox.pop()
        if self.operand & 0x02:
            LOG.error("TODO: Handle keyword values")
            sandbox.pop()
        if self.operand & 0x01:
            function.default_args = sandbox.pop()
        sandbox.push(function)


class SetupAnnotations(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        get_name_obj = sandbox.context.get_name_obj
        assert get_name_obj
        get_name_obj.name_dict["__annotations__"] = {}


class StoreAttribute(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        obj = sandbox.pop()
        value = sandbox.pop()
        obj.set_attr(self.note, value)


class StoreName(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        get_name_obj = sandbox.context.get_name_obj
        assert get_name_obj and self.note
        get_name_obj.name_dict[self.note] = sandbox.pop()
