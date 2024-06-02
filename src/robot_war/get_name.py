from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class GetName:
    """Base class for classes """
    name_dict: Dict[str, Any] = field(default_factory=dict)

    def get_name(self, name: str):
        return self.name_dict[name]
