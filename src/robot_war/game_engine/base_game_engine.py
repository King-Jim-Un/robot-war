import pygame

from robot_war.game_engine.sprites import Sprites


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

        pygame.quit()

    def paint_ui(self):
        pass

    def backend(self):
        self.clock.tick(60)
