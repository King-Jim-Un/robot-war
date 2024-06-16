from dataclasses import dataclass, field
import logging
from pathlib import Path
import pygame
from typing import Dict, Optional, Generator, List

from robot_war.exceptions import RobotWarSystemExit, BlockThread, ReturnException
from robot_war.vm.api_class import ApiClass
from robot_war.vm.exec_context import Playground, SandBox
from robot_war.vm.source_module import Module

# Constants:
LOG = logging.getLogger(__name__)
ROOT_PATH = Path(__file__).parent
ROBOT_IMAGE_FILENAME = ROOT_PATH / "assets" / "robot1.png"
FIREBALL_IMAGE_FILENAME = ROOT_PATH / "assets" / "fireball1.png"
USER_FILENAME = ROOT_PATH / "user-scripts" / "test-script.py"


@dataclass
class Sprite:
    image: pygame.Surface
    position: pygame.Vector2 = pygame.Vector2(0.0, 0.0)
    facing: float = 0.0

    def draw(self, screen: pygame.Surface):
        transformed = pygame.transform.rotate(self.image, -self.facing)
        size = pygame.Vector2(transformed.get_size())
        screen.blit(transformed, self.position - (size / 2))


@dataclass
class Sprites:
    sprites: Dict[int, Sprite] = field(default_factory=dict)

    def add(self, sprite: Sprite) -> Sprite:
        self.sprites[id(sprite)] = sprite
        return sprite

    def delete(self, sprite: Sprite):
        del self.sprites[id(sprite)]

    def draw(self, screen: pygame.Surface):
        for sprite in self.sprites.values():
            sprite.draw(screen)


class GameEngine:
    def __init__(self, video_size):
        pygame.init()
        self.screen = pygame.display.set_mode(video_size)
        self.clock = pygame.time.Clock()
        self.sprites = Sprites()

    def loop(self):
        ui_running = True
        while ui_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    ui_running = False

            self.paint_ui()
            pygame.display.flip()
            self.backend()
            self.clock.tick(60)

        pygame.quit()

    def paint_ui(self):
        pass

    def backend(self):
        pass


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
class MyPlayground(Playground):
    game_engine: Optional["RobotWarEngine"] = None

    def set_robot(self, robot: ApiClass):
        super().set_robot(robot)
        sprite = RobotSprite(self.game_engine.robot_image, robot)
        self.game_engine.sprites.add(sprite)


class MySandbox(SandBox):
    def block_thread(self, block_thread: BlockThread):
        self.playground.game_engine.block_thread(self, block_thread)


@dataclass
class BlockGenerator:
    generator: Generator
    sandbox: SandBox


class RobotWarEngine(GameEngine):
    def __init__(self, video_size):
        super().__init__(video_size)
        self.robot_image = pygame.transform.scale_by(pygame.image.load(ROBOT_IMAGE_FILENAME), 0.25)
        self.fireball_image = pygame.transform.scale_by(pygame.image.load(FIREBALL_IMAGE_FILENAME), 0.2)

        # Note that call_function doesn't block while the program runs. It loads a program into the VM and the execution
        # must be advanced by steps in backend()
        self.playground = MyPlayground(USER_FILENAME, game_engine=self)
        sandbox = MySandbox(self.playground)
        self.playground.sandboxes = [sandbox]
        self.workers: List[BlockGenerator] = []
        module = Module("__main__")
        # TODO: Check if there's an __init__.py first? Not sure if that's right. Should test.
        sandbox.call_function(module.read_source_file(USER_FILENAME))
        self.user_running = True

    def paint_ui(self):
        self.screen.fill("slateblue4")
        self.sprites.draw(self.screen)

    def backend(self):
        if self.user_running:
            for sandbox in self.playground.sandboxes:
                try:
                    sandbox.step()
                except (RobotWarSystemExit, ReturnException):
                    self.user_running = False

        index = 0
        while index < len(self.workers):
            worker = self.workers[index]
            try:
                next(worker.generator)
            except StopIteration as stop:
                del self.workers[index]
                worker.sandbox.playground.sandboxes.append(worker.sandbox)
                worker.sandbox.push(stop.value)
            else:
                index += 1

    def block_thread(self, sandbox: SandBox, block_thread: BlockThread):
        # Find the sandbox
        for index, the_sandbox in enumerate(self.playground.sandboxes):
            if sandbox is the_sandbox:
                del self.playground.sandboxes[index]
                self.workers.append(BlockGenerator(block_thread.generator, sandbox))
                break
        else:
            raise KeyError("sandbox not found")

    def create_sprite(self, image: pygame.Surface, position: pygame.Vector2, facing: float) -> Sprite:
        return self.sprites.add(Sprite(image, pygame.Vector2(position), facing))

    def delete_sprite(self, sprite: Sprite):
        return self.sprites.delete(sprite)


def main():
    game = RobotWarEngine((1280, 720))
    game.loop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("robot_war.vm.instructions").setLevel(logging.WARNING)
    logging.getLogger("robot_war.vm.exec_context").setLevel(logging.WARNING)
    main()
