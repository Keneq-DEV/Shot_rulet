import pygame
import os
import threading
import time
from lib import general_vars

_music_cache = {}
_music_lock = threading.Lock()
_active_music_channels = set()

def get_cached_music(path: str, name: str, format: str):
    key = os.path.join(path, f"{name}.{format}")
    
    # Bloqueo seguro para operaciones con hilos en la caché de música
    with _music_lock:
        if key not in _music_cache:
            if os.path.exists(key):
                # Cargamos la música como un objeto Sound de Pygame
                _music_cache[key] = pygame.mixer.Sound(key)
            else:
                print(f"No se encontró el archivo de música en: {key}")
                return None
                
    return _music_cache[key]

def set_music_volume(volume: float | None = None):
    if not pygame.mixer.get_init():
        return

    if volume is None:
        volume = general_vars.VOLUME_MUSIC

    final_volume = volume * general_vars.VOLUME_GENERAL
    for channel_id in list(_active_music_channels):
        pygame.mixer.Channel(channel_id).set_volume(final_volume)


def play_music(path: str, name: str, format: str, id: int):
    if not pygame.mixer.get_init():
        pygame.mixer.init()
        
    sound = get_cached_music(path, name, format)
    
    if sound is not None:
        # Obtener el canal de reproducción específico (ID)
        channel = pygame.mixer.Channel(id)
        _active_music_channels.add(id)
        
        # Conexión de volúmenes: Volumen Música * Volumen General
        final_volume = general_vars.VOLUME_MUSIC * general_vars.VOLUME_GENERAL
        channel.set_volume(final_volume)
        
        # Reproducir la música en bucle infinito en ese canal
        channel.play(sound, loops=-1)

def play_music_transition(current_music: str, path_new_m: str, name_new_m: str, format: str, interval: float, id: int):
    if not pygame.mixer.get_init():
        pygame.mixer.init()
        
    # EVITAR CORTES: Si la música nueva es la misma que ya está sonando, cancelamos la transición
    if current_music == name_new_m:
        return
        
    fade_out_ms = int((interval / 2) * 1000)
    fade_in_ms = int((interval / 2) * 1000)

    def transition_worker():
        channel = pygame.mixer.Channel(id)
        
        # 1. Desvanecer de forma segura el canal de esta música específica
        channel.fadeout(fade_out_ms)
        time.sleep(interval / 2)
        
        # 2. Cargar y reproducir la nueva pista con fade-in
        sound = get_cached_music(path_new_m, name_new_m, format)
        if sound is not None:
            final_volume = general_vars.VOLUME_MUSIC * general_vars.VOLUME_GENERAL
            channel.set_volume(final_volume)
            channel.play(sound, loops=-1, fade_ms=fade_in_ms)

    # Hilo secundario para que la transición ocurra en segundo plano
    thread = threading.Thread(target=transition_worker, daemon=True)
    thread.start()

def stop_music(id: int, fade: float = None):
    if pygame.mixer.get_init():
        # Detiene únicamente la música del canal especificado
        pygame.mixer.Channel(id).stop()
    _active_music_channels.discard(id)