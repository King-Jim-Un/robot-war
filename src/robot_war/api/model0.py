from dataclasses import dataclass
from pygame import Vector2

from robot_war.vm.api_class import ApiClass
from robot_war.vm.source_module import Module


@dataclass
class Robot(ApiClass):
    position: Vector2 = Vector2(500.0, 300.0)
    facing: float = 0.0

    def turn_right(self, angle):
        self.facing += angle

    def forward(self, distance):
        self.position += Vector2.from_polar((distance, self.facing))

    def shoot(self, distance):
        print(f"shoot({distance})")


MODEL0_MODULE = Module("model0", name_dict={"Robot": Robot})
