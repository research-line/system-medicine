"""System-Medizin Prototyp - Einstiegspunkt.

Funktionspfad-zentrierter medizinischer Knowledge Graph mit Ausschlusslogik.
"""
import sys
import os
from pathlib import Path

# Sicherstellen dass prototype/ im Python-Pfad ist
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Windows Encoding
os.environ["PYTHONIOENCODING"] = "utf-8"

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from gui.app import MainWindow
from gui.theme import DARK_THEME


def load_app_icon() -> QIcon:
    icon_path = Path(__file__).with_name("system-medicine.ico")
    return QIcon(str(icon_path)) if icon_path.exists() else QIcon()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("System-Medizin")
    icon = load_app_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)
    app.setStyleSheet(DARK_THEME)
    
    window = MainWindow()
    if not icon.isNull():
        window.setWindowIcon(icon)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
