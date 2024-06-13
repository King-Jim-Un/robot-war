import logging
from pathlib import Path
from typing import List, Tuple, Optional

from robot_war.vm.instructions import CodeLine

try:
    from robot_war.vm.exec_context import SandBox
    from robot_war.vm.source_module import Module
except ImportError:
    SandBox = Module = None

# Constants:
LOG = logging.getLogger(__name__)
ROBOT_WAR = "robot_war"

# Import parameters are kinda arcane, so here's a reference:
#
# =================== CODE: ===================  ==================== NOTES: ====================
# >>> import x
#     LOAD_CONST               0 (0)
#     LOAD_CONST               1 (None)
#     IMPORT_NAME              0 (x)             find and load x
#     STORE_NAME               0 (x)             module.x = x
# >>> import x.y
#     LOAD_CONST               0 (0)
#     LOAD_CONST               1 (None)
#     IMPORT_NAME              0 (x.y)           find and load x, y
#     STORE_NAME               1 (x)             x.y = y; module.x = x
# >>> from x import y
#     LOAD_CONST               0 (0)
#     LOAD_CONST               1 (('y',))
#     IMPORT_NAME              0 (x)             find and load x
#     IMPORT_FROM              1 (y)
#     STORE_NAME               1 (y)             module.y = x.y
#     POP_TOP
# >>> from x.y import z
#     LOAD_CONST               0 (0)
#     LOAD_CONST               1 (('z',))
#     IMPORT_NAME              0 (x.y)           find and load x, y
#     IMPORT_FROM              1 (z)
#     STORE_NAME               1 (z)             x.y = y; module.z = x.y.z
#     POP_TOP
# >>> from x.y import *
#     LOAD_CONST               0 (0)
#     LOAD_CONST               1 (('*',))
#     IMPORT_NAME              0 (x.y)           find and load x, y
#     IMPORT_STAR                                x.y = y; module.* = x.y.* (visible symbols only)
# >>> from .x import y, z
#     LOAD_CONST               0 (1)
#     LOAD_CONST               1 (('y', 'z'))
#     IMPORT_NAME              0 (x)             load x from .
#     IMPORT_FROM              1 (y)             module.y = x.y
#     STORE_NAME               1 (y)
#     IMPORT_FROM              2 (z)             module.z = x.z
#     STORE_NAME               2 (z)
#     POP_TOP
# >>> from ..x import y, z
#     LOAD_CONST               0 (2)
#     LOAD_CONST               1 (('y', 'z'))
#     IMPORT_NAME              0 (x)             load x from ..
#     IMPORT_FROM              1 (y)             module.y = x.y
#     STORE_NAME               1 (y)
#     IMPORT_FROM              2 (z)             module.z = x.z
#     STORE_NAME               2 (z)
#     POP_TOP


