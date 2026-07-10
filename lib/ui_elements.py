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
            # Detectar el clic únicamente al soltar el botón (MOUSEBUTTONUP) para evitar doble disparo
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.rect.collidepoint(mouse_pos):
                    return True
            return False
    
class Slider:
    def __init__(self, x, y, width, label, font, current_val=1.0):
        self.x = x
        self.y = y
        self.width = width
        self.label = label
        self.font = font
        self.current_val = current_val
        
        self.bar_rect = pygame.Rect(self.x, self.y + 10, self.width, 6)
        self.handle_radius = 8
        self.handle_x = self.x + int(self.current_val * self.width)
        self.is_dragging = False

    def update(self, mouse_pos, mouse_pressed):
        # Tirador circular
        handle_rect = pygame.Rect(self.handle_x - self.handle_radius, self.y + 10 - self.handle_radius, self.handle_radius * 2, self.handle_radius * 2)
        # Rectángulo de colisión ensanchado para toda la barra del slider
        bar_click_rect = pygame.Rect(self.x, self.y - 5, self.width, 25)
        
        if mouse_pressed[0]: 
            # Iniciar arrastre si se hace clic sobre el tirador o sobre cualquier parte de la barra
            if handle_rect.collidepoint(mouse_pos) or bar_click_rect.collidepoint(mouse_pos):
                self.is_dragging = True
            
            if self.is_dragging:
                # Mantener arrastre activo aunque el cursor se salga por velocidad
                self.handle_x = max(self.x, min(mouse_pos[0], self.x + self.width))
                self.current_val = (self.handle_x - self.x) / self.width
        else:
            self.is_dragging = False

    def draw(self, surface):
        text_surf = self.font.render(f"{self.label}: {int(self.current_val * 100)}%", True, (150, 150, 150))
        surface.blit(text_surf, (self.x, self.y - 15))
        pygame.draw.rect(surface, (60, 60, 60), self.bar_rect)
        color = (255, 255, 255) if self.is_dragging else (180, 180, 180)
        pygame.draw.circle(surface, color, (self.handle_x, self.y + 13), self.handle_radius)


class InputBox:
    def __init__(self, x, y, width, height, label, font, initial_text=""):
        self.rect = pygame.Rect(x, y + 10, width, height)
        self.label = label
        self.font = font
        self.text = initial_text
        self.is_active = False
        self.color_inactive = (60, 60, 60)
        self.color_active = (255, 255, 255)
        self.current_color = self.color_inactive

    def handle_event(self, event):
        # Captura de teclas únicamente cuando la caja está activa
        if event.type == pygame.KEYDOWN and self.is_active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit(): # Solo números
                if len(self.text) < 4: # Límite de 4 dígitos (ej: 1920)
                    self.text += event.unicode

    def draw(self, surface):
        # Dibujar etiqueta arriba de la caja
        label_surf = self.font.render(self.label, True, (150, 150, 150))
        surface.blit(label_surf, (self.rect.x, self.rect.y - 25))
        
        # Dibujar texto ingresado adentro de la caja
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        surface.blit(text_surf, (self.rect.x + 8, self.rect.y + (self.rect.height - text_surf.get_height()) // 2))
        
        # Dibujar borde de la caja
        pygame.draw.rect(surface, self.current_color, self.rect, 2)