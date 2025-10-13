# assets.py
from pathlib import Path
import pygame

BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "assets"

def _ensure_exists(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Imagem não encontrada: {path}")

def load_image(name: str, use_alpha: bool = True) -> pygame.Surface:
    path = IMAGES_DIR / name
    _ensure_exists(path)
    surf = pygame.image.load(str(path))
    try:
        return surf.convert_alpha() if use_alpha else surf.convert()
    except pygame.error:
        # fallback se conversão falhar por algum motivo
        return surf

def load_assets():
    assets = {}
    files = {
        "fundo": "fundo_img.png",
        "gordo": "gordo_img.png",
        "inimigo": "inimigo_img.png",
    }
    for key, fname in files.items():
        try:
            img = load_image(fname, use_alpha=True)
            print(f"[ASSET] carregado {key} -> {fname} size={img.get_size()}")
            assets[key] = img
        except Exception as e:
            print(f"[ASSET-ERROR] {key}: {e}")
            assets[key] = None
    return assets
