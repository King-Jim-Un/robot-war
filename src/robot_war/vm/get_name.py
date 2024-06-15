from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class GetName:
    """Base class for classes """
    name_dict: Dict[str, Any] = field(default_factory=dict)

    def get_name(self, name: str):
        return self.name_dict[name]

    def get_attr(self, name: str):
        return self.name_dict[name]

    def set_name(self, name: str, value: Any):
        self.name_dict[name] = value

    def set_attr(self, name: str, value: Any):
        self.name_dict[name] = value

    def del_name(self, name: str):
        del self.name_dict[name]
