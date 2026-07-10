import pygame
import os
import random
from lib import general_vars
from lib import music_manager as mm

from lib import ui_elements as uie
from lib import general_func as fnc

class FallingShell:
    def __init__(self, images):
        self.images = images
        self.reset(start_random_y=True)

    def reset(self, start_random_y=False):
        self.image = random.choice(self.images)
        self.x = random.randint(0, general_vars.WINDOW_WIDTH)
        self.y = random.randint(-general_vars.WINDOW_HEIGHT, -20) if not start_random_y else random.randint(-100, general_vars.WINDOW_HEIGHT)
        self.speed_y = random.uniform(1.5, 4.0)
        self.angle = random.randint(0, 360)
        self.rot_speed = random.uniform(-1.5, 1.5)

    def update(self):
        self.y += self.speed_y
        self.angle += self.rot_speed
        if self.y > general_vars.WINDOW_HEIGHT + 50:
            self.reset()

    def draw(self, surface):
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        rect = rotated_image.get_rect(center=(self.x, self.y))
        surface.blit(rotated_image, rect.topleft)


class WindowManager:
    def __init__(self):
        
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((general_vars.WINDOW_WIDTH, general_vars.WINDOW_HEIGHT), pygame.SCALED)
        pygame.display.set_caption("Shot Rulet")
        self.clock = pygame.time.Clock()
        self.running = True
        self.menu_state = "MAIN"      # Estado activo del menú
        # Escanear automáticamente todos los archivos .lang disponibles en la carpeta
        self.available_langs = [f for f in os.listdir(general_vars.DATA_DIR) if f.endswith(".lang")]
        
        # Cargar esp.lang por defecto
        self.current_lang = "esp.lang" if "esp.lang" in self.available_langs else self.available_langs[0]
        
        lang_path = os.path.join(general_vars.DATA_DIR, self.current_lang)
        self.translations = fnc.load_language(lang_path)
        menu_text = self.translations.get("main-menu", {})

       
    
        self.is_fullscreen = False    # Estado de pantalla completa

        # DEFINIR ATRIBUTOS AL INICIO PARA EVITAR ATTRIBUTE-ERROR
        self.buttons = {}
        self.falling_shells = []
        self.shell_images = []
        self.title_sprite = None

        bg_path = os.path.join("Assets", "textures", "sprites", "background_menu.png")
        self.background_image = None
        if os.path.exists(bg_path):
            self.background_image = pygame.image.load(bg_path).convert()
            self.background_image = pygame.transform.scale(
                self.background_image, 
                (general_vars.WINDOW_WIDTH, general_vars.WINDOW_HEIGHT)
            )

        # 1. Cargar y reproducir música de fondo desde el music_manager
        mm.play_menu_music()

        # 2. Cargar Sprite del Título 
        title_path = os.path.join("Assets", "textures", "sprites", "Title.png")
        self.title_sprite = None
        if os.path.exists(title_path):
            
            self.title_sprite = pygame.image.load(title_path).convert_alpha()

        # 3. Cargar Sprites de los Cartuchos para la animación del fondo
        shells_dir = os.path.join("Assets", "textures", "sprites", "Shells")
        shell_filenames = ["Shell_empty.png", "Shell_explosive.png", "Shell_live.png", "Shell_unknown.png"]
        self.shell_images = []

        for name in shell_filenames:
            path = os.path.join(shells_dir, name)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (100, 100))
                self.shell_images.append(img)

        # 4. Crear lista de cartuchos cayendo
        self.falling_shells = []
        if self.shell_images:
            for _ in range(15):
                self.falling_shells.append(FallingShell(self.shell_images))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()

    def update_button_texts(self):
        menu_text = self.translations.get("main-menu", {})
        
        # 1. Actualizar textos del menú principal
        for key, btn in self.buttons.items():
            btn.text = menu_text.get(key, key)
            
        # 2. Actualizar etiquetas de los Sliders
        self.settings_sliders["volume_m"].label = menu_text.get("volume_m", "Musica")
        self.settings_sliders["volume_s"].label = menu_text.get("volume_s", "Sonido")
            
        # 3. Actualizar etiquetas de las cajas de texto
        # self.settings_inputs["with_win"].label = menu_text.get("with_win", "Ancho")
        # self.settings_inputs["height_win"].label = menu_text.get("height_win", "Alto")
            
        # 4. Actualizar textos de los botones restantes de configuración
        self.settings_buttons["save_rate"].text = f"{menu_text.get('save_rate', 'Guardado')}: {general_vars.config.get('MaxAutoSaves', '20')} slots"
        
        fs_state = "ON" if self.is_fullscreen else "OFF"
        self.settings_buttons["fullsc_win"].text = f"{menu_text.get('fullsc_win', 'Pantalla Completa')}: {fs_state}"

        lang_display = self.current_lang.split(".")[0].upper()
        self.settings_buttons["change_lang"].text = f"{menu_text.get('change_lang', 'Idioma')}: {lang_display}"
        self.settings_buttons["back_game"].text = menu_text.get("back_game", "Atras")

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # --- Eventos de Menú Principal ---
            if self.menu_state == "MAIN":
                for key, button in self.buttons.items():
                    if button.is_clicked(event, mouse_pos):
                        if key == "exit_game":
                            self.running = False
                        elif key == "settings_game":
                            self.menu_state = "SETTINGS"
                            self.update_button_texts()
            
            # --- Eventos de Configuración (Settings) ---
            elif self.menu_state == "SETTINGS":
                # Control centralizado y estable de foco para las cajas de texto
                # if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                #     for input_box in self.settings_inputs.values():
                #         # Si haces clic dentro, se activa; si no, se apaga
                #         if input_box.rect.collidepoint(mouse_pos):
                #             input_box.is_active = True
                #             input_box.current_color = input_box.color_active
                #         else:
                #             input_box.is_active = False
                #             input_box.current_color = input_box.color_inactive
                
                # Pasar los eventos de teclado únicamente a las cajas activas
                # for input_box in self.settings_inputs.values():
                #     input_box.handle_event(event)
                
                # Clics del resto de botones en settings
                for key, button in self.settings_buttons.items():
                    if button.is_clicked(event, mouse_pos):
                        
                        if key == "back_game":
                            # w_text = self.settings_inputs["with_win"].text
                            # h_text = self.settings_inputs["height_win"].text
                            
                            # w = int(w_text) if w_text else 1280
                            # h = int(h_text) if h_text else 720
                            
                            # w = max(640, min(w, 2560))
                            # h = max(480, min(h, 1440))
                            
                            # general_vars.WINDOW_WIDTH, general_vars.WINDOW_HEIGHT = w, h
                            # general_vars.config["window_with"] = str(w)
                            # general_vars.config["window_height"] = str(h)
                            
                            # self.screen = pygame.display.set_mode((w, h), pygame.SCALED)
                            # if self.background_image:
                            #     self.background_image = pygame.transform.scale(self.background_image, (w, h))
                            
                            # fnc.save_config(general_vars.CONFIG_PATH, general_vars.config)
                            # self.menu_state = "MAIN"
                             # Guardar cambios finales en el .cfg al salir
                            fnc.save_config(general_vars.CONFIG_PATH, general_vars.config)
                            self.menu_state = "MAIN"
                            
                        elif key == "save_rate":
                            rate = int(general_vars.config.get("MaxAutoSaves", "20"))
                            rate = rate + 5 if rate < 20 else 5
                            general_vars.config["MaxAutoSaves"] = str(rate)
                                
                        elif key == "fullsc_win":
                            self.is_fullscreen = not self.is_fullscreen
                            if self.is_fullscreen:
                                self.screen = pygame.display.set_mode((general_vars.WINDOW_WIDTH, general_vars.WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
                            else:
                                self.screen = pygame.display.set_mode((general_vars.WINDOW_WIDTH, general_vars.WINDOW_HEIGHT), pygame.SCALED)
                                
                        elif key == "change_lang":
                            if self.available_langs:
                                idx = self.available_langs.index(self.current_lang)
                                self.current_lang = self.available_langs[(idx + 1) % len(self.available_langs)]
                                
                                # Cargar la ruta absoluta del nuevo idioma
                                lang_path = os.path.join(general_vars.DATA_DIR, self.current_lang)
                                self.translations = fnc.load_language(lang_path)
                                
                                self.update_button_texts()

                        self.update_button_texts()

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        for shell in self.falling_shells:
            shell.update()
            
        if self.menu_state == "MAIN":
            for button in self.buttons.values():
                button.update(mouse_pos)
                
        elif self.menu_state == "SETTINGS":
            # Actualizar arrastre de los Sliders de volumen
            for key, slider in self.settings_sliders.items():
                slider.update(mouse_pos, mouse_pressed)
                
                # Guardar el valor flotante en el config del general_vars en vivo
                val_str = str(round(slider.current_val, 2))
                if key == "volume_m":
                    general_vars.config["Volume_music"] = val_str
                    general_vars.VOLUME_MUSIC = slider.current_val
                    # Ajustar volumen de la música reproduciéndose al instante
                    pygame.mixer.music.set_volume(slider.current_val * general_vars.VOLUME_GENERAL)
                elif key == "volume_s":
                    general_vars.config["Volume_sfx"] = val_str
                    general_vars.VOLUME_SFX = slider.current_val
            
            # Actualizar hover del resto de botones normales en configuración
            for button in self.settings_buttons.values():
                button.update(mouse_pos)

    def draw(self):
        # Dibujar imagen de fondo
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill((15, 15, 15))
        
        # Dibujar cartuchos del fondo
        for shell in self.falling_shells:
            shell.draw(self.screen)

        # Dibujar logo del título
        if self.title_sprite:
            title_rect = self.title_sprite.get_rect(center=(general_vars.WINDOW_WIDTH // 2, 180))
            self.screen.blit(self.title_sprite, title_rect)

        # Dibujar botones e interfaces según la pantalla activa
        if self.menu_state == "MAIN":
            for button in self.buttons.values():
                button.draw(self.screen)
        elif self.menu_state == "SETTINGS":
            # Dibujar los Sliders de volumen
            for slider in self.settings_sliders.values():
                slider.draw(self.screen)
                
            # Dibujar las cajas de entrada de texto
            # for input_box in self.settings_inputs.values():
            #     input_box.draw(self.screen)
                
            # Dibujar botones de opciones restantes
            for button in self.settings_buttons.values():
                button.draw(self.screen)

        pygame.display.flip()

        # Cargar Idioma y crear Botones de Menú
        lang_path = os.path.join("Assets", "data", "esp.lang") 
        self.translations = fnc.load_language(lang_path)
        menu_text = self.translations.get("main-menu", {})

        # Crear fuente para los botones (tamaño 40)
        self.font = pygame.font.Font(None, 40)

        # Claves de los botones en tu .lang
        self.button_keys = ["new_game", "load_game", "settings_game", "int_game", "exit_game"]
        self.buttons = {}

        # Posicionamiento vertical de los botones
        start_y = 360
        spacing_y = 55
        
        for i, key in enumerate(self.button_keys):
            text = menu_text.get(key, key)
            btn = uie.Button(
                x=general_vars.WINDOW_WIDTH // 2, 
                y=start_y + (i * spacing_y), 
                text=text, 
                font=self.font
            )
            self.buttons[key] = btn

            # Inicializar los botones de configuración vacíos en el arranque
        # Crear los Sliders de Volumen y el resto de Botones de Opciones
        # Crear los Sliders, InputBoxes y Botones de Opciones
        self.settings_sliders = {}
        self.settings_inputs = {}
        self.settings_buttons = {}

        # Crear los dos Sliders de volumen
        vol_m_init = float(general_vars.config.get("Volume_music", "1.0"))
        vol_s_init = float(general_vars.config.get("Volume_sfx", "1.0"))
        
        self.settings_sliders["volume_m"] = uie.Slider(
            x=general_vars.WINDOW_WIDTH // 2 - 100,
            y=230,
            width=200,
            label=menu_text.get("volume_m", "Musica"),
            font=self.font,
            current_val=vol_m_init
        )
        self.settings_sliders["volume_s"] = uie.Slider(
            x=general_vars.WINDOW_WIDTH // 2 - 100,
            y=290,
            width=200,
            label=menu_text.get("volume_s", "Sonido"),
            font=self.font,
            current_val=vol_s_init
        )

        # # Crear las cajas de entrada de texto (InputBoxes) para Ancho y Alto
        # self.settings_inputs["with_win"] = uie.InputBox(
        #     x=general_vars.WINDOW_WIDTH // 2 - 100,
        #     y=350,
        #     width=200,
        #     height=35,
        #     label=menu_text.get("with_win", "Ancho"),
        #     font=self.font,
        #     initial_text=str(general_vars.WINDOW_WIDTH)
        # )
        # self.settings_inputs["height_win"] = uie.InputBox(
        #     x=general_vars.WINDOW_WIDTH // 2 - 100,
        #     y=410,
        #     width=200,
        #     height=35,
        #     label=menu_text.get("height_win", "Alto"),
        #     font=self.font,
        #     initial_text=str(general_vars.WINDOW_HEIGHT)
        # )

        # Crear los botones restantes de configuración (sin resoluciones, solo comportamiento)
        settings_keys = ["save_rate", "fullsc_win", "change_lang", "back_game"]
        start_y_settings = 470
        spacing_y_settings = 45
        for i, key in enumerate(settings_keys):
            text = menu_text.get(key, key)
            self.settings_buttons[key] = uie.Button(
                general_vars.WINDOW_WIDTH // 2, 
                start_y_settings + (i * spacing_y_settings), 
                text, 
                self.font
            )

        # Forzar que aparezcan los números y traducciones correctas al iniciar
        self.update_button_texts()