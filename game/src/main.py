import pygame
import pytweening as tween
import random
from .settings import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, FONT, SMALL_FONT, TITLE_FONT
from .assets import load_assets, tint_image
from .personagem import Personagem
from .ui import Button, draw_text
from .combat import add_log, combat_log


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("RPG Python")

    # Carrega assets
    assets = load_assets()

    # Cria personagens com imagens originais (não redimensionadas)
    player = Personagem("Você", 120, 60, 50, assets["player"])
    base_enemy_img = assets["enemy"]
    enemy = Personagem("Esqueleto", 90, 50, 30, base_enemy_img)

    # Estado de jogo e turnos
    state = "player_turn"  # player_turn | enemy_turn | enemy_dying | game_over
    enemy_prev_alive = True
    enemy_is_dying = False
    death_start = 0
    death_duration = 800  # ms
    enemy_turn_started = 0
    enemy_turn_delay = 450  # ms para dar tempo de ler o log
    hp_text_color = (139, 0, 0)  # vermelho escuro

    # Animações de dano
    hit_duration = 320  # ms
    player_hit_start = None
    enemy_hit_start = None

    # Wrappers de ação do jogador para detectar dano e controlar turno
    def do_attack():
        nonlocal enemy_hit_start
        before = enemy.hp
        msg = player.attack(enemy)
        add_log(msg)
        if enemy.hp < before:
            enemy_hit_start = pygame.time.get_ticks()

    def do_fireball():
        nonlocal enemy_hit_start
        before = enemy.hp
        msg = player.cast_fireball(enemy)
        add_log(msg)
        if enemy.hp < before:
            enemy_hit_start = pygame.time.get_ticks()

    def do_heal():
        msg = player.heal()
        add_log(msg)

    def do_defend():
        msg = player.defend()
        add_log(msg)

    # Botões centralizados na base
    btn_w, btn_h, btn_gap = 200, 52, 20
    total_w = 4 * btn_w + 3 * btn_gap
    start_x = int((WINDOW_WIDTH - total_w) / 2)
    base_y = WINDOW_HEIGHT - 110
    buttons = [
        Button("Atacar", start_x + (btn_w + btn_gap) * 0, base_y, btn_w, btn_h, do_attack, FONT),
        Button("Fireball", start_x + (btn_w + btn_gap) * 1, base_y, btn_w, btn_h, do_fireball, FONT),
        Button("Curar", start_x + (btn_w + btn_gap) * 2, base_y, btn_w, btn_h, do_heal, FONT),
        Button("Defender", start_x + (btn_w + btn_gap) * 3, base_y, btn_w, btn_h, do_defend, FONT),
    ]

    clock = pygame.time.Clock()
    running = True

    while running:
        screen_width, screen_height = screen.get_size()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Verifica cliques nos botões (apenas no turno do jogador e se inimigo vivo)
        if state == "player_turn" and enemy.alive and player.alive and not enemy_is_dying:
            for btn in buttons:
                if btn.is_clicked(screen_width, screen_height, WINDOW_WIDTH, WINDOW_HEIGHT):
                    btn.action()
                    # Após a ação do jogador, passa para o turno do inimigo
                    state = "enemy_turn"
                    enemy_turn_started = pygame.time.get_ticks()
                    break

        # Detecta início de morte do inimigo
        if enemy_prev_alive and not enemy.alive and not enemy_is_dying:
            enemy_is_dying = True
            state = "enemy_dying"
            death_start = pygame.time.get_ticks()
        enemy_prev_alive = enemy.alive

        # Fundo: redimensiona para cobrir toda a tela responsivamente
        fundo_redimensionado = pygame.transform.scale(assets["background"], (screen_width, screen_height))
        screen.blit(fundo_redimensionado, (0, 0))

        # Posição dos personagens (mantendo tamanho original)
        # Player à esquerda (20% da largura), vertical centralizado em 30% da altura
        player_pos = (int(screen_width * 0.2), int(screen_height * 0.3))
        # Enemy à direita (70% da largura), mesmo eixo vertical
        enemy_pos = (int(screen_width * 0.7), int(screen_height * 0.3))

        # Funções utilitárias de animação de dano (shake/flash)
        def get_shake_offset(start_time):
            if start_time is None:
                return 0, 0, 0.0
            elapsed = pygame.time.get_ticks() - start_time
            t = min(1.0, elapsed / hit_duration)
            amt = int(8 * tween.easeOutQuad(1.0 - t))
            # alterna direção rapidamente
            sign = -1 if (pygame.time.get_ticks() // 30) % 2 == 0 else 1
            return amt * sign, 0, t

        # Player render com shake/flash se tomou dano
        px_off, py_off, _ = get_shake_offset(player_hit_start)
        player_draw_pos = (player_pos[0] + px_off, player_pos[1] + py_off)
        screen.blit(player.img, player_draw_pos)
        # Texto de HP acima do sprite do player
        player_rect = player.img.get_rect(topleft=player_draw_pos)
        draw_text(screen, f"HP {player.hp}/{player.max_hp}", player_rect.centerx, player_rect.top - 12, SMALL_FONT, hp_text_color, centered=True)
        # Flash de dano do player (sem quadrado branco)
        if player_hit_start is not None:
            elapsed_ph = pygame.time.get_ticks() - player_hit_start
            if elapsed_ph < hit_duration:
                k = 1.0 - min(1.0, elapsed_ph / hit_duration)
                flash_alpha = int(110 * tween.easeOutSine(k))
                flash = player.img.copy()
                flash.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
                flash.set_alpha(flash_alpha)
                screen.blit(flash, player_draw_pos)
            else:
                player_hit_start = None
        if enemy_is_dying:
            elapsed = pygame.time.get_ticks() - death_start
            t = min(1.0, elapsed / death_duration)
            ease = tween.easeOutQuad(1.0 - t)  # 1 -> 0
            scale = max(0.05, ease)
            alpha = int(255 * ease)
            dead_img = assets["enemy_dead"]
            scaled = pygame.transform.rotozoom(dead_img, 0, scale)
            scaled.set_alpha(alpha)
            rect = scaled.get_rect(center=(enemy_pos[0] + dead_img.get_width() // 2, enemy_pos[1] + dead_img.get_height() // 2))
            screen.blit(scaled, rect.topleft)
            if t >= 1.0:
                enemy_is_dying = False
                # Respawn do inimigo com leve variação de cor
                tint_choices = [
                    (255, 240, 240),  # leve vermelho
                    (240, 255, 240),  # leve verde
                    (240, 240, 255),  # leve azul
                    (255, 255, 240),  # leve amarelo
                    (245, 240, 255)   # leve lilás
                ]
                tint_color = random.choice(tint_choices)
                tinted_img = tint_image(base_enemy_img, tint_color)
                enemy = Personagem("Esqueleto", 90, 50, 30, tinted_img)
                state = "enemy_turn"  # após matar, inimigo novo ataca para manter ritmo
                enemy_turn_started = pygame.time.get_ticks()
        else:
            ex_off, ey_off, et = get_shake_offset(enemy_hit_start)
            enemy_draw_pos = (enemy_pos[0] + ex_off, enemy_pos[1] + ey_off)
            screen.blit(enemy.img, enemy_draw_pos)
            # Texto de HP acima do sprite do inimigo
            enemy_rect = enemy.img.get_rect(topleft=enemy_draw_pos)
            draw_text(screen, f"HP {enemy.hp}/{enemy.max_hp}", enemy_rect.centerx, enemy_rect.top - 12, SMALL_FONT, hp_text_color, centered=True)
            # Flash branco leve no pico de dano
            if enemy_hit_start is not None:
                elapsed = pygame.time.get_ticks() - enemy_hit_start
                if elapsed < hit_duration:
                    k = 1.0 - min(1.0, elapsed / hit_duration)
                    flash_alpha = int(120 * tween.easeOutSine(k))
                    flash = enemy.img.copy()
                    flash.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
                    flash.set_alpha(flash_alpha)
                    screen.blit(flash, enemy_draw_pos)
                else:
                    enemy_hit_start = None

        # Turno do inimigo (uma ação após pequeno atraso)
        if state == "enemy_turn" and player.alive and not enemy_is_dying:
            if pygame.time.get_ticks() - enemy_turn_started >= enemy_turn_delay:
                # IA simples: se tiver stamina, ataca; senão defende para recuperar
                if enemy.stamina >= 10:
                    before = player.hp
                    add_log(enemy.attack(player))
                    if player.hp < before:
                        player_hit_start = pygame.time.get_ticks()
                else:
                    add_log(enemy.defend())
                if not player.alive:
                    state = "game_over"
                else:
                    state = "player_turn"

        # Título centralizado no topo
        draw_text(screen, "RPG Python", screen_width // 2, 30, TITLE_FONT, WHITE, centered=True)

        # Barras e status na tela
        def draw_bar(x, y, w, h, current, maximum, color):
            pygame.draw.rect(screen, (40, 40, 40), (x, y, w, h))
            ratio = 0 if maximum == 0 else max(0, min(1, current / maximum))
            pygame.draw.rect(screen, color, (x, y, int(w * ratio), h))
            pygame.draw.rect(screen, (10, 10, 10), (x, y, w, h), 2)

        # Player status (canto superior esquerdo)
        draw_text(screen, f"{player.name}", 20, 60, FONT, hp_text_color)
        draw_bar(20, 90, 360, 18, player.hp, player.max_hp, (200, 50, 50))
        draw_bar(20, 114, 360, 12, player.stamina, player.max_stamina, (50, 160, 60))
        draw_bar(20, 132, 360, 12, player.mana, player.max_mana, (60, 120, 200))

        # Enemy status
        enemy_status_x = screen_width - 380
        draw_text(screen, f"{enemy.name}", enemy_status_x, 60, FONT, hp_text_color)
        draw_bar(enemy_status_x, 90, 360, 18, enemy.hp, enemy.max_hp, (200, 50, 50))

        # Desenha os botões (centralizados na base)
        for btn in buttons:
            btn.draw(screen, screen_width, screen_height, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Log de combate: 2 linhas, acima dos botões
        base_y = WINDOW_HEIGHT - 110
        panel_w, panel_h = 700, 60
        panel_x = (screen_width - panel_w) // 2
        panel_y = base_y - panel_h - 20
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 120))
        screen.blit(panel, (panel_x, panel_y))
        log_y = panel_y + 8
        for msg in combat_log[-2:]:
            draw_text(screen, msg, panel_x + 10, log_y, SMALL_FONT, WHITE)
            log_y += 24

        # Game over overlay
        if state == "game_over":
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            draw_text(screen, "Game Over", screen_width // 2, screen_height // 2 - 10, TITLE_FONT, WHITE, centered=True)
            draw_text(screen, "Pressione ESC para sair", screen_width // 2, screen_height // 2 + 40, FONT, WHITE, centered=True)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                running = False

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
