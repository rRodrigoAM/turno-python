from pathlib import Path
import pygame
from typing import Tuple

# Diretórios
BASE_DIR = Path(__file__).resolve().parents[1]   # sobe 1 nível: src/ -> raiz do projeto
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"

BACKGROUND_NAME = "fundo.png"
PLAYER_NAME = "gordo.png"
ENEMY_NAME = "inimigo.png"
ENEMY_DEAD_NAME = "inimigo_morreu.png"
BOSS_NAME = "guardiao.png"
EMERALD_NAME = "esmeralda.png"

def _safe_load_image(path: Path, size: Tuple[int, int] = None) -> pygame.Surface:
    """
    Carrega a imagem do disco. Se o arquivo estiver ausente ou inválido,
    devolve um placeholder para o jogo continuar rodando sem quebrar.
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
        print(f"Falha ao carregar {path}: {e}. Usando placeholder.")
        w, h = size if size else (128, 128)
        placeholder = pygame.Surface((w, h), pygame.SRCALPHA)
        placeholder.fill((120, 120, 120, 255))
        pygame.draw.line(placeholder, (200, 50, 50), (0, 0), (w, h), 4)
        pygame.draw.line(placeholder, (200, 50, 50), (w, 0), (0, h), 4)
        return placeholder

def load_assets():
    """Carrega as imagens do jogo, chaveadas pelo papel de cada uma (fundo, herói, inimigo...)."""
    assets = {
        "background": _safe_load_image(IMAGES_DIR / BACKGROUND_NAME),
        "player": _safe_load_image(IMAGES_DIR / PLAYER_NAME),
        "enemy": _safe_load_image(IMAGES_DIR / ENEMY_NAME),
        "enemy_dead": _safe_load_image(IMAGES_DIR / ENEMY_DEAD_NAME),
        "boss": _safe_load_image(IMAGES_DIR / BOSS_NAME),
        "emerald": _safe_load_image(IMAGES_DIR / EMERALD_NAME),
    }
    return assets

def tint_image(surface: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
    """
    Aplica um leve "tint" multiplicativo na imagem base, preservando transparência.
    color: RGB (valores 0-255). Use tons próximos ao branco para efeitos sutis.
    """
    base = surface.convert_alpha()
    tinted = base.copy()
    overlay = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    overlay.fill((*color, 255))
    tinted.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted
