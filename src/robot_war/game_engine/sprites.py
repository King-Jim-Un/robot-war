from dataclasses import dataclass, field
import pygame
from typing import Dict


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
