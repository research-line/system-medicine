"""Diagnose-Query und Daten-Browser Panels."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QGroupBox, QLabel, QPushButton, QComboBox, QLineEdit,
    QTableWidget, QTableWidgetItem, QTextEdit,
    QHeaderView, QAbstractItemView, QCheckBox, QSpinBox,
    QDoubleSpinBox, QFormLayout, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from config import NODE_COLORS
from database import get_all_nodes
from engine.query import GraphQuery
from engine.exclusion import ExclusionEngine
from engine.reasoning import explain_diagnosis_query, generate_patient_summary, explain_pattern_detection


class DiagnoseQueryPanel(QWidget):
    """Tab 3: Diagnose-Query - Messwerte eingeben, Verdacht erhalten."""
    
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.query_engine = GraphQuery(conn)
        self.exclusion_engine = ExclusionEngine(conn)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Linke Seite: Eingabe
        left = QWidget()
        left_layout = QVBoxLayout(left)
        
        # Messwert-Eingabe
        grp_meas = QGroupBox("Auffaellige Messwerte")
        meas_layout = QVBoxLayout(grp_meas)
        
        self.measurement_list = QListWidget()
        meas_layout.addWidget(self.measurement_list)
        
        # Messwert hinzufuegen
        add_layout = QHBoxLayout()
        self.meas_combo = QComboBox()
        self._load_measurements()
        add_layout.addWidget(self.meas_combo, 2)
        
        self.meas_value = QDoubleSpinBox()
        self.meas_value.setRange(0, 99999)
        self.meas_value.setDecimals(1)
        add_layout.addWidget(self.meas_value, 1)
        
        self.meas_direction = QComboBox()
        self.meas_direction.addItems(["niedrig", "hoch"])
        add_layout.addWidget(self.meas_direction, 1)
        
        btn_add = QPushButton("+")
        btn_add.clicked.connect(self._add_measurement)
        add_layout.addWidget(btn_add)
        
        btn_remove = QPushButton("-")
        btn_remove.clicked.connect(self._remove_measurement)
        add_layout.addWidget(btn_remove)
        
        meas_layout.addLayout(add_layout)
        left_layout.addWidget(grp_meas)
        
        # Diagnose-Vorauswahl
        grp_diag = QGroupBox("Diagnose-Fokus (optional)")
        diag_layout = QVBoxLayout(grp_diag)
        self.diag_combo = QComboBox()
        self.diag_combo.addItem("-- Keine --")
        self._load_diagnoses()
        diag_layout.addWidget(self.diag_combo)
        left_layout.addWidget(grp_diag)
        
        # Analyse starten
        btn_analyze = QPushButton("Diagnose-Query starten")
        btn_analyze.setObjectName("primary")
        btn_analyze.clicked.connect(self._run_query)
        left_layout.addWidget(btn_analyze)
        
        left_layout.addStretch()
        splitter.addWidget(left)
        
        # Rechte Seite: Ergebnisse
        right = QWidget()
        right_layout = QVBoxLayout(right)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("font-family: 'Consolas', monospace; font-size: 12px;")
        right_layout.addWidget(self.result_text)
        
        splitter.addWidget(right)
        splitter.setSizes([350, 650])
        layout.addWidget(splitter)
    
    def _load_measurements(self):
        rows = self.conn.execute("SELECT name, unit FROM measurements ORDER BY name LIMIT 500").fetchall()
        for r in rows:
            unit = f" [{r['unit']}]" if r["unit"] else ""
            self.meas_combo.addItem(f"{r['name']}{unit}", r["name"])
    
    def _load_diagnoses(self):
        rows = self.conn.execute("SELECT name FROM diagnoses ORDER BY name").fetchall()
        for r in rows:
            self.diag_combo.addItem(r["name"])
    
    def _add_measurement(self):
        name = self.meas_combo.currentData()
        if not name:
            return
        value = self.meas_value.value()
        direction = self.meas_direction.currentText()
        item = QListWidgetItem(f"{name}: {value} ({direction})")
        item.setData(Qt.UserRole, {"name": name, "value": value, "direction": direction})
        self.measurement_list.addItem(item)
    
    def _remove_measurement(self):
        row = self.measurement_list.currentRow()
        if row >= 0:
            self.measurement_list.takeItem(row)
    
    def _run_query(self):
        # Messwerte sammeln
        abnormal = []
        for i in range(self.measurement_list.count()):
            item = self.measurement_list.item(i)
            abnormal.append(item.data(Qt.UserRole))
        
        if not abnormal:
            self.result_text.setPlainText("Bitte mindestens einen auffaelligen Messwert eingeben.")
            return
        
        # Intakte Pfade aus DB holen
        intact = [r["id"] for r in self.conn.execute(
            "SELECT id FROM functional_pathways WHERE status = 'intakt'"
        ).fetchall()]
        
        # Query ausfuehren
        diag_result = self.query_engine.diagnose_from_measurements(abnormal, intact)
        
        # Ausschluss-Analyse
        excl_result = self.exclusion_engine.run_exclusion()
        
        # Ergebnis anzeigen
        text_parts = [explain_diagnosis_query(diag_result)]
        
        # Diagnose-Fokus
        diag_name = self.diag_combo.currentText()
        if diag_name != "-- Keine --":
            pathways = self.query_engine.get_pathways_for_diagnosis(diag_name)
            if pathways:
                text_parts.append(f"\n--- Diagnose-Fokus: {diag_name} ---")
                text_parts.append("Betroffene Pfade:")
                for p in pathways:
                    text_parts.append(f"  - {p['name']} (Status: {p.get('status', '?')})")
        
        text_parts.append("\n" + generate_patient_summary(excl_result, diag_result))
        
        # Pattern-Detection
        patterns = self.query_engine.detect_patterns(abnormal)
        if patterns:
            text_parts.append("\n" + explain_pattern_detection(patterns))
        
        self.result_text.setPlainText("\n".join(text_parts))
    
    def refresh(self):
        self.meas_combo.clear()
        self._load_measurements()
        self.diag_combo.clear()
        self.diag_combo.addItem("-- Keine --")
        self._load_diagnoses()


class DataBrowserPanel(QWidget):
    """Tab 4: Rohdaten-Browser."""
    
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self._current_table = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Tabellen-Auswahl
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Tabelle:"))
        
        self.table_combo = QComboBox()
        self.table_combo.addItems([
            "functional_pathways", "body_locations", "cell_types",
            "genes_proteins", "measurements", "diagnoses",
            "gene_pathways", "pathway_locations", "pathway_cells",
            "measurement_pathways", "pathway_diagnoses", "gene_expressions",
            "data_sources",
            "measurement_signatures", "signature_components"
        ])
        self.table_combo.currentTextChanged.connect(self._load_table)
        toolbar.addWidget(self.table_combo, 2)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filtern...")
        self.search_input.textChanged.connect(self._filter_table)
        toolbar.addWidget(self.search_input, 1)
        
        self.count_label = QLabel("")
        toolbar.addWidget(self.count_label)
        
        layout.addLayout(toolbar)
        
        # Daten-Tabelle
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.data_table.setSortingEnabled(True)
        layout.addWidget(self.data_table)
        
        # Initial laden
        self._load_table(self.table_combo.currentText())
    
    def _load_table(self, table_name):
        """Laedt eine Tabelle in die Ansicht (max 1000 Zeilen, gepuffert)."""
        if table_name == self._current_table:
            return
        self._current_table = table_name
        
        ROW_LIMIT = 1000
        try:
            total = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            rows = self.conn.execute(f"SELECT * FROM {table_name} LIMIT {ROW_LIMIT}").fetchall()
        except Exception:
            return
        
        if not rows:
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            self.count_label.setText("0 Eintraege")
            return
        
        # Rendering pausieren waehrend Befuellung
        self.data_table.setUpdatesEnabled(False)
        self.data_table.setSortingEnabled(False)
        
        columns = rows[0].keys()
        col_list = list(columns)
        self.data_table.setColumnCount(len(col_list))
        self.data_table.setHorizontalHeaderLabels(col_list)
        self.data_table.setRowCount(len(rows))
        
        for row_idx, row in enumerate(rows):
            for col_idx, col in enumerate(col_list):
                value = row[col]
                item = QTableWidgetItem(str(value) if value is not None else "")
                self.data_table.setItem(row_idx, col_idx, item)
        
        # Spaltenbreite: erste Spalte stretch, Rest interaktiv
        header = self.data_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        if len(col_list) > 1:
            header.setSectionResizeMode(0, QHeaderView.Stretch)
        # Nur sichtbare Spalten anhand Header-Text + erste Zeile bemessen
        for col_idx in range(min(len(col_list), 10)):
            self.data_table.resizeColumnToContents(col_idx)
        
        self.data_table.setSortingEnabled(True)
        self.data_table.setUpdatesEnabled(True)
        
        suffix = f" (zeige {ROW_LIMIT})" if total > ROW_LIMIT else ""
        self.count_label.setText(f"{total} Eintraege{suffix}")
    
    def _filter_table(self, text):
        """Filtert die Tabelle nach Suchtext."""
        if not text:
            for row in range(self.data_table.rowCount()):
                self.data_table.setRowHidden(row, False)
            return
        
        text = text.lower()
        for row in range(self.data_table.rowCount()):
            visible = False
            for col in range(self.data_table.columnCount()):
                item = self.data_table.item(row, col)
                if item and text in item.text().lower():
                    visible = True
                    break
            self.data_table.setRowHidden(row, not visible)
    
    def refresh(self):
        self._current_table = None  # Cache invalidieren
        self._load_table(self.table_combo.currentText())
