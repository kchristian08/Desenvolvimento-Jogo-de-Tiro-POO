import pygame
import random
import math
pygame.init()

LARGURA = 1280
ALTURA = 720
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("AstroWarfare")

# Clock
FPS = 60
clock = pygame.time.Clock()

# Sprites
SPACE = pygame.image.load("sprites/background/space pixel art.png").convert() 
FUNDO = pygame.image.load("sprites/background/corredor pixel art.png").convert()
MAO_ARMA = pygame.image.load("sprites/mao/arms.png").convert_alpha()
ROBO_IMG = pygame.image.load("sprites/robos/Robo.png").convert_alpha()
ROBO_CHEFAO_IMG = pygame.image.load("sprites/robos/chefão.png").convert_alpha()
EXPLOSAO_IMG = pygame.image.load("sprites/robos/kabum.png").convert_alpha()
POWERUP_IMG = pygame.image.load("sprites/powerup/velocidade de tiro.png").convert_alpha()

# Sons
TIRO_SOM = pygame.mixer.Sound("")
EXPLOSAO_SOM = pygame.mixer.Sound("")
POWERUP_SOM = pygame.mixer.Sound("")

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = MAO_ARMA
        self.rect = self.image.get_rect(center=(LARGURA//2, ALTURA//2))
        self.health = 5
        self.score = 0

    def update(self):
        # Mira segue o mouse
        self.rect.center = pygame.mouse.get_pos()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=pos)
        self.speed = 15

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

# Classe base para todos os robôs (polimorfismo)
class Robo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = ROBO_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2

    def update(self):
        self.rect.y += self.speed

class RoboLento(Robo):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 1

class RoboRapido(Robo):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 4

class RoboZigueZague(Robo):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 2
        self.direction = 1
        self.counter = 0

    def update(self):
        self.rect.y += self.speed
        self.rect.x += self.direction * 3
        self.counter += 1
        if self.counter % 50 == 0:
            self.direction *= -1

class RoboCiclico(Robo):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.angle = 0
        self.radius = 50
        self.center = (x, y)

    def update(self):
        self.angle += 0.05
        self.rect.x = self.center[0] + math.cos(self.angle) * self.radius
        # desce devagar
        self.rect.y = self.center[1] + math.sin(self.angle) * self.radius + 1

class RoboSaltador(Robo):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.jump_timer = random.randint(30, 60)

    def update(self):
        self.jump_timer -= 1
        if self.jump_timer <= 0:
            self.rect.y += random.randint(-50, 50)
            self.jump_timer = random.randint(30, 60)
        self.rect.y += 2

class RoboCacador(Robo):
    def __init__(self, x, y, player):
        super().__init__(x, y)
        self.player = player
        self.speed = 2

    def update(self):
        dx = self.player.rect.x - self.rect.x
        dy = self.player.rect.y - self.rect.y
        distance = math.hypot(dx, dy)
        if distance != 0:
            dx, dy = dx / distance, dy / distance
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

# Chefão
class RoboChefe(Robo):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = ROBO_CHEFAO_IMG
        self.health = 50

    def update(self):
        self.rect.y += 1

# Power-up
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo):
        super().__init__()
        self.image = POWERUP_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.tipo = tipo

# Explosão
class Explosao(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = EXPLOSAO_IMG
        self.rect = self.image.get_rect(center=pos)
        self.timer = 10

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

# Grupos de Sprites
all_sprites = pygame.sprite.Group()
robos = pygame.sprite.Group()
bullets = pygame.sprite.Group()
explosions = pygame.sprite.Group()
powerups = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Funções auxiliares
def spawn_robo():
    tipo = random.choice([RoboLento, RoboRapido, RoboZigueZague, RoboCiclico, RoboSaltador, RoboCacador])
    if tipo == RoboCacador:
        robo = tipo(random.randint(100, LARGURA-100), -50, player)
    else:
        robo = tipo(random.randint(100, LARGURA-100), -50)
    robos.add(robo)
    all_sprites.add(robo)

# Loop principal
running = True
spawn_timer = 0

while running:
    clock.tick(FPS)
    TELA.blit(FUNDO, (0, 0))

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            bullet = Bullet(player.rect.center)
            bullets.add(bullet)
            all_sprites.add(bullet)
            TIRO_SOM.play()

    # Spawn de robôs
    spawn_timer += 1
    # tempo de spawn
    if spawn_timer > 60:
        spawn_robo()
        spawn_timer = 0

    # Atualizações
    all_sprites.update()

    # Colisões
    hits = pygame.sprite.groupcollide(robos, bullets, True, True)
    for hit in hits:
        player.score += 10
        EXPLOSAO_SOM.play()
        explosao = Explosao(hit.rect.center)
        explosions.add(explosao)
        all_sprites.add(explosao)

    # Robôs atingem nave
    for robo in robos:
        if robo.rect.top > ALTURA:
            robo.kill()
            player.health -= 1
            if player.health <= 0:
                print("Game Over")
                running = False

    # Desenhar sprites
    all_sprites.draw(TELA)

    # HUD
    font = pygame.font.SysFont(None, 36)
    text_score = font.render(f"Pontos: {player.score}", True, (255, 255, 255))
    text_health = font.render(f"Vidas: {player.health}", True, (255, 0, 0))
    TELA.blit(text_score, (10, 10))
    TELA.blit(text_health, (10, 50))

    pygame.display.flip()

pygame.quit()