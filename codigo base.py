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
# CONFIGURAÇÕES DO JOGO
# =========================
VIDA_NAVE = 5
pontos = 0


# =========================
# CLASSE BASE (não usada diretamente)
# =========================
class Entidade(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()


# =========================
# JOGADOR - PRIMEIRA PESSOA
# =========================
class Jogador:
    def __init__(self):
        self.vida = VIDA_NAVE
        # imagem da arma (temporária)
        self.image = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (0, 200, 255), (60, 60, 80, 140))  # arma placeholder

        self.posicao = (LARGURA - 350, ALTURA - 260)  # posição fixa na tela

    def desenhar(self, tela):
        tela.blit(self.image, self.posicao)


# =========================
# TIRO
# (RAYCAST SIMPLIFICADO)
# =========================
class Tiro:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# =========================
# ROBO (APPROACH / ESCALA)
# =========================
class Robo(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # imagem base do robô (substituir depois)
        self.base_image = pygame.Surface((60, 60))
        self.base_image.fill((255, 0, 0))

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

        # Se chegar na janela → dano
        if tamanho >= 160:  # robô "encostou" na janela
            global VIDA_NAVE
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

        # TIRO
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            tiro = Tiro(mx, my)

            # verificar se atingiu robô
            for robo in list(robos):
                if robo.rect.collidepoint(mx, my):
                    robo.kill()
                    pontos += 1

    # Spawna robôs
    spawn_timer += 1
    if spawn_timer >= 50:
        novo = Robo()
        robos.add(novo)
        spawn_timer = 0

    robos.update()

    # GAME OVER
    if VIDA_NAVE <= 0:
        print("A NAVE FOI INVADIDA!")
        rodando = False

    # DESENHO
    TELA.fill((5, 5, 20))

    # (coloque aqui a imagem da janela futuramente)
    pygame.draw.rect(TELA, (40, 40, 60), (300, 50, 680, 350))

    robos.draw(TELA)
    jogador.desenhar(TELA)

    # mira
    mx, my = pygame.mouse.get_pos()
    pygame.draw.circle(TELA, (255, 255, 255), (mx, my), 8, 2)

    # HUD
    font = pygame.font.SysFont(None, 32)
    hud = font.render(f"Vida da Nave: {VIDA_NAVE}  |  Pontos: {pontos}", True, (255, 255, 255))
    TELA.blit(hud, (10, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()