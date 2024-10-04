import json
import os

CONFIG_FILE = "config.json"

def save_config(window, settings):
    """
    설정을 저장하는 함수
    """
    config = {
        "width": window.winfo_width(),
        "height": window.winfo_height(),
        "x": window.winfo_x(),
        "y": window.winfo_y(),
        "font_family": settings.get("font_family", "Arial"),
        "font_size": settings.get("font_size", 10),
        "theme": settings.get("theme", "light"),
        "button_style": settings.get("button_style", "default")
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def load_config():
    """
    설정을 불러오는 함수
    """
    default_config = {
        "width": 300, "height": 200, "x": 100, "y": 100,
        "font_family": "Arial", "font_size": 10,
        "theme": "light", "button_style": "default"
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return {**default_config, **json.load(f)}
    return default_config