import pygame
import random
import math
pygame.init()

# ====================================================================
# CONFIGURAÇÕES INICIAIS
# ====================================================================

LARGURA = 1280
ALTURA = 720
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("AstroWarfare")

FPS = 60
clock = pygame.time.Clock()

# ====================================================================
# SPRITES
# ====================================================================

SPACE = pygame.image.load("sprites/background/space pixel art.png").convert()
FUNDO = pygame.image.load("sprites/background/corredor pixel art.png").convert()
MAO_ARMA = pygame.image.load("sprites/mao/arms.png").convert_alpha()

ROBO_IMG = pygame.image.load("sprites/robos/Robo.png").convert_alpha()
ROBO_IMG = pygame.transform.scale(ROBO_IMG, (150, 150))

ROBO_CHEFAO_IMG = pygame.image.load("sprites/robos/chefão.png").convert_alpha()
ROBO_CHEFAO_IMG = pygame.transform.scale(ROBO_CHEFAO_IMG, (250, 250))

EXPLOSAO_IMG = pygame.image.load("sprites/robos/kabum.png").convert_alpha()
EXPLOSAO_IMG = pygame.transform.scale(EXPLOSAO_IMG, (150, 150))

POWERUP_IMG = pygame.image.load("sprites/powerup/velocidade de tiro.png").convert_alpha()
POWERUP_IMG = pygame.transform.scale(POWERUP_IMG, (75, 75))

# Sons
TIRO_SOM = pygame.mixer.Sound("sons/tiro.mpeg")
EXPLOSAO_SOM = pygame.mixer.Sound("sons/explosao.mpeg")
POWERUP_SOM = pygame.mixer.Sound("sons/power up.mpeg")

# ====================================================================
# CLASSES
# ====================================================================

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = MAO_ARMA
        self.rect = self.image.get_rect(bottomright=(LARGURA - 70, ALTURA - 0))
        self.health = 3
        self.score = 0

    def get_mira_pos(self):
        return pygame.mouse.get_pos()

    def update(self):
        pass


class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=start_pos)

        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        dist = math.hypot(dx, dy)
        if dist == 0: dist = 1
        speed = 30

        self.velocity = (dx / dist * speed, dy / dist * speed)

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        if (self.rect.bottom < 0 or self.rect.top > ALTURA or
            self.rect.left > LARGURA or self.rect.right < 0):
            self.kill()


# ====================================================================
# ROBÔS (Polimorfismo)
# ====================================================================

class Robo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = ROBO_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed


class RoboLento(Robo):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 1


class RoboRapido(Robo):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 6


class RoboZigueZague(Robo):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 3
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
        self.radius = 70
        self.center = (x, y)

    def update(self):
        self.angle += 0.10
        self.rect.x = self.center[0] + math.cos(self.angle) * self.radius
        self.rect.y = self.center[1] + math.sin(self.angle) * self.radius + 1


class RoboSaltador(Robo):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.jump_timer = random.randint(60, 90)

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
        dist = math.hypot(dx, dy)

        if dist != 0:
            dx, dy = dx / dist, dy / dist
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed


# ====================================================================
# CHEFÃO
# ====================================================================

class RoboChefe(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = ROBO_CHEFAO_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 250

    def update(self):
        pass  # boss fica completamente parado no Easter Egg


# ====================================================================
# POWER-UP
# ====================================================================

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo):
        super().__init__()
        self.image = POWERUP_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.tipo = tipo

    def update(self):
        self.rect.y += 2
        if self.rect.top > ALTURA:
            self.kill()


# ====================================================================
# EXPLOSÃO
# ====================================================================

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


# ====================================================================
# PERSONAGENS ESPECIAIS DO EASTER EGG
# ====================================================================

class PersonagemEaster(pygame.sprite.Sprite):
    def __init__(self, imagem_path, y):
        super().__init__()
        self.image = pygame.image.load().convert_alpha()
        self.image = pygame.transform.scale(self.image, (90, 140))
        self.rect = self.image.get_rect(midleft=(-120, y))
        self.vel = 3

    def update(self):
        self.rect.x += self.vel
        if self.rect.left > LARGURA + 50:
            self.kill()

# ====================================================================
# GRUPOS
# ====================================================================

all_sprites = pygame.sprite.Group()
robos = pygame.sprite.Group()
bullets = pygame.sprite.Group()
explosions = pygame.sprite.Group()
powerups = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
easter_group = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# ====================================================================
# VARIÁVEIS
# ====================================================================

triple_shot_active = False
triple_shot_timer = 0
boss_spawned = False
boss = None
easter_egg_ativado = False
pode_atirar = True

# ====================================================================
# FUNÇÃO SPAWN
# ====================================================================

