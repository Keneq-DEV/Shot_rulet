import os
import pygame
from lib import general_vars
from lib import sound_manager as sm
from lib import music_manager as mm

class GameLoader:
    def __init__(self):
        self.current_step = 0
        self.tasks = [
            ("Cargando base de datos de juego...", self._load_game_db),
            ("Pre-cargando texturas del tablero de juego...", self._load_board_textures),
            ("Pre-cargando sonidos (disparo, recarga)...", self._preload_sfx_cache),
            ("Inicializando Algoritmos de IA...", self._init_dealer_ai_logic),
            ("Generando cartuchos de escopeta...", self._prepare_bullets_data)
        ]

    def is_complete(self):
        # Retorna verdadero si ya se completaron todas las tareas
        return self.current_step >= len(self.tasks)

    def get_current_task_name(self):
        if self.is_complete():
            return "Completado"
        return self.tasks[self.current_step][0]

    def update_step(self):
        # Ejecuta la tarea actual y avanza el paso
        if not self.is_complete():
            task_name, task_func = self.tasks[self.current_step]
            task_func()
            self.current_step += 1

    def _load_game_db(self):
        pass

    def _load_board_textures(self):
        pass

    def _preload_sfx_cache(self):
        # Pre-carga real de efectos de sonido en la caché de disco
        pass

    def _init_dealer_ai_logic(self):
        pass

    def _prepare_bullets_data(self):
        pass