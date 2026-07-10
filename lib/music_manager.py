import pygame
import os
from lib import general_vars

def play_menu_music():
    if not pygame.mixer.get_init():
        pygame.mixer.init()
        
    music_path = os.path.join("Assets", "music", "main_menu.ogg")
    
    if os.path.exists(music_path):
        pygame.mixer.music.load(music_path)
        
        # Conexión de volúmenes: Volumen Música * Volumen General
        final_volume = general_vars.VOLUME_MUSIC * general_vars.VOLUME_GENERAL
        pygame.mixer.music.set_volume(final_volume)
        
        pygame.mixer.music.play(-1) # Bucle infinito
    else:
        print(f"No se encontró el archivo de música en: {music_path}")

def stop_music():
    pygame.mixer.music.stop()