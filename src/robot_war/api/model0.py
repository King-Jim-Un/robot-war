from dataclasses import dataclass

from robot_war.vm.api_class import ApiClass
from robot_war.vm.source_module import Module


@dataclass
class Robot(ApiClass):
    x: float = 0.0
    y: float = 0.0
    facing: float = 0.0

    def turn_right(self, distance):
        print(f"turn_right({distance})")

    def forward(self, distance):
        print(f"forward({distance})")

    def shoot(self, distance):
        print(f"shoot({distance})")


MODEL0_MODULE = Module("model0", name_dict={"Robot": Robot})
