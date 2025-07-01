# pygame_init.py
import pygame
from graficos import ANCHO, ALTO, FPS


def initialize_pygame_environment():
    """
    Inicializa Pygame, sus módulos (font, mixer), configura la pantalla,
    crea el reloj y carga/inicia la música de fondo.
    Retorna la superficie de pantalla y el objeto de reloj configurados.
    """
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Solitario")
    clock = pygame.time.Clock()

    pygame.mixer.music.load('musica_fondo.mp3')
    pygame.mixer.music.play(-1) # -1 reproduce indefinidamente
    pygame.mixer.music.set_volume(0.5)

    return screen, clock

def control_game_loop_timing(clock_object):
    """
    Controla la velocidad de fotogramas del juego basándose en el FPS global.
    """
    clock_object.tick(FPS)

def quit_pygame_environment():
    """
    Desinicializa todos los módulos de Pygame.
    """
    pygame.quit()