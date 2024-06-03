from dataclasses import dataclass
import logging
from pygame import Vector2

from robot_war.exceptions import BlockThread
from robot_war.vm.api_class import ApiClass
from robot_war.vm.source_module import Module

# Constants:
LOG = logging.getLogger(__name__)
DEG_PER_TICK = 2.0
DIST_PER_TICK = 3.0


@dataclass
class Robot(ApiClass):
    position: Vector2 = Vector2(500.0, 300.0)
    facing: float = 0.0

    def turn_right(self, angle):
        LOG.warning("turn_right(%f)", angle)
        stop_facing = self.facing + angle

        def turn():
            while self.facing < stop_facing:
                self.facing += DEG_PER_TICK
                yield
            self.facing = stop_facing

        raise BlockThread(turn())

    def forward(self, distance):
        LOG.warning("forward(%f)", distance)
        stop = self.position + Vector2.from_polar((distance, self.facing))

        def move():
            moved = 0.0
            while moved < distance:
                self.position += Vector2.from_polar((DIST_PER_TICK, self.facing))
                moved += DIST_PER_TICK
                yield
            self.position = stop

        raise BlockThread(move())

    def shoot(self, distance):
        LOG.warning("shoot(%f)", distance)


MODEL0_MODULE = Module("model0", name_dict={"Robot": Robot})
