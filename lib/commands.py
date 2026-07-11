import pygame

class CommandConsole:
    def __init__(self, font):
        self.font = font
        self.active = False
        self.input_text = ""
        # Rectángulo arriba a la izquierda
        self.rect = pygame.Rect(15, 15, 450, 35)
        self.color_bg = (20, 20, 20)
        self.color_border = (220, 50, 50) # Contorno rojo de consola de comandos dev

    def handle_event(self, event):
        # F12: Activa / Desactiva la consola
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F12:
                self.active = not self.active
                self.input_text = "" # Limpiar al abrir/cerrar
                return None

        # Capturar el teclado solo si la consola está activa
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                command = self.input_text.strip().lower()
                self.input_text = ""
                self.active = False # Auto-cerrar al ingresar comando
                return command
                
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                # Limitar longitud para que no se salga del rectángulo
                if len(self.input_text) < 25 and event.unicode:
                    self.input_text += event.unicode
                    
        return None

    def draw(self, surface):
        if not self.active:
            return
            
        # Dibujar fondo negro y contorno rojo de la caja
        pygame.draw.rect(surface, self.color_bg, self.rect)
        pygame.draw.rect(surface, self.color_border, self.rect, 2)
        
        # Dibujar indicador de comando ">" y el texto en vivo
        text_surf = self.font.render(f"> {self.input_text}", True, (255, 255, 255))
        surface.blit(text_surf, (self.rect.x + 8, self.rect.y + (self.rect.height - text_surf.get_height()) // 2))