def spawn_robo():
    tipo = random.choice([RoboLento, RoboRapido, RoboZigueZague,
                          RoboCiclico, RoboSaltador, RoboCacador])
    if tipo == RoboCacador:
        robo = tipo(random.randint(100, LARGURA - 100), -50, player)
    else:
        robo = tipo(random.randint(100, LARGURA - 100), -50)

    robos.add(robo)
    all_sprites.add(robo)

# ====================================================================
# LOOP PRINCIPAL
# ====================================================================

running = True
spawn_timer = 0

while running:
    dt = clock.tick(FPS)
    TELA.blit(FUNDO, (0, 0))

    # EVENTOS ==========================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # TIRO
        if event.type == pygame.MOUSEBUTTONDOWN:

            # bloqueia tiro se o Easter Egg estiver ativo
            if not pode_atirar:
                continue

            mx, my = pygame.mouse.get_pos()
            cx, cy = player.rect.center

            if triple_shot_active:
                spread = 20
                for off in [0, -spread, +spread]:
                    b = Bullet((cx, cy), (mx + off, my))
                    bullets.add(b)
                    all_sprites.add(b)
            else:
                b = Bullet((cx, cy), (mx, my))
                bullets.add(b)
                all_sprites.add(b)

            TIRO_SOM.play()

    # SPAWN ROBÔS ======================
    spawn_timer += 1
    if spawn_timer > 30:
        spawn_robo()
        spawn_timer = 0

    # UPDATE ===========================
    all_sprites.update()
    easter_group.update()

    # TIMER DO TIRO TRIPLO
    if triple_shot_active:
        triple_shot_timer -= dt
        if triple_shot_timer <= 0:
            triple_shot_active = False

    # COLISÕES ROBÔ X BULLET ===========
    hits = pygame.sprite.groupcollide(robos, bullets, True, True)
    for hit in hits:
        player.score += 300
        EXPLOSAO_SOM.play()

        explosao = Explosao(hit.rect.center)
        explosions.add(explosao)
        all_sprites.add(explosao)

        # CHANCE DE POWER UP
        if random.random() < 0.10:
            p = PowerUp(hit.rect.centerx, hit.rect.centery, "triple_shot")
            powerups.add(p)
            all_sprites.add(p)

    # COLISÃO POWER-UP X BULLET ========
    hits_power = pygame.sprite.groupcollide(powerups, bullets, True, True)
    if hits_power:
        triple_shot_active = True
        triple_shot_timer = 5000
        POWERUP_SOM.play()

    # EASTER EGG ATIVA AOS 2000 PONTOS ========
    if player.score >= 2000 and not easter_egg_ativado:
        easter_egg_ativado = True
        pode_atirar = False  # bloqueia tiro

        # CHEFÃO PARADO NO CENTRO
        boss = RoboChefe(LARGURA // 2, ALTURA // 2)
        boss_spawned = True
        boss_group.add(boss)
        all_sprites.add(boss)

        # PERSONAGENS APARECEM
        h2d2 = PersonagemEaster("sprites/easter/h2d2.png", ALTURA - 200)
        c3po = PersonagemEaster("sprites/easter/c3po.png", ALTURA - 350)

        easter_group.add(h2d2)
        easter_group.add(c3po)
        all_sprites.add(h2d2)
        all_sprites.add(c3po)

    # DANO NO CHEFÃO ===================
    if boss_spawned and boss is not None:
        hits_boss = pygame.sprite.spritecollide(boss, bullets, True)
        if hits_boss:
            for _ in hits_boss:
                boss.health -= 5

            EXPLOSAO_SOM.play()

        if boss.health <= 0:
            boss.kill()
            boss = None
            boss_spawned = False
            easter_egg_ativado = False
            pode_atirar = True
            player.score += 100

    # ROBÔS PASSANDO ===================
    for robo in list(robos):
        if robo.rect.top > ALTURA:
            robo.kill()
            player.health -= 1
            if player.health <= 0:
                print("Game Over")
                running = False

    # DRAW =============================
    all_sprites.draw(TELA)
    easter_group.draw(TELA)
    TELA.blit(player.image, player.rect)

    # HUD ===============================
    font = pygame.font.SysFont(None, 36)

    TELA.blit(font.render(f"Pontos: {player.score}", True, (255, 255, 255)), (10, 10))
    TELA.blit(font.render(f"Vidas: {player.health}", True, (255, 0, 0)), (10, 50))

    if triple_shot_active:
        segundos = max(0, triple_shot_timer // 1000)
        TELA.blit(font.render(f"Tiro Triplo: {segundos}s", True, (255, 255, 0)), (10, 90))

    if boss_spawned and boss is not None:
        texto = font.render(f"Boss HP: {max(0, boss.health)}", True, (255, 0, 0))
        rect = texto.get_rect(bottomright=(LARGURA - 20, ALTURA - 20))
        TELA.blit(texto, rect)

    pygame.display.flip()

pygame.quit()