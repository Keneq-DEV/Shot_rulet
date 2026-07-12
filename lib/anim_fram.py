import pygame
import os
from lib import general_vars

class DealerAnimator:
    def __init__(self):
        # Posición base en la mesa
        self.x = general_vars.WINDOW_WIDTH // 2
        self.y = 180
        
        # --- Variables de Animación Cinética ---
        self.hand_scale = 0.0         # Zoom de las manos (0.0 a 1.0)
        self.head_scale = 0.0         # Zoom de la cabeza/cuerpo (0.0 a 1.0)
        self.hand_y_offset = 110.0    # Offset vertical de las manos (110 es Normal, 135 es Rest)
        
        # Estados secuenciales del Dealer
        # "HANDS_APPROACH" -> "HANDS_DESCEND" -> "REST_WAIT" -> "HEAD_APPROACH" -> "HANDS_ASCEND" -> "FINAL"
        self.state = "HANDS_APPROACH" 
        self.timer = pygame.time.get_ticks()

        # Rutas de carpetas de recursos
        sprites_dir = os.path.join(general_vars.BASE_DIR, "Assets", "textures", "dealer")
        hands_dir = os.path.join(sprites_dir, "hands")
        
        # Cargar recursos originales sin pre-escalar para permitir el zoom de calidad
        self.body_raw = self._load_img(sprites_dir, "Dealer_st_normal.png")
        self.l_hand_rest = self._load_img(hands_dir, "Dealer_st_left_hand_rest.png")
        self.r_hand_rest = self._load_img(hands_dir, "Dealer_st_right_hand_rest.png")
        self.l_hand_norm = self._load_img(hands_dir, "Dealer_st_left_hand_normal.png")
        self.r_hand_norm = self._load_img(hands_dir, "Dealer_st_right_hand_normal.png")

    def _load_img(self, path, name):
        p = os.path.join(path, name)
        return pygame.image.load(p).convert_alpha() if os.path.exists(p) else None

    def update(self):
        curr = pygame.time.get_ticks()
        
        # FASE 1: Las manos normales aparecen lejanas y se acercan (Zoom 0.0 a 1.0)
        if self.state == "HANDS_APPROACH":
            if self.hand_scale < 1.0:
                self.hand_scale += 0.015  # Velocidad de zoom de manos
                if self.hand_scale >= 1.0:
                    self.hand_scale = 1.0
                    self.state = "HANDS_DESCEND"
        
        # FASE 2: Las manos bajan físicamente un poco y cambian al sprite REST
        elif self.state == "HANDS_DESCEND":
            if self.hand_y_offset < 135:
                self.hand_y_offset += 0.8  # Descenso suave
            else:
                self.state = "REST_WAIT"
                self.timer = curr
        
        # FASE 3: Espera un momento con las manos apoyadas abajo en la mesa (1 segundo)
        elif self.state == "REST_WAIT":
            if curr - self.timer >= 1000:
                self.state = "HEAD_APPROACH"
        
        # FASE 4: La cabeza aparece lejana y se acerca con zoom de escala (0.0 a 1.0)
        elif self.state == "HEAD_APPROACH":
            if self.head_scale < 1.0:
                self.head_scale += 0.015  # Velocidad de zoom de cabeza
                if self.head_scale >= 1.0:
                    self.head_scale = 1.0
                    self.state = "HANDS_ASCEND"
        
        # FASE 5: Las manos vuelven a subir físicamente a la mesa y se ponen NORMAL
        elif self.state == "HANDS_ASCEND":
            if self.hand_y_offset > 110:
                self.hand_y_offset -= 0.8  # Ascenso suave
            else:
                self.hand_y_offset = 110
                self.state = "FINAL"

    def draw(self, screen):
        # 1. Dibujar Cabeza/Cuerpo (Solo si la escala es mayor a 0)
        if self.head_scale > 0 and self.body_raw:
            size = int(220 * self.head_scale)
            body_img = pygame.transform.scale(self.body_raw, (size, size))
            body_rect = body_img.get_rect(center=(self.x, self.y))
            screen.blit(body_img, body_rect.topleft)

        # 2. Seleccionar texturas de manos
        # Usamos REST durante el descenso, la espera y el zoom de la cabeza.
        # Usamos NORMAL durante el acercamiento inicial y en la pose final.
        use_rest = self.state in ["HANDS_DESCEND", "REST_WAIT", "HEAD_APPROACH"]
        l_img = self.l_hand_rest if use_rest else self.l_hand_norm
        r_img = self.r_hand_rest if use_rest else self.r_hand_norm

        # 3. Dibujar Manos con escala y offsets dinámicos
        if l_img and r_img:
            # En la Fase 1 la escala depende del zoom de manos, en las demás ya es fija (1.0)
            current_scale = self.hand_scale if self.state == "HANDS_APPROACH" else 1.0
            h_size = int(80 * current_scale)
            
            if h_size > 0:
                l_final = pygame.transform.scale(l_img, (h_size, h_size))
                r_final = pygame.transform.scale(r_img, (h_size, h_size))
                
                # Las posiciones se recalculan respecto al centro multiplicadas por la escala de zoom
                l_rect = l_final.get_rect(center=(self.x - int(130 * current_scale), self.y + int(self.hand_y_offset * current_scale)))
                r_rect = r_final.get_rect(center=(self.x + int(130 * current_scale), self.y + int(self.hand_y_offset * current_scale)))
                
                screen.blit(l_final, l_rect.topleft)
                screen.blit(r_final, r_rect.topleft)