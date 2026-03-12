"""Hauptfenster der System-Medizin GUI."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QLabel,
    QApplication, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from config import DB_PATH, ensure_dirs
from database import get_connection, init_db
from gui.theme import DARK_THEME
from gui.graph_view import GraphExplorer
from gui.exclusion_panel import ExclusionPanel
from gui.data_panel import DiagnoseQueryPanel, DataBrowserPanel


class MainWindow(QMainWindow):
    """Hauptfenster mit 4 Tabs."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System-Medizin - Funktionspfad-zentrierter Knowledge Graph")
        self.setMinimumSize(1200, 800)
        
        # DB initialisieren
        ensure_dirs()
        self.conn = get_connection(DB_PATH)
        init_db(self.conn)
        
        # Pruefen ob Daten vorhanden
        count = self.conn.execute("SELECT COUNT(*) FROM functional_pathways").fetchone()[0]
        if count == 0:
            self._show_setup_wizard()
        
        self._setup_ui()
        self._setup_statusbar()
    
    def _show_setup_wizard(self):
        """Zeigt den Setup-Wizard bei leerer DB."""
        from gui.setup_wizard import SetupWizard
        wizard = SetupWizard(self.conn, self)
        wizard.exec()
    
    def _setup_ui(self):
        """Erstellt die Tab-basierte UI."""
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Tab 1: Graph-Explorer
        self.graph_explorer = GraphExplorer(self.conn)
        self.tabs.addTab(self.graph_explorer, "Graph-Explorer")
        
        # Tab 2: Ausschluss-Analyse
        self.exclusion_panel = ExclusionPanel(self.conn)
        self.exclusion_panel.pathways_changed.connect(self._on_pathways_changed)
        self.tabs.addTab(self.exclusion_panel, "Ausschluss-Analyse")
        
        # Tab 3: Diagnose-Query
        self.diagnose_panel = DiagnoseQueryPanel(self.conn)
        self.tabs.addTab(self.diagnose_panel, "Diagnose-Query")
        
        # Tab 4: Daten-Browser
        self.data_browser = DataBrowserPanel(self.conn)
        self.tabs.addTab(self.data_browser, "Daten-Browser")
        
        # Tab-Wechsel: Daten aktualisieren
        self.tabs.currentChanged.connect(self._on_tab_changed)
    
    def _setup_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status()
    
    def _update_status(self):
        counts = {}
        for table, label in [
            ("functional_pathways", "Pfade"),
            ("genes_proteins", "Gene"),
            ("body_locations", "Orte"),
            ("measurements", "Messwerte"),
            ("diagnoses", "Diagnosen"),
        ]:
            counts[label] = self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        
        parts = [f"{label}: {count}" for label, count in counts.items()]
        self.status_bar.showMessage(" | ".join(parts))
    
    def _on_pathways_changed(self):
        """Reagiert auf Pfad-Status-Aenderungen."""
        self.graph_explorer.refresh()
        self._update_status()
    
    def _on_tab_changed(self, index):
        """Aktualisiert den aktiven Tab."""
        widget = self.tabs.widget(index)
        if hasattr(widget, "refresh"):
            widget.refresh()
        self._update_status()
    
    def closeEvent(self, event):
        if self.conn:
            self.conn.close()
        super().closeEvent(event)
