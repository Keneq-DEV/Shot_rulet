import pygame
import os
from lib import general_vars
from lib import anim_fram as af
from lib import music_manager as mm

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

        # 7.5 Cargar texturas de la escopeta sostenida por el jugador
        self.player_shotgun_1 = None
        self.player_shotgun_pump = None
        self.player_shotgun_2 = None
        self.player_shotgun_3 = None
        self.player_shotgun_pump_3 = None
        self.defib_1 = None
        self.defib_2 = None
        self.flash_sprite = None

        p_shot_1_path = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "shotgun", "shotgun_h_st_player_1.png")
        if os.path.exists(p_shot_1_path):
            self.player_shotgun_1 = pygame.image.load(p_shot_1_path).convert_alpha()
        p_shot_pump_path = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "shotgun", "shotgun_h_st_player_pump.png")
        if os.path.exists(p_shot_pump_path):
            self.player_shotgun_pump = pygame.image.load(p_shot_pump_path).convert_alpha()
        p_shot_2_path = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "shotgun", "shotgun_h_st_player_2.png")
        if os.path.exists(p_shot_2_path):
            self.player_shotgun_2 = pygame.image.load(p_shot_2_path).convert_alpha()
        p_shot_3_path = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "shotgun", "shotgun_h_st_player_3.png")
        if os.path.exists(p_shot_3_path):
            self.player_shotgun_3 = pygame.image.load(p_shot_3_path).convert_alpha()
        p_shot_pump3_path = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "shotgun", "shotgun_h_st_player_pump_3.png")
        if os.path.exists(p_shot_pump3_path):
            self.player_shotgun_pump_3 = pygame.image.load(p_shot_pump3_path).convert_alpha()


        defib1_path = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "sprites", "defib_1.png")
        if os.path.exists(defib1_path):
            self.defib_1 = pygame.image.load(defib1_path).convert_alpha()
        defib2_path = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "sprites", "defib_2.png")
        if os.path.exists(defib2_path):
            self.defib_2 = pygame.image.load(defib2_path).convert_alpha()
        flash_path = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "sprites", "flash.png")
        if os.path.exists(flash_path):
            self.flash_sprite = pygame.image.load(flash_path).convert_alpha()

        # Variables de interacción y estados de la escopeta para el jugador
        self.table_shotgun_y_offset = 0
        self.player_shotgun_state = "TABLE"  # "TABLE", "GRABBING", "HELD_RAISING", "HELD_READY"
        self.grabbed_shotgun_y = 580.0
        self.held_shotgun_y = 720.0          # Y de la escopeta en primera persona
        self.player_shotgun_timer = 0
        self.show_choices = False

        # Variables para la expulsión de cartuchos y el bombeo del jugador
        self.ejected_shell_active = False
        self.ejected_shell_sprite = None
        self.ejected_shell_x = 0.0
        self.ejected_shell_y = 0.0
        self.ejected_shell_vx = 0.0
        self.ejected_shell_vy = 0.0
        self.ejected_shell_angle = 0.0
        self.player_pump_y_offset = 0.0
        self.player_pump_x_offset = 0.0

        # Variables de desfibrilador, flash y cámara
        self.defib_1_x = 0.0
        self.defib_2_x = 835.0
        self.defib_phase = "SHOW"
        self.defib_play_timer = 0
        self.camera_zoom = 1.0
        self.temp_surface = pygame.Surface((general_vars.WINDOW_WIDTH, general_vars.WINDOW_HEIGHT))

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

        # Clic en la escopeta para agarrarla
        if self.game_state == "PLAY" and self.player_shotgun_state == "TABLE":
            shotgun_w, shotgun_h = 200, 320
            shotgun_x = general_vars.WINDOW_WIDTH // 2 - shotgun_w // 2
            shotgun_y = 580 - shotgun_h // 2
            shot_rect = pygame.Rect(shotgun_x, shotgun_y, shotgun_w, shotgun_h)
            if shot_rect.collidepoint(mouse_pos):
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.player_shotgun_state = "GRABBING"
                    self.grabbed_shotgun_y = 580.0 + self.table_shotgun_y_offset

        # Clic en las opciones de disparo (choices1 / choices2)
        if self.show_choices:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # rect1 para choice1 (- TU -)
                rect1 = pygame.Rect(general_vars.WINDOW_WIDTH // 2 - 100, general_vars.WINDOW_HEIGHT - 100, 200, 40)
                if rect1.collidepoint(mouse_pos):
                    self.player_shotgun_state = "HELD_LOWERING"
                    self.show_choices = False
                
                # rect2 para choice2 (- DEALER -)
                rect2 = pygame.Rect(general_vars.WINDOW_WIDTH // 2 - 100, 100, 200, 40)
                if rect2.collidepoint(mouse_pos):
                    self.player_shotgun_state = "HELD_LOWERING_DEALER"
                    self.show_choices = False

        # Presionar espacio para disparar en SELF_READY
        if self.player_shotgun_state == "SELF_READY":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # Comprobar el tipo de cartucho en la recámara
                if self.bullets_list:
                    current_bullet = self.bullets_list[0]
                    if current_bullet == "live":
                        self.player_shotgun_state = "SHOT_FLASH"
                        self.player_shotgun_timer = pygame.time.get_ticks()
                        self.sound_triggered = False
                        from lib import sound_manager as sm
                        sm.play_sound("Assets/sounds", "shotgun_shot_cut", "wav", type=1, id=3)
                        mm.play_music_transition(
                            "club_ambience1", "Assets/music", "second_m", "ogg", 1, 0
                        )
                    else:  # blank
                        self.player_shotgun_state = "SHOT_BLANK_CLICK"
                        self.player_shotgun_timer = pygame.time.get_ticks()
                        self.sound_triggered = False
                        from lib import sound_manager as sm
                        sm.play_sound("Assets/sounds", "shotgun_shot_blank", "wav", type=1, id=3)

        # Presionar espacio para disparar en DEALER_READY
        if self.player_shotgun_state == "DEALER_READY":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.bullets_list:
                    current_bullet = self.bullets_list[0]
                    if current_bullet == "live":
                        self.player_shotgun_state = "SHOT_FLASH_DEALER"
                        self.player_shotgun_timer = pygame.time.get_ticks()
                        self.sound_triggered = False
                        self.dealer_anim.state = "SHOT_BACK" # El dealer es mandado hacia atrás
                        from lib import sound_manager as sm
                        sm.play_sound("Assets/sounds", "shotgun_shot", "wav", type=1, id=3)
                    else:  # blank
                        self.player_shotgun_state = "SHOT_BLANK_CLICK_DEALER"
                        self.player_shotgun_timer = pygame.time.get_ticks()
                        self.sound_triggered = False
                        from lib import sound_manager as sm
                        sm.play_sound("Assets/sounds", "shotgun_shot_blank", "wav", type=1, id=3)
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
        # Actualizar física del cartucho expulsado (si está activo)
        if self.ejected_shell_active:
            self.ejected_shell_x += self.ejected_shell_vx
            self.ejected_shell_vy += 1.2  # Gravedad
            self.ejected_shell_y += self.ejected_shell_vy
            self.ejected_shell_angle += 15.0  # Rotación
            if self.ejected_shell_y > general_vars.WINDOW_HEIGHT + 100:
                self.ejected_shell_active = False

        # Actualizar la animación de aparición del dealer de forma modular
        self.dealer_anim.update()

        curr_time = pygame.time.get_ticks()

        # Hover y animaciones de la escopeta del jugador
        if self.game_state == "PLAY":
            if self.player_shotgun_state == "TABLE":
                mouse_pos = pygame.mouse.get_pos()
                shotgun_w, shotgun_h = 200, 320
                shotgun_x = general_vars.WINDOW_WIDTH // 2 - shotgun_w // 2
                shotgun_y = 580 - shotgun_h // 2
                shot_rect = pygame.Rect(shotgun_x, shotgun_y, shotgun_w, shotgun_h)
                if shot_rect.collidepoint(mouse_pos):
                    self.table_shotgun_y_offset = -15
                else:
                    self.table_shotgun_y_offset = 0

            elif self.player_shotgun_state == "GRABBING":
                self.grabbed_shotgun_y += 25
                if self.grabbed_shotgun_y > general_vars.WINDOW_HEIGHT + 200:
                    self.player_shotgun_state = "HELD_RAISING"
                    self.held_shotgun_y = float(general_vars.WINDOW_HEIGHT)

            elif self.player_shotgun_state == "HELD_RAISING":
                target_y = float(general_vars.WINDOW_HEIGHT - self.player_shotgun_1.get_height())
                # Deslizar hacia arriba con interpolación suave
                self.held_shotgun_y += (target_y - self.held_shotgun_y) * 0.1
                
                if abs(self.held_shotgun_y - target_y) < 2:
                    self.held_shotgun_y = target_y
                    self.player_shotgun_state = "HELD_READY"
                    self.show_choices = True

            elif self.player_shotgun_state == "HELD_LOWERING":
                self.held_shotgun_y += 20
                if self.held_shotgun_y >= general_vars.WINDOW_HEIGHT:
                    self.player_shotgun_state = "HELD_RAISING_SELF"
                    self.held_shotgun_y = float(general_vars.WINDOW_HEIGHT)

            elif self.player_shotgun_state == "HELD_RAISING_SELF":
                target_y = float(general_vars.WINDOW_HEIGHT - self.player_shotgun_2.get_height())
                self.held_shotgun_y += (target_y - self.held_shotgun_y) * 0.1
                if abs(self.held_shotgun_y - target_y) < 2:
                    self.held_shotgun_y = target_y
                    self.player_shotgun_state = "SELF_READY"

            elif self.player_shotgun_state == "SHOT_FLASH":
                if curr_time - self.player_shotgun_timer >= 60:  # Mostrar destello por 60ms
                    self.player_shotgun_state = "SHOT_WHITE"
                    self.player_shotgun_timer = curr_time

            elif self.player_shotgun_state == "SHOT_WHITE":
                if curr_time - self.player_shotgun_timer >= 100:  # Blanco por 100ms
                    self.player_shotgun_state = "SHOT_BLACK"
                    self.player_shotgun_timer = curr_time
                    self.sound_triggered = False

            elif self.player_shotgun_state == "SHOT_BLACK":
                # Silencio y pantalla negra, luego desfibrilador
                if curr_time - self.player_shotgun_timer >= 1000:
                    if not self.sound_triggered:
                        from lib import sound_manager as sm
                        sm.play_sound("Assets/sounds", "defib_discharge", "ogg", type=1, id=4)
                        self.sound_triggered = True
                        self.defib_play_timer = curr_time
                if self.sound_triggered and curr_time - self.defib_play_timer >= 1458:
                    # Al acabar el sonido, se quita la pantalla negra.
                    # Para entonces, la escopeta ya debe figurar en la mesa (estado "TABLE" pero en DEFIB_ANIM)
                    self.player_shotgun_state = "DEFIB_ANIM"
                    self.player_shotgun_timer = curr_time
                    self.defib_1_x = 0.0
                    self.defib_2_x = float(general_vars.WINDOW_WIDTH - self.defib_2.get_width())
                    self.defib_phase = "SHOW"

            elif self.player_shotgun_state == "DEFIB_ANIM":
                if self.defib_phase == "SHOW":
                    if curr_time - self.player_shotgun_timer >= 1200:
                        self.defib_phase = "SLIDE_OUT"
                elif self.defib_phase == "SLIDE_OUT":
                    self.defib_1_x -= 20
                    self.defib_2_x += 20
                    if self.defib_1_x < -500:
                        self.player_shotgun_state = "ZOOM_IN"

            elif self.player_shotgun_state == "ZOOM_IN":
                # Zoom suave al hud de vida
                self.camera_zoom += (2.2 - self.camera_zoom) * 0.08
                if self.camera_zoom >= 2.18:
                    self.camera_zoom = 2.2
                    self.player_hp = max(0, self.player_hp - 1)
                    if self.bullets_list:
                        self.bullets_list.pop(0)
                    from lib import sound_manager as sm
                    sm.play_sound("Assets/sounds", "reduce_health", "ogg", type=1, id=5)
                    self.player_shotgun_state = "ZOOM_HOLD"
                    self.player_shotgun_timer = curr_time

            elif self.player_shotgun_state == "ZOOM_HOLD":
                if curr_time - self.player_shotgun_timer >= 1500:
                    self.player_shotgun_state = "ZOOM_OUT"

            elif self.player_shotgun_state == "ZOOM_OUT":
                self.camera_zoom += (1.0 - self.camera_zoom) * 0.08
                if self.camera_zoom <= 1.02:
                    self.camera_zoom = 1.0
                    # Regresa a la normalidad, la escopeta ya está en la mesa, sin animación
                    self.player_shotgun_state = "TABLE"
                    self.show_choices = False

            # === NUEVOS ESTADOS PARA EL DISPARO DE CARTUCHO BLANK ===
            elif self.player_shotgun_state == "SHOT_BLANK_CLICK":
                if curr_time - self.player_shotgun_timer >= 500:  # Esperar 500ms
                    self.player_shotgun_state = "SHOT_BLANK_LOWERING"

            elif self.player_shotgun_state == "SHOT_BLANK_LOWERING":
                self.held_shotgun_y += 20
                if self.held_shotgun_y >= general_vars.WINDOW_HEIGHT:
                    self.player_shotgun_state = "SHOT_BLANK_RAISING_1"
                    self.held_shotgun_y = float(general_vars.WINDOW_HEIGHT)

            elif self.player_shotgun_state == "SHOT_BLANK_RAISING_1":
                target_y = float(general_vars.WINDOW_HEIGHT - self.player_shotgun_1.get_height())
                self.held_shotgun_y += (target_y - self.held_shotgun_y) * 0.1
                if abs(self.held_shotgun_y - target_y) < 2:
                    self.held_shotgun_y = target_y
                    self.player_shotgun_state = "SHOT_BLANK_PUMP"
                    self.player_shotgun_timer = curr_time
                    self.sound_triggered = False
                    self.player_pump_y_offset = 0.0

            elif self.player_shotgun_state == "SHOT_BLANK_PUMP":
                elapsed = curr_time - self.player_shotgun_timer
                
                # Fase 1: Tirar hacia atrás (0 - 200 ms)
                if elapsed < 200:
                    progress = elapsed / 200.0
                    self.player_pump_y_offset = 25.0 * progress
                    self.player_pump_x_offset = self.player_pump_y_offset * 1.28 # Desplazamiento diagonal
                    
                    if not self.sound_triggered:
                        from lib import sound_manager as sm
                        sm.play_sound("Assets/sounds", "rack_shotgun", "ogg", type=1, id=2)
                        self.sound_triggered = True
                        
                        # Expulsar cartucho blank
                        self.ejected_shell_active = True
                        self.ejected_shell_sprite = self.shell_blank_hud
                        self.ejected_shell_x = general_vars.WINDOW_WIDTH // 2 + 30
                        self.ejected_shell_y = self.held_shotgun_y + 150
                        self.ejected_shell_vx = 10.0
                        self.ejected_shell_vy = -12.0
                        self.ejected_shell_angle = 0.0
                        
                        # Quitar el cartucho blank de la recámara
                        if self.bullets_list:
                            self.bullets_list.pop(0)
                
                # Fase 2: Mantener atrás (200 - 400 ms)
                elif elapsed < 400:
                    self.player_pump_y_offset = 25.0
                    self.player_pump_x_offset = self.player_pump_y_offset * 1.28
                    
                # Fase 3: Regresar adelante (400 - 600 ms)
                elif elapsed < 600:
                    progress = (elapsed - 400.0) / 200.0
                    self.player_pump_y_offset = 25.0 * (1.0 - progress)
                    self.player_pump_x_offset = self.player_pump_y_offset * 1.28
                    
                else:
                    self.player_pump_y_offset = 0.0
                    self.player_pump_x_offset = 0.0
                    self.player_shotgun_state = "HELD_READY"
                    self.show_choices = True

            elif self.player_shotgun_state == "HELD_LOWERING_DEALER":
                self.held_shotgun_y += 20
                if self.held_shotgun_y >= general_vars.WINDOW_HEIGHT:
                    self.player_shotgun_state = "HELD_RAISING_DEALER"
                    self.held_shotgun_y = float(general_vars.WINDOW_HEIGHT)

            elif self.player_shotgun_state == "HELD_RAISING_DEALER":
                target_y = float(general_vars.WINDOW_HEIGHT - self.player_shotgun_3.get_height())
                self.held_shotgun_y += (target_y - self.held_shotgun_y) * 0.1
                if abs(self.held_shotgun_y - target_y) < 2:
                    self.held_shotgun_y = target_y
                    self.player_shotgun_state = "DEALER_READY"

            elif self.player_shotgun_state == "SHOT_FLASH_DEALER":
                if curr_time - self.player_shotgun_timer >= 100:  # Mostrar destello por 100ms
                    self.player_shotgun_state = "DEALER_SHOT_FALL"
                    self.player_shotgun_timer = curr_time

            elif self.player_shotgun_state == "DEALER_SHOT_FALL":
                if curr_time - self.player_shotgun_timer >= 500:  # Esperar que caiga hacia atrás
                    self.player_shotgun_state = "ZOOM_IN_DEALER"

            elif self.player_shotgun_state == "ZOOM_IN_DEALER":
                # Zoom suave al hud de vida (donde está la del dealer)
                self.camera_zoom += (2.2 - self.camera_zoom) * 0.08
                if self.camera_zoom >= 2.18:
                    self.camera_zoom = 2.2
                    self.dealer_hp = max(0, self.dealer_hp - 1)
                    from lib import sound_manager as sm
                    sm.play_sound("Assets/sounds", "reduce_health", "ogg", type=1, id=5)
                    self.player_shotgun_state = "ZOOM_HOLD_DEALER"
                    self.player_shotgun_timer = curr_time

            elif self.player_shotgun_state == "ZOOM_HOLD_DEALER":
                if curr_time - self.player_shotgun_timer >= 1500:
                    self.player_shotgun_state = "ZOOM_OUT_DEALER"

            elif self.player_shotgun_state == "ZOOM_OUT_DEALER":
                self.camera_zoom += (1.0 - self.camera_zoom) * 0.08
                if self.camera_zoom <= 1.02:
                    self.camera_zoom = 1.0
                    # Antes de bajar la escopeta, hacer el bombeo si fue bala LIVE
                    self.player_shotgun_state = "SHOT_LIVE_PUMP_DEALER"
                    self.player_shotgun_timer = curr_time
                    self.sound_triggered = False
                    self.player_pump_y_offset = 0.0
                    self.player_pump_x_offset = 0.0
                    self.held_shotgun_y = float(general_vars.WINDOW_HEIGHT - self.player_shotgun_3.get_height())

            # === ESTADO BOMBEO LIVE CONTRA DEALER ===
            elif self.player_shotgun_state == "SHOT_LIVE_PUMP_DEALER":
                elapsed = curr_time - self.player_shotgun_timer
                
                # Fase 1: Tirar hacia atrás (0 - 200 ms)
                if elapsed < 200:
                    progress = elapsed / 200.0
                    self.player_pump_y_offset = 25.0 * progress
                    self.player_pump_x_offset = self.player_pump_y_offset * 1.28 # Desplazamiento diagonal
                    
                    if not self.sound_triggered:
                        from lib import sound_manager as sm
                        sm.play_sound("Assets/sounds", "rack_shotgun", "ogg", type=1, id=2)
                        self.sound_triggered = True
                        
                        # Expulsar cartucho LIVE
                        self.ejected_shell_active = True
                        self.ejected_shell_sprite = self.shell_live_hud # Aquí expulsamos el rojo
                        self.ejected_shell_x = general_vars.WINDOW_WIDTH // 2 + 30
                        self.ejected_shell_y = self.held_shotgun_y + 150
                        self.ejected_shell_vx = 10.0
                        self.ejected_shell_vy = -12.0
                        self.ejected_shell_angle = 0.0
                        
                        # Quitar el cartucho LIVE de la recámara
                        if self.bullets_list:
                            self.bullets_list.pop(0)
                
                # Fase 2: Mantener atrás (200 - 400 ms)
                elif elapsed < 400:
                    self.player_pump_y_offset = 25.0
                    self.player_pump_x_offset = self.player_pump_y_offset * 1.28
                    
                # Fase 3: Regresar adelante (400 - 600 ms)
                elif elapsed < 600:
                    progress = (elapsed - 400.0) / 200.0
                    self.player_pump_y_offset = 25.0 * (1.0 - progress)
                    self.player_pump_x_offset = self.player_pump_y_offset * 1.28
                    
                else:
                    self.player_pump_y_offset = 0.0
                    self.player_pump_x_offset = 0.0
                    self.player_shotgun_state = "HELD_LOWERING_DEALER_DONE"

            elif self.player_shotgun_state == "HELD_LOWERING_DEALER_DONE":
                self.held_shotgun_y += 20
                if self.held_shotgun_y >= general_vars.WINDOW_HEIGHT:
                    self.player_shotgun_state = "TABLE"
                    self.show_choices = False
                    
                    # Activar la animación de levantarse/recuperarse del dealer
                    self.dealer_anim.state = "RECOVER_RISING"
                    self.dealer_anim.hand_l_y = 720.0
                    self.dealer_anim.hand_r_y = 720.0
                    self.dealer_anim.is_shooted = True
                    self.dealer_anim.recover_phase = "HANDS"
                    self.dealer_anim.head_scale = 0.0
                    self.dealer_anim.y = 170

            # === ESTADOS BLANK CONTRA DEALER ===
            elif self.player_shotgun_state == "SHOT_BLANK_CLICK_DEALER":
                if curr_time - self.player_shotgun_timer >= 500:  # Esperar 500ms con la escopeta en alto
                    self.player_shotgun_state = "SHOT_BLANK_PUMP_DEALER"
                    self.player_shotgun_timer = curr_time
                    self.sound_triggered = False
                    self.player_pump_y_offset = 0.0
                    self.player_pump_x_offset = 0.0

            elif self.player_shotgun_state == "SHOT_BLANK_PUMP_DEALER":
                elapsed = curr_time - self.player_shotgun_timer
                
                # Fase 1: Tirar hacia atrás (0 - 200 ms)
                if elapsed < 200:
                    progress = elapsed / 200.0
                    self.player_pump_y_offset = 25.0 * progress
                    self.player_pump_x_offset = self.player_pump_y_offset * 1.28 # Desplazamiento diagonal
                    
                    if not self.sound_triggered:
                        from lib import sound_manager as sm
                        sm.play_sound("Assets/sounds", "rack_shotgun", "ogg", type=1, id=2)
                        self.sound_triggered = True
                        
                        # Expulsar cartucho blank
                        self.ejected_shell_active = True
                        self.ejected_shell_sprite = self.shell_blank_hud
                        self.ejected_shell_x = general_vars.WINDOW_WIDTH // 2 + 30
                        self.ejected_shell_y = self.held_shotgun_y + 150
                        self.ejected_shell_vx = 10.0
                        self.ejected_shell_vy = -12.0
                        self.ejected_shell_angle = 0.0
                        
                        # Quitar el cartucho blank de la recámara
                        if self.bullets_list:
                            self.bullets_list.pop(0)
                
                # Fase 2: Mantener atrás (200 - 400 ms)
                elif elapsed < 400:
                    self.player_pump_y_offset = 25.0
                    self.player_pump_x_offset = self.player_pump_y_offset * 1.28
                    
                # Fase 3: Regresar adelante (400 - 600 ms)
                elif elapsed < 600:
                    progress = (elapsed - 400.0) / 200.0
                    self.player_pump_y_offset = 25.0 * (1.0 - progress)
                    self.player_pump_x_offset = self.player_pump_y_offset * 1.28
                    
                else:
                    self.player_pump_y_offset = 0.0
                    self.player_pump_x_offset = 0.0
                    self.player_shotgun_state = "DEALER_READY"
                    self.show_choices = True
        
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
            if self.bullets_on_table == 0 and self.dealer_anim.state == "FINAL":
                # Transicionar al bucle de juego activo y apagar diálogos
                self.game_state = "PLAY"
                self.dialogue_text = ""

    def draw(self):
        # Manejo de pantallas completas de disparo
        if self.player_shotgun_state == "SHOT_WHITE":
            self.screen.fill((255, 255, 255))
            return

        elif self.player_shotgun_state == "SHOT_BLACK":
            self.screen.fill((0, 0, 0))
            return

        # Dibujar el contenido normal sobre la superficie temporal
        self.temp_surface.fill((0, 0, 0))
        
        # 1. Dibujar el fondo de la mesa de juego en perspectiva (scene_5.png)
        if self.background:
            self.temp_surface.blit(self.background, (0, 0))
        else:
            self.temp_surface.fill((20, 20, 20)) # Respaldo si no encuentra la mesa
            
        # 2. Dibujar la escopeta sobre el tablero (si no la tiene el dealer ni está en las manos del jugador)
        if self.shotgun_image and self.dealer_anim.state not in ["HOLDING_GUN", 
                                                                 "PULL_GUN", 
                                                                 "HOLDING_PULLED", 
                                                                 "INSERT_PREP", 
                                                                 "INSERT_READY", 
                                                                 "INSERTING", 
                                                                 "PUMP_PREP", 
                                                                 "PUMP_ACTION", 
                                                                 "PUSH_GUN"]:
            
            if self.player_shotgun_state not in ["GRABBING", 
                                                 "HELD_RAISING", 
                                                 "HELD_READY", 
                                                 "HELD_LOWERING", 
                                                 "HELD_RAISING_SELF", 
                                                 "SELF_READY", 
                                                 "SHOT_FLASH", 
                                                 "SHOT_WHITE", 
                                                 "SHOT_BLACK", 
                                                 "SHOT_BLANK_CLICK", 
                                                 "SHOT_BLANK_LOWERING", 
                                                 "SHOT_BLANK_RAISING_1", 
                                                 "SHOT_BLANK_PUMP",
                                                 "HELD_LOWERING_DEALER",
                                                 "HELD_RAISING_DEALER",
                                                 "DEALER_READY",
                                                 "SHOT_FLASH_DEALER",
                                                 "DEALER_SHOT_FALL",
                                                 "HELD_LOWERING_DEALER_DONE",
                                                 "SHOT_BLANK_CLICK_DEALER",
                                                 "SHOT_BLANK_PUMP_DEALER",
                                                 "SHOT_LIVE_PUMP_DEALER", # Agregado aquí
                                                 "ZOOM_IN_DEALER",
                                                 "ZOOM_HOLD_DEALER",
                                                 "ZOOM_OUT_DEALER"]:
                y_pos = 580 + self.table_shotgun_y_offset
                shotgun_rect = self.shotgun_image.get_rect(center=(general_vars.WINDOW_WIDTH // 2, y_pos))
                self.temp_surface.blit(self.shotgun_image, shotgun_rect.topleft)
            elif self.player_shotgun_state == "GRABBING":
                shotgun_rect = self.shotgun_image.get_rect(center=(general_vars.WINDOW_WIDTH // 2, int(self.grabbed_shotgun_y)))
                self.temp_surface.blit(self.shotgun_image, shotgun_rect.topleft)

        # 3. Dibujar al dealer después (para que sus manos se pinten ENCIMA de la escopeta)
        self.dealer_anim.draw(self.temp_surface)
            
        # 4. Dibujar el HUD de Inventario, HUD de vida, y cartuchos
        self.draw_inventory_hud(self.temp_surface)
        self.draw_life_hud(self.temp_surface)
        self.draw_game_round_hud(self.temp_surface)

        # Texto de estado temporal para el prototipo
        text_surf = self.font.render("Partida Iniciada - Presiona ESCAPE para salir", True, (255, 255, 255))
        self.temp_surface.blit(text_surf, (40, 40))

        # Dibujar la escopeta sostenida por el jugador
        if self.player_shotgun_state in ["HELD_RAISING", 
                                         "HELD_READY", 
                                         "HELD_LOWERING", 
                                         "SHOT_BLANK_RAISING_1", 
                                         "SHOT_BLANK_PUMP"]:
            sprite = self.player_shotgun_1
            if sprite:
                x_pos = general_vars.WINDOW_WIDTH // 2 - sprite.get_width() // 2
                self.temp_surface.blit(sprite, (x_pos, int(self.held_shotgun_y)))
                # Dibujar el pump encima (capa acoplada que se mueve en sincronía con offset diagonal de bombeo)
                if self.player_shotgun_pump:
                    pump_x = x_pos + self.player_pump_x_offset
                    pump_y = self.held_shotgun_y + self.player_pump_y_offset
                    self.temp_surface.blit(self.player_shotgun_pump, (int(pump_x), int(pump_y)))

        elif self.player_shotgun_state in ["HELD_RAISING_SELF", 
                                           "SELF_READY", 
                                           "SHOT_FLASH", 
                                           "SHOT_BLANK_CLICK", 
                                           "SHOT_BLANK_LOWERING"]:
            sprite = self.player_shotgun_2
            if sprite:
                x_pos = general_vars.WINDOW_WIDTH // 2 - sprite.get_width() // 2
                self.temp_surface.blit(sprite, (x_pos, int(self.held_shotgun_y)))
                # Si estamos en la fase de flash, pintar el destello encima de la boquilla
                if self.player_shotgun_state == "SHOT_FLASH" and self.flash_sprite:
                    fx = general_vars.WINDOW_WIDTH // 2 - self.flash_sprite.get_width() // 2
                    fy = int(self.held_shotgun_y) - 60
                    self.temp_surface.blit(self.flash_sprite, (fx, fy))

        elif self.player_shotgun_state in ["HELD_RAISING_DEALER", 
                                           "DEALER_READY", 
                                           "SHOT_FLASH_DEALER", 
                                           "DEALER_SHOT_FALL", 
                                           "HELD_LOWERING_DEALER_DONE", 
                                           "SHOT_BLANK_CLICK_DEALER", 
                                           "SHOT_BLANK_PUMP_DEALER",
                                           "SHOT_LIVE_PUMP_DEALER", # <--- Agregado el nuevo estado aquí
                                           "ZOOM_IN_DEALER", 
                                           "ZOOM_HOLD_DEALER", 
                                           "ZOOM_OUT_DEALER"]:
            sprite = self.player_shotgun_3
            if sprite:
                x_pos = general_vars.WINDOW_WIDTH // 2 - sprite.get_width() // 100
                self.temp_surface.blit(sprite, (x_pos, int(self.held_shotgun_y)))
                
                # Dibujar el pump 3 encima CON EL OFFSET aplicado
                if self.player_shotgun_pump_3:
                    pump_x = x_pos + self.player_pump_x_offset
                    pump_y = self.held_shotgun_y + self.player_pump_y_offset
                    self.temp_surface.blit(self.player_shotgun_pump_3, (int(pump_x), int(pump_y)))
                
                # Si estamos en la fase de flash, pintar el destello en la boquilla de la escopeta 3
                if self.player_shotgun_state == "SHOT_FLASH_DEALER" and self.flash_sprite:
                    fx = x_pos + 4 - self.flash_sprite.get_width() // 2
                    fy = int(self.held_shotgun_y) + 7 - self.flash_sprite.get_height() // 2
                    self.temp_surface.blit(self.flash_sprite, (fx, fy))

        # Dibujar los desfibriladores
        if self.player_shotgun_state == "DEFIB_ANIM":
            if self.defib_1:
                self.temp_surface.blit(self.defib_1, (int(self.defib_1_x), general_vars.WINDOW_HEIGHT - self.defib_1.get_height()))
            if self.defib_2:
                self.temp_surface.blit(self.defib_2, (int(self.defib_2_x), general_vars.WINDOW_HEIGHT - self.defib_2.get_height()))

        # Dibujar el cartucho expulsado (si está activo)
        if self.ejected_shell_active and self.ejected_shell_sprite:
            rotated_shell = pygame.transform.rotate(self.ejected_shell_sprite, self.ejected_shell_angle)
            shell_rect = rotated_shell.get_rect(center=(int(self.ejected_shell_x), int(self.ejected_shell_y)))
            self.temp_surface.blit(rotated_shell, shell_rect.topleft)

        # Dibujar las opciones (choices1 y choices2 de la categoría ui del .lang)
        if self.show_choices:
            ui_text = self.translations.get("ui", {})
            choice1_text = ui_text.get("choices1", "- TU -")
            choice2_text = ui_text.get("choices2", "- DEALER -")

            # Renderizar choices2 (arriba)
            surf2 = self.font.render(choice2_text, True, (255, 255, 255))
            rect2 = surf2.get_rect(center=(general_vars.WINDOW_WIDTH // 2, 120))
            self.temp_surface.blit(surf2, rect2)

            # Renderizar choices1 (abajo)
            surf1 = self.font.render(choice1_text, True, (255, 255, 255))
            rect1 = surf1.get_rect(center=(general_vars.WINDOW_WIDTH // 2, general_vars.WINDOW_HEIGHT - 80))
            self.temp_surface.blit(surf1, rect1)

        # Aplicar el renderizado con Zoom de cámara en self.screen
        if self.camera_zoom == 1.0:
            self.screen.blit(self.temp_surface, (0, 0))
        else:
            cx = (general_vars.WINDOW_WIDTH // 2 + 200) + 130
            cy = 1 + 20  # Elevado un poco más arriba para centrar mejor el HUD
            w = int(general_vars.WINDOW_WIDTH * self.camera_zoom)
            h = int(general_vars.WINDOW_HEIGHT * self.camera_zoom)
            scaled_surf = pygame.transform.smoothscale(self.temp_surface, (w, h))
            offset_x = cx - cx * self.camera_zoom
            offset_y = cy - cy * self.camera_zoom
            self.screen.blit(scaled_surf, (offset_x, offset_y))

    def draw_inventory_hud(self, surface=None):
        surf = surface if surface is not None else self.screen
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
                surf.blit(self.slot_image, (x_pos, y_pos))
            else:
                # Dibujar un recuadro de respaldo si no carga la imagen
                rect = pygame.Rect(x_pos, y_pos, slot_size, slot_size)
                pygame.draw.rect(surf, (30, 30, 30), rect)
                pygame.draw.rect(surf, (50, 50, 50), rect, 2)
                
            # (Futuro: Si self.inventory[index] tiene un objeto, se dibujará centrado dentro de x_pos y y_pos)

    def draw_life_hud(self, surface=None):
        surf = surface if surface is not None else self.screen
        # Posición horizontal a la derecha del inventario (360px de inventario + 20px de espacio = 380px)
        start_x = general_vars.WINDOW_WIDTH // 2 + 200  # Centrado horizontal 
        start_y = 15 
        
        # 1. Dibujar el contenedor de vida
        if self.life_container:
            surf.blit(self.life_container, (start_x, start_y))
        else:
            # Respaldo visual si no se encuentra life_container.png
            rect = pygame.Rect(start_x, start_y, 260, 160)
            pygame.draw.rect(surf, (30, 30, 30), rect)
            pygame.draw.rect(surf, (50, 50, 50), rect, 2)

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
                surf.blit(player_point, (x_pos, y_player))
            else:
                # Respaldo de color azul
                pygame.draw.rect(surf, self.player_color, pygame.Rect(x_pos, y_player, 15, 25))

        # 4. Dibujar rayos de vida del Dealer (Dealer HP)
        for i in range(self.dealer_hp):
            x_pos = start_x + 25 + (i * 35)
            if self.life_point:
                # Duplicamos y aplicamos el color rojo al rayo del dealer en vivo
                dealer_point = self.life_point.copy()
                dealer_point.fill(self.dealer_color, special_flags=pygame.BLEND_RGBA_MULT)
                surf.blit(dealer_point, (x_pos, y_dealer))
            else:
                # Respaldo de color rojo
                pygame.draw.rect(surf, self.dealer_color, pygame.Rect(x_pos, y_dealer, 15, 25))

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

    def draw_game_round_hud(self, surface=None):
        surf = surface if surface is not None else self.screen
        # 1. Dibujar Cartuchos parados en la mesa (a la derecha de la escopeta)
        if self.game_state == "SHELLS_REVEAL" and self.bullets_on_table > 0:
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
                    surf.blit(temp_sprite, (start_x + (i * spacing_x), start_y))

        # 2. Dibujar Caja de Diálogo (Contenedor negro abajo centrado)
        if self.dialogue_text:
            box_width = 640
            box_height = 80
            box_x = general_vars.WINDOW_WIDTH // 2 - box_width // 2
            box_y = general_vars.WINDOW_HEIGHT - 100
            
            box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
            
            # Dibujar caja con bordes
            pygame.draw.rect(surf, (10, 10, 10), box_rect)
            pygame.draw.rect(surf, (40, 40, 40), box_rect, 2)
            
            # Dibujar el texto centrado adentro de la caja
            text_surf = self.font.render(self.dialogue_text, True, (240, 240, 240))
            text_rect = text_surf.get_rect(center=(box_x + box_width // 2, box_y + box_height // 2))
            surf.blit(text_surf, text_rect.topleft)
