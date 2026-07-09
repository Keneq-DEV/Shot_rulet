import os
import xml.etree.ElementTree as ET

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
    
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        for category in root.findall('CATEGORY'):
            cat_name = category.get('Name')
            translations[cat_name] = {}
            for entry in category.findall('Entry'):
                entry_name = entry.get('Name')
                translations[cat_name][entry_name] = entry.text
    except ET.ParseError as e:
        print(f"Error XML en el archivo de idioma {filepath}: {e}")
        
    return translations

