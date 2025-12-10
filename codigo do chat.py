import pygame
import random
import math
import sys

pygame.init()

# -------------------
# CONFIG
# -------------------
LARGURA = 1280
ALTURA = 720
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Robot Defense - OOP Edition")

FPS = 60
clock = pygame.time.Clock()

VIDA_NAVE = 5
pontos = 0

# caminhos de exemplo para imagens (opcional)
IMG_ROBO_PATH = "sprites/robots/robot.png"        # fallback se existir
IMG_BOSS_PATH = "sprites/robots/boss.png"
IMG_PLAYER_GUN = "sprites/player/gun.png"

# -------------------
# UTIL
# -------------------
def carregar_imagem(path, size=None, fallback_color=(200, 50, 50)):
    """Tenta carregar uma imagem; se falhar, cria um Surface colorido."""
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        surf = pygame.Surface(size if size else (60, 60), pygame.SRCALPHA)
        surf.fill(fallback_color)
        return surf

# -------------------
# ENTIDADE BASE (Herança)
# -------------------
class Entidade(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # encapsulamento: atributos "privados"
        self._hp = 1

    def dano(self, qtd=1):
        self._hp -= qtd
        if self._hp <= 0:
            self.kill()

    def update(self, *args):
        """Polimorfismo: subclasses vão sobrescrever este método."""
        pass

# -------------------
# JOGADOR (First Person)
# -------------------
class Jogador:
    def __init__(self):
        self.vida = VIDA_NAVE
        # tentar carregar sprite da arma, senão fallback
        self._image = carregar_imagem(IMG_PLAYER_GUN, (200, 200), (0, 200, 255))
        # posição fixa da arma (primeira pessoa)
        self.posicao = (LARGURA - 350, ALTURA - 260)
        # ponto de disparo central aproximado
        self._muzzle = (self.posicao[0] + 100, self.posicao[1] + 100)

    @property
    def muzzle_pos(self):
        return self._muzzle

    def desenhar(self, tela):
        tela.blit(self._image, self.posicao)

# -------------------
# TIRO (agora sprite para colisão)
# -------------------
class Tiro(pygame.sprite.Sprite):
    def __init__(self, x, y, target_pos, speed=900):
        super().__init__()
        self.image = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 240, 0), (3, 3), 3)
        self.rect = self.image.get_rect(center=(x, y))

        # direção e velocidade (pixels por segundo)
        dx = target_pos[0] - x
        dy = target_pos[1] - y
        dist = math.hypot(dx, dy) or 1
        self.vx = dx / dist * speed / FPS
        self.vy = dy / dist * speed / FPS

        self._life = 90  # frames de vida

    def update(self, *args):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self._life -= 1
        if self._life <= 0:
            self.kill()
        # se sair da tela, remove
        if (self.rect.right < 0 or self.rect.left > LARGURA or
            self.rect.bottom < 0 or self.rect.top > ALTURA):
            self.kill()

# -------------------
# ROBO BASE (comportamento comum)
# -------------------
class Robo(Entidade):
    def __init__(self, x=None, y=None, image=None):
        super().__init__()
        # try load image or fallback
        self.base_image = image if image else carregar_imagem(IMG_ROBO_PATH, (60, 60), (180, 30, 30))
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()

        # spawn posição
        self._x = x if x is not None else random.randint(300, 1100)
        self._y = y if y is not None else random.randint(60, 200)
        self.rect.center = (self._x, self._y)

        # velocidade padrão (pixels/frame)
        self._speed = random.uniform(1.0, 3.0)
        self._hp = 1

    def update(self, *args):
        """Base: escala igual ao seu 'depth' original (preservado do exemplo antigo)"""
        # por padrão não faz nada; subclasses movem-se
        pass

    def kill(self):
        """Sobrepor kill se quiser fazer efeitos; por enquanto apenas mata."""
        super().kill()

# -------------------
# SUBCLASSES (Comportamentos específicos)
# -------------------

# 1) RoboLento -> anda devagar em linha reta (para baixo)
class RoboLento(Robo):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._speed = random.uniform(0.6, 1.2)
        self._hp = 1

    def update(self, *args):
        # anda em linha reta para baixo em direção à "janela" (área central)
        self._y += self._speed
        self.rect.center = (int(self._x), int(self._y))
        # se chegar muito baixo -> causa dano na nave
        if self.rect.top > ALTURA - 120:
            global VIDA_NAVE
            VIDA_NAVE -= 1
            self.kill()

