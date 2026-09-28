import pygame
import pytweening as tween
import random
from math import cos, pi, sin
from .settings import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, FONT, SMALL_FONT, TITLE_FONT
from .assets import load_assets, tint_image
from .personagem import Personagem
from .ui import Button, draw_text
from .combat import add_log, combat_log

FINAL_LEVEL = 10
ENEMY_STRENGTH_MULTIPLIER = 0.9
EMERALD_BRIGHT = (112, 255, 145)
EMERALD_LIGHT = (190, 255, 205)
EMERALD_SOFT = (143, 232, 166)


def create_enemy(level, base_image, boss_image):
    if level >= FINAL_LEVEL:
        boss_sprite = pygame.transform.scale(boss_image, (352, 400))
        return Personagem(
            "Guardião da Esmeralda",
            hp=round(300 * ENEMY_STRENGTH_MULTIPLIER),
            stamina=75,
            mana=0,
            img=boss_sprite,
            attack_damage=(14, 20),
            attack_cost=15,
            damage_dealt_multiplier=0.9 * ENEMY_STRENGTH_MULTIPLIER,
            is_boss=True,
        )

    damage_bonus = (level - 1) // 3
    is_poisoned = random.random() < 0.25
    enemy_image = tint_image(base_image, (155, 225, 125)) if is_poisoned else base_image
    return Personagem(
        "Esqueleto Envenenado" if is_poisoned else "Esqueleto",
        hp=round((80 + (level - 1) * 10) * ENEMY_STRENGTH_MULTIPLIER),
        stamina=36 + (level - 1) * 3,
        mana=0,
        img=enemy_image,
        attack_damage=(10 + damage_bonus, 16 + damage_bonus),
        damage_taken_multipliers=(
            {"physical": 1.1, "magic": 1.4} if is_poisoned else None
        ),
        is_poisoned=is_poisoned,
        damage_dealt_multiplier=0.85 * ENEMY_STRENGTH_MULTIPLIER,
    )


def draw_boss_aura(screen, rect, ticks, intensity=1.0):
    pulse = (sin(ticks * 0.004) + 1) / 2
    for index in range(3):
        spread = int((12 + pulse * 12 + index * 12) * intensity)
        aura_rect = rect.inflate(spread * 2, spread)
        pygame.draw.ellipse(
            screen,
            (30 + index * 12, 155 + index * 20, 92 + index * 16),
            aura_rect,
            width=2,
        )

    for index in range(6):
        angle = ticks * 0.0012 + index * (pi / 3)
        orbit = rect.width * (0.47 + pulse * 0.05)
        x = rect.centerx + int(cos(angle) * orbit)
        y = rect.centery + int(sin(angle) * orbit * 0.55)
        pygame.draw.circle(screen, (114, 255, 128), (x, y), 3 + index % 2)


def draw_poison_effect(screen, rect, ticks):
    pulse = (sin(ticks * 0.005) + 1) / 2
    aura_rect = rect.inflate(int(16 + pulse * 16), int(10 + pulse * 12))
    pygame.draw.ellipse(screen, (65, 145, 70), aura_rect, width=3)

    for index in range(3):
        phase = (ticks * 0.0007 + index / 3) % 1
        x = rect.left + int(rect.width * (0.25 + index * 0.25 + 0.04 * sin(ticks * 0.004 + index)))
        y = rect.top + int(rect.height * 0.18) - int(phase * 42)
        radius = 2 + int(sin(phase * pi) * 2)
        pygame.draw.circle(screen, (142, 210, 100), (x, y), radius)


