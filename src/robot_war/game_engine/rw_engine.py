from dataclasses import dataclass
import logging
import pygame
from typing import Optional, List

from robot_war.constants import CONSTANTS
from robot_war.exceptions import BlockGenerator
from robot_war.game_engine.base_game_engine import GameEngine
from robot_war.game_engine.sprites import Sprite
from robot_war.vm.api_class import ApiClass
from robot_war.vm.exec_context import Playground, SandBox
from robot_war.vm.source_module import Module

# Constants:
LOG = logging.getLogger(__name__)
USER_SCRIPT = CONSTANTS.PATHS.ROOT / "user-scripts" / "test-script.py"


class RobotSprite:
    def __init__(self, image: pygame.Surface, robot: ApiClass):
        self.image, self.robot = image, robot

    @property
    def position(self):
        return self.robot.position

    @property
    def facing(self):
        return self.robot.facing

    def draw(self, screen: pygame.Surface):
        transformed = pygame.transform.rotate(self.image, -self.facing)
        size = pygame.Vector2(transformed.get_size())
        screen.blit(transformed, self.position - (size / 2))


@dataclass(repr=False)
class ThreadGround(Playground):
    game_engine: Optional["RWEngine"] = None

    def set_robot(self, robot: ApiClass):
        super().set_robot(robot)
        sprite = RobotSprite(self.game_engine.robot_image, robot)
        self.game_engine.sprites.add(sprite)


class RWEngine(GameEngine):
    next_frame_time: float = 0

    def __init__(self, video_size):
        super().__init__(video_size)
        self.robot_image = pygame.transform.scale_by(pygame.image.load(CONSTANTS.PATHS.ROBOT_IMAGE), 0.25)
        self.fireball_image = pygame.transform.scale_by(pygame.image.load(CONSTANTS.PATHS.FIREBALL_IMAGE), 0.2)

        # Note that call_function doesn't block while the program runs. It loads a program into the VM and the execution
        # must be advanced by steps in backend()
        self.playground = ThreadGround(USER_SCRIPT, game_engine=self)
        sandbox = SandBox(self.playground)
        self.playground.sandboxes = [sandbox]
        self.workers: List[BlockGenerator] = []
        module = Module("__main__")
        # TODO: Check if there's an __init__.py first? Not sure if that's right. Should test.
        sandbox.call_function(module.read_source_file(USER_SCRIPT))
        self.user_running = True

    def paint_ui(self):
        self.screen.fill("slateblue4")
        self.sprites.draw(self.screen)

    def backend(self):
        self.playground.step_all(CONSTANTS.TIMING.FRAMES)
        self.clock.tick(CONSTANTS.TIMING.FRAME_RATE)

    def create_sprite(self, image: pygame.Surface, position: pygame.Vector2, facing: float) -> Sprite:
        return self.sprites.add(Sprite(image, pygame.Vector2(position), facing))

    def delete_sprite(self, sprite: Sprite):
        return self.sprites.delete(sprite)
