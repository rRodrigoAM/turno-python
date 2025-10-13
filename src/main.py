import pygame
from pathlib import Path
from .settings import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, BLACK, FONT, TITLE_FONT
from .assets import load_assets
from .personagem import Personagem
from .ui import Button, draw_text
from .combat import add_log, combat_log

def _ensure_surface(obj):
    """
    Se obj for Surface: retorna.
    Se for str/Path: tenta carregar como imagem.
    Se for None ou falhar: retorna None.
    """
    if obj is None:
        return None
    if isinstance(obj, pygame.Surface):
        return obj
    if isinstance(obj, (str, Path)):
        try:
            return pygame.image.load(str(obj))
        except Exception as e:
            print(f"[_ensure_surface] erro ao carregar {obj}: {e}")
            return None
    # caso inesperado
    return None


def _scale_surface_to_pct(surf: pygame.Surface, screen_w: int, screen_h: int, pct_w: float = 0.15, pct_h: float | None = None):
    """
    Escala surf mantendo aspect ratio.
    pct_w = proporção da largura da tela que a imagem deve ocupar (ex: 0.15 = 15%).
    pct_h opcional: se fornecido, limita também pela altura (proporção da altura).
    """
    if not surf:
        return None
    sw, sh = surf.get_size()
    if sw == 0 or sh == 0:
        return None
    target_w = int(screen_w * pct_w)
    if pct_h is not None:
        target_h = int(screen_h * pct_h)
    else:
        target_h = int((target_w / sw) * sh)
    scale_w = target_w / sw
    scale_h = target_h / sh
    scale = min(scale_w, scale_h)
    new_size = (max(1, int(sw * scale)), max(1, int(sh * scale)))
    try:
        return pygame.transform.smoothscale(surf, new_size)
    except Exception:
        return pygame.transform.scale(surf, new_size)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Meu RPG")

    # --- Carrega assets (load_assets deve retornar Surfaces já carregadas) ---
    try:
        assets = load_assets()  # dicionário
    except Exception as e:
        print("Erro ao carregar assets:", e)
        assets = {}

    # Aceita ambos os conjuntos de chaves (pt/en)
    fundo_raw = assets.get("fundo") or assets.get("background")
    gordo_raw = assets.get("gordo") or assets.get("player")
    inimigo_raw = assets.get("inimigo") or assets.get("enemy")

    # Garante que sejam pygame.Surface ou None
    fundo_img = _ensure_surface(fundo_raw)
    gordo_img = _ensure_surface(gordo_raw)
    inimigo_img = _ensure_surface(inimigo_raw)

    # Debug de carga
    for name, surf in (("fundo", fundo_img), ("gordo", gordo_img), ("inimigo", inimigo_img)):
        if surf:
            try:
                print(f"[ASSET-DEBUG] {name} size={surf.get_size()}")
            except Exception as e:
                print(f"[ASSET-DEBUG] {name} erro ao medir size: {e}")
        else:
            print(f"[ASSET-DEBUG] {name} = None")

    # Fallback de fundo
    if not fundo_img:
        fundo_img = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        fundo_img.fill((20, 20, 40))

    # Cria personagens — assume que Personagem aceita uma surface no construtor
    player = Personagem("Herói", 100, 50, 40, gordo_img)
    enemy = Personagem("Inimigo", 80, 40, 30, inimigo_img)

    # Botões (mantive sua lógica)
    buttons = [
        Button("Atacar", 50, 500, 200, 50, lambda: add_log(player.attack(enemy)), FONT),
        Button("Fireball", 50, 560, 200, 50, lambda: add_log(player.cast_fireball(enemy)), FONT),
        Button("Curar", 50, 620, 200, 50, lambda: add_log(player.heal()), FONT),
        Button("Defender", 50, 680, 200, 50, lambda: add_log(player.defend()), FONT),
    ]

    clock = pygame.time.Clock()
    running = True

    # Cache de imagens escaladas
    last_size = screen.get_size()
    try:
        scaled_fundo = pygame.transform.smoothscale(fundo_img, last_size)
    except Exception:
        scaled_fundo = pygame.transform.scale(fundo_img, last_size)
    scaled_player_img = _scale_surface_to_pct(player.img, *last_size, pct_w=0.18)
    scaled_enemy_img = _scale_surface_to_pct(enemy.img, *last_size, pct_w=0.18)

    while running:
        screen_width, screen_height = screen.get_size()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                # opcional: você já trata resize fora do loop de eventos também
                pass
            if event.type == pygame.MOUSEBUTTONDOWN:
                # se precisar encaminhar para buttons, faça aqui
                pass

        # Atualiza escalados só quando a janela mudou
        if (screen_width, screen_height) != last_size:
            last_size = (screen_width, screen_height)
            try:
                scaled_fundo = pygame.transform.smoothscale(fundo_img, last_size)
            except Exception:
                scaled_fundo = pygame.transform.scale(fundo_img, last_size)
            scaled_player_img = _scale_surface_to_pct(player.img, screen_width, screen_height, pct_w=0.18)
            scaled_enemy_img = _scale_surface_to_pct(enemy.img, screen_width, screen_height, pct_w=0.18)

        # Verifica cliques nos botões (se sua implementação usa is_clicked)
        for btn in buttons:
            try:
                if btn.is_clicked(screen_width, screen_height, WINDOW_WIDTH, WINDOW_HEIGHT):
                    btn.action()
            except Exception:
                # protege caso is_clicked tenha assinatura diferente
                pass

        # Render: limpar antes, desenhar, depois flip
        screen.fill((0, 0, 0))  # garante que não haja resíduos
        if scaled_fundo:
            screen.blit(scaled_fundo, (0, 0))
        else:
            # fallback de cor caso algo dê errado
            screen.fill((20, 20, 40))

        # Desenha personagens (posições relativas)
        if scaled_player_img:
            px = int(screen_width * 0.2 - scaled_player_img.get_width() / 2)
            py = int(screen_height * 0.35 - scaled_player_img.get_height() / 2)
            screen.blit(scaled_player_img, (px, py))
        if scaled_enemy_img:
            ex = int(screen_width * 0.7 - scaled_enemy_img.get_width() / 2)
            ey = int(screen_height * 0.35 - scaled_enemy_img.get_height() / 2)
            screen.blit(scaled_enemy_img, (ex, ey))

        # Status
        draw_text(screen, f"{player.name}: HP {player.hp}/{player.max_hp} | STA {player.stamina}/{player.max_stamina} | MANA {player.mana}/{player.max_mana}",
                  50, 20, FONT, WHITE)
        draw_text(screen, f"{enemy.name}: HP {enemy.hp}/{enemy.max_hp}",
                  screen_width - 400, 20, FONT, WHITE)

        # Botões
        for btn in buttons:
            btn.draw(screen, screen_width, screen_height, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Log de combate
        log_y = screen_height - 150
        for msg in combat_log[-5:]:
            draw_text(screen, msg, 300, log_y, FONT, WHITE)
            log_y += 30

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()