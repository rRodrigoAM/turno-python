import pygame
from pathlib import Path

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
BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = 'turno-python/game'
FONTS_DIR = 'turno-python/game/assets/fonts'

pygame.font.init()

FONT = pygame.font.Font(str(FONTS_DIR / "regular.ttf"), 30)
SMALL_FONT = pygame.font.Font(str(FONTS_DIR / "regular.ttf"), 20)
TITLE_FONT = pygame.font.Font(str(FONTS_DIR / "title.ttf"), 40)