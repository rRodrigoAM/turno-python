# src/assets.py
from pathlib import Path
import pygame
from typing import Tuple

# Assets dir: projeto/
BASE_DIR = Path(__file__).resolve().parents[1]   # sobe 1 nível: src/ -> projeto/
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR

# nomes esperados (ajuste se necessário)S
BACKGROUND_NAME = "fundo.png"
PLAYER_NAME = "gordo.png"
ENEMY_NAME = "inimigo.png"

def _safe_load_image(path: Path, size: Tuple[int,int] = None) -> pygame.Surface:
    """
    Tenta carregar a imagem. Se falhar, retorna um placeholder Surface
    e imprime o erro para debug.
    """
    try:
        surf = pygame.image.load(str(path))
        # convert_alpha melhora performance ao desenhar (transparência)
        try:
            surf = surf.convert_alpha()
        except Exception:
            surf = surf.convert()
        if size:
            surf = pygame.transform.scale(surf, size)
        return surf
    except Exception as e:
        print(f"[assets] Falha ao carregar {path}: {e}. Usando placeholder.")
        # placeholder simples: cor sólida com texto opcional
        w, h = size if size else (128, 128)
        placeholder = pygame.Surface((w, h), pygame.SRCALPHA)
        placeholder.fill((120, 120, 120, 255))  # cinza
        # desenha um X simples
        pygame.draw.line(placeholder, (200,50,50), (0,0), (w,h), 4)
        pygame.draw.line(placeholder, (200,50,50), (w,0), (0,h), 4)
        return placeholder

def load_assets():
    """Carrega e retorna os assets como dicionário"""
    assets = {
        "background": pygame.image.load(IMAGES_DIR / BACKGROUND_NAME).convert(),
        "player": pygame.image.load(IMAGES_DIR / PLAYER_NAME).convert_alpha(),
        "enemy": pygame.image.load(IMAGES_DIR / ENEMY_NAME).convert_alpha(),
    }
    return assets
