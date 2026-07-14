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

def execute_command(command, window):
    import importlib
    from lib import general_vars
    from lib import game as g
    from lib import anim_fram as af_direct

    if not command:
        return

    if command == "start":
        window.start_game_loading()
    elif command == "re":
        # Si estamos jugando, recargamos la mesa de juego del disco al instante
        if window.menu_state == "GAME":
            importlib.reload(general_vars)
            importlib.reload(af_direct) # Forzar recarga física de anim_fram.py
            importlib.reload(g)         # Forzar recarga física de game.py
            window.game_session = g.GamePlay(window.screen, window.selected_difficulty, window.translations)
    elif command == "gb":
        # Comando 'gb': Omitir la introducción de 5 segundos e iniciar directo el agarre de escopeta
        if window.menu_state == "GAME":
            # Recarga física total en caliente de tus coordenadas
            importlib.reload(general_vars)
            importlib.reload(af_direct) # Forzar recarga física de anim_fram.py
            importlib.reload(g)         # Forzar recarga física de game.py
            
            # Instanciar de nuevo la mesa de juego con los datos nuevos
            window.game_session = g.GamePlay(window.screen, window.selected_difficulty, window.translations)
            
            # OMITIR INTRODUCCIÓN: Forzar al dealer a estar ya sentado de inmediato en pose final
            window.game_session.dealer_anim.state = "FINAL"
            window.game_session.dealer_anim.head_scale = 1.0
            window.game_session.dealer_anim.hand_scale = 1.0
            window.game_session.dealer_anim.hand_y_offset = 160.0
            
            # Forzar al juego a disparar el deslizamiento de manos en una fracción de segundo
            window.game_session.game_state = "SHELLS_REVEAL"
            window.game_session.game_timer = pygame.time.get_ticks() - 3200