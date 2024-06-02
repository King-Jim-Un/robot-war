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
        super().exec(sandbox)
        module: Module = sandbox.peek(-1)
        sandbox.push(module.get_name(self.note))


class ImportName(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        from_list = sandbox.pop()
        level = sandbox.pop()
        assert level == 0, "TODO: non-zero level imports"
        parts = self.note.split(".")

        from robot_war.exec_context import CODE_STEP
        from robot_war.instructions.data import LoadFast, LoadConst, LoadSubscript
        from robot_war.instructions.flow_control import ReturnValue
        from robot_war.source_functions import Function, CodeBlock
        code_block = CodeBlock()
        ip = 0

        def add(instruction):
            code_block.code_lines[instruction.offset] = instruction
            return instruction.offset + CODE_STEP

        if parts[0] == ROBOT_WAR:
            self.load_api(sandbox, parts)
        else:
            modules_loaded, tuples_to_load = self.find_load_files(sandbox, parts)
            ip = add(LoadFast(None, ip, "LOAD_FAST", 0, "modules_loaded"))
            link_up = bool(modules_loaded)
            for index in range(len(tuples_to_load)):
                ip = add(LoadFast(None, ip, "LOAD_FAST", index + 1, f"tuples_to_load[{index}]"))
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
            # TODO: Need to be some sort of mechanism to verify that we actually imported the name

    @staticmethod
    def load_api(sandbox: SandBox, parts: List[str]):
        if parts == [ROBOT_WAR]:
            from robot_war.api import API_MODULE
            sandbox.push(API_MODULE)
        elif len(parts) == 2:
            from robot_war.api import MODELS
            sandbox.push(MODELS[parts[1]])
        else:
            raise ImportError(f"Unable to import {'.'.join(parts)}")

    @staticmethod
    def find_files(sandbox: SandBox, parts: List[str], from_dot_path: List[str],
                   start_dir: Path) -> Tuple[List[Module], List[Tuple[str, Path]]]:
        """
        Searches files and returns a tuple like this:
        (
            [Module(a), Module(a.b)],  # Modules already loaded
            [("a.b.c", Path(a.b.c)), ("a.b.c.d", Path(a.b.c.d))]  # Modules we still need to load
        )
        """
        # Nothing to find?
        if not parts:
            return [], []  # Simpler to test once here than everywhere we call us

        # Is the next part already loaded?
        dot_path = from_dot_path + parts[:1]
        dotted = ".".join(dot_path)
        if dotted in sandbox.all_modules:
            # Great, continue from there
            modules_loaded, tuples_to_load = ImportName.find_files(sandbox, parts[1:], dot_path, start_dir / parts[0])
            return [sandbox.all_modules[dotted]] + modules_loaded, tuples_to_load

        # Does the next part exist as a directory?
        path = start_dir / parts[0] / "__init__.py"
        if path.exists():
            # Yes, continue from there
            modules_loaded, tuples_to_load = ImportName.find_files(sandbox, parts[1:], dot_path, start_dir / parts[0])
            return modules_loaded, [(dot_path, path)] + tuples_to_load

        # Does the next part exist as a regular file?
        path = start_dir / f"{parts[0]}.py"
        if path.exists():
            # Yes, stop there
            return [], [(dotted, path)]

        # We can't find the next bit
        raise ImportError(f"Can't find module {parts[0]}")

    @staticmethod
    def find_load_files(sandbox: SandBox, parts: List[str]) -> Tuple[List[Module], List[Tuple[str, Path]]]:
        # First, let's check if we've already loaded some of this path starting from the root of the user's program
        if parts[0] in sandbox.all_modules:
            # Found it; start there
            return ImportName.find_files(sandbox, parts, [], sandbox.root_path)

        # We haven't loaded any of that yet, but the files might exist. Look for the files.
        if (sandbox.root_path / f"{parts[0]}.py").exists() or (sandbox.root_path / parts[0] / "__init__.py").exists():
            # Found it; start there
            return ImportName.find_files(sandbox, parts, [], sandbox.root_path)

        # We can't find it from the root, so let's do some relative searching.

        # Is the current module a directory?
        current_module = sandbox.context.function.code_block.module
        if current_module.path.name == "__init__.py":
            # Yes, so search from here
            return ImportName.find_files(sandbox, parts, current_module.dot_path, current_module.path.parent)

        # The current module is a regular file, so search for a sibling
        return ImportName.find_files(sandbox, parts, current_module.dot_path[:-1], current_module.path.parent)


class LoadModuleFile1(CodeLine):  # Not in parser
    def exec(self, sandbox: SandBox):
        """
        pop TOS: (module_dot_name: str, file_path: Path)
        pop TOS1: [module(0), module(1), ... module(N-1)]
        Load a module_name as module(N) from file_path
        push TOS: [module(0), module(1), ... module(N)]
        """
        super().exec(sandbox)
        from robot_war.source_module import Module
        module_dot_name, file_path = sandbox.pop()
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
        module_block = parse_source_file(sandbox, module_dot_name, file_path)
        module_list.append(sandbox.all_modules[module_dot_name])
        sandbox.call_function(Function("__load_module_file_1__", launcher_block), module_list)
        sandbox.call_function(Function(module_dot_name, module_block))


class LoadModuleFile2(CodeLine):  # Not in parser
    def exec(self, sandbox: SandBox):
        """
        pop TOS: module_dot_name: str
        TOS1: [module(0), module(1), ... module(N)]
        Set module(N-1).module_dot_name = module(N)
        """
        module_dot_name: str = sandbox.pop()
        module_name = module_dot_name.split(".")[-1]
        from robot_war.source_module import Module
        module_list: List[Module] = sandbox.peek(-1)
        module_list[-2].name_dict[module_name] = module_list[-1]
