import pygame

class Button:
    def __init__(self, x, y, text, font, text_color=(150, 150, 150), hover_color=(255, 255, 255)):
        self.text = text
        self.font = font
        self.text_color = text_color
        self.hover_color = hover_color
        
        # Renderizado inicial para obtener las dimensiones del botón
        self.image = self.font.render(self.text, True, self.text_color)
        self.rect = self.image.get_rect(center=(x, y))
        self.is_hovered = False

    def update(self, mouse_pos):
        # Detectar si el cursor del mouse está sobre el botón
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        # Cambiar el color del texto si el mouse está encima
        color = self.hover_color if self.is_hovered else self.text_color
        self.image = self.font.render(self.text, True, color)
        surface.blit(self.image, self.rect.topleft)

    def is_clicked(self, event, mouse_pos):
        # Detectar clic izquierdo del mouse
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False