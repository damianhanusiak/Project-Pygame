import pygame
from pygame.locals import *
from variables import *
import random
import button
import background

pygame.init()

clock = pygame.time.Clock()

# Rozmiar okna
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# Tytułu okna
pygame.display.set_caption('Python Warrior')
# Tło dół
ground = pygame.image.load('img/ground.png')

# Menu
level_1_img = pygame.image.load("img/button_level_1.png").convert_alpha()
level_2_img = pygame.image.load("img/button_level_2.png").convert_alpha()
level_3_img = pygame.image.load("img/button_level_3.png").convert_alpha()
quit_img = pygame.image.load("img/button_quit.png").convert_alpha()
level_1_button = button.Button(336.5, 200, level_1_img, 1)
level_2_button = button.Button(336.5, 325, level_2_img, 1)
level_3_button = button.Button(336.5, 450, level_3_img, 1)
quit_button = button.Button(336.5, 570, quit_img, 1)

# muzyka
music = pygame.mixer.Sound('sounds/music.mp3')
music.set_volume(0.1)
music.play(loops=-1)

# dźwięk zdobytego punktu
point_sound = pygame.mixer.Sound('sounds/point.mp3')

# dźwięk uderzenia w przeciwnika
explosion_enemy = pygame.mixer.Sound('sounds/explosion.wav')
explosion_enemy.set_volume(0.25)

# dźwięk uderzenia w statek
explosion_us = pygame.mixer.Sound('sounds/explosion2.wav')
explosion_us.set_volume(0.25)

# dźwięk strzału
shoot_sound = pygame.mixer.Sound('sounds/laser.wav')
shoot_sound.set_volume(0.25)

# czcionka
font = pygame.font.SysFont('Exotc350 Bd BT', 80)
font2 = pygame.font.SysFont('Exotc350 Bd BT', 30)

# kolory
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)


# Klasa postaci - pythonBird
class PythonBird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.import_images()
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False
        self.jump_sound = pygame.mixer.Sound('sounds/jump.mp3')
        self.jump_sound.set_volume(0.2)

    def import_images(self):
        self.images = []
        for i in range(1, 4):
            img = pygame.image.load(f'img/python{i}.png')
            self.images.append(img)

    def add_gravity(self):
        self.vel += 0.5
        if self.vel > 8:
            self.vel = 8
        if self.rect.bottom < 768:
            self.rect.y += int(self.vel)

    def jump(self):
        if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
            self.clicked = True
            self.vel = -10
            self.jump_sound.play()
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

    def animation(self):
        self.counter += 1
        flap_cooldown = 5

        if self.counter > flap_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
        self.image = self.images[self.index]

    def rotate(self):
        self.image = pygame.transform.rotate(
            self.images[self.index], self.vel * -2)

    def kill_rotate(self):
        self.image = pygame.transform.rotate(
            self.images[self.index], -90)

    def update(self):
        if FLYING == True:
            self.add_gravity()
        if GAME_OVER == False:
            self.jump()
            self.animation()
            self.rotate()
        else:
            self.kill_rotate()


# Klasa przeszkód - rury
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()
        # Pozycja 1 - góra, pozycja -1 - dół
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(PIPE_GAP/2)]
        if position == -1:
            self.rect.topleft = [x, y + int(PIPE_GAP/2)]

    def update(self):
        self.rect.x -= SCROLL_SPEED
        if self.rect.right < 0:
            self.kill()


# Reset gry
def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(SCREEN_HEIGHT/2)
    SCORE = 0
    return SCORE


# Funckja zliczająca zdobyte punkty
def add_score():
    global PASS_PIPE, SCORE
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right and PASS_PIPE == False:
            PASS_PIPE = True
        if PASS_PIPE == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                SCORE += 1
                point_sound.play()
                PASS_PIPE = False


# Wykrywanie kolizji
def collision_detection():
    global GAME_OVER, FLYING
    # Wykrywanie kolizji
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        GAME_OVER = True
    # Jeśli postać uderzy w ziemię
    if flappy.rect.bottom >= 768:
        GAME_OVER = True
        FLYING = False


# Funkcja drukująca zdobyte punkty
def draw_score(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# Generowanie rur
def generate_pipes():
    global LAST_PIPE, PIPE_FREQUENCY
    time_now = pygame.time.get_ticks()
    if time_now - LAST_PIPE > PIPE_FREQUENCY:
        pipe_height = random.randint(-150, 150)
        btm_pipe = Pipe(SCREEN_WIDTH, int(
            SCREEN_HEIGHT/2) + pipe_height, -1)
        top_pipe = Pipe(SCREEN_WIDTH, int(
            SCREEN_HEIGHT/2) + pipe_height, 1)
        pipe_group.add(btm_pipe)
        pipe_group.add(top_pipe)
        LAST_PIPE = time_now


# --------------------------- LEVEL 1,2 ---------------------------
class Level_1():
    def __init__(self, speed_game, pipe_frequency):
        global SCROLL_SPEED, PIPE_FREQUENCY
        SCROLL_SPEED = speed_game
        PIPE_FREQUENCY = pipe_frequency


class Level_2(Level_1):
    def __init__(self, speed_game, pipe_frequency, add_speed, update_frequency):
        super().__init__(speed_game, pipe_frequency)
        global SCROLL_SPEED, PIPE_FREQUENCY
        SCROLL_SPEED = speed_game + add_speed
        PIPE_FREQUENCY = pipe_frequency - update_frequency
# -------------------------------------------------------------------


bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
background_group = pygame.sprite.Group()

flappy = PythonBird(100, int(SCREEN_HEIGHT / 2))
bird_group.add(flappy)

background = background.Background()
background_group.add(background)

# --------------------------- LEVEL 3 ---------------------------
# tło poziomu 3
bg = pygame.image.load('img/level3/bg.png')


def draw_bg():
    screen.blit(bg, (0, 0))


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# Klasa Pythonship - statek kosmiczny
class Pythonship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/level3/spaceship.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        # szybkość poruszania się statku
        speed = 8
        cooldown = 500
        GAME_OVER_LV3 = 0

        # poruszanie się statku
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += speed

        # aktualny czas
        time_now = pygame.time.get_ticks()
        # strzelanie
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            shoot_sound.play()
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = time_now

        self.mask = pygame.mask.from_surface(self.image)

        # pasek zdrowia
        pygame.draw.rect(
            screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(
                self.rect.width * (self.health_remaining / self.health_start)), 15))
        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            GAME_OVER_LV3 = -1
        return GAME_OVER_LV3


