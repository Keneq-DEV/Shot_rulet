import pygame
import os
import random
import threading
from lib import general_vars

_sound_cache = {}
_sound_lock = threading.Lock()
_last_play_time = 0
_active_sfx_channels = set()

def get_cached_sound(path: str, name: str, format: str):
    key = os.path.join(path, f"{name}.{format}")
    
    with _sound_lock:
        if key not in _sound_cache:
            if os.path.exists(key):
                _sound_cache[key] = pygame.mixer.Sound(key)
            else:
                print(f"No se encontró el archivo de sonido en: {key}")
                return None
                
    return _sound_cache[key]

def set_sfx_volume(volume: float | None = None):
    if not pygame.mixer.get_init():
        return

    if volume is None:
        volume = general_vars.VOLUME_SFX

    final_volume = volume * general_vars.VOLUME_GENERAL
    for channel_id in list(_active_sfx_channels):
        pygame.mixer.Channel(channel_id).set_volume(final_volume)


def play_sound(path: str, name: str, format: str, type: int, id: int, volume: float = None):
    """
    Path: la ruta donde esta el sonido
    Name: el nombre del archivo
    Format: el formato sin poner el punto
    Type: que es una vez o en loop -1 loop 1 una vez
    Id: el id del archivo
    Volume: pues ya sabes
    
    
    """
    if not pygame.mixer.get_init():
        pygame.mixer.init()
        
    sound = get_cached_sound(path, name, format)
    
    if sound is not None:
        # Obtener el canal específico para este efecto de sonido
        channel = pygame.mixer.Channel(id)
        _active_sfx_channels.add(id)
        
        # Mapeo de tipos: 1 = Reproducción única (loops=0), -1 = Bucle infinito (loops=-1)
        pygame_loops = 0 if type == 1 else -1
        
        # Cálculo del volumen (Estándar o Personalizado respetando el volumen General Maestro)
        if volume is None:
            final_volume = general_vars.VOLUME_SFX * general_vars.VOLUME_GENERAL
        else:
            final_volume = volume * general_vars.VOLUME_GENERAL
            
        channel.set_volume(final_volume)
        
        # Reproducir el sonido en el canal e ID especificados
        channel.play(sound, loops=pygame_loops)

def play_random_sound(path: str, name: list, format: str, interval: float, id: int, volume: float = None):
    global _last_play_time
    current_time = pygame.time.get_ticks()
    interval_ms = interval * 1000
    
    if current_time - _last_play_time >= interval_ms:
        _last_play_time = current_time
        if name:
            random_name = random.choice(name)
            # Pasar el volumen opcional de forma directa a play_sound
            play_sound(path, random_name, format, type=1, id=id, volume=volume)

def stop_sound(id: int):
    if pygame.mixer.get_init():
        # Detiene únicamente el sonido del canal de efectos especificado (id)
        pygame.mixer.Channel(id).stop()
    _active_sfx_channels.discard(id)