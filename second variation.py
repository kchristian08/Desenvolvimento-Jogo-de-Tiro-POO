import pygame
import random
import sys

pygame.init()

LARGURA = 1280
ALTURA = 720
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Robot Defense - First Person")

FPS = 60
clock = pygame.time.Clock()

# =========================
# CARREGAMENTO DAS IMAGENS
# =========================

# ➤ CENÁRIO
try:
    IMG_FUNDO = pygame.image.load("").convert()
    IMG_FUNDO = pygame.transform.scale(IMG_FUNDO, (LARGURA, ALTURA))

    IMG_JANELA = pygame.image.load("").convert_alpha()

except:
    # Se as imagens não existirem, gera placeholders
    IMG_FUNDO = pygame.Surface((LARGURA, ALTURA))
    IMG_FUNDO.fill((5, 5, 20))

    IMG_JANELA = pygame.Surface((700, 350))
    IMG_JANELA.fill((40, 40, 60))

# ➤ ARMA DO JOGADOR (ANIMAÇÃO DO TIRO)
try:
    ARMA_IDLE = pygame.image.load("assets/jogador/arma_idle.png").convert_alpha()
    ARMA_TIRO = [
        pygame.image.load("assets/jogador/arma_tiro1.png").convert_alpha(),
        pygame.image.load("assets/jogador/arma_tiro2.png").convert_alpha(),
        pygame.image.load("assets/jogador/arma_tiro3.png").convert_alpha(),
    ]
except:
    ARMA_IDLE = pygame.Surface((200, 200), pygame.SRCALPHA)
    pygame.draw.rect(ARMA_IDLE, (0, 200, 255), (60, 60, 80, 140))

    ARMA_TIRO = [pygame.Surface((200, 200), pygame.SRCALPHA) for _ in range(3)]
    for surf in ARMA_TIRO:
        pygame.draw.rect(surf, (0, 150, 255), (60, 60, 80, 140))


# ➤ ROBÔS (MODELOS DIFERENTES)
ROBO_SPRITES = []
for i in range(1, 4):  # robo1.png robo2.png robo3.png
    try:
        img = pygame.image.load(f"assets/robos/robo{i}.png").convert_alpha()
        ROBO_SPRITES.append(img)
    except:
        surf = pygame.Surface((60, 60))
        surf.fill((255, 0, 0))
        ROBO_SPRITES.append(surf)

# =========================
# VARIÁVEIS DO JOGO
# =========================
VIDA_NAVE = 5
pontos = 0


# =========================
# JOGADOR
# =========================
class Jogador:
    def __init__(self):
        self.vida = VIDA_NAVE
        self.posicao = (LARGURA - 350, ALTURA - 260)

        self.anim_index = 0
        self.anim_timer = 0
        self.atirando = False

    def atirar(self):
        self.atirando = True
        self.anim_index = 0
        self.anim_timer = 0

    def desenhar(self, tela):
        if self.atirando:
            self.anim_timer += 1
            frame = ARMA_TIRO[self.anim_index]

            # controla a velocidade da animação
            if self.anim_timer >= 5:
                self.anim_index += 1
                self.anim_timer = 0

                if self.anim_index >= len(ARMA_TIRO):
                    self.atirando = False  # volta ao idle

            tela.blit(frame, self.posicao)

        else:
            tela.blit(ARMA_IDLE, self.posicao)


# =========================
# ROBO (APPROACH / ESCALA)
# =========================
class Robo(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # escolhe aleatoriamente um dos sprites
        self.base_image = random.choice(ROBO_SPRITES)

        self.scale = 0.2
        self.image = pygame.transform.scale(self.base_image, (20, 20))

        self.x = random.randint(500, 800)
        self.y = random.randint(50, 150)

        self.speed = random.uniform(0.005, 0.012)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        self.scale += self.speed

        tamanho = int(60 * self.scale)
        self.image = pygame.transform.scale(self.base_image, (tamanho, tamanho))
        self.rect = self.image.get_rect(center=(self.x, self.y))

        global VIDA_NAVE
        if tamanho >= 160:
            VIDA_NAVE -= 1
            self.kill()


# =========================
# GRUPOS
# =========================
robos = pygame.sprite.Group()
jogador = Jogador()

spawn_timer = 0

# =========================
# LOOP PRINCIPAL
# =========================
rodando = True
while rodando:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            jogador.atirar()

            mx, my = pygame.mouse.get_pos()

            # verifica se acertou algum robo
            for robo in list(robos):
                if robo.rect.collidepoint(mx, my):
                    robo.kill()
                    pontos += 1

    # spawna robo
    spawn_timer += 1
    if spawn_timer >= 50:
        robos.add(Robo())
        spawn_timer = 0

    robos.update()

    if VIDA_NAVE <= 0:
        print("A NAVE FOI INVADIDA!")
        rodando = False

    # DESENHO
    TELA.blit(IMG_FUNDO, (0, 0))
    TELA.blit(IMG_JANELA, (290, 40))  # posição central da janela

    robos.draw(TELA)
    jogador.desenhar(TELA)

    # MIRA
    mx, my = pygame.mouse.get_pos()
    pygame.draw.circle(TELA, (255, 255, 255), (mx, my), 8, 2)

    # HUD
    font = pygame.font.SysFont(None, 32)
    hud = font.render(f"Vida da Nave: {VIDA_NAVE}  |  Pontos: {pontos}", True, (255, 255, 255))
    TELA.blit(hud, (10, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()