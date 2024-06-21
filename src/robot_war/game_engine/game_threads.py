from robot_war.exceptions import BlockGenerator
from robot_war.vm.exec_context import SandBox


class ThreadBox(SandBox):
    def block_generator(self, block_generator: BlockGenerator):
        self.playground.game_engine.block_generator(self, block_generator)
