from dataclasses import dataclass
import logging
from pygame import Vector2

from robot_war.exceptions import BlockGenerator
from robot_war.vm.api_class import RobotApi
from robot_war.vm.source_module import Module

# Constants:
LOG = logging.getLogger(__name__)
DEG_PER_TICK = 6.0
DIST_PER_TICK = 10.0
FIRE_PER_TICK = 20.0


@dataclass
class Robot(RobotApi):
    # NOTE: START MEMBER NAMES WITH AN UNDERSCORE UNLESS IT'S OKAY FOR THE USER TO ACCESS THEM!
    _moving: bool = False
    _turning: bool = False
    _shooting: bool = False

    def turn_right(self, angle):
        LOG.warning("turn_right(%f)", angle)
        stop_facing = self.facing + angle

        def turn():
            assert not self._turning
            self._turning = True
            try:
                while self.facing < stop_facing:
                    self.facing += DEG_PER_TICK
                    yield
                self.facing = stop_facing
            finally:
                self._turning = False

        raise BlockGenerator(turn())

    def forward(self, distance):
        LOG.warning("forward(%f)", distance)
        stop = self.position + Vector2.from_polar((distance, self.facing))

        def move():
            assert not self._moving
            self._moving = True
            try:
                moved = 0.0
                while moved < distance:
                    self.position += Vector2.from_polar((DIST_PER_TICK, self.facing))
                    moved += DIST_PER_TICK
                    yield
                self.position = stop
            finally:
                self._moving = False

        raise BlockGenerator(move())

    def shoot(self, distance):
        LOG.warning("shoot(%f)", distance)
        game_engine = self._playground.game_engine
        fireball = game_engine.create_sprite(game_engine.fireball_image, self.position, self.facing)
        stop = self.position + Vector2.from_polar((distance, self.facing))

        def shot():
            assert not self._shooting
            self._shooting = True
            try:
                moved = 0.0
                while moved < distance:
                    fireball.position += Vector2.from_polar((FIRE_PER_TICK, self.facing))
                    moved += FIRE_PER_TICK
                    yield
                fireball.position = stop
                game_engine.delete_sprite(fireball)
            finally:
                self._shooting = False

        raise BlockGenerator(shot())


MODEL0_MODULE = Module("model0", name_dict={"Robot": Robot})
