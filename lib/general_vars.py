import os
from lib import general_func as fnc

# Ruta absoluta a la raíz del proyecto (evita fallos de directorio según desde dónde se ejecute)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "Assets", "data")

# Ruta al archivo settings.cfg
CONFIG_PATH = os.path.join("Assets", "data", "settings.cfg")

# Cargar el diccionario de configuración
config = fnc.load_config(CONFIG_PATH)

# Dimensiones de la ventana
WINDOW_WIDTH = int(config.get("window_with", 1280))
WINDOW_HEIGHT = int(config.get("window_height", 720))

# Volúmenes
VOLUME_MUSIC = float(config.get("Volume_music", 1.0))
VOLUME_SFX = float(config.get("Volume_sfx", 1.0))
VOLUME_GENERAL = float(config.get("Volume_general", 1.0))

# Colores comunes (RGB)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)