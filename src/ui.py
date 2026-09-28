import pygame
from .settings import GRAY, LIGHT_GRAY, WHITE

class Button:
    def __init__(self, text, x, y, width, height, action, font, enabled=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.font = font
        self.enabled = enabled or (lambda: True)
        self.color = GRAY
        self.hover_color = LIGHT_GRAY

    def draw(self, screen, screen_width, screen_height, base_width, base_height):
        ratio_x = screen_width / base_width
        ratio_y = screen_height / base_height
        adjusted_rect = pygame.Rect(self.rect.x * ratio_x, self.rect.y * ratio_y,
                                    self.rect.width * ratio_x, self.rect.height * ratio_y)
        mouse_pos = pygame.mouse.get_pos()
        is_enabled = self.enabled()
        color = (self.hover_color if adjusted_rect.collidepoint(mouse_pos) else self.color) if is_enabled else (45, 45, 45)
        shadow_rect = adjusted_rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(screen, (0, 0, 0, 60), shadow_rect, border_radius=8)
        pygame.draw.rect(screen, color, adjusted_rect, border_radius=8)
        pygame.draw.rect(screen, (20, 20, 20), adjusted_rect, width=2, border_radius=8)
        text_color = WHITE if is_enabled else (135, 135, 135)
        draw_text(screen, self.text, adjusted_rect.centerx, adjusted_rect.centery, self.font, text_color, centered=True)

    def is_clicked(self, screen_width, screen_height, base_width, base_height, position):
        ratio_x = screen_width / base_width
        ratio_y = screen_height / base_height
        adjusted_rect = pygame.Rect(self.rect.x * ratio_x, self.rect.y * ratio_y,
                                    self.rect.width * ratio_x, self.rect.height * ratio_y)
        return self.enabled() and adjusted_rect.collidepoint(position)

def draw_text(screen, text, x, y, font_obj, color=WHITE, centered=False):
    surface = font_obj.render(text, True, color)
    rect = surface.get_rect(center=(x, y)) if centered else surface.get_rect(topleft=(x, y))
    screen.blit(surface, rect)
