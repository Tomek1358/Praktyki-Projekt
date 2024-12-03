import pygame #należy wpisać w terminalu: pip install pygame
import random
import sys

# Inicjalizacja Pygame
pygame.init()

SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 1000
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jakas tam gra")

jump_sound = pygame.mixer.Sound("jump.wav")
shoot_sound = pygame.mixer.Sound("shoot.wav")

player_image = pygame.image.load("gracz.png").convert_alpha()
enemy_image = pygame.image.load("wrog.png").convert_alpha()
powerup_bigger_bullets_image = pygame.image.load("wiekszepociski.png").convert_alpha()
powerup_higher_damage_image = pygame.image.load("wiekszydmg.png").convert_alpha()
powerup_higher_jump_image = pygame.image.load("wiekszyskok.png").convert_alpha()
bullet_image = pygame.image.load("pocisk.png").convert_alpha()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(player_image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed_x = 0
        self.speed_y = 0
        self.on_ground = False
        self.bullet_size = (10, 5)
        self.damage = 1
        self.jump_height = -20

    def update(self):
        self.speed_y += 1
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.speed_y = 0
            self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.speed_y = self.jump_height
            self.on_ground = False
            jump_sound.play()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(enemy_image, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed_x = random.choice([-2, 2])
        self.hp = 2

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed_x *= -1

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, effect):
        super().__init__()
        self.effect = effect
        if effect == "bigger_bullets":
            self.image = pygame.transform.scale(powerup_bigger_bullets_image, (30, 30))
        elif effect == "higher_damage":
            self.image = pygame.transform.scale(powerup_higher_damage_image, (30, 30))
        elif effect == "higher_jump":
            self.image = pygame.transform.scale(powerup_higher_jump_image, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, size, damage):
        super().__init__()
        self.image = pygame.transform.scale(bullet_image, size)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_x = 10 * direction
        self.damage = damage

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
            self.kill()

all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
power_ups = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

for i in range(10):
    platform = Platform(random.randint(0, SCREEN_WIDTH - 100), random.randint(200, SCREEN_HEIGHT - 50), 100, 20)
    all_sprites.add(platform)
    platforms.add(platform)

power_up_effects = ["bigger_bullets", "higher_damage", "higher_jump"]
for i in range(5):
    effect = random.choice(power_up_effects)
    power_up = PowerUp(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT - 100), effect)
    all_sprites.add(power_up)
    power_ups.add(power_up)

for i in range(5):
    enemy = Enemy(random.randint(0, SCREEN_WIDTH - 40), random.randint(100, SCREEN_HEIGHT - 100))
    all_sprites.add(enemy)
    enemies.add(enemy)

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.speed_x = -5
            elif event.key == pygame.K_RIGHT:
                player.speed_x = 5
            elif event.key == pygame.K_SPACE:
                player.jump()
            elif event.key == pygame.K_f:
                direction = 1 if player.speed_x >= 0 else -1
                bullet = Bullet(player.rect.centerx, player.rect.centery, direction, player.bullet_size, player.damage)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                player.speed_x = 0

    all_sprites.update()

    for platform in platforms:
        if player.rect.colliderect(platform.rect) and player.speed_y > 0:
            player.rect.bottom = platform.rect.top
            player.speed_y = 0
            player.on_ground = True

    power_up_hits = pygame.sprite.spritecollide(player, power_ups, True)
    for power_up in power_up_hits:
        if power_up.effect == "bigger_bullets":
            player.bullet_size = (20, 10)
        elif power_up.effect == "higher_damage":
            player.damage += 1
        elif power_up.effect == "higher_jump":
            player.jump_height = -30

    for bullet in bullets:
        enemy_hits = pygame.sprite.spritecollide(bullet, enemies, False)
        for enemy in enemy_hits:
            enemy.hp -= bullet.damage
            bullet.kill()
            if enemy.hp <= 0:
                enemy.kill()

    screen.fill(BLACK)
    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()