# 2) RoboRapido -> anda rápido
class RoboRapido(Robo):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._speed = random.uniform(3.0, 5.5)
        self._hp = 1

    def update(self, *args):
        self._y += self._speed
        self.rect.center = (int(self._x), int(self._y))
        if self.rect.top > ALTURA - 120:
            global VIDA_NAVE
            VIDA_NAVE -= 1
            self.kill()

# 3) RoboZigueZague -> muda direção a cada n pixels
class RoboZigueZague(Robo):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._speed = random.uniform(1.2, 2.4)
        self._direction = 1
        self._steps = 0
        self._change_every = random.randint(30, 60)
        self._hp = 1

    def update(self, *args):
        # zigue zague combinando movimento vertical e lateral
        self._y += self._speed
        self._x += self._direction * (self._speed * 1.2)
        self._steps += 1
        if self._steps >= self._change_every:
            self._direction *= -1
            self._steps = 0
        self.rect.center = (int(self._x), int(self._y))
        if self.rect.top > ALTURA - 120:
            global VIDA_NAVE
            VIDA_NAVE -= 1
            self.kill()

# 4) RoboCiclico -> movimento circular
class RoboCiclico(Robo):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._radius = random.randint(30, 90)
        self._angle = random.uniform(0, math.tau)
        self._angular_speed = random.uniform(0.02, 0.07)
        # center of circular motion slowly moves downward
        self._center_x = self._x
        self._center_y = self._y
        self._hp = 1

    def update(self, *args):
        self._angle += self._angular_speed
        self._center_y += 0.6  # drift down
        self._x = self._center_x + math.cos(self._angle) * self._radius
        self._y = self._center_y + math.sin(self._angle) * self._radius
        self.rect.center = (int(self._x), int(self._y))
        if self.rect.top > ALTURA - 120:
            global VIDA_NAVE
            VIDA_NAVE -= 1
            self.kill()

# 5) RoboSaltador -> dá "pulos" aleatórios
class RoboSaltador(Robo):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._speed = random.uniform(0.6, 1.6)
        self._jump_timer = random.randint(20, 60)
        self._hp = 1

    def update(self, *args):
        self._y += self._speed
        self._jump_timer -= 1
        if self._jump_timer <= 0:
            # pulo aleatório lateral e vertical
            self._x += random.randint(-80, 80)
            self._y -= random.randint(15, 60)
            self._jump_timer = random.randint(20, 80)
        # manter dentro das bordas horizontais
        self._x = max(50, min(LARGURA - 50, self._x))
        self.rect.center = (int(self._x), int(self._y))
        if self.rect.top > ALTURA - 120:
            global VIDA_NAVE
            VIDA_NAVE -= 1
            self.kill()

# 6) RoboCacador -> segue o jogador (mais difícil)
class RoboCacador(Robo):
    def __init__(self, jogador: Jogador, *a, **k):
        super().__init__(*a, **k)
        self._player = jogador
        self._speed = random.uniform(1.2, 2.6)
        self._hp = 1

    def update(self, *args):
        # move-se na direção do muzzle do jogador (ou centro da arma)
        target = self._player.muzzle_pos
        dx = target[0] - self._x
        dy = target[1] - self._y
        dist = math.hypot(dx, dy) or 1
        # vai em direção, com uma pequena variação
        self._x += dx / dist * self._speed
        self._y += dy / dist * self._speed
        self.rect.center = (int(self._x), int(self._y))
        if self.rect.collidepoint(target):
            global VIDA_NAVE
            VIDA_NAVE -= 1
            self.kill()

