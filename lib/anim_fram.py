import pygame
import os
import re
from lib import general_vars
from lib import sound_manager as sm

class DealerAnimator:
    def __init__(self):
        # Posición fija en la mesa
        self.x = general_vars.WINDOW_WIDTH // 2
        self.y = 270

        # COORDENADAS DESTINO DE AGARRE (Tus valores exactos, completamente intactos)
        self.target_l_x = self.x - 20
        self.target_l_y = 610          
        self.target_r_x = self.x + 66
        self.target_r_y = 490         
        
        # --- Variables de Animación Cinética ---
        self.hand_scale = 0.0         # Zoom de las manos (0.0 a 1.0)
        self.head_scale = 0.0         # Zoom de la cabeza/cuerpo (0.0 a 1.0)
        self.hand_y_offset = 110.0    # Offset vertical de las manos (110 es Normal, 135 es Rest)
        
        # Posiciones dinámicas de las manos en pantalla (para el deslizamiento)
        self.hand_l_x = self.x - 130
        self.hand_l_y = self.y + 110
        self.hand_r_x = self.x + 130
        self.hand_r_y = self.y + 110

        # --- Variables Unificadas para jalar la Escopeta (Fase 7) ---
        self.shotgun_y = 580.0        # Inicia donde dibujas la escopeta en tu mesa (Y = 580)
        self.shotgun_scale = 1.0      # Escala (1.0 = mesa, 0.6 = alejado cerca del dealer)
        self.shotgun_angle = 0.0      # Inclinación (0.0 = diagonal original, 45.0 = horizontal)
        
        # --- Variables de Inserción y Bombeo ---
        self.bullets_to_insert = 0    # Sincronizado dinámicamente desde game.py
        self.l_hand_angle = 0.0       # Ángulo para rotar la mano izquierda holding_3 arriba y abajo
        self.sound_triggered = False  # Bandera de seguridad para que el sonido suene una sola vez por ciclo
        self.insert_cycle_duration = 750 # Duración del ciclo de inserción en ms
        

        # Estados secuenciales del Dealer
        # "HANDS_APPROACH" -> "HANDS_DESCEND" -> "REST_WAIT" -> "HEAD_APPROACH" -> "HANDS_ASCEND" -> "FINAL" -> "GRAB_GUN" -> "HOLDING_GUN" -> "PULL_GUN" -> "HOLDING_PULLED"
        self.state = "HANDS_APPROACH" 
        self.timer = pygame.time.get_ticks()
        self.state_timer = 0

        # Rutas de carpetas de recursos
        sprites_dir = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "dealer")
        hands_dir = os.path.join(sprites_dir, "hands")
        holding_dir = os.path.join(hands_dir, "holding")
        
        # 1. Cargar cuerpo original
        self.body_raw = self._load_img(sprites_dir, "Dealer_st_normal.png")
        
        # 2. Cargar manos rest y normal
        self.l_hand_rest = self._load_img(hands_dir, "Dealer_st_left_hand_rest.png")
        self.r_hand_rest = self._load_img(hands_dir, "Dealer_st_right_hand_rest.png")
        self.l_hand_norm = self._load_img(hands_dir, "Dealer_st_left_hand_normal.png")
        self.r_hand_norm = self._load_img(hands_dir, "Dealer_st_right_hand_normal.png")

        # 3. Cargar manos de sujeción (holding_1 y la variante holding_3 para la mano izquierda)
        self.l_hand_holding = None
        l_hold_path = os.path.join(holding_dir, "Dealer_st_left_hand_holding_1.png")
        if os.path.exists(l_hold_path):
            img = pygame.image.load(l_hold_path).convert_alpha()
            self.l_hand_holding = pygame.transform.scale(img, (100, 100)) # Tamaño óptimo para sujetar

        self.l_hand_holding_3 = None
        l_hold_3_path = os.path.join(holding_dir, "Dealer_st_left_hand_holding_3.png")
        if os.path.exists(l_hold_3_path):
            img = pygame.image.load(l_hold_3_path).convert_alpha()
            self.l_hand_holding_3 = pygame.transform.scale(img, (100, 100))

        self.r_hand_holding = None
        r_hold_path = os.path.join(holding_dir, "Dealer_st_right_hand_holding_1.png")
        if os.path.exists(r_hold_path):
            img = pygame.image.load(r_hold_path).convert_alpha()
            self.r_hand_holding = pygame.transform.scale(img, (100, 100))

        self.r_hand_holding_3 = None
        r_hold_3_path = os.path.join(holding_dir, "Dealer_st_right_hand_holding_3.png")
        if os.path.exists(r_hold_3_path):
            img = pygame.image.load(r_hold_3_path).convert_alpha()
            self.r_hand_holding_3 = pygame.transform.scale(img, (100, 100))

        # --- UNIFICACIÓN ABSOLUTA: Una sola variable de progreso controla todo el jale ---
        self.pull_progress = 0.0
        self.shotgun_y = 580.0        # Inicia donde dibujas la escopeta en tu mesa (Y = 580)
        self.shotgun_scale = 1.0      # Escala (1.0 = mesa, 0.65 = alejado)
        self.shotgun_angle = 0.0      # Inclinación (0.0 = diagonal, -48.0 = horizontal)

        # Cargar la escopeta de forma local en el animador para soldarla con las manos
        shot_path = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "shotgun", "shotgun_table.png")
        self.shotgun_raw = pygame.image.load(shot_path).convert_alpha() if os.path.exists(shot_path) else None

        # 4. Cargar la escopeta de forma local para moverla en un solo bloque con las manos
        shot_path = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "shotgun", "shotgun_table.png")
        self.shotgun_raw = pygame.image.load(shot_path).convert_alpha() if os.path.exists(shot_path) else None

    def _load_img(self, path, name):
        p = os.path.join(path, name)
        return pygame.image.load(p).convert_alpha() if os.path.exists(p) else None
    
    def update(self):
        curr = pygame.time.get_ticks()
        
        # FASE 1: Las manos normales se acercan
        if self.state == "HANDS_APPROACH":
            if self.hand_scale < 1.0:
                self.hand_scale += 0.015
                if self.hand_scale >= 1.0:
                    self.hand_scale = 1.0
                    self.state = "HANDS_DESCEND"
                    
        
        # FASE 2: Las manos bajan a la posición REST
        elif self.state == "HANDS_DESCEND":
            if self.hand_y_offset < 135:
                self.hand_y_offset += 0.8
            else:
                self.state = "REST_WAIT"
                if not self.sound_triggered:
                    sm.play_sound("Assets/sounds/dealer", "dealer_hands_on_table", "ogg", 1, 2, 3.0)
                    self.sound_triggered = True
                self.timer = curr
        
        # FASE 3: Espera con las manos apoyadas abajo en la mesa
        elif self.state == "REST_WAIT":
            if curr - self.timer >= 1000:
                self.state = "HEAD_APPROACH"
        
        # FASE 4: La cabeza se acerca con zoom
        elif self.state == "HEAD_APPROACH":
            if self.head_scale < 1.0:
                self.head_scale += 0.015
                if self.head_scale >= 1.0:
                    self.head_scale = 1.0
                    self.state = "HANDS_ASCEND"
        
        # FASE 5: Las manos suben y se ponen NORMAL
        elif self.state == "HANDS_ASCEND":
            if self.hand_y_offset > 110:
                self.hand_y_offset -= 0.8
            else:
                self.hand_y_offset = 110
                self.state = "FINAL"

        # Sincronizar posiciones X e Y en las fases iniciales de reposo
        if self.state in ["HANDS_APPROACH",
                          "HANDS_DESCEND", 
                          "REST_WAIT", 
                          "HEAD_APPROACH", 
                          "HANDS_ASCEND", 
                          "FINAL"]:
            self.hand_l_x = self.x - int(130 * (self.hand_scale if self.state == "HANDS_APPROACH" else 1.0))
            self.hand_l_y = self.y + int(self.hand_y_offset * (self.hand_scale if self.state == "HANDS_APPROACH" else 1.0))
            self.hand_r_x = self.x + int(130 * (self.hand_scale if self.state == "HANDS_APPROACH" else 1.0))
            self.hand_r_y = self.y + int(self.hand_y_offset * (self.hand_scale if self.state == "HANDS_APPROACH" else 1.0))

        # === FASE 6: DESLIZAR MANOS HACIA LA ESCOPETA (DIAGONAL) ===
        elif self.state == "GRAB_GUN":
            # Interpolación lineal usando las variables globales de la clase (self.target...)
            self.hand_l_x += (self.target_l_x - self.hand_l_x) * 0.08
            self.hand_l_y += (self.target_l_y - self.hand_l_y) * 0.08
            self.hand_r_x += (self.target_r_x - self.hand_r_x) * 0.08
            self.hand_r_y += (self.target_r_y - self.hand_r_y) * 0.08
           
            
            # Al llegar lo suficientemente cerca, cambiamos de pose a HOLDING (sujetar)
            if abs(self.hand_l_x - self.target_l_x) < 2 and abs(self.hand_l_y - self.target_l_y) < 2:
                
                self.hand_l_x, self.hand_l_y = self.target_l_x, self.target_l_y
                self.hand_r_x, self.hand_r_y = self.target_r_x, self.target_r_y
                self.state = "HOLDING_GUN"
                
                self.state_timer = curr

        # === FASE 7: MOVER MANO IZQUIERDA A LA RECÁMARA (Y CAMBIAR DE SPRITE) ===
        elif self.state == "INSERT_PREP":
            # Coordenadas destino de la recámara (un poco a la izquierda del centro de la escopeta)
            target_l_x = self.x - int(15 * self.shotgun_scale)
            target_l_y = self.shotgun_y + int(10 * self.shotgun_scale)
            
            # Deslizar mano izquierda suavemente hacia la recámara
            self.hand_l_x += (target_l_x - self.hand_l_x) * 0.08
            self.hand_l_y += (target_l_y - self.hand_l_y) * 0.08
            
            # Si llega a la recámara, fijamos la posición y pasamos a insertar
            if abs(self.hand_l_x - target_l_x) < 2:
                self.hand_l_x = target_l_x
                self.hand_l_y = target_l_y
                self.state = "INSERTING"
                self.state_timer = curr
                self.sound_triggered = False
                
                # Regla: Muchos cartuchos carga rápido (ej. 350ms), pocos carga lento (ej. 700ms)
                if self.bullets_to_insert >= 5:
                    self.insert_cycle_duration = 350   # Muy rápido
                elif self.bullets_to_insert == 4:
                    self.insert_cycle_duration = 400   # Rápido
                elif self.bullets_to_insert == 3:
                    self.insert_cycle_duration = 450   # Moderado
                else: # 2 o menos
                    self.insert_cycle_duration = 500   # Lento

        # === FASE 9: INSERTAR BALAS UNA A UNA (Mano izquierda holding_3 rota arriba y abajo con sonido) ===
        elif self.state == "INSERTING":
            target_l_x = self.x - int(15 * self.shotgun_scale)
            target_l_y = self.shotgun_y + int(10 * self.shotgun_scale)
            self.hand_l_x += (target_l_x - self.hand_l_x) * 0.1
            self.hand_l_y += (target_l_y - self.hand_l_y) * 0.1

            cycle_duration = self.insert_cycle_duration
            elapsed = curr - self.state_timer

            if self.bullets_to_insert > 0:
                progress = elapsed / cycle_duration
                
                if progress < 0.5:
                    self.l_hand_angle = 25.0 * (progress / 0.5)
                    if progress >= 0.45 and not self.sound_triggered:
                        sm.play_sound("Assets/sounds", "load_single shell", "ogg", type=1, id=1)
                        self.sound_triggered = True
                else:
                    self.l_hand_angle = 25.0 - 25.0 * ((progress - 0.5) / 0.5)
                
                if elapsed >= cycle_duration:
                    self.bullets_to_insert -= 1
                    self.sound_triggered = False
                    self.state_timer = curr
            else:
                self.l_hand_angle = 0.0
                self.state = "PUMP_PREP"
                self.state_timer = curr
                self.sound_triggered = False

        # === FASE 7: JALAR LA ESCOPETA (UNIFICACIÓN MATEMÁTICA CON PROGRESO ÚNICO) ===
        elif self.state == "PULL_GUN":
            if self.pull_progress < 1.0:
                self.pull_progress += 0.03  # Velocidad del tirón
                if self.pull_progress > 1.0:
                    self.pull_progress = 1.0
            else:
                self.state = "HOLDING_PULLED"

            # 1. Interpolar la posición Y, Escala y Ángulo de la escopeta basados en el progreso
            self.shotgun_y = 580.0 + (380.0 - 580.0) * self.pull_progress
            self.shotgun_scale = 1.0 + (0.65 - 1.0) * self.pull_progress
            
            # ROTACIÓN DE APLANADO: Rotamos hacia la derecha (valores negativos) para aplanar la diagonal
            self.shotgun_angle = 0.0 + (-48.0 - 0.0) * self.pull_progress

            # 2. Interpolar los offsets de las manos (desde tus posiciones diagonales hasta la alineación horizontal)
            # Mano Izquierda: de diagonal (target_l_x, target_l_y) a horizontal plana (-45 respecto al centro de la escopeta, altura neutra)
            off_l_x = -20.0 + (-45.0 - (-20.0)) * self.pull_progress
            off_l_y = (610.0 - 580.0) + (10.0 - (610.0 - 580.0)) * self.pull_progress
            
            # Mano Derecha: de diagonal (target_r_x, target_r_y) a horizontal plana (+45 respecto al centro de la escopeta, altura neutra)
            off_r_x = 66.0 + (100.0 - 66.0) * self.pull_progress
            off_r_y = (490.0 - 580.0) + (-19.0 - (490.0 - 580.0)) * self.pull_progress

            # 3. Aplicar las coordenadas unificadas (Soldadas a la escopeta y escaladas proporcionalmente)
            self.hand_l_x = self.x + (off_l_x * self.shotgun_scale)
            self.hand_l_y = self.shotgun_y + (off_l_y * self.shotgun_scale)
            self.hand_r_x = self.x + (off_r_x * self.shotgun_scale)
            self.hand_r_y = self.shotgun_y + (off_r_y * self.shotgun_scale)

        # === FASE 10: BOMBEAR LA ESCOPETA (MANO DERECHA CAMBIA DE SPRITE Y HACE EL MOVIMIENTO) ===
        elif self.state == "PUMP_PREP":
            # Mantener la mano izquierda en su lugar
            off_l_x = -45.0
            off_l_y = 10.0
            self.hand_l_x = self.x + (off_l_x * self.shotgun_scale)
            self.hand_l_y = self.shotgun_y + (off_l_y * self.shotgun_scale)

            # Mover mano derecha hacia adelante/atrás para simular el pump
            elapsed = curr - self.state_timer
            duration = 250  # 0.25 segundos para tirar hacia atrás
            progress = min(1.0, elapsed / duration)

            # Interpolar offset de mano derecha para el tirón
            off_r_x = 100.0 - 30.0 * progress
            off_r_y = -19.0 + 8.0 * progress

            self.hand_r_x = self.x + (off_r_x * self.shotgun_scale)
            self.hand_r_y = self.shotgun_y + (off_r_y * self.shotgun_scale)

            if not self.sound_triggered:
                # Reproducir sonido de recarga de escopeta
                sm.play_sound("Assets/sounds", "rack_shotgun", "ogg", type=1, id=2)
                self.sound_triggered = True

            if elapsed >= duration:
                self.state = "PUMP_ACTION"
                self.state_timer = curr

        elif self.state == "PUMP_ACTION":
            # Mantener la mano izquierda en su lugar
            off_l_x = -45.0
            off_l_y = 10.0
            self.hand_l_x = self.x + (off_l_x * self.shotgun_scale)
            self.hand_l_y = self.shotgun_y + (off_l_y * self.shotgun_scale)

            # Retornar mano derecha a su posición original
            elapsed = curr - self.state_timer
            duration = 200  # 0.2 segundos para regresar
            progress = min(1.0, elapsed / duration)

            off_r_x = 70.0 + 30.0 * progress
            off_r_y = -11.0 - 8.0 * progress

            self.hand_r_x = self.x + (off_r_x * self.shotgun_scale)
            self.hand_r_y = self.shotgun_y + (off_r_y * self.shotgun_scale)

            if elapsed >= duration:
                self.state = "PUSH_GUN"

        # === FASE 11: DEPOSITAR LA ESCOPETA EN LA MESA (JALE AL REVÉS) ===
        elif self.state == "PUSH_GUN":
            if self.pull_progress > 0.0:
                self.pull_progress -= 0.03  # Velocidad de regreso
                if self.pull_progress < 0.0:
                    self.pull_progress = 0.0
            else:
                self.state = "UNGRAB_GUN"

            # 1. Interpolar la posición Y, Escala y Ángulo de la escopeta de regreso
            self.shotgun_y = 580.0 + (380.0 - 580.0) * self.pull_progress
            self.shotgun_scale = 1.0 + (0.65 - 1.0) * self.pull_progress
            self.shotgun_angle = 0.0 + (-48.0 - 0.0) * self.pull_progress

            # 2. Interpolar los offsets de las manos de regreso
            off_l_x = -20.0 + (-45.0 - (-20.0)) * self.pull_progress
            off_l_y = (610.0 - 580.0) + (10.0 - (610.0 - 580.0)) * self.pull_progress
            off_r_x = 66.0 + (100.0 - 66.0) * self.pull_progress
            off_r_y = (490.0 - 580.0) + (-19.0 - (490.0 - 580.0)) * self.pull_progress

            # 3. Aplicar las coordenadas unificadas
            self.hand_l_x = self.x + (off_l_x * self.shotgun_scale)
            self.hand_l_y = self.shotgun_y + (off_l_y * self.shotgun_scale)
            self.hand_r_x = self.x + (off_r_x * self.shotgun_scale)
            self.hand_r_y = self.shotgun_y + (off_r_y * self.shotgun_scale)

        # === FASE 12: SOLTAR LA ESCOPETA Y RETIRAR LAS MANOS ===
        elif self.state == "UNGRAB_GUN":
            target_l_x = self.x - 130
            target_l_y = self.y + 110
            target_r_x = self.x + 130
            target_r_y = self.y + 110

            # Deslizar manos suavemente a sus posiciones de descanso
            self.hand_l_x += (target_l_x - self.hand_l_x) * 0.08
            self.hand_l_y += (target_l_y - self.hand_l_y) * 0.08
            self.hand_r_x += (target_r_x - self.hand_r_x) * 0.08
            self.hand_r_y += (target_r_y - self.hand_r_y) * 0.08

            if abs(self.hand_l_x - target_l_x) < 2:
                self.hand_l_x, self.hand_l_y = target_l_x, target_l_y
                self.hand_r_x, self.hand_r_y = target_r_x, target_r_y
                self.state = "FINAL"

    def draw(self, screen):
        # 1. Dibujar Cabeza/Cuerpo
        if self.head_scale > 0 and self.body_raw:
            size = int(220 * self.head_scale)
            body_img = pygame.transform.scale(self.body_raw, (size, size))
            body_rect = body_img.get_rect(center=(self.x, self.y))
            screen.blit(body_img, body_rect.topleft)
        
        # 2. Dibujar Escopeta (Unificada: Solo cuando el dealer la toma físicamente)
        if self.state in ["HOLDING_GUN", 
                          "PULL_GUN", 
                          "HOLDING_PULLED", 
                          "INSERT_PREP", 
                          "INSERT_READY", 
                          "INSERTING", 
                          "PUMP_PREP", 
                          "PUMP_ACTION", 
                          "PUSH_GUN"] and self.shotgun_raw:
            s_width = int(200 * self.shotgun_scale)
            s_height = int(320 * self.shotgun_scale)
            shot_scaled = pygame.transform.scale(self.shotgun_raw, (s_width, s_height))
            
            # Rotar la escopeta hacia la derecha (valores negativos) para aplanar la diagonal
            if self.shotgun_angle != 0:
                shot_scaled = pygame.transform.rotate(shot_scaled, self.shotgun_angle)
                
            shot_rect = shot_scaled.get_rect(center=(self.x, int(self.shotgun_y)))
            screen.blit(shot_scaled, shot_rect.topleft)

        # 3. Seleccionar e imprimir las texturas de manos
        if self.state in ["INSERT_PREP", 
                          "INSERT_READY", 
                          "INSERTING"]:
            # Cambiar mano izquierda a holding_3 cuando se mueva a la recámara
            l_img, r_img = self.l_hand_holding_3, self.r_hand_holding
        elif self.state in ["PUMP_PREP", 
                            "PUMP_ACTION"]:
            # Usar holding_3 para la mano derecha al bombear
            l_img, r_img = self.l_hand_holding, self.r_hand_holding_3
        elif self.state in ["HOLDING_GUN", 
                            "PULL_GUN", 
                            "HOLDING_PULLED", 
                            "PUSH_GUN"]:
            l_img, r_img = self.l_hand_holding, self.r_hand_holding
        else:
            use_rest = self.state in ["HANDS_DESCEND", 
                                      "REST_WAIT", 
                                      "HEAD_APPROACH", 
                                      "GRAB_GUN", 
                                      "UNGRAB_GUN"]
            l_img = self.l_hand_rest if use_rest else self.l_hand_norm
            r_img = self.r_hand_rest if use_rest else self.r_hand_norm

        # 4. Dibujar Manos en sus coordenadas dinámicas
        if l_img and r_img:
            # Seleccionar escala según la fase activa (zoom inicial, zoom de jale o normal)
            if self.state in ["PULL_GUN", 
                              "HOLDING_PULLED", 
                              "INSERT_PREP", 
                              "INSERT_READY", 
                              "INSERTING", 
                              "PUMP_PREP", 
                              "PUMP_ACTION", 
                              "PUSH_GUN", 
                              "PLAY"]:
                current_scale = self.shotgun_scale
            else:
                current_scale = self.hand_scale if self.state == "HANDS_APPROACH" else 1.0
                
            h_size = int(80 * current_scale)
            
            if h_size > 0:
                l_final = pygame.transform.scale(l_img, (h_size, h_size))
                r_final = pygame.transform.scale(r_img, (h_size, h_size))
                
                if self.state == "INSERTING" and self.l_hand_angle != 0:
                    l_final = pygame.transform.rotate(l_final, self.l_hand_angle)
                
                l_rect = l_final.get_rect(center=(int(self.hand_l_x), int(self.hand_l_y)))
                r_rect = r_final.get_rect(center=(int(self.hand_r_x), int(self.hand_r_y)))
                
                screen.blit(l_final, l_rect.topleft)
                screen.blit(r_final, r_rect.topleft)
                