from typing import Dict, Any

from robot_war.user_functions import CodeDict


class Module:
    # Class members:
    all_modules: Dict[str, "Module"] = {}

    # Instance members:
    name: str
    code_blocks_by_name: CodeDict

    def __init__(self, name: str):
        self.name = name
        self.code_blocks_by_name = {}

    def __repr__(self):
        return f"Module({self.name}, {len(self.code_blocks_by_name)} code blocks)"