def draw_cinematic_text(screen, text, center, font_obj, color, alpha=255):
    text_surface = font_obj.render(text, True, color)
    text_surface.set_alpha(alpha)
    rect = text_surface.get_rect(center=center)

    shadow = font_obj.render(text, True, (0, 0, 0))
    shadow.set_alpha(alpha)
    screen.blit(shadow, rect.move(0, 4))

    glow = font_obj.render(text, True, (70, 255, 150))
    glow.set_alpha(alpha // 5)
    screen.blit(glow, rect.move(-2, 0))
    screen.blit(glow, rect.move(2, 0))
    screen.blit(text_surface, rect)


def draw_victory_scene(screen, player_image, emerald_image, elapsed, screen_width, screen_height):
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((2, 10, 14, 208))
    screen.blit(overlay, (0, 0))

    ground_y = int(screen_height * 0.82)
    player_height = min(340, int(screen_height * 0.48))
    player_width = max(1, int(player_image.get_width() * player_height / player_image.get_height()))
    small_player = pygame.transform.scale(player_image, (player_width, player_height))
    walk_progress = max(0.0, min(1.0, (elapsed - 1.5) / 2.5))
    walk_progress = tween.easeOutQuad(walk_progress)
    start_x = screen_width * 0.23
    end_x = screen_width * 0.43
    player_center_x = int(start_x + (end_x - start_x) * walk_progress)
    walking = 1.5 <= elapsed <= 4.1
    step_bob = int(abs(sin(elapsed * 10)) * 5) if walking else int(sin(elapsed * 2.8) * 2)
    player_rect = small_player.get_rect(midbottom=(player_center_x, ground_y - step_bob))

    emerald_center = (int(screen_width * 0.64), int(screen_height * 0.49 + sin(elapsed * 3.2) * 11))
    pickup_start = 4.0
    pickup_progress = max(0.0, min(1.0, (elapsed - pickup_start) / 1.05))
    pickup_progress = pickup_progress * pickup_progress * (3 - 2 * pickup_progress)
    pickup_target = (player_center_x + int(player_width * 0.34), ground_y - int(player_height * 0.63))
    gem_x = int(emerald_center[0] + (pickup_target[0] - emerald_center[0]) * pickup_progress)
    gem_y = int(emerald_center[1] + (pickup_target[1] - emerald_center[1]) * pickup_progress)

    floor_glow = pygame.Rect(0, 0, int(screen_width * 0.68), 26)
    floor_glow.center = (int(screen_width * 0.5), ground_y + 7)
    pygame.draw.ellipse(screen, (19, 107, 65), floor_glow, width=2)
    pygame.draw.ellipse(screen, (20, 69, 57), floor_glow.inflate(-48, -10), width=1)

    player_glow = pygame.Surface((player_width * 2, player_height * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(
        player_glow,
        (24, 190, 100, 48 if elapsed >= 5.0 else 20),
        player_glow.get_rect().inflate(-player_width // 2, -player_height // 2),
    )
    screen.blit(player_glow, player_glow.get_rect(center=player_rect.center).topleft, special_flags=pygame.BLEND_RGBA_ADD)
    screen.blit(small_player, player_rect)

    if elapsed < 5.08:
        pulse = (sin(elapsed * 5) + 1) / 2
        gem_size = max(12, int(min(180, screen_height * 0.25) * (0.94 + pulse * 0.08) * (1 - pickup_progress * 0.72)))
        for layer in range(3):
            radius = gem_size // 2 + 18 + layer * 18 + int(pulse * 9)
            pygame.draw.circle(screen, (17, 125 + layer * 20, 82 + layer * 18), (gem_x, gem_y), radius, width=2)
        emerald = pygame.transform.scale(emerald_image, (gem_size, gem_size))
        emerald.set_alpha(max(0, int(255 * (1 - pickup_progress))))
        gem_rect = emerald.get_rect(center=(gem_x, gem_y))
        screen.blit(emerald, gem_rect)

    if elapsed >= 4.65:
        burst_progress = min(1.0, (elapsed - 4.65) / 0.85)
        for index in range(34):
            angle = index * (2 * pi / 34) + elapsed * 0.7
            distance = 22 + burst_progress * (55 + index % 5 * 8)
            x = pickup_target[0] + int(cos(angle) * distance)
            y = pickup_target[1] + int(sin(angle) * distance)
            radius = 1 + ((index + int(elapsed * 12)) % 4)
            pygame.draw.circle(screen, (115, 255, 142), (x, y), radius)

    if elapsed < 1.35:
        headline, subline = "O GUARDIÃO FOI VENCIDO", "A floresta volta a respirar."
        text_alpha = min(255, int(elapsed * 260))
    elif elapsed < 3.9:
        headline, subline = "A ESMERALDA DESPERTA", "Seu brilho guia os últimos passos."
        text_alpha = min(255, int((elapsed - 1.35) * 260))
    elif elapsed < 5.25:
        headline, subline = "A RELÍQUIA RECONHECE VOCÊ", "A luz antiga agora está em suas mãos."
        text_alpha = 255
    else:
        headline, subline = "VITÓRIA!", "A Esmeralda da Floresta agora é sua."
        text_alpha = 255

    draw_cinematic_text(
        screen,
        headline,
        (screen_width // 2, int(screen_height * 0.14)),
        TITLE_FONT,
        EMERALD_LIGHT if elapsed < 5.25 else EMERALD_BRIGHT,
        text_alpha,
    )
    draw_cinematic_text(
        screen,
        subline,
        (screen_width // 2, int(screen_height * 0.21)),
        FONT,
        EMERALD_SOFT,
        text_alpha,
    )

    if elapsed >= 5.25:
        draw_cinematic_text(
            screen,
            "O reino está salvo. Uma nova lenda começa.",
            (screen_width // 2, int(screen_height * 0.28)),
            SMALL_FONT,
            EMERALD_SOFT,
        )
        prompt = SMALL_FONT.render("Pressione ESC para encerrar sua jornada", True, EMERALD_BRIGHT)
        prompt.set_alpha(180 + int(60 * (sin(elapsed * 2.5) + 1) / 2))
        screen.blit(prompt, prompt.get_rect(center=(screen_width // 2, int(screen_height * 0.91))))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("RPG Python")

    assets = load_assets()

    # Cria personagens com imagens originais (não redimensionadas)
    player = Personagem("Você", 120, 60, 50, assets["player"], attack_cost=11)
    base_enemy_img = assets["enemy"]
    level = 1
    enemy = create_enemy(level, base_enemy_img, assets["boss"])
    combat_log.clear()
    add_log("Dica: Defender recupera recursos e bloqueia o próximo golpe.")

    # Estado de jogo e turnos
    state = "player_turn"  # player_turn | enemy_turn | enemy_dying | game_over
    enemy_prev_alive = True
    enemy_is_dying = False
    death_start = 0
    death_duration = 800  # ms
    enemy_turn_started = 0
    enemy_turn_delay = 450  # ms para dar tempo de ler o log
    boss_intro_start = None
    boss_intro_duration = 2400
    victory_start = None
    hp_text_color = (139, 0, 0)

    # Animações de dano
    hit_duration = 320  # ms
    player_hit_start = None
    enemy_hit_start = None

    # Wrappers de ação do jogador para detectar dano e controlar turno
    def do_attack():
        nonlocal enemy_hit_start
        before = enemy.hp
        msg, turn_used = player.attack(enemy)
        add_log(msg)
        if enemy.hp < before:
            enemy_hit_start = pygame.time.get_ticks()
        return turn_used

    def do_fireball():
        nonlocal enemy_hit_start
        before = enemy.hp
        msg, turn_used = player.cast_fireball(enemy)
        add_log(msg)
        if enemy.hp < before:
            enemy_hit_start = pygame.time.get_ticks()
        return turn_used

    def do_heal():
        msg, turn_used = player.heal()
        add_log(msg)
        return turn_used

    def do_defend():
        msg, turn_used = player.defend()
        add_log(msg)
        return turn_used

    # Botões centralizados na base
    btn_w, btn_h, btn_gap = 200, 52, 20
    total_w = 4 * btn_w + 3 * btn_gap
    start_x = int((WINDOW_WIDTH - total_w) / 2)
    base_y = WINDOW_HEIGHT - 110
    buttons = [
        Button("Ataque · 11 ST", start_x + (btn_w + btn_gap) * 0, base_y, btn_w, btn_h, do_attack, SMALL_FONT,
               enabled=lambda: player.stamina >= player.attack_cost),
        Button("Fogo · 16 MP", start_x + (btn_w + btn_gap) * 1, base_y, btn_w, btn_h, do_fireball, SMALL_FONT,
               enabled=lambda: player.mana >= player.FIREBALL_COST),
        Button("Curar · 13 MP", start_x + (btn_w + btn_gap) * 2, base_y, btn_w, btn_h, do_heal, SMALL_FONT,
               enabled=lambda: player.mana >= player.HEAL_COST and player.hp < player.max_hp),
        Button("Defender", start_x + (btn_w + btn_gap) * 3, base_y, btn_w, btn_h, do_defend, SMALL_FONT),
    ]

    clock = pygame.time.Clock()
    running = True

    while running:
        screen_width, screen_height = screen.get_size()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and state == "player_turn"
                and enemy.alive
                and player.alive
                and not enemy_is_dying
            ):
                for btn in buttons:
                    if btn.is_clicked(
                        screen_width,
                        screen_height,
                        WINDOW_WIDTH,
                        WINDOW_HEIGHT,
                        event.pos,
                    ):
                        if btn.action():
                            state = "enemy_turn"
                            enemy_turn_started = pygame.time.get_ticks()
                        break

        # Detecta início de morte do inimigo
        if enemy_prev_alive and not enemy.alive and not enemy_is_dying:
            enemy_is_dying = True
            state = "enemy_dying"
            death_start = pygame.time.get_ticks()
            death_duration = 1800 if enemy.is_boss else 800
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
        if state != "victory":
            px_off, py_off, _ = get_shake_offset(player_hit_start)
            player_draw_pos = (player_pos[0] + px_off, player_pos[1] + py_off)
            screen.blit(player.img, player_draw_pos)
            player_rect = player.img.get_rect(topleft=player_draw_pos)
            draw_text(screen, f"HP {player.hp}/{player.max_hp}", player_rect.centerx, player_rect.top - 12, SMALL_FONT, hp_text_color, centered=True)
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
            if enemy.is_boss:
                ticks = pygame.time.get_ticks()
                boss_center = (enemy_pos[0] + enemy.img.get_width() // 2, enemy_pos[1] + enemy.img.get_height() - 75)
                base_rect = enemy.img.get_rect(topleft=enemy_pos)
                draw_boss_aura(screen, base_rect, ticks, intensity=max(0.05, ease))
                scale = max(0.08, 1.0 - 0.72 * tween.easeInQuad(t))
                rotation = (1 - ease) * 22 * sin(t * pi)
                collapsing = pygame.transform.rotozoom(enemy.img, rotation, scale)
                collapsing.set_alpha(int(255 * ease))
                collapsing_rect = collapsing.get_rect(center=(boss_center[0], boss_center[1] - int(t * 45)))
                screen.blit(collapsing, collapsing_rect)
                for index in range(28):
                    angle = index * (2 * pi / 28) + ticks * 0.003
                    orbit = 28 + int(((t * 1.4 + index / 28) % 1) * 160)
                    x = boss_center[0] + int(cos(angle) * orbit)
                    y = boss_center[1] + int(sin(angle) * orbit * 0.58) - int(t * 72)
                    pygame.draw.circle(screen, (75, 231, 111), (x, y), max(1, 4 - int(t * 2)))
                ring_radius = int(48 + t * 165)
                pygame.draw.ellipse(
                    screen,
                    (60, 225, 111),
                    pygame.Rect(boss_center[0] - ring_radius, boss_center[1] - ring_radius // 3, ring_radius * 2, ring_radius * 2 // 3),
                    width=3,
                )
            else:
                scale = max(0.05, ease)
                alpha = int(255 * ease)
                dead_img = assets["enemy_dead"]
                scaled = pygame.transform.rotozoom(dead_img, 0, scale)
                scaled.set_alpha(alpha)
                rect = scaled.get_rect(center=(enemy_pos[0] + dead_img.get_width() // 2, enemy_pos[1] + dead_img.get_height() // 2))
                screen.blit(scaled, rect.topleft)
            if t >= 1.0:
                enemy_is_dying = False
                if enemy.is_boss:
                    victory_start = pygame.time.get_ticks()
                    state = "victory"
                    add_log("A Esmeralda da Floresta agora pertence a você!")
                else:
                    level += 1
                    hp_gained = min(12, player.max_hp - player.hp)
                    stamina_gained = min(12, player.max_stamina - player.stamina)
                    mana_gained = min(8, player.max_mana - player.mana)
                    player.hp += hp_gained
                    player.stamina += stamina_gained
                    player.mana += mana_gained
                    enemy = create_enemy(level, base_enemy_img, assets["boss"])
                    enemy_hit_start = None
                    add_log(f"Nível {level}: {enemy.name} com {enemy.max_hp} HP.")
                    add_log(
                        f"Respiro: +{hp_gained} HP, +{stamina_gained} ST, "
                        f"+{mana_gained} MP."
                    )
                    if enemy.is_boss:
                        state = "boss_intro"
                        boss_intro_start = pygame.time.get_ticks()
                        add_log("O Guardião da Esmeralda desperta no nível final!")
                    else:
                        state = "player_turn"
        elif state != "victory":
            ex_off, ey_off, et = get_shake_offset(enemy_hit_start)
            enemy_draw_pos = (enemy_pos[0] + ex_off, enemy_pos[1] + ey_off)
            enemy_rect = enemy.img.get_rect(topleft=enemy_draw_pos)
            if enemy.is_poisoned:
                draw_poison_effect(screen, enemy_rect, pygame.time.get_ticks())
            if enemy.is_boss:
                draw_boss_aura(screen, enemy_rect, pygame.time.get_ticks())
            boss_intro_progress = 1.0
            if state == "boss_intro" and boss_intro_start is not None:
                boss_intro_progress = max(0.0, min(1.0, (pygame.time.get_ticks() - boss_intro_start) / boss_intro_duration))
                boss_intro_progress = tween.easeOutQuad(boss_intro_progress)
            if enemy.is_boss and state == "boss_intro":
                intro_sprite = pygame.transform.rotozoom(enemy.img, 0, 0.72 + 0.28 * boss_intro_progress)
                intro_sprite.set_alpha(int(255 * boss_intro_progress))
                intro_rect = intro_sprite.get_rect(center=enemy_rect.center)
                screen.blit(intro_sprite, intro_rect)
            else:
                screen.blit(enemy.img, enemy_draw_pos)
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

        if state == "boss_intro" and boss_intro_start is not None:
            intro_elapsed = pygame.time.get_ticks() - boss_intro_start
            if intro_elapsed >= boss_intro_duration:
                state = "player_turn"
                add_log("Prepare-se: o Guardião golpeia com força, mas ainda pode ser contido.")

        # Turno do inimigo (uma ação após pequeno atraso)
        if state == "enemy_turn" and player.alive and not enemy_is_dying:
            if pygame.time.get_ticks() - enemy_turn_started >= enemy_turn_delay:
                if enemy.stamina >= enemy.attack_cost:
                    before = player.hp
                    message, _ = enemy.attack(player)
                    add_log(message)
                    if player.hp < before:
                        player_hit_start = pygame.time.get_ticks()
                else:
                    message, _ = enemy.defend()
                    add_log(message)
                if not player.alive:
                    state = "game_over"
                else:
                    state = "player_turn"

        title_color = EMERALD_LIGHT if enemy.is_boss else WHITE
        draw_text(screen, "RPG Python", screen_width // 2, 30, TITLE_FONT, title_color, centered=True)
        draw_text(
            screen,
            f"Nível {level} · Confronto final" if level == FINAL_LEVEL else f"Nível {level}",
            screen_width // 2,
            68,
            SMALL_FONT,
            title_color,
            centered=True,
        )

        # Barras e status na tela
        def draw_bar(x, y, w, h, current, maximum, color):
            pygame.draw.rect(screen, (40, 40, 40), (x, y, w, h))
            ratio = 0 if maximum == 0 else max(0, min(1, current / maximum))
            pygame.draw.rect(screen, color, (x, y, int(w * ratio), h))
            pygame.draw.rect(screen, (10, 10, 10), (x, y, w, h), 2)

        # Player status (canto superior esquerdo)
        draw_text(screen, f"{player.name}", 20, 60, FONT, hp_text_color)
        draw_bar(20, 90, 280, 18, player.hp, player.max_hp, (200, 50, 50))
        draw_text(screen, f"{player.hp}/{player.max_hp}", 310, 87, SMALL_FONT, WHITE)
        draw_bar(20, 114, 280, 12, player.stamina, player.max_stamina, (50, 160, 60))
        draw_text(screen, f"{player.stamina}/{player.max_stamina} ST", 310, 108, SMALL_FONT, WHITE)
        draw_bar(20, 132, 280, 12, player.mana, player.max_mana, (60, 120, 200))
        draw_text(screen, f"{player.mana}/{player.max_mana} MP", 310, 126, SMALL_FONT, WHITE)

        # Enemy status
        enemy_status_x = screen_width - 380
        enemy_label = f"{enemy.name} · CHEFE" if enemy.is_boss else f"{enemy.name} · Nv. {level}"
        draw_text(
            screen,
            enemy_label,
            enemy_status_x,
            60,
            SMALL_FONT if enemy.is_boss else FONT,
            (156, 255, 166) if enemy.is_boss else hp_text_color,
        )
        draw_bar(enemy_status_x, 90, 280, 18, enemy.hp, enemy.max_hp, (200, 50, 50))
        boss_status_color = EMERALD_BRIGHT if enemy.is_boss else WHITE
        draw_text(screen, f"{enemy.hp}/{enemy.max_hp}", enemy_status_x + 290, 87, SMALL_FONT, boss_status_color)
        draw_bar(enemy_status_x, 114, 280, 12, enemy.stamina, enemy.max_stamina, (50, 160, 60))
        draw_text(
            screen,
            f"{enemy.stamina}/{enemy.max_stamina} ST",
            enemy_status_x + 290,
            108,
            SMALL_FONT,
            boss_status_color,
        )
        if enemy.is_poisoned:
            draw_text(
                screen,
                "Vulnerável: magia +40% · físico +10%",
                enemy_status_x,
                132,
                SMALL_FONT,
                (142, 210, 100),
            )
        elif enemy.is_boss:
            draw_text(
                screen,
                "Guardião ancestral · 270 HP",
                enemy_status_x,
                132,
                SMALL_FONT,
                (156, 255, 166),
            )

        for btn in buttons:
            btn.draw(screen, screen_width, screen_height, WINDOW_WIDTH, WINDOW_HEIGHT)
        draw_text(
            screen,
            "Defender bloqueia 40% do próximo golpe e recupera até 24 ST / 10 MP",
            screen_width // 2,
            screen_height - 24,
            SMALL_FONT,
            WHITE,
            centered=True,
        )

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
            log_color = EMERALD_LIGHT if enemy.is_boss else WHITE
            draw_text(screen, msg, panel_x + 10, log_y, SMALL_FONT, log_color)
            log_y += 24

        # Game over overlay
        if state == "game_over":
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            draw_text(screen, "Game Over", screen_width // 2, screen_height // 2 - 10, TITLE_FONT, WHITE, centered=True)
            draw_text(screen, f"Você chegou ao nível {level}", screen_width // 2, screen_height // 2 + 34, FONT, WHITE, centered=True)
            draw_text(screen, "Pressione ESC para sair", screen_width // 2, screen_height // 2 + 74, FONT, WHITE, centered=True)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                running = False
        elif state == "victory":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                running = False

        # Abertura dramática do chefe, desenhada por cima da interface.
        if state == "boss_intro" and boss_intro_start is not None:
            intro_elapsed = pygame.time.get_ticks() - boss_intro_start
            vignette = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            vignette.fill((2, 12, 9, int(105 * (1 - intro_elapsed / boss_intro_duration))))
            screen.blit(vignette, (0, 0))
            draw_cinematic_text(
                screen,
                "O GUARDIÃO DA ESMERALDA",
                (screen_width // 2, int(screen_height * 0.19)),
                TITLE_FONT,
                EMERALD_BRIGHT,
                min(255, int(intro_elapsed * 0.35)),
            )
            draw_cinematic_text(
                screen,
                "270 HP · A relíquia não será entregue sem uma última batalha.",
                (screen_width // 2, int(screen_height * 0.25)),
                SMALL_FONT,
                EMERALD_LIGHT,
                min(255, int(intro_elapsed * 0.4)),
            )

        # A cena final cobre a interface de combate e fica até o jogador sair.
        if state == "victory" and victory_start is not None:
            draw_victory_scene(
                screen,
                player.img,
                assets["emerald"],
                (pygame.time.get_ticks() - victory_start) / 1000,
                screen_width,
                screen_height,
            )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
