import pygame
from .settings import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, BLACK, FONT, TITLE_FONT
from .assets import load_assets
from .personagem import Personagem
from .ui import Button, draw_text
from .combat import add_log, combat_log


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Meu RPG")

    # Carrega imagens
    fundo_img, gordo_img, inimigo_img = load_assets()

    # Cria personagens
    player = Personagem("Herói", 100, 50, 40, player_img)
    enemy = Personagem("Inimigo", 80, 40, 30, enemy_img)

    # Botões
    buttons = [
        Button("Atacar", 50, 500, 200, 50, lambda: add_log(player.attack(enemy)), FONT),
        Button("Fireball", 50, 560, 200, 50, lambda: add_log(player.cast_fireball(enemy)), FONT),
        Button("Curar", 50, 620, 200, 50, lambda: add_log(player.heal()), FONT),
        Button("Defender", 50, 680, 200, 50, lambda: add_log(player.defend()), FONT),
    ]

    clock = pygame.time.Clock()
    running = True

    while running:
        screen_width, screen_height = screen.get_size()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Verifica cliques nos botões
        for btn in buttons:
            if btn.is_clicked(screen_width, screen_height, WINDOW_WIDTH, WINDOW_HEIGHT):
                btn.action()

        # Render
        screen.blit(pygame.transform.scale(fundo_img, (screen_width, screen_height)), (0, 0))

        # Desenha personagens
        screen.blit(player.img, (screen_width * 0.2, screen_height * 0.3))
        screen.blit(enemy.img, (screen_width * 0.7, screen_height * 0.3))

        # Status
        draw_text(screen, f"{player.name}: HP {player.hp}/{player.max_hp} | STA {player.stamina}/{player.max_stamina} | MANA {player.mana}/{player.max_mana}",
                  50, 50, FONT, WHITE)
        draw_text(screen, f"{enemy.name}: HP {enemy.hp}/{enemy.max_hp}", 
                  screen_width - 400, 50, FONT, WHITE)

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
