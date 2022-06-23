import pygame
import pygame


class Background(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/bg.png')
        self.rect = self.image.get_rect(topleft=(0, 0))


class Ground(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/ground.png')
        self.rect = self.image.get_rect(topleft=(GROUND_SCROLL, 768))

    def update(self):
        global GROUND_SCROLL, SCROLL_SPEED
        GROUND_SCROLL -= SCROLL_SPEED
        if abs(GROUND_SCROLL) > 35:
            GROUND_SCROLL = 0