# klasa pocisków
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/level3/bullet.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            explosion_enemy.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)


# klasa przeciwników
class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(
            'img/level3/alien' + str(random.randint(1, 5)) + '.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction


# klasa pocisków przeciwników
class AlienBullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/level3/alien_bullet.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 3
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion_us.play()
            # uderzenie w statek
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)


# klasa eksplozji po strzale
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for i in range(1, 6):
            img = pygame.image.load(f'img/level3/exp{i}.png')
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        # animacja eksplozji
        self.counter += 1
        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]
        # jeśli ekspolzja się skończy tu usuń ją
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()


# Stworzenie sprite groups
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

# Stworzenie instancji statku
spaceship = Pythonship(int(SCREEN_WIDTH/2), SCREEN_HEIGHT - 100, 3)
spaceship_group.add(spaceship)


def create_aliens():
    for row in range(ROWS):
        for item in range(COLS):
            alien = Aliens(120 + item * 100, 100 + row * 70)
            alien_group.add(alien)


create_aliens()

level_3 = True
# ---------------------------------------------------------------

run = True
while run:
    clock.tick(FPS)
    # Rysowanie tła
    background_group.draw(screen)
    # Rysowanie postaci
    bird_group.draw(screen)
    bird_group.update()
    # Rysowanie rur
    pipe_group.draw(screen)
    # Rysowanie ziemi
    screen.blit(ground, (GROUND_SCROLL, 768))
    # Przyznawanie punktów
    add_score()
    # Drukowanie punktów
    font = pygame.font.SysFont('Arial Black', 70)
    white = (255, 255, 255)
    draw_score(str(SCORE), font, white, int(SCREEN_WIDTH / 2), 20)
    # Wykrywanie kolizji
    collision_detection()

    if GAME_OVER == False and FLYING == True:
        # Generowanie rur
        generate_pipes()
        # Porusznie dolnego tła, jeśli game over to stop
        GROUND_SCROLL -= SCROLL_SPEED
        if abs(GROUND_SCROLL) > 35:
            GROUND_SCROLL = 0
        pipe_group.update()

    # Menu
    if GAME_OVER == True:
        screen.fill((102, 178, 255))
        if level_1_button.draw(screen):
            GAME_OVER = False
            level_1 = Level_1(4, 1500)
            SCORE = reset_game()
        if level_2_button.draw(screen):
            GAME_OVER = False
            level_2 = Level_2(4, 1500, 2, 750)
            SCORE = reset_game()
        if level_3_button.draw(screen):
            run = False
            run_lvl_3 = True
            while run_lvl_3:
                clock.tick(FPS)
                # tło level 3
                draw_bg()
                time_now = pygame.time.get_ticks()
                # strzelanie
                if time_now - LAST_ALIEN_SHOT > ALIEN_COOLDOWN and len(alien_bullet_group) < 5 and len(alien_group) > 0:
                    attacking_alien = random.choice(alien_group.sprites())
                    alien_bullet = AlienBullets(
                        attacking_alien.rect.centerx, attacking_alien.rect.bottom)
                    alien_bullet_group.add(alien_bullet)
                    LAST_ALIEN_SHOT = time_now

                if len(alien_group) == 0:
                    GAME_OVER_LV3 = 1

                if GAME_OVER_LV3 == 0:
                    GAME_OVER_LV3 = spaceship.update()
                    bullet_group.update()
                    alien_group.update()
                    alien_bullet_group.update()
                    explosion_group.update()
                else:
                    if GAME_OVER_LV3 == -1:
                        draw_text('GAME OVER!', font, white, int(
                            SCREEN_WIDTH / 2 - 250), int(SCREEN_HEIGHT / 2))
                        draw_text('OTHER PROGRAMMING LANGUAGES HAVE BEATEN YOU.. PYTHON!', font2, white, int(
                            SCREEN_WIDTH / 2 - 340), int(SCREEN_HEIGHT / 2 + 150))
                    if GAME_OVER_LV3 == 1:
                        draw_text('PYTHON WIN!', font, white, int(
                            SCREEN_WIDTH / 2 - 250), int(SCREEN_HEIGHT / 2))
                        draw_text('YOU ARE THE BEST PROGRAMMING LANGUAGE.. PYTHON!', font2, white, int(
                            SCREEN_WIDTH / 2 - 270), int(SCREEN_HEIGHT / 2 + 150))

                spaceship_group.draw(screen)
                bullet_group.draw(screen)
                alien_group.draw(screen)
                alien_bullet_group.draw(screen)
                explosion_group.draw(screen)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run_lvl_3 = False

                pygame.display.update()

        if quit_button.draw(screen):
            run = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and FLYING == False and GAME_OVER == False:
            FLYING = True

    pygame.display.update()

pygame.quit()
