import pygame
import os
from lib import general_vars

class GamePlay:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        
        # Cargar la textura de la mesa de juego en perspectiva
        bg_path = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "scenario", "Scene_0.png")
        self.background = None
        
        if os.path.exists(bg_path):
            self.background = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(
                self.background, 
                (general_vars.WINDOW_WIDTH, general_vars.WINDOW_HEIGHT)
            )

    def handle_event(self, event, mouse_pos):
        # Por ahora, detectar la tecla ESCAPE para regresar al menú principal
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "MENU_RETORNO"
        return None

    def update(self):
        # Aquí se actualizarán los elementos del gameplay (turnos, vida, escopeta)
        pass

    def draw(self):
        # Dibujar el fondo de la mesa de juego
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((20, 20, 20)) # Color de respaldo si no encuentra la imagen
            
        # Texto de estado temporal para el prototipo
        text_surf = self.font.render("Partida Iniciada - Presiona ESCAPE para salir", True, (255, 255, 255))
        self.screen.blit(text_surf, (40, 40))