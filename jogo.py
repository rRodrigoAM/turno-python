import pygame
import sys
import random

pygame.init()

# --- Obtém as dimensões da tela antes de definir o modo ---
info = pygame.display.Info()
# Guardamos as dimensões originais da janela para quando o jogo não estiver em tela cheia
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT = info.current_w, info.current_h
is_fullscreen = False

# Configurações da janela inicial (modo de janela)
WIDTH, HEIGHT = WINDOW_WIDTH, WINDOW_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Batalha Épica - Versão Mágica")

# Carregar imagens (certifique-se de que o caminho está correto)
try:
    background_img = pygame.image.load("assets/background.png")
    # Redimensionar para as dimensões atuais da tela
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    player_img = pygame.image.load("assets/player_img.png")
    player_img = pygame.transform.scale(player_img, (200, 200))
    enemy_img = pygame.image.load("assets/enemy_img.png")
    enemy_img = pygame.transform.scale(enemy_img, (200, 200))
except pygame.error as e:
    print(f"Erro ao carregar imagem: {e}")
    sys.exit()

# Fonte
font = pygame.font.SysFont("Arial", 26, bold=True)
small_font = pygame.font.SysFont("Arial", 20)
title_font = pygame.font.SysFont("Arial", 40, bold=True)

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (100, 100, 100)

# Classes
class Personagem:
    def __init__(self, name, hp, stamina, mana, img):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.max_stamina = stamina
        self.stamina = stamina
        self.max_mana = mana
        self.mana = mana
        self.img = img
        self.alive = True

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def attack(self, target):
        cost = 10
        if self.stamina >= cost:
            damage = random.randint(10, 20)
            target.take_damage(damage)
            self.stamina -= cost
            return f"{self.name} atacou {target.name} causando {damage} de dano físico!"
        else:
            return f"{self.name} está exausto e não pode atacar!"

    def cast_fireball(self, target):
        cost = 15
        if self.mana >= cost:
            damage = random.randint(20, 30)
            target.take_damage(damage)
            self.mana -= cost
            return f"{self.name} lançou uma Bola de Fogo em {target.name} causando {damage} de dano mágico!"
        else:
            return f"{self.name} não tem mana suficiente para Bola de Fogo!"

    def heal(self):
        cost = 10
        if self.mana >= cost:
            healed = random.randint(15, 25)
            self.hp += healed
            if self.hp > self.max_hp:
                self.hp = self.max_hp
            self.mana -= cost
            return f"{self.name} usou magia de cura e recuperou {healed} de HP!"
        else:
            return f"{self.name} não tem mana suficiente para se curar!"

    def defend(self):
        self.stamina += 15
        if self.stamina > self.max_stamina:
            self.stamina = self.max_stamina
        return f"{self.name} se defendeu e recuperou {15} de stamina!"

class Button:
    def __init__(self, text, x, y, width, height, action, font_size=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.font = pygame.font.SysFont("Arial", font_size)
        self.color = GRAY
        self.hover_color = LIGHT_GRAY

    def draw(self, screen_width, screen_height):
        # Ajusta a posição do botão para a resolução atual
        ratio_x = screen_width / WINDOW_WIDTH
        ratio_y = screen_height / WINDOW_HEIGHT
        adjusted_rect = pygame.Rect(self.rect.x * ratio_x, self.rect.y * ratio_y, self.rect.width * ratio_x, self.rect.height * ratio_y)

        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if adjusted_rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, adjusted_rect, border_radius=5)
        draw_text(self.text, adjusted_rect.centerx, adjusted_rect.centery, self.font, BLACK, centered=True)

    def is_clicked(self, screen_width, screen_height):
        ratio_x = screen_width / WINDOW_WIDTH
        ratio_y = screen_height / WINDOW_HEIGHT
        adjusted_rect = pygame.Rect(self.rect.x * ratio_x, self.rect.y * ratio_y, self.rect.width * ratio_x, self.rect.height * ratio_y)
        return adjusted_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]

# Funções de desenho
def draw_bar(x, y, current, max_value, color, bar_name):
    ratio = current / max_value
    bar_width = 200
    bar_height = 20
    pygame.draw.rect(screen, GRAY, (x, y, bar_width, bar_height), border_radius=10)
    pygame.draw.rect(screen, color, (x, y, int(bar_width * ratio), bar_height), border_radius=10)
    draw_text(f"{bar_name}: {current}/{max_value}", x + bar_width + 10, y + 2, small_font, WHITE)

def draw_text(text, x, y, font_obj, color=WHITE, centered=False):
    surface = font_obj.render(text, True, color)
    rect = surface.get_rect()
    if centered:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)

# Log de combate
combat_log = []
def add_log(message):
    combat_log.append(message)
    if len(combat_log) > 5:
        combat_log.pop(0)

# Instâncias dos personagens
player = Personagem("Jogador", 100, 50, 50, player_img)
enemy = Personagem("Inimigo", 100, 50, 50, enemy_img)

# Botões de ação
button_width = 150
button_height = 40
button_spacing = 20

