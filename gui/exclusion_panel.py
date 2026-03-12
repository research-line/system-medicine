"""Ausschluss-Analyse Panel.

Ermoeglicht:
- Pfad-Status setzen (intakt/gestoert/unbekannt)
- Ausschlusslogik ausfuehren (binaer oder probabilistisch)
- Ergebnisse anzeigen mit farblicher Hervorhebung
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QGroupBox, QLabel, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QTextEdit,
    QHeaderView, QAbstractItemView, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from config import STATUS_COLORS
from database import set_pathway_status
from engine.exclusion import ExclusionEngine, ProbabilisticExclusionEngine
from engine.reasoning import explain_exclusion, explain_probabilistic_exclusion


class ExclusionPanel(QWidget):
    """Tab 2: Ausschluss-Analyse."""
    
    pathways_changed = Signal()  # Emitted wenn Status geaendert wird
    
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.engine = ExclusionEngine(conn)
        self.probabilistic_engine = ProbabilisticExclusionEngine(conn)
        self._pathways_loaded = False
        self._setup_ui()
        self._load_pathways()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Linke Seite: Pfad-Status
        left = QWidget()
        left_layout = QVBoxLayout(left)
        
        grp_status = QGroupBox("Funktionspfade - Status")
        grp_layout = QVBoxLayout(grp_status)
        
        self.pathway_table = QTableWidget()
        self.pathway_table.setColumnCount(2)
        self.pathway_table.setHorizontalHeaderLabels(["Pfad", "Status"])
        self.pathway_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.pathway_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.pathway_table.setAlternatingRowColors(True)
        self.pathway_table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        self.pathway_table.setToolTip("Doppelklick auf Status: unbekannt -> intakt -> gestoert -> ...")
        grp_layout.addWidget(self.pathway_table)
        
        left_layout.addWidget(grp_status)
        
        btn_layout = QHBoxLayout()
        btn_run = QPushButton("Ausschluss-Analyse starten")
        btn_run.setObjectName("primary")
        btn_run.clicked.connect(self._run_exclusion)
        btn_layout.addWidget(btn_run)
        
        self.chk_probabilistic = QCheckBox("Probabilistisch")
        self.chk_probabilistic.setToolTip(
            "Probabilistische Analyse mit Konfidenzwerten statt binaerer Ausschlusslogik"
        )
        btn_layout.addWidget(self.chk_probabilistic)
        
        btn_reset = QPushButton("Alle zuruecksetzen")
        btn_reset.clicked.connect(self._reset_all)
        btn_layout.addWidget(btn_reset)
        left_layout.addLayout(btn_layout)
        
        splitter.addWidget(left)
        
        # Rechte Seite: Ergebnisse
        right = QWidget()
        right_layout = QVBoxLayout(right)
        
        grp_results = QGroupBox("Analyse-Ergebnisse")
        results_layout = QVBoxLayout(grp_results)
        
        # Statistik
        self.stats_label = QLabel("Noch keine Analyse durchgefuehrt.")
        self.stats_label.setObjectName("subtitle")
        results_layout.addWidget(self.stats_label)
        
        # Ergebnis-Tabelle
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["Gen", "Entscheidung", "Begruendung", "Konfidenz"])
        self.result_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        results_layout.addWidget(self.result_table)
        
        # Text-Erklaerung
        self.explanation_text = QTextEdit()
        self.explanation_text.setReadOnly(True)
        self.explanation_text.setMaximumHeight(200)
        self.explanation_text.setStyleSheet("font-family: 'Consolas', monospace;")
        results_layout.addWidget(self.explanation_text)
        
        right_layout.addWidget(grp_results)
        splitter.addWidget(right)
        
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
    
    def _load_pathways(self, force=False):
        """Laedt Pfade in die Tabelle (nicht-unbekannte zuerst, max 500)."""
        if self._pathways_loaded and not force:
            return
        self._pathways_loaded = True
        
        ROW_LIMIT = 500
        # Nicht-unbekannte Pfade zuerst, dann Rest
        rows = self.conn.execute("""
            SELECT id, name, status FROM functional_pathways
            ORDER BY CASE status
                WHEN 'gestoert' THEN 0
                WHEN 'intakt' THEN 1
                ELSE 2
            END, name
            LIMIT ?
        """, (ROW_LIMIT,)).fetchall()
        
        total = self.conn.execute("SELECT COUNT(*) FROM functional_pathways").fetchone()[0]
        pathways = [(r["id"], r["name"], r["status"]) for r in rows]
        
        self.pathway_table.setUpdatesEnabled(False)
        self.pathway_table.setRowCount(len(pathways))
        
        for row, (pid, name, status) in enumerate(pathways):
            name_item = QTableWidgetItem(name)
            name_item.setData(Qt.UserRole, pid)
            self.pathway_table.setItem(row, 0, name_item)
            
            status_item = QTableWidgetItem(status.upper())
            color = QColor(STATUS_COLORS.get(status, "#9E9E9E"))
            status_item.setForeground(color)
            self.pathway_table.setItem(row, 1, status_item)
        
        if total > ROW_LIMIT:
            self.pathway_table.setRowCount(len(pathways) + 1)
            info = QTableWidgetItem(f"... {total - ROW_LIMIT} weitere")
            info.setForeground(QColor("#6c7086"))
            self.pathway_table.setItem(len(pathways), 0, info)
        
        self.pathway_table.setUpdatesEnabled(True)
    
    def _on_cell_double_clicked(self, row, col):
        """Doppelklick wechselt Status: unbekannt -> intakt -> gestoert -> ..."""
        name_item = self.pathway_table.item(row, 0)
        if not name_item:
            return
        pid = name_item.data(Qt.UserRole)
        if pid is None:
            return
        
        cycle = ["unbekannt", "intakt", "gestoert"]
        status_item = self.pathway_table.item(row, 1)
        current = status_item.text().lower() if status_item else "unbekannt"
        idx = cycle.index(current) if current in cycle else 0
        new_status = cycle[(idx + 1) % len(cycle)]
        
        set_pathway_status(self.conn, pid, new_status)
        status_item.setText(new_status.upper())
        status_item.setForeground(QColor(STATUS_COLORS.get(new_status, "#9E9E9E")))
        self.pathways_changed.emit()
    
    def _run_exclusion(self):
        """Fuehrt die Ausschluss-Analyse durch (binaer oder probabilistisch)."""
        if self.chk_probabilistic.isChecked():
            self._run_probabilistic_exclusion()
        else:
            self._run_binary_exclusion()
    
    def _run_binary_exclusion(self):
        """Binaere Ausschluss-Analyse (Original-Logik)."""
        result = self.engine.run_exclusion()
        
        # Statistik
        n_excl = len(result["excluded_genes"])
        n_cand = len(result["candidate_genes"])
        total = result["total_genes_analyzed"]
        self.stats_label.setText(
            f"Analysiert: {total} Gene | Ausgeschlossen: {n_excl} | Kandidaten: {n_cand} | "
            f"Intakte Pfade: {result['intact_pathways']} | Gestoerte: {result['disturbed_pathways']}"
        )
        
        # Ergebnis-Tabelle: 4 Spalten
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["Gen", "Entscheidung", "Begruendung", "Konfidenz"])
        self.result_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        reasoning = result["reasoning"]
        self.result_table.setRowCount(len(reasoning))
        
        for row, r in enumerate(reasoning):
            gene_item = QTableWidgetItem(r["gene"])
            self.result_table.setItem(row, 0, gene_item)
            
            decision_item = QTableWidgetItem(r["decision"].upper())
            if r["decision"] == "ausgeschlossen":
                decision_item.setForeground(QColor("#a6e3a1"))  # Gruen
            else:
                decision_item.setForeground(QColor("#fab387"))  # Orange
            self.result_table.setItem(row, 1, decision_item)
            
            reason_item = QTableWidgetItem(r["reason"])
            self.result_table.setItem(row, 2, reason_item)
            
            conf_item = QTableWidgetItem(r.get("confidence", ""))
            self.result_table.setItem(row, 3, conf_item)
        
        # Text-Erklaerung
        self.explanation_text.setPlainText(explain_exclusion(result))
    
    def _run_probabilistic_exclusion(self):
        """Probabilistische Ausschluss-Analyse mit Konfidenzwerten."""
        result = self.probabilistic_engine.run_probabilistic_exclusion()
        
        # Statistik
        s = result["summary"]
        self.stats_label.setText(
            f"Analysiert: {s['total_analyzed']} Gene | "
            f"Hohe Ausschluss-Konfidenz: {s['high_exclusion_count']} | "
            f"Moderat: {s['moderate_count']} | "
            f"Verdaechtig: {s['suspect_count']}"
        )
        
        # Ergebnis-Tabelle: 5 Spalten
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels([
            "Gen", "Ausschluss-Konfidenz", "Verdachts-Score", "Redundanz", "Pfade"
        ])
        self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        gene_scores = result["gene_scores"]
        self.result_table.setRowCount(len(gene_scores))
        
        for row, g in enumerate(gene_scores):
            # Zeilenfarbe nach Konfidenz
            if g["exclusion_confidence"] >= 0.8:
                row_color = QColor("#a6e3a1")   # Gruen
            elif g["exclusion_confidence"] >= 0.3:
                row_color = QColor("#f9e2af")   # Gelb
            else:
                row_color = QColor("#f38ba8")   # Rot
            
            # Gen-Symbol
            gene_item = QTableWidgetItem(g["symbol"])
            gene_item.setForeground(row_color)
            self.result_table.setItem(row, 0, gene_item)
            
            # Ausschluss-Konfidenz
            conf_item = QTableWidgetItem(f"{g['exclusion_confidence']*100:.0f}%")
            conf_item.setForeground(row_color)
            self.result_table.setItem(row, 1, conf_item)
            
            # Verdachts-Score
            susp_item = QTableWidgetItem(f"{g['suspicion_score']*100:.0f}%")
            susp_item.setForeground(row_color)
            self.result_table.setItem(row, 2, susp_item)
            
            # Redundanz
            red_item = QTableWidgetItem(g["redundancy"])
            red_item.setForeground(row_color)
            self.result_table.setItem(row, 3, red_item)
            
            # Pfade
            pathway_str = f"{g['n_intact']}/{g['n_pathways']} intakt"
            path_item = QTableWidgetItem(pathway_str)
            path_item.setForeground(row_color)
            self.result_table.setItem(row, 4, path_item)
        
        # Text-Erklaerung
        self.explanation_text.setPlainText(explain_probabilistic_exclusion(result))
    
    def _reset_all(self):
        """Setzt alle Pfade auf 'unbekannt'."""
        self.conn.execute("UPDATE functional_pathways SET status = 'unbekannt'")
        self.conn.commit()
        self._load_pathways(force=True)
        self.pathways_changed.emit()
    
    def refresh(self):
        self._load_pathways(force=True)
