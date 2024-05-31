import logging
from pathlib import Path
from typing import List, Tuple

from robot_war.instructions import CodeLine

try:
    from robot_war.exec_context import SandBox
    from robot_war.source_module import Module
except ImportError:
    SandBox = Module = None

# Constants:
LOG = logging.getLogger(__name__)
ROBOT_WAR = "robot_war"


class ImportFrom(CodeLine):
    def exec(self, sandbox: SandBox):
        module = sandbox.peek(-1)
        LOG.error("TODO: ImportFrom(module=%r, name=%s)", module, self.note)
        sandbox.push(None)
        sandbox.next()


class ImportName(CodeLine):
    def exec(self, sandbox: SandBox):
        from_list = sandbox.pop()
        level = sandbox.pop()
        assert level == 0, "TODO: non-zero level imports"
        parts = self.note.split(".")

        from robot_war.exec_context import CODE_STEP

        def add(instruction):
            code_block.code_lines[instruction.offset] = instruction
            return instruction.offset + CODE_STEP

        ip = 0
        from robot_war.instructions.data import LoadFast, BuildTuple, LoadConst, LoadSubscript
        from robot_war.instructions.flow_control import ReturnValue
        from robot_war.source_functions import Function, CodeBlock
        code_block = CodeBlock()

        if parts[0] == ROBOT_WAR:
            modules_loaded, tuples_to_load = self.load_api(parts)
        else:
            modules_loaded, tuples_to_load = self.find_load_files(sandbox, parts)
            ip = add(LoadFast(None, ip, "LOAD_FAST", 0, "modules_loaded"))
            link_up = bool(modules_loaded)
            for index in range(len(tuples_to_load)):
                ip = add(LoadFast(None, ip, "LOAD_FAST", index + 1, f"tuples_to_load[{index}]"))
                ip = add(BuildTuple(None, ip, "BUILD_TUPLE", 2, None))
                ip = add(LoadModuleFile1(None, ip, "LOAD_MODULE_FILE_1", 0, None))
                if link_up:
                    ip = add(LoadFast(None, ip, "LOAD_FAST", index + 1, f"tuples_to_load[{index}]"))
                    ip = add(LoadConst(None, ip, "LOAD_CONST", 0, "0"))
                    ip = add(LoadSubscript(None, ip, "LOAD_SUBSCR", 0, None))
                    ip = add(LoadModuleFile2(None, ip, "LOAD_MODULE_FILE_2", 0, None))
                    link_up = True

        if from_list is None:
            ip = add(LoadConst(None, ip, "LOAD_CONST", 0, "0"))
        else:
            ip = add(LoadConst(None, ip, "LOAD_CONST", 1, "-1"))
        ip = add(LoadSubscript(None, ip, "LOAD_SUBSCR", 0, None))
        add(ReturnValue(None, ip, "RETURN_VALUE", 0, None))
        sandbox.call_function(Function("__import_name__", code_block), modules_loaded, *tuples_to_load)

        sandbox.next()

    @staticmethod
    def find_load_files(sandbox: SandBox, parts: List[str]) -> Tuple[List[Module], List[Tuple[str, Path]]]:
        modules_loaded = []
        tuples_to_load = []
        return modules_loaded, tuples_to_load


class LoadModuleFile1(CodeLine):  # Not in parser
    def exec(self, sandbox: SandBox):
        """
        pop TOS: (module_name: str, file_path: Path)
        pop TOS1: [module(0), module(1), ... module(N-1)]
        Load a module_name as module(N) from file_path
        push TOS: [module(0), module(1), ... module(N)]
        """
        super().exec(sandbox)
        from robot_war.source_module import Module
        module_name, file_path = sandbox.pop()
        module_list: List[Module] = sandbox.pop()
        from robot_war.source_functions import Function, CodeBlock
        from robot_war.instructions.data import PopTop, LoadFast
        from robot_war.instructions.flow_control import ReturnValue
        launcher_block = CodeBlock({
            # Note that we're not putting a call on this stack since we don't want this to be user-callable!
            0: PopTop(None, 0, "POP_TOP", 0, None),  # Discard the None that will be returned by importing the module
            2: LoadFast(None, 2, "LOAD_FAST", 0, "module_list"),  # Return the module list we create in advance
            4: ReturnValue(None, 4, "RETURN_VALUE", 0, None)  # This will do the push
        })
        from robot_war.parse_source_file import parse_source_file
        module_block = parse_source_file(sandbox, module_name, file_path)
        module_list.append(sandbox.all_modules[module_name])
        sandbox.call_function(Function("__load_module_file_1__", launcher_block), module_list)
        sandbox.call_function(Function(module_name, module_block))


class LoadModuleFile2(CodeLine):  # Not in parser
    def exec(self, sandbox: SandBox):
        """
        pop TOS: module_name: str
        TOS1: [module(0), module(1), ... module(N)]
        Set module(N-1).module_name = module(N)
        """
        module_name: str = sandbox.pop()
        from robot_war.source_module import Module
        module_list: List[Module] = sandbox.peek(-1)
        module_list[-2].name_dict[module_name] = module_list[-1]