attack_button = Button("Ataque", 50, WINDOW_HEIGHT - 100, button_width, button_height, "attack")
fireball_button = Button("Bola de Fogo", 50 + button_width + button_spacing, WINDOW_HEIGHT - 100, button_width, button_height, "fireball")
heal_button = Button("Curar", 50, WINDOW_HEIGHT - 50, button_width, button_height, "heal")
defend_button = Button("Defender", 50 + button_width + button_spacing, WINDOW_HEIGHT - 50, button_width, button_height, "defend")

turn = "player"
game_state = "running"
add_log("Começou a batalha! Sua vez de atacar.")

# Loop principal
clock = pygame.time.Clock()
running = True

while running:
    # --- NOVO: Lógica de tela cheia ---
    if is_fullscreen:
        current_width, current_height = FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT
    else:
        current_width, current_height = WINDOW_WIDTH, WINDOW_HEIGHT

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Lógica para alternar a tela cheia com F11
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            is_fullscreen = not is_fullscreen
            if is_fullscreen:
                screen = pygame.display.set_mode((FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT), pygame.FULLSCREEN)
                WIDTH, HEIGHT = FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT
            else:
                screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                WIDTH, HEIGHT = WINDOW_WIDTH, WINDOW_HEIGHT
            
            # Recarrega e redimensiona o background para a nova resolução
            background_img = pygame.image.load("assets/background.png")
            background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))


        if game_state == "running" and turn == "player":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if attack_button.is_clicked(current_width, current_height):
                    log_msg = player.attack(enemy)
                    add_log(log_msg)
                    turn = "enemy"
                elif fireball_button.is_clicked(current_width, current_height):
                    log_msg = player.cast_fireball(enemy)
                    add_log(log_msg)
                    turn = "enemy"
                elif heal_button.is_clicked(current_width, current_height):
                    log_msg = player.heal()
                    add_log(log_msg)
                    turn = "enemy"
                elif defend_button.is_clicked(current_width, current_height):
                    log_msg = player.defend()
                    add_log(log_msg)
                    turn = "enemy"

    # Lógica do inimigo (a mesma)
    if game_state == "running" and turn == "enemy" and enemy.alive:
        pygame.time.delay(1000)
        
        if enemy.hp < 50 and enemy.mana >= 10:
            log_msg = enemy.heal()
        elif enemy.mana >= 15:
            log_msg = enemy.cast_fireball(player)
        elif enemy.stamina >= 10:
            log_msg = enemy.attack(player)
        else:
            log_msg = enemy.defend()
        
        add_log(log_msg)
        turn = "player"
    
    # Desenho na tela
    screen.blit(background_img, (0, 0))

    # --- Ajusta a posição de todos os elementos para a nova resolução ---
    # Para as barras de status
    ratio_x = current_width / WINDOW_WIDTH
    ratio_y = current_height / WINDOW_HEIGHT

    # Personagens
    screen.blit(player.img, (100 * ratio_x, HEIGHT - 300 * ratio_y))
    screen.blit(enemy.img, (WIDTH - 300 * ratio_x, HEIGHT - 300 * ratio_y))

    # Barras de status
    draw_bar(100 * ratio_x, 50 * ratio_y, player.hp, player.max_hp, GREEN, "HP Jogador")
    draw_bar(100 * ratio_x, 80 * ratio_y, player.stamina, player.max_stamina, YELLOW, "Stamina Jogador")
    draw_bar(100 * ratio_x, 110 * ratio_y, player.mana, player.max_mana, BLUE, "Mana Jogador")

    draw_bar(WIDTH - 300 * ratio_x, 50 * ratio_y, enemy.hp, enemy.max_hp, RED, "HP Inimigo")
    draw_bar(WIDTH - 300 * ratio_x, 80 * ratio_y, enemy.stamina, enemy.max_stamina, YELLOW, "Stamina Inimigo")
    draw_bar(WIDTH - 300 * ratio_x, 110 * ratio_y, enemy.mana, enemy.max_mana, BLUE, "Mana Inimigo")

    # Logs de combate
    log_y_start = 200 * ratio_y
    for i, log in enumerate(combat_log):
        draw_text(log, WIDTH // 2, log_y_start + i * 25 * ratio_y, small_font, WHITE, centered=True)

    # Botões de ação
    if turn == "player":
        draw_text("Sua vez de atacar!", WIDTH // 2, HEIGHT - 130 * ratio_y, font, WHITE, centered=True)
        attack_button.draw(current_width, current_height)
        fireball_button.draw(current_width, current_height)
        heal_button.draw(current_width, current_height)
        defend_button.draw(current_width, current_height)

    # Mensagem de vitória ou derrota
    if not player.alive:
        game_state = "game_over"
        draw_text("Você perdeu!", WIDTH // 2, HEIGHT // 2, title_font, RED, centered=True)
    elif not enemy.alive:
        game_state = "game_over"
        draw_text("Você venceu!", WIDTH // 2, HEIGHT // 2, title_font, GREEN, centered=True)

    if game_state == "game_over":
        pygame.display.flip()
        pygame.time.delay(3000)
        running = False
        
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()