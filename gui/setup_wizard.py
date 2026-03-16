"""Setup-Wizard fuer Erststart: Datenquellen herunterladen und importieren."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QProgressBar, QTextEdit, QHBoxLayout
)
from PySide6.QtCore import Qt, QThread, Signal


class DownloadWorker(QThread):
    """Worker-Thread fuer Download + Import."""
    progress = Signal(str)  # Log-Nachricht
    step_progress = Signal(int, int)  # current, total
    finished = Signal(bool, str)  # success, message
    
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
    
    def run(self):
        try:
            from ingestion.manager import IngestionManager
            from database import get_connection, init_db
            
            # Eigene Connection im Worker-Thread oeffnen
            conn = get_connection(self.db_path)
            
            init_db(conn)
            
            manager = IngestionManager()
            sources = list(manager._importers.keys())
            total = len(sources)
            
            # Download
            self.progress.emit("Starte Downloads...")
            for i, name in enumerate(sources):
                self.step_progress.emit(i, total * 2)
                self.progress.emit(f"Lade {name}...")
                try:
                    if not manager.manifest.is_downloaded(name):
                        manager.download_source(name)
                        self.progress.emit(f"  {name} heruntergeladen.")
                    else:
                        self.progress.emit(f"  {name} bereits vorhanden.")
                except Exception as e:
                    self.progress.emit(f"  FEHLER bei {name}: {e}")
            
            # Import
            self.progress.emit("\nStarte Import...")
            for i, name in enumerate(sources):
                self.step_progress.emit(total + i, total * 2)
                self.progress.emit(f"Importiere {name}...")
                try:
                    count = manager.import_source(name, conn)
                    self.progress.emit(f"  {name}: {count} Eintraege importiert.")
                except Exception as e:
                    self.progress.emit(f"  FEHLER bei {name}: {e}")
            
            self.step_progress.emit(total * 2, total * 2)
            conn.close()
            self.finished.emit(True, "Alle Datenquellen erfolgreich geladen!")
            
        except Exception as e:
            self.finished.emit(False, f"Fehler: {e}")


class SetupWizard(QDialog):
    """Dialog fuer Erststart-Konfiguration."""
    
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self._worker = None
        self.setWindowTitle("System-Medizin - Ersteinrichtung")
        self.setMinimumSize(500, 400)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Willkommen bei System-Medizin")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel(
            "Die Datenbank ist leer. Waehlen Sie eine Option zur Initialisierung:"
        )
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Option 1: Seed-Daten
        self.btn_seed = QPushButton("Demo-Daten laden (Haemolyse-Szenario)")
        self.btn_seed.setObjectName("primary")
        self.btn_seed.setMinimumHeight(40)
        self.btn_seed.clicked.connect(self._load_seed)
        layout.addWidget(self.btn_seed)
        
        # Option 2: Vollstaendiger Download
        self.btn_download = QPushButton("Vollstaendige Datenquellen herunterladen (~200 MB)")
        self.btn_download.setMinimumHeight(40)
        self.btn_download.clicked.connect(self._start_download)
        layout.addWidget(self.btn_download)
        
        layout.addSpacing(10)
        
        # Fortschritt
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(200)
        self.log.setVisible(False)
        layout.addWidget(self.log)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_close = QPushButton("Schliessen")
        self.btn_close.clicked.connect(self.accept)
        self.btn_close.setEnabled(False)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)
    
    def _disable_buttons(self):
        self.btn_seed.setEnabled(False)
        self.btn_download.setEnabled(False)
        self.progress.setVisible(True)
        self.log.setVisible(True)
    
    def _load_seed(self):
        """Laedt die Seed-Daten."""
        self._disable_buttons()
        self.progress.setRange(0, 0)
        
        self.log.append("Initialisiere Datenbank...")
        from database import init_db
        init_db(self.conn)
        
        self.log.append("Lade Haemolyse-Szenario...")
        from ingestion.seed_data import seed_haemolyse, seed_clinical_panels
        seed_haemolyse(self.conn)

        self.log.append("Lade klinische Laborpanels (65+ Messwerte)...")
        seed_clinical_panels(self.conn)

        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.log.append("Fertig! Demo-Daten + klinische Panels geladen.")
        self.btn_close.setEnabled(True)
    
    def _start_download(self):
        """Startet den vollstaendigen Download in einem Worker-Thread."""
        self._disable_buttons()
        self.progress.setRange(0, 100)
        
        from config import DB_PATH
        self._worker = DownloadWorker(DB_PATH)
        self._worker.progress.connect(self._on_log)
        self._worker.step_progress.connect(self._on_step)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()
    
    def _on_log(self, msg):
        self.log.append(msg)
    
    def _on_step(self, current, total):
        if total > 0:
            self.progress.setValue(int(current / total * 100))
    
    def _on_finished(self, success, message):
        self.log.append(f"\n{'Erfolg' if success else 'Fehler'}: {message}")
        self.progress.setValue(100 if success else 0)
        self.btn_close.setEnabled(True)
        self._worker = None
        # Hauptfenster-Connection muss DB-Aenderungen sehen
        if success and self.conn:
            try:
                self.conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
            except Exception:
                self.conn.execute("SELECT 1")
