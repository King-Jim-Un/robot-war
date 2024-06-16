from dataclasses import dataclass
from typing import Generator

from robot_war.exceptions import BlockThread
from robot_war.vm.exec_context import SandBox


@dataclass
class BlockGenerator:
    generator: Generator
    sandbox: SandBox


class ThreadBox(SandBox):
    def block_thread(self, block_thread: BlockThread):
        self.playground.game_engine.block_thread(self, block_thread)
