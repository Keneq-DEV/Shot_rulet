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
        
        self.screen = pygame.display.set_mode((general_vars.WINDOW_WIDTH, general_vars.WINDOW_HEIGHT))
        pygame.display.set_caption("Shot Rulet")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.menu_state = "MAIN"      # Estado activo del menú
        self.current_lang = "esp"     # Idioma cargado por defecto
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

        # 2. Cargar Sprite del Título (title.png en Assets/textures)
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

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Detectar clics en los botones del diccionario
            for key, button in self.buttons.items():
                if button.is_clicked(event, mouse_pos):
                    if key == "exit_game":
                        self.running = False
                    elif key == "new_game":
                        print("Iniciando nuevo juego...")
                    else:
                        print(f"Botón pulsado: {key}")

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        
        # Actualizar cartuchos del fondo
        for shell in self.falling_shells:
            shell.update()
            
        # Actualizar estado de los botones (hover)
        for button in self.buttons.values():
            button.update(mouse_pos)

    def draw(self):
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill((15, 15, 15))
        
        for shell in self.falling_shells:
            shell.draw(self.screen)

        if self.title_sprite:
            title_rect = self.title_sprite.get_rect(center=(general_vars.WINDOW_WIDTH // 2, 180))
            self.screen.blit(self.title_sprite, title_rect)

        for button in self.buttons.values():
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