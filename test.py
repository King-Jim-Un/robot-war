import logging
from pathlib import Path
import pygame

from robot_war.exceptions import RobotWarSystemExit
from robot_war.vm.run_program import run_program, exec_through

# Constants:
LOG = logging.getLogger(__name__)
ROOT_PATH = Path(__file__).parent
ROBOT_IMAGE_FILENAME = ROOT_PATH / "assets" / "robot1.png"
USER_FILENAME = ROOT_PATH / "test-script.py"


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    robot_image = pygame.transform.scale_by(pygame.image.load(ROBOT_IMAGE_FILENAME), 0.25)

    # Note that run_program doesn't block while the program runs. It loads a program into the VM and the execution must
    # be advanced by steps or by calling exec_through()
    sandbox = run_program(USER_FILENAME).sandboxes[0]

    ui_running = user_running = True
    while ui_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ui_running = False

        screen.fill("slateblue4")
        screen.blit(robot_image, (500, 300))

        if user_running:
            try:
                sandbox.step()
            except RobotWarSystemExit:
                user_running = False

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("robot_war.vm.instructions").setLevel(logging.WARNING)
    main()
