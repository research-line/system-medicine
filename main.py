"""System-Medizin Prototyp - Einstiegspunkt.

Funktionspfad-zentrierter medizinischer Knowledge Graph mit Ausschlusslogik.
"""
import sys
import os

# Sicherstellen dass prototype/ im Python-Pfad ist
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Windows Encoding
os.environ["PYTHONIOENCODING"] = "utf-8"

from PySide6.QtWidgets import QApplication
from gui.app import MainWindow
from gui.theme import DARK_THEME


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("System-Medizin")
    app.setStyleSheet(DARK_THEME)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
