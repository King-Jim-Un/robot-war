import logging
from pathlib import Path
from typing import List, Tuple

from robot_war.vm.instructions import CodeLine

try:
    from robot_war.vm.exec_context import SandBox
    from robot_war.vm.source_module import Module
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

        if parts[0] == ROBOT_WAR:
            self.load_api(sandbox, parts)
        else:
            from robot_war.vm.source_functions import Function
            modules_loaded, tuples_to_load = self.find_load_files(sandbox, parts)
            arg_names = ["modules_loaded"] + [f"to_load{index}" for index in range(len(tuples_to_load))]
            with Function("__import_name__", arg_names) as import_name:
                import_name.LOAD_FAST("modules_loaded")
                link_up = bool(modules_loaded)
                for index in range(len(tuples_to_load)):
                    import_name.LOAD_FAST(f"to_load{index}")
                    import_name.LOAD_MODULE_FILE_1()
                    if link_up:
                        import_name.LOAD_FAST(f"to_load{index}")
                        import_name.LOAD_CONST("0")
                        import_name.LOAD_SUBSCR()
                        import_name.LOAD_MODULE_FILE_2()
                        link_up = True

                import_name.LOAD_CONST("0" if from_list is None else "-1")
                import_name.LOAD_SUBSCR()
                import_name.RETURN_VALUE()
            sandbox.call_function(import_name, modules_loaded, *tuples_to_load)
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
        if dotted in sandbox.playground.all_modules:
            # Great, continue from there
            modules_loaded, tuples_to_load = ImportName.find_files(sandbox, parts[1:], dot_path, start_dir / parts[0])
            return [sandbox.playground.all_modules[dotted]] + modules_loaded, tuples_to_load

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
        if parts[0] in sandbox.playground.all_modules:
            # Found it; start there
            return ImportName.find_files(sandbox, parts, [], sandbox.playground.root_path)

        # We haven't loaded any of that yet, but the files might exist. Look for the files.
        if (sandbox.playground.root_path / f"{parts[0]}.py").exists() or \
                (sandbox.playground.root_path / parts[0] / "__init__.py").exists():
            # Found it; start there
            return ImportName.find_files(sandbox, parts, [], sandbox.playground.root_path)

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
        from robot_war.vm.source_module import Module
        module_dot_name, file_path = sandbox.pop()
        module_list: List[Module] = sandbox.pop()
        from robot_war.vm.source_functions import Function
        with Function("__load_module_file_1__", ["module_list"]) as load:
            # Note that we're not putting a call on this stack since we don't want this to be user-callable!
            load.POP_TOP()  # Discard the None that will be returned by importing the module
            load.LOAD_FAST("module_list")  # Return the module list we create in advance
            load.RETURN_VALUE()  # This will do the push
        sandbox.call_function(load, module_list)
        module = Module(module_dot_name.split(".")[-1])
        module_list.append(module)
        sandbox.call_function(module.read_source_file(file_path))


class LoadModuleFile2(CodeLine):  # Not in parser
    def exec(self, sandbox: SandBox):
        """
        pop TOS: module_dot_name: str
        TOS1: [module(0), module(1), ... module(N)]
        Set module(N-1).module_dot_name = module(N)
        """
        module_dot_name: str = sandbox.pop()
        module_name = module_dot_name.split(".")[-1]
        from robot_war.vm.source_module import Module
        module_list: List[Module] = sandbox.peek(-1)
        module_list[-2].name_dict[module_name] = module_list[-1]
