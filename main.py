import pygame 
from pygame.locals import *
from sys import exit

pygame.init()

# Tamanho da tela
x = 1280
y = 720

screen = pygame.display.set_mode((x, y))
pygame.display.set_caption("AstroWarfare")

# FUNDOS E ELEMENTOS PRINCIPAIS
bg = pygame.image.load('sprites/background/1.jpg').convert_alpha()
bg = pygame.transform.scale(bg, (x, y))

# BOTÕES DO MENU
new = pygame.image.load('sprites/botoes/new.png').convert_alpha()
new_hover = pygame.image.load('sprites/botoes/new_hover.png').convert_alpha()
new = pygame.transform.scale(new, (300, 150))
new_hover = pygame.transform.scale(new_hover, (300, 150))

continuar = pygame.image.load('sprites/botoes/continue.png').convert_alpha()
continuar_hover = pygame.image.load('sprites/botoes/continue_hover.png').convert_alpha()
continuar = pygame.transform.scale(continuar, (300, 150))
continuar_hover = pygame.transform.scale(continuar_hover, (300, 150))

exit_button = pygame.image.load('sprites/botoes/exit.png').convert_alpha()
exit_button = pygame.transform.scale(exit_button, (300, 150))

new_pos = (150, 250)
continuar_pos = (150, 350)
exit_button_pos = (150, 450)

new_rect = new.get_rect(topleft=new_pos)
continuar_rect = continuar.get_rect(topleft=continuar_pos)
exit_rect = exit_button.get_rect(topleft=exit_button_pos)

Rodando = True
clock = pygame.time.Clock()

while Rodando:
    for event in pygame.event.get():
        if event.type == QUIT:
            Rodando = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if new_rect.collidepoint(event.pos):
                print("New clicado!")

            elif continuar_rect.collidepoint(event.pos):
                print("Continuar clicado!")

            elif exit_rect.collidepoint(event.pos):
                print("Exit clicado!")
                Rodando = False  # Sai imediatamente

    # Fundo
    screen.blit(bg, (0, 0))

    # Hover dos botões
    mouse_pos = pygame.mouse.get_pos()

    # NEW
    if new_rect.collidepoint(mouse_pos):
        screen.blit(new_hover, new_pos)
    else:
        screen.blit(new, new_pos)

    # CONTINUAR
    if continuar_rect.collidepoint(mouse_pos):
        screen.blit(continuar_hover, continuar_pos)
    else:
        screen.blit(continuar, continuar_pos)

    # EXIT (sem hover)
    screen.blit(exit_button, exit_button_pos)

    pygame.display.update()
    clock.tick(60)

pygame.quit()