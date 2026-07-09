import pygame
from lib import general_vars

class WindowManager:
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((general_vars.WINDOW_WIDTH, general_vars.WINDOW_HEIGHT))
        pygame.display.set_caption("Shot Rulet")
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60) # Limitar a 60 FPS
            
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        # Actualización de estados del juego
        pass

    def draw(self):
        # Limpiar pantalla con el color de vars.py
        self.screen.fill(general_vars.COLOR_BLACK)
        pygame.display.flip()