# 7) RoboChefao -> boss final com mais hp e ataque
class RoboChefao(Robo):
    def __init__(self, jogador: Jogador, *a, **k):
        # tentar carregar imagem do boss com maior tamanho
        image = carregar_imagem(IMG_BOSS_PATH, (180, 180), (120, 30, 180))
        super().__init__(x=LARGURA//2, y=80, image=image)
        self._hp = 15
        self._player = jogador
        self._phase_timer = 0
        self._vx = 2.0
        self._vy = 0.0

    def update(self, *args):
        # comportamento: move horizontalmente, ocasionalmente desce e atira (pode ser estendido)
        self._phase_timer += 1
        # balança horizontalmente
        self._x += self._vx
        if self._x < 200 or self._x > LARGURA - 200:
            self._vx *= -1
        # flutuação vertical lenta
        self._y += math.sin(self._phase_timer * 0.02) * 0.6
        self.rect.center = (int(self._x), int(self._y))
        # se o boss descer demais, causa dano
        if self.rect.top > ALTURA - 220:
            global VIDA_NAVE
            VIDA_NAVE -= 1
            self.kill()

    def dano(self, qtd=1):
        super().dano(qtd)
        # quando morrer, pode dar bastante pontos
        if not self.alive():
            global pontos
            pontos += 10

# -------------------
# GRUPOS
# -------------------
robos = pygame.sprite.Group()
tiros = pygame.sprite.Group()
todos = pygame.sprite.Group()  # caso queira agrupar tudo

# jogador
jogador = Jogador()

# spawn config
spawn_timer = 0
spawn_interval = 45  # frames
boss_spawned = False

# função fábrica de robôs (escolhe tipo aleatório)
def spawn_robo():
    tipo = random.choices(
        population=["lento","rapido","zig","ciclo","salta","caca"],
        weights=[20, 18, 18, 14, 14, 16],
        k=1
    )[0]
    if tipo == "lento":
        r = RoboLento()
    elif tipo == "rapido":
        r = RoboRapido()
    elif tipo == "zig":
        r = RoboZigueZague()
    elif tipo == "ciclo":
        r = RoboCiclico()
    elif tipo == "salta":
        r = RoboSaltador()
    else:
        r = RoboCacador(jogador)
    robos.add(r)
    todos.add(r)

# -------------------
# MAIN LOOP
# -------------------
rodando = True
font = pygame.font.SysFont(None, 32)

while rodando:
    dt = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # dispara tiro do jogador na direção do mouse
            mx, my = pygame.mouse.get_pos()
            sx, sy = jogador.muzzle_pos
            tiro = Tiro(sx, sy, (mx, my))
            tiros.add(tiro)
            todos.add(tiro)

    # spawn automático
    spawn_timer += 1
    # spawn mais rápido com o tempo ou pontuação
    if spawn_timer >= spawn_interval:
        spawn_robo()
        spawn_timer = 0
        # ajustar intervalo levemente
        spawn_interval = max(8, 45 - (pontos // 5))

    # spawn do boss quando pontos alcançados e boss não spawnado
    if pontos >= 20 and not boss_spawned:
        boss = RoboChefao(jogador)
        robos.add(boss)
        todos.add(boss)
        boss_spawned = True

    # atualizações
    robos.update()
    tiros.update()

    # colisões: tiros atingem robos
    hits = pygame.sprite.groupcollide(robos, tiros, False, True)  # remove tiro, não remove robo automático
    for robo_hit, lista_tiros in hits.items():
        # aplicar dano conforme o tipo (boss mais resistente)
        if isinstance(robo_hit, RoboChefao):
            robo_hit.dano(len(lista_tiros))  # cada tiro um dano
        else:
            robo_hit.kill()
            pontos += 1

    # checar se algum robo bateu diretamente na "janela" (tratado nas classes)
    # ver game over
    if VIDA_NAVE <= 0:
        print("A NAVE FOI INVADIDA!")
        rodando = False

    # DESENHO
    TELA.fill((5, 5, 20))
    # "janela" (área central)
    pygame.draw.rect(TELA, (40, 40, 60), (300, 50, 680, 350))

    # desenhar robôs e tiros (os sprites já carregam imagens)
    robos.draw(TELA)
    tiros.draw(TELA)

    # desenhar jogador em primeira pessoa
    jogador.desenhar(TELA)

    # mira
    mx, my = pygame.mouse.get_pos()
    pygame.draw.circle(TELA, (255, 255, 255), (mx, my), 8, 2)

    # HUD
    hud = font.render(f"Vida da Nave: {VIDA_NAVE}  |  Pontos: {pontos}", True, (255, 255, 255))
    TELA.blit(hud, (10, 10))

    # dica de boss
    if not boss_spawned and pontos >= 15:
        text = font.render("Boss chegando em breve...", True, (255, 200, 0))
        TELA.blit(text, (LARGURA//2 - 100, 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
