import sys
import os
from lib import ui_windows as uiw


def main():
    # Instanciamos el manejador de la ventana y lo arrancamos
    game_app = uiw.WindowManager()
    game_app.run()

if __name__ == "__main__":
    main()