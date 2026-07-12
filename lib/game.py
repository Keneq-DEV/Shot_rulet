import pygame
import os
from lib import general_vars
from lib import anim_fram as af

class GamePlay:
    def __init__(self, screen, difficulty="change_dif_game_n"):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        
        # 1. Cargar la textura de fondo de la mesa de juego
        bg_path = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "scenario", "scene_5.png")
        self.background = None
        if os.path.exists(bg_path):
            self.background = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(
                self.background, 
                (general_vars.WINDOW_WIDTH, general_vars.WINDOW_HEIGHT)
            )

        # 2. Cargar la textura del slot individual del inventario
        slot_path = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "ui", "Hud", "Item_slot.png")
        self.slot_image = None
        if os.path.exists(slot_path):
            self.slot_image = pygame.image.load(slot_path).convert_alpha()
            self.slot_image = pygame.transform.scale(self.slot_image, (80, 80))

        # 3. Lógica del Inventario (8 espacios)
        self.inventory = [None] * 8

        # 4. Lógica de HP basada en la dificultad seleccionada
        hp_map = {
            "change_dif_game_e": 6,   # Fácil: 6 HP
            "change_dif_game_n": 4,   # Normal: 4 HP
            "change_dif_game_h": 3,   # Difícil: 3 HP
            "change_dif_game_hc": 2   # Hardcore: 2 HP
        }
        self.max_hp = hp_map.get(difficulty, 4)
        self.player_hp = self.max_hp
        self.dealer_hp = self.max_hp

        # 5. Cargar textura del contenedor de vida (life_container.png)
        container_path = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "ui", "Hud", "health_container.png")
        self.life_container = None
        if os.path.exists(container_path):
            self.life_container = pygame.image.load(container_path).convert_alpha()
            self.life_container = pygame.transform.scale(self.life_container, (260, 160)) # Ajustado a la altura del inventario

        # 6. Cargar textura del rayo de HP (life_point.png)
        point_path = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "ui", "Hud", "health_life.png")
        self.life_point = None
        if os.path.exists(point_path):
            self.life_point = pygame.image.load(point_path).convert_alpha()
            self.life_point = pygame.transform.scale(self.life_point, (24, 32)) # Tamaño de los rayos dentro del panel

        # Colores RGB para tintar los rayos de vida (puedes ajustar el del dealer aquí si lo deseas)
        self.player_color = (63, 92, 255)  # Azul (#3F5CFF)
        self.dealer_color = (255, 63, 63)  # Rojo (#FF3F3F)

        self.dealer_anim = af.DealerAnimator()

    def handle_event(self, event, mouse_pos):
        # Detectar la tecla ESCAPE para regresar al menú principal
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "MENU_RETORNO"
        return None

    def update(self):
        # Aquí se actualizarán los estados de la partida e interacción con ítems
        self.dealer_anim.update()

    def draw(self):
        # 1. Dibujar el fondo de la mesa de juego en perspectiva (scene_5.png)
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((20, 20, 20)) # Respaldo si no encuentra la mesa
            
        # 2. Dibujar al dealer animado (Fuera del 'else' para que se dibuje ENCIMA del fondo)
        self.dealer_anim.draw(self.screen)
            
        # 3. Dibujar el HUD de Inventario (Cuadrícula de 2x4 en la esquina inferior izquierda)
        self.draw_inventory_hud()
        self.draw_life_hud()

        # Texto de estado temporal para el prototipo
        text_surf = self.font.render("Partida Iniciada - Presiona ESCAPE para salir", True, (255, 255, 255))
        self.screen.blit(text_surf, (40, 40))

    def draw_inventory_hud(self):
        # Posición inicial del grid (Esquina inferior izquierda de la pantalla)
        start_x = 40
        start_y = general_vars.WINDOW_HEIGHT - 190 # Espaciado vertical desde el fondo
        slot_size = 80 # Ancho y alto de cada celda del inventario (coincide con el escalado)
        
        # Dibujar la cuadrícula lógica de 8 ranuras
        for index in range(8):
            # Calcular en qué fila (0 o 1) y columna (0, 1, 2, 3) va esta ranura
            row = index // 4
            col = index % 4
            
            # Posición final en pantalla para la celda actual
            x_pos = start_x + (col * slot_size)
            y_pos = start_y + (row * slot_size)
            
            # Dibujar la ranura física
            if self.slot_image:
                self.screen.blit(self.slot_image, (x_pos, y_pos))
            else:
                # Dibujar un recuadro de respaldo si no carga la imagen
                rect = pygame.Rect(x_pos, y_pos, slot_size, slot_size)
                pygame.draw.rect(self.screen, (30, 30, 30), rect)
                pygame.draw.rect(self.screen, (50, 50, 50), rect, 2)
                
            # (Futuro: Si self.inventory[index] tiene un objeto, se dibujará centrado dentro de x_pos y y_pos)

    def draw_life_hud(self):
        # Posición horizontal a la derecha del inventario (360px de inventario + 20px de espacio = 380px)
        start_x = 380
        start_y = general_vars.WINDOW_HEIGHT - 190
        
        # 1. Dibujar el contenedor de vida
        if self.life_container:
            self.screen.blit(self.life_container, (start_x, start_y))
        else:
            # Respaldo visual si no se encuentra life_container.png
            rect = pygame.Rect(start_x, start_y, 260, 160)
            pygame.draw.rect(self.screen, (30, 30, 30), rect)
            pygame.draw.rect(self.screen, (50, 50, 50), rect, 2)

        # 2. Posiciones verticales centradas dentro del contenedor para cada fila (Fila 1: Jugador, Fila 2: Dealer)
        y_player = start_y + 24
        y_dealer = start_y + 104
        
        # 3. Dibujar rayos de vida del Jugador (Player HP)
        for i in range(self.player_hp):
            x_pos = start_x + 25 + (i * 35)
            if self.life_point:
                # Duplicamos y aplicamos el color azul al rayo del jugador en vivo
                player_point = self.life_point.copy()
                player_point.fill(self.player_color, special_flags=pygame.BLEND_RGBA_MULT)
                self.screen.blit(player_point, (x_pos, y_player))
            else:
                # Respaldo de color azul
                pygame.draw.rect(self.screen, self.player_color, pygame.Rect(x_pos, y_player, 15, 25))

        # 4. Dibujar rayos de vida del Dealer (Dealer HP)
        for i in range(self.dealer_hp):
            x_pos = start_x + 25 + (i * 35)
            if self.life_point:
                # Duplicamos y aplicamos el color rojo al rayo del dealer en vivo
                dealer_point = self.life_point.copy()
                dealer_point.fill(self.dealer_color, special_flags=pygame.BLEND_RGBA_MULT)
                self.screen.blit(dealer_point, (x_pos, y_dealer))
            else:
                # Respaldo de color rojo
                pygame.draw.rect(self.screen, self.dealer_color, pygame.Rect(x_pos, y_dealer, 15, 25))