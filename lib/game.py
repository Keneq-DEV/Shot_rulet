import pygame
import os
from lib import general_vars
from lib import anim_fram as af

class GamePlay:
    def __init__(self, screen, difficulty="change_dif_game_n", translations=None):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        
        # Guardar las traducciones pasadas desde la ventana principal de forma segura
        self.translations = translations if translations is not None else {}

        # 1. Cargar la textura de fondo de la mesa de juego
        bg_path = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "scenario", "scene.png")
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

        # 7. Cargar y escalar la escopeta (shotgun.png)
        shotgun_path = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "shotgun", "shotgun_table.png")
        self.shotgun_image = None
        if os.path.exists(shotgun_path):
            self.shotgun_image = pygame.image.load(shotgun_path).convert_alpha()
            # Escalar la escopeta de forma proporcional para que encaje en el centro de la mesa
            self.shotgun_image = pygame.transform.scale(self.shotgun_image, (200, 320))

        # 8. Cargar los mismos sprites de cartuchos y rotarlos para que queden parados verticalmente
        shells_dir = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "sprites", "Shells")
        
        self.shell_live_hud = None
        live_path = os.path.join(shells_dir, "Shell_live.png")
        if os.path.exists(live_path):
            img = pygame.image.load(live_path).convert_alpha()
            # Rotamos 30 grados (coincidiendo con tu rotación) y escalamos proporcionalmente
            img = pygame.transform.rotate(img, 190)
            self.shell_live_hud = pygame.transform.scale(img, (35, 75))

        self.shell_blank_hud = None
        blank_path = os.path.join(shells_dir, "Shell_empty.png")
        if os.path.exists(blank_path):
            img = pygame.image.load(blank_path).convert_alpha()
            img = pygame.transform.rotate(img, 190)
            self.shell_blank_hud = pygame.transform.scale(img, (35, 75))

        # Variables de control de ronda y caja de diálogos (Cerrados al inicio)
        self.game_state = "DEALER_INTRO"   # Estado inicial: Esperar que el dealer termine de aparecer
        self.game_timer = pygame.time.get_ticks()
        self.dialogue_text = ""
        self.bullets_list = []
        self.bullets_on_table = 0         # Balas que se dibujan en mesa actualmente
        self.shells_opacity = 0           # Opacidad para la transición bonita de los cartuchos

        # Generar cartuchos de esta ronda
        self.generate_round_shells()

    def handle_event(self, event, mouse_pos):
        # Detectar la tecla ESCAPE para regresar al menú principal
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "MENU_RETORNO"
        return None

    def restart_grab_sequence(self):
        self.game_state = "GRAB_GUN"
        self.dialogue_text = ""
        self.bullets_list = []
        self.bullets_on_table = 0
        self.shells_opacity = 255
        self.dealer_anim.reset_to_grab_sequence()
        self.dealer_anim.update()
        self.dealer_anim.draw(self.screen)

    def update(self):
        # Actualizar la animación de aparición del dealer de forma modular
        self.dealer_anim.update()

        curr_time = pygame.time.get_ticks()
        
        # --- FASE 0: ESPERAR AL DEALER (Mesa vacía hasta que el dealer apoye sus manos) ---
        if self.game_state == "DEALER_INTRO":
            if self.dealer_anim.state == "FINAL":
                self.game_state = "SHELLS_REVEAL"
                self.game_timer = curr_time
                self.show_reveal_dialogue() # Cargar y formatear el conteo de balas en vivo

        # --- FASE 1: REVELAR CARTUCHOS (Aparecen con desvanecimiento de opacidad) ---
        elif self.game_state == "SHELLS_REVEAL":
            if self.shells_opacity < 255:
                self.shells_opacity = min(255, self.shells_opacity + 6)
            
            # Tras 3.5 segundos viendo las balas, pasamos a la fase de agarrar la escopeta
            if curr_time - self.game_timer >= 3500:
                self.game_state = "GRAB_GUN"
                self.dealer_anim.state = "GRAB_GUN"

        # --- FASE 2: DETECTAR EL AGARRE DE LA ESCOPETA ---
        elif self.game_state == "GRAB_GUN":
            if self.dealer_anim.state == "HOLDING_GUN":
                # Esperar 1 segundo en la mesa y luego iniciar la animación de jalar (PULL_GUN)
                if curr_time - self.dealer_anim.state_timer >= 1000:
                    self.game_state = "PULL_GUN"
                    self.dealer_anim.state = "PULL_GUN"
                    # REPARACIÓN: Limpiar el diálogo viejo y reiniciar el temporizador para dial_1
                    self.dialogue_text = ""
                    self.game_timer = curr_time

        # --- FASE 3: MONITOREAR EL JALE DE LA ESCOPETA Y MOSTRAR/QUITAR DIAL_1 ---
        elif self.game_state == "PULL_GUN":
            if self.dealer_anim.state == "HOLDING_PULLED":
                # Si el diálogo aún no se ha cargado en este estado, lo inicializamos
                if self.dialogue_text == "":
                    menu_text = self.translations.get("dialogue", {})
                    self.dialogue_text = menu_text.get("dial_1", "inserto los cartuchos en un orden desconocido")
                    self.game_timer = curr_time # Guardamos el tiempo en el que apareció el diálogo
                else:
                    # Transcurridos 2.5 segundos de lectura, quitamos el diálogo y cambiamos de estado
                    if curr_time - self.game_timer >= 2500:
                        self.dialogue_text = ""
                        self.game_state = "PULL_COMPLETE" # Transicionar para romper el bucle infinito

        # --- FASE 4: ENVIAR MANO IZQUIERDA A LA RECÁMARA ---
        elif self.game_state == "PULL_COMPLETE":
            self.game_state = "INSERT_PREP"
            self.dealer_anim.bullets_to_insert = self.bullets_on_table
            self.dealer_anim.state = "INSERT_PREP" # Ordenar al dealer que mueva e intercambie la mano izq
                                    
        elif self.game_state == "INSERT_PREP":
            if self.dealer_anim.state == "INSERTING":
                self.game_state = "SHELLS_INSERT"
                self.game_timer = curr_time

        # --- FASE 2: INSERTAR CARTUCHOS (Se van metiendo de uno en uno) ---
        elif self.game_state == "SHELLS_INSERT":
            # Sincronizar la cantidad de cartuchos en mesa con los que el dealer aún tiene que insertar
            self.bullets_on_table = self.dealer_anim.bullets_to_insert
            if self.bullets_on_table == 0 and self.dealer_anim.state == "HOLDING_PULLED":
                # Transicionar al bucle de juego activo y apagar diálogos
                self.game_state = "PLAY"
                self.dialogue_text = ""

    def draw(self):
        # 1. Dibujar el fondo de la mesa de juego en perspectiva (scene_5.png)
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((20, 20, 20)) # Respaldo si no encuentra la mesa
            
        # 2. Dibujar primero la escopeta centrada sobre el tablero
        if self.shotgun_image and self.dealer_anim.state not in ["HOLDING_GUN", "PULL_GUN", "HOLDING_PULLED", "INSERT_PREP", "INSERT_READY", "INSERTING"]:
            # Centrada en X, y posicionada verticalmente a Y = 580 (en medio de la mesa)
            shotgun_rect = self.shotgun_image.get_rect(center=(general_vars.WINDOW_WIDTH // 2, 580))
            self.screen.blit(self.shotgun_image, shotgun_rect.topleft)

        # 3. Dibujar al dealer después (para que sus manos se pinten ENCIMA de la escopeta)
        self.dealer_anim.draw(self.screen)
            
        # 4. Dibujar el HUD de Inventario (Cuadrícula de 2x4 en la esquina inferior izquierda)
        self.draw_inventory_hud()
        self.draw_life_hud()

        # 4. Dibujar los cartuchos revelados en mesa y la caja de diálogos
        self.draw_game_round_hud()

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
        start_x = general_vars.WINDOW_WIDTH // 2 + 200  # Centrado horizontal 
        start_y = 15 
        
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

    def generate_round_shells(self):
        import random
        # 1. Generar cantidad total aleatoria de balas (entre 2 y 6)
        total_shells = random.randint(2, 6)
        # 2. Respetar regla: Asegurar que SIEMPRE haya al menos 1 real (live) Y al menos 1 falsa (blank)
        self.lives_count = random.randint(1, total_shells - 1)
        self.blanks_count = total_shells - self.lives_count
        
        # 3. Construir la lista de cartuchos mezclados aleatoriamente
        self.bullets_list = ["live"] * self.lives_count + ["blank"] * self.blanks_count
        random.shuffle(self.bullets_list)
        self.bullets_on_table = len(self.bullets_list)

    def show_reveal_dialogue(self):
        # Formatear dinámicamente el diálogo 'dial_0' usando las plantillas en el momento oportuno
        items_text = self.translations.get("items_name", {}) or self.translations.get("items-name", {})
        menu_text = self.translations.get("dialogue", {})
        
        live_name = items_text.get("sheel_r", "Real")
        blank_name = items_text.get("sheel_f", "Fake")
        
        template = menu_text.get("dial_0", "{{count_s1}} {{type_sheel1}}, {{count_s2}} {{type_sheel2}}.")
        self.dialogue_text = template.replace("{{count_s1}}", str(self.lives_count))\
                                     .replace("{{type_sheel1}}", live_name)\
                                     .replace("{{count_s2}}", str(self.blanks_count))\
                                     .replace("{{type_sheel2}}", blank_name)

    def draw_game_round_hud(self):
        # 1. Dibujar Cartuchos parados en la mesa (a la derecha de la escopeta)
        if self.game_state in ["SHELLS_REVEAL", "SHELLS_INSERT"] and self.bullets_on_table > 0:
            start_x = general_vars.WINDOW_WIDTH // 2 + 100
            start_y = 440
            spacing_x = 30
            
            for i in range(self.bullets_on_table):
                bullet_type = self.bullets_list[i]
                sprite = self.shell_live_hud if bullet_type == "live" else self.shell_blank_hud
                
                if sprite:
                    # Copia para aplicar la opacidad en vivo (transición bonita)
                    temp_sprite = sprite.copy()
                    temp_sprite.set_alpha(self.shells_opacity)
                    self.screen.blit(temp_sprite, (start_x + (i * spacing_x), start_y))

        # 2. Dibujar Caja de Diálogo (Contenedor negro abajo centrado)
        if self.dialogue_text:
            box_width = 640
            box_height = 80
            box_x = general_vars.WINDOW_WIDTH // 2 - box_width // 2
            box_y = general_vars.WINDOW_HEIGHT - 100
            
            box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
            
            # Dibujar caja con bordes
            pygame.draw.rect(self.screen, (10, 10, 10), box_rect)
            pygame.draw.rect(self.screen, (40, 40, 40), box_rect, 2)
            
            # Dibujar el texto centrado adentro de la caja
            text_surf = self.font.render(self.dialogue_text, True, (240, 240, 240))
            text_rect = text_surf.get_rect(center=(box_x + box_width // 2, box_y + box_height // 2))
            self.screen.blit(text_surf, text_rect.topleft)