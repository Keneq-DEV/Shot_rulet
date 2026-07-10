import os
import xml.etree.ElementTree as ET
import re

def load_config(filepath):
    config_data = {}
    if not os.path.exists(filepath):
        # Valores por defecto en caso de que no exista el archivo
        return {
            "window_with": "1280",
            "window_height": "720",
            "Volume_music": "1.0",
            "Volume_sfx": "1.0",
            "Volume_general": "1.0"
        }
    
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().replace('"', '').replace("'", "")
                config_data[key] = value
    return config_data

################################

def load_language(filepath):
    translations = {}
    if not os.path.exists(filepath):
        return translations
        
    current_category = None
    
    # Expresiones regulares ultra-robustas (ignoran mayúsculas, espacios y tipos de comillas)
    cat_re = re.compile(r'<CATEGORY\s+name\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
    entry_re = re.compile(r'<Entry\s+name\s*=\s*["\']([^"\']+)["\']\s*>(.*?)</Entry>', re.IGNORECASE)
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            line = line.strip()
            
            # Buscar coincidencia de categoría
            cat_match = cat_re.search(line)
            if cat_match:
                current_category = cat_match.group(1)
                translations[current_category] = {}
                continue
                
            # Buscar coincidencia de entrada de texto
            entry_match = entry_re.search(line)
            if entry_match and current_category is not None:
                entry_name = entry_match.group(1)
                entry_value = entry_match.group(2)
                translations[current_category][entry_name] = entry_value
                
    return translations

def save_config(filepath, config):
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write("<config\n")
        file.write(f'    Player_name = "{config.get("Player_name", "player01")}"\n')
        file.write(f'    Volume_music = "{config.get("Volume_music", "1.0")}"\n')
        file.write(f'    Volume_sfx = "{config.get("Volume_sfx", "1.0")}"\n')
        file.write(f'    Volume_general = "{config.get("Volume_general", "1.0")}"\n')
        file.write(f'    window_with = "{config.get("window_with", "1280")}"\n')
        file.write(f'    window_height = "{config.get("window_height", "720")}"\n')
        file.write("/>\n\n")
        
        file.write("<keys\n")
        file.write(f'    use = "{config.get("use", "U")}"\n')
        file.write(f'    quick_save = "{config.get("quick_save", ",")}"\n')
        file.write(f'    quick_load = "{config.get("quick_load", ".")}"\n')
        file.write(f'    Move_slot_right = "{config.get("Move_slot_right", "RightArrow")}"\n')
        file.write(f'    Move_slot_left = "{config.get("Move_slot_left", "LeftArrow")}"\n')
        file.write(f'    Escape_exit = "{config.get("Escape_exit", "Escape")}"\n')
        file.write("/>\n\n")
        
        file.write("<Saving\n")
        file.write(f'    MaxAutoSaves = "{config.get("MaxAutoSaves", "20")}"\n')
        file.write(f'    SaveRoute = "{config.get("SaveRoute", "data/savegame/")}"\n')
        file.write("/>\n")