import logging

from robot_war.game_engine.rw_engine import RWEngine

# Constants:
LOG = logging.getLogger(__name__)
SCREEN_SIZE = 1280, 720


def main():
    RWEngine(SCREEN_SIZE).loop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("robot_war.vm.instructions").setLevel(logging.WARNING)  # Op-codes executed
    logging.getLogger("robot_war.vm.exec_context").setLevel(logging.WARNING)  # push/pop values
    main()
