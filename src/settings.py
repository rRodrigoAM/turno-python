import pygame

# Dimensões
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (100, 100, 100)

# Fontes
pygame.font.init()
FONT = pygame.font.SysFont("Arial", 26, bold=True)
SMALL_FONT = pygame.font.SysFont("Arial", 20)
TITLE_FONT = pygame.font.SysFont("Arial", 40, bold=True)
