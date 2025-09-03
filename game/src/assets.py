# src/assets.py
from pathlib import Path
import pygame
from typing import Tuple

# Diretórios
BASE_DIR = Path(__file__).resolve().parents[1]   # sobe 1 nível: src/ -> projeto/
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR

# Nomes dos arquivos (ajuste se necessário)
BACKGROUND_NAME = "fundo.png"
PLAYER_NAME = "gordo.png"
ENEMY_NAME = "inimigo.png"

def _safe_load_image(path: Path, size: Tuple[int, int] = None) -> pygame.Surface:
    """
    Tenta carregar a imagem. Se falhar, retorna um placeholder Surface
    e imprime o erro para debug.
    """
    try:
        surf = pygame.image.load(str(path))
        try:
            surf = surf.convert_alpha()
        except Exception:
            surf = surf.convert()
        if size:
            surf = pygame.transform.scale(surf, size)
        return surf
    except Exception as e:
        print(f"[assets] Falha ao carregar {path}: {e}. Usando placeholder.")
        w, h = size if size else (128, 128)
        placeholder = pygame.Surface((w, h), pygame.SRCALPHA)
        placeholder.fill((120, 120, 120, 255))  # cinza
        pygame.draw.line(placeholder, (200, 50, 50), (0, 0), (w, h), 4)
        pygame.draw.line(placeholder, (200, 50, 50), (w, 0), (0, h), 4)
        return placeholder

def load_assets():
    """
    Carrega os assets principais e retorna como um dicionário.
    Usa _safe_load_image para evitar que o jogo quebre.
    """
    assets = {
        "background": _safe_load_image(IMAGES_DIR / BACKGROUND_NAME),
        "player": _safe_load_image(IMAGES_DIR / PLAYER_NAME),
        "enemy": _safe_load_image(IMAGES_DIR / ENEMY_NAME),
    }
    return assets

# Exemplo de uso de log para combate
combat_log = []

def add_log(message: str):
    combat_log.append(message)
    if len(combat_log) > 5:
        combat_log.pop(0)
