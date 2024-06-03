from dataclasses import dataclass, field
import logging
from pathlib import Path
import pygame
from typing import Dict, Optional, Generator, List

from robot_war.exceptions import RobotWarSystemExit, BlockThread
from robot_war.vm.api_class import ApiClass
from robot_war.vm.exec_context import Playground, SandBox
from robot_war.vm.run_program import run_program

# Constants:
LOG = logging.getLogger(__name__)
ROOT_PATH = Path(__file__).parent
ROBOT_IMAGE_FILENAME = ROOT_PATH / "assets" / "robot1.png"
USER_FILENAME = ROOT_PATH / "user-scripts" / "test-script.py"


@dataclass
class Sprite:
    image: pygame.Surface
    position: tuple = (0.0, 0.0)
    facing: float = 0.0

    def draw(self, screen: pygame.Surface):
        screen.blit(pygame.transform.rotate(self.image, -self.facing), self.position)


@dataclass
class Sprites:
    sprites: Dict[int, Sprite] = field(default_factory=dict)

    def add(self, sprite: Sprite) -> int:
        self.sprites[id(sprite)] = sprite
        return id(sprite)

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
        screen.blit(pygame.transform.rotate(self.image, -self.facing), self.position)


@dataclass
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

        # Note that run_program doesn't block while the program runs. It loads a program into the VM and the execution
        # must be advanced by steps or by calling exec_through()
        self.playground = MyPlayground(USER_FILENAME, game_engine=self)
        sandbox = MySandbox(self.playground)
        self.playground.sandboxes = [sandbox]
        self.workers: List[BlockGenerator] = []

        run_program(USER_FILENAME, sandbox)
        self.user_running = True

    def paint_ui(self):
        self.screen.fill("slateblue4")
        self.sprites.draw(self.screen)

    def backend(self):
        if self.user_running:
            for sandbox in self.playground.sandboxes:
                try:
                    sandbox.step()
                except RobotWarSystemExit:
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


def main():
    game = RobotWarEngine((1280, 720))
    game.loop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("robot_war.vm.instructions").setLevel(logging.WARNING)
    main()