class ImportFrom(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        module: Module = sandbox.peek(-1)
        sandbox.push(module.get_name(self.note))


class ImportName(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        from_list: Optional[Tuple[str]] = sandbox.pop()
        # None: import x.y.z
        # Tuple[str] like ("y", "z"): from x import y, z
        level: int = sandbox.pop()
        # 0: from x import y
        # 1: from .x import y
        # 2: from ..x import y
        parts: List[str] = self.note.split(".")
        # ["x", "y", "z"]: import x.y.z

        if (level == 0) and (parts[0] == ROBOT_WAR):
            self.load_api(sandbox, parts)
        else:
            from robot_war.vm.source_functions import Function
            modules_loaded, tuples_to_load = self.find_load_files(sandbox, level, parts, from_list)

            # Now that we know which modules we have and which files must be loaded, we can create a function to do this
            # for us. We can't just do it here because loading modules involves running the top-level code in those
            # modules. We don't do that. We just add it to the stack and let it run at its own rate. But when it
            # completes, we will need to discard the return code (a None) and handle the rest of the operation.
            arg_names = ["modules_loaded"] + [f"to_load{index}" for index in range(len(tuples_to_load))]
            with Function("__import_name__", arg_names) as import_name:
                import_name.LOAD_FAST("modules_loaded")
                link_up = bool(modules_loaded)  # if we've got any loaded, we'll need to link the module name into it
                for index in range(len(tuples_to_load)):
                    import_name.LOAD_FAST(f"to_load{index}")
                    import_name.LOAD_MODULE_FILE_1()  # load the module
                    if link_up:
                        import_name.LOAD_FAST(f"to_load{index}")
                        import_name.LOAD_CONST("0")
                        import_name.LOAD_SUBSCR()  # push module_dot_name
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
                   start_dir: Path, from_list: Optional[Tuple[str]]) -> Tuple[List[Module], List[Tuple[str, Path]]]:
        """
        Searches files and returns a tuple like this:
        (
            [Module(a), Module(a.b)],  # Modules already loaded
            [("a.b.c", Path(a.b.c)), ("a.b.c.d", Path(a.b.c.d))]  # Modules we still need to load
        )
        """
        # parts:
        #     ["x", "y", "z"]: import x.y.z
        # from_dot_path:
        #     ["x", "y", "z"]: we're currently at package x.y.z and searching children in there
        # start_dir:
        #     current directory we're searching in
        # from_list:
        #     None: import x.y.z
        #     Tuple[str] like ("y", "z"): from x import y, z
        if parts in ([], ["*"]):
            if not from_list:
                # No more files to find (simpler to test once here than everywhere we call us)
                return [], []
            else:
                modules_loaded = []
                tuples_to_load = []
                for name in from_list:
                    loaded, to_load = ImportName.find_files(sandbox, [name], from_dot_path, start_dir, [])
                    modules_loaded += loaded
                    tuples_to_load += to_load
                return modules_loaded, tuples_to_load

        # Is the next part already loaded?
        dot_path = from_dot_path + parts[:1]
        dotted = ".".join(dot_path)
        if dotted in sandbox.playground.all_modules:
            # Great, continue from there
            modules_loaded, tuples_to_load = ImportName.find_files(
                sandbox, parts[1:], dot_path, start_dir / parts[0], from_list)
            return [sandbox.playground.all_modules[dotted]] + modules_loaded, tuples_to_load

        # Does the next part exist as a directory?
        path = start_dir / parts[0] / "__init__.py"
        if path.exists():
            # Yes, continue from there
            modules_loaded, tuples_to_load = ImportName.find_files(
                sandbox, parts[1:], dot_path, start_dir / parts[0], from_list)
            return modules_loaded, [(dot_path, path)] + tuples_to_load

        # Does the next part exist as a regular file?
        path = start_dir / f"{parts[0]}.py"
        if path.exists():
            # Yes, stop there
            return [], [(dotted, path)]

        # We can't find the next bit
        raise ImportError(f"Can't find module {parts[0]}")

    @staticmethod
    def find_load_files(sandbox: SandBox, level: int, parts: List[str],
                        from_list: Optional[Tuple[str]]) -> Tuple[List[Module], List[Tuple[str, Path]]]:
        # from_list:
        #     None: import x.y.z
        #     Tuple[str] like ("y", "z"): from x import y, z
        # level:
        #     0: from x import y
        #     1: from .x import y
        #     2: from ..x import y
        # parts:
        #     ["x", "y", "z"]: import x.y.z

        current_module = sandbox.context.function.code_block.module

        # Are we searching in the dark?
        if level == 0:
            # Yes, let's check if we've already loaded some of this path starting from the root of the user's program
            if parts[0] in sandbox.playground.all_modules:
                # Found it; start there
                return ImportName.find_files(sandbox, parts, [], sandbox.playground.root_path, from_list)

            # We haven't loaded any of that yet, but the files might exist. Look for the files.
            if (sandbox.playground.root_path / f"{parts[0]}.py").exists() or \
                    (sandbox.playground.root_path / parts[0] / "__init__.py").exists():
                # Found it; start there
                return ImportName.find_files(sandbox, parts, [], sandbox.playground.root_path, from_list)

            # We can't find it from the root, so let's do some relative searching.

            # Is the current module a package?
            if current_module.path.name == "__init__.py":
                # Yes, so search from here
                return ImportName.find_files(
                    sandbox, parts, current_module.dot_path, current_module.path.parent, from_list)

            # The current module is a regular file, so search for a sibling
            return ImportName.find_files(
                sandbox, parts, current_module.dot_path[:-1], current_module.path.parent, from_list)

        else:
            # We know this is a relative import, but is the current module a package?
            assert current_module.path.name == "__init__.py"
            dot_path = current_module.dot_path if level == 1 else current_module.dot_path[:1 - level]
            path = current_module.path.parents[level - 1]
            return ImportName.find_files(sandbox, parts, dot_path, path, from_list)


class ImportStar(CodeLine):
    def exec(self, sandbox: SandBox):
        """
        """
        super().exec(sandbox)
        from robot_war.vm.source_module import Module
        import_from: Module = sandbox.pop()
        import_to = sandbox.context.function.code_block.module
        for name, value in import_from.name_dict.items():
            if name[0] not in ["<", "-"]:
                import_to.set_name(name, value)


class LoadModuleFile1(CodeLine):
    def exec(self, sandbox: SandBox):
        """
        pop TOS: (module_dot_list: str, file_path: Path)
        pop TOS1: [module(0), module(1), ... module(N-1)]
        Load a module_name as module(N) from file_path
        push TOS: [module(0), module(1), ... module(N)]
        """
        super().exec(sandbox)
        from robot_war.vm.source_module import Module
        module_dot_list, file_path = sandbox.pop()
        module_list: List[Module] = sandbox.pop()
        from robot_war.vm.source_functions import Function
        with Function("__load_module_file_1__", ["module_list"]) as load:
            # Note that we're not putting a call on this stack since we don't want this to be user-callable!
            load.POP_TOP()  # Discard the None that will be returned by importing the module
            load.LOAD_FAST("module_list")  # Return the module list we create in advance
            load.RETURN_VALUE()  # This will do the push
        sandbox.call_function(load, module_list)
        module = Module(module_dot_list[-1], path=file_path, dot_path=module_dot_list)
        module_list.append(module)
        sandbox.call_function(module.read_source_file(file_path))


class LoadModuleFile2(CodeLine):
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
