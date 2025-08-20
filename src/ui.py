import pygame
from .settings import GRAY, LIGHT_GRAY, WHITE

class Button:
    def __init__(self, text, x, y, width, height, action, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.font = font
        self.color = GRAY
        self.hover_color = LIGHT_GRAY

    def draw(self, screen, screen_width, screen_height, base_width, base_height):
        ratio_x = screen_width / base_width
        ratio_y = screen_height / base_height
        adjusted_rect = pygame.Rect(self.rect.x * ratio_x, self.rect.y * ratio_y,
                                    self.rect.width * ratio_x, self.rect.height * ratio_y)
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if adjusted_rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, adjusted_rect, border_radius=5)
        draw_text(screen, self.text, adjusted_rect.centerx, adjusted_rect.centery, self.font, WHITE, centered=True)

    def is_clicked(self, screen_width, screen_height, base_width, base_height):
        ratio_x = screen_width / base_width
        ratio_y = screen_height / base_height
        adjusted_rect = pygame.Rect(self.rect.x * ratio_x, self.rect.y * ratio_y,
                                    self.rect.width * ratio_x, self.rect.height * ratio_y)
        return adjusted_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]

def draw_text(screen, text, x, y, font_obj, color=WHITE, centered=False):
    surface = font_obj.render(text, True, color)
    rect = surface.get_rect(center=(x, y)) if centered else surface.get_rect(topleft=(x, y))
    screen.blit(surface, rect)
