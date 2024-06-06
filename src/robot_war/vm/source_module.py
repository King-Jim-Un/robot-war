from dataclasses import dataclass, field
from dis import get_instructions, code_info
from inspect import getsource
import logging
from pathlib import Path
import re
from typing import Optional, List, Callable

from robot_war.constants import CODE_CLASS
from robot_war.vm.get_name import GetName
from robot_war.vm.source_functions import Function, CodeBlock

# Constants:
LOG = logging.getLogger(__name__)
SEARCH_NUM_ARGS = re.compile(r"^Argument count:\s+(\d+)", re.MULTILINE)
SEARCH_VAR_NAMES1 = re.compile(r"^Variable names:(.*)", re.MULTILINE | re.DOTALL)
SEARCH_VAR_NAMES2 = re.compile(r"(.*?)^\S", re.MULTILINE | re.DOTALL)
SEARCH_VAR_NAMES3 = re.compile(r"(\d+): (\w+)")


@dataclass(repr=False)
class Module(GetName, Function):
    path: Optional[Path] = None
    dot_path: List[str] = field(default_factory=list)  # ["animal", "feline", "cat"] means: import animal.feline.cat

    def __repr__(self):
        return f"Module({self.name}, {len(self.name_dict)} names)"

    def get_method(self, name: str):
        return self.get_name(name)

    def add_standard_python_function(self, standard_python_function: Callable):
        self.add_code(compile(getsource(standard_python_function), str(self.path), "exec"))

    def add_code(self, code: CODE_CLASS):
        from robot_war.vm.parse_source_file import OP_CODE_CLASSES

        # Code block
        code_block = CodeBlock(module=self)
        for instr in get_instructions(code):
            line_class = OP_CODE_CLASSES[instr.opname]
            instr_obj = line_class(instr.starts_line, instr.offset, instr.opname, instr.arg, instr.argrepr)
            code_block.code_lines[instr.offset] = instr_obj
        # self.set_name(str(code), code_block)

        # Number of arguments
        info_str = code_info(code)
        match = SEARCH_NUM_ARGS.search(info_str)
        assert match
        code_block.num_params = int(match.group(1))

        # Argument names
        match = SEARCH_VAR_NAMES1.search(info_str)
        if match:
            var_name_str = match.group(1)
            match = SEARCH_VAR_NAMES2.search(var_name_str)
            if match:
                var_name_str = match.group(1)
            var_name_dict = {int(index): name for index, name in SEARCH_VAR_NAMES3.findall(var_name_str)}
            code_block.param_names = [var_name_dict[index] for index in range(code_block.num_params)]

        # Function
        self.set_name(code.co_name, Function(code.co_name, code_block.param_names, code_block))

        # Grab other code blocks
        for constant in code.co_consts:
            if isinstance(constant, CODE_CLASS):
                self.add_code(constant)
