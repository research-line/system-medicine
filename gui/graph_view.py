"""Interaktive Graph-Visualisierung mit QGraphicsScene.

Knoten werden nach Typ farbkodiert, Kanten zeigen Relationen.
Unterstuetzt Zoom, Pan, Drag und Knoten-Selektion.
Lazy-Loading: Nur Nachbarschaft wird geladen, nicht der komplette Graph.
"""
import sys
import os
import math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QGraphicsScene, QGraphicsView, QGraphicsEllipseItem,
    QGraphicsTextItem, QGraphicsLineItem, QGraphicsItem,
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QComboBox, QLabel, QCheckBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal, QPointF, QRectF, QThread, QObject
from PySide6.QtGui import (
    QColor, QBrush, QPen, QFont, QPainter, QWheelEvent
)

from config import NODE_COLORS, STATUS_COLORS, DB_PATH


class GraphWorker(QObject):
    """Worker fuer Graph-Berechnungen im Hintergrund-Thread."""
    finished = Signal(object)  # networkx Graph
    
    def __init__(self, task, args):
        super().__init__()
        self.task = task
        self.args = args
    
    def run(self):
        import networkx as nx
        from database import get_connection
        conn = get_connection(DB_PATH)
        try:
            if self.task == "overview":
                G = self._build_overview(conn, **self.args)
            elif self.task == "neighborhood":
                G = self._build_neighborhood(conn, **self.args)
            else:
                G = nx.Graph()
        finally:
            conn.close()
        self.finished.emit(G)
    
    def _build_overview(self, conn, max_nodes=200):
        """Baut Uebersichtsgraph. Bei kleinen Datensaetzen (<100 Knoten)
        werden ALLE Knotentypen angezeigt, sonst nur Pathways."""
        import networkx as nx
        from database import get_all_nodes, get_all_edges

        # Gesamtanzahl pruefen
        total = 0
        for table in ("functional_pathways", "body_locations", "cell_types",
                       "genes_proteins", "measurements", "diagnoses"):
            total += conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

        if total <= 100:
            return self._build_full_graph(conn, max_nodes)

        # Bei grossen Datensaetzen: nur Pathways (bisheriges Verhalten)
        G = nx.Graph()
        pathways = conn.execute(
            "SELECT * FROM functional_pathways LIMIT ?", (max_nodes,)
        ).fetchall()

        pid_set = set()
        for p in pathways:
            p = dict(p)
            node_id = f"pathway_{p['id']}"
            G.add_node(node_id, label=p["name"], node_type="pathway", **p)
            pid_set.add(p["id"])

        if pid_set:
            placeholders = ",".join("?" * len(pid_set))
            edges = conn.execute(f"""
                SELECT DISTINCT gp1.pathway_id as p1, gp2.pathway_id as p2
                FROM gene_pathways gp1
                JOIN gene_pathways gp2 ON gp1.gene_id = gp2.gene_id
                WHERE gp1.pathway_id < gp2.pathway_id
                  AND gp1.pathway_id IN ({placeholders})
                  AND gp2.pathway_id IN ({placeholders})
                LIMIT 500
            """, list(pid_set) + list(pid_set)).fetchall()

            for e in edges:
                src = f"pathway_{e['p1']}"
                tgt = f"pathway_{e['p2']}"
                if G.has_node(src) and G.has_node(tgt):
                    G.add_edge(src, tgt, relation="gemeinsame Gene")

        # Layout im Worker berechnen
        if len(G.nodes) > 0:
            pos = nx.spring_layout(G, k=3.0, iterations=50, scale=400)
            for nid in G.nodes:
                G.nodes[nid]["_pos"] = pos.get(nid, (0, 0))

        return G

    def _build_full_graph(self, conn, max_nodes=200):
        """Baut vollstaendigen Graphen mit ALLEN Knotentypen und Kanten."""
        import networkx as nx
        from database import get_all_nodes, get_all_edges

        G = nx.Graph()

        nodes = get_all_nodes(conn)
        node_count = 0
        for node_type, node_list in nodes.items():
            for node in node_list:
                if node_count >= max_nodes:
                    break
                node_id = f"{node_type}_{node['id']}"
                label = node.get("name") or node.get("symbol") or node.get("organ", "?")
                G.add_node(node_id, label=label, node_type=node_type, **node)
                node_count += 1

        edges = get_all_edges(conn)
        for edge in edges:
            src = f"{edge['source_type']}_{edge['source_id']}"
            tgt = f"{edge['target_type']}_{edge['target_id']}"
            if G.has_node(src) and G.has_node(tgt):
                G.add_edge(src, tgt,
                           relation=edge.get("relation", ""),
                           is_essential=edge.get("is_essential"))

        if len(G.nodes) > 0:
            pos = nx.spring_layout(G, k=2.5, iterations=80, scale=500)
            for nid in G.nodes:
                G.nodes[nid]["_pos"] = pos.get(nid, (0, 0))

        return G
    
    def _build_neighborhood(self, conn, center_type, center_id, depth=1, max_nodes=200):
        import networkx as nx
        from engine.query import GraphQuery
        
        query_engine = GraphQuery(conn)
        G = nx.Graph()
        
        visited = set()
        queue = [(center_type, center_id, 0)]
        node_count = 0
        
        table_map = {
            "pathway": "functional_pathways", "location": "body_locations",
            "cell": "cell_types", "gene": "genes_proteins",
            "measurement": "measurements", "diagnosis": "diagnoses",
        }
        
        # Zentralen Knoten laden
        table = table_map.get(center_type)
        if table:
            row = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (center_id,)).fetchone()
            center_data = dict(row) if row else {}
        else:
            center_data = {}
        
        center_node_id = f"{center_type}_{center_id}"
        label = center_data.get("name") or center_data.get("symbol") or center_data.get("organ", "?")
        G.add_node(center_node_id, label=label, node_type=center_type, is_center=True, **center_data)
        visited.add(center_node_id)
        node_count += 1
        
        type_map = {
            "locations": "location", "cells": "cell", "genes": "gene",
            "measurements": "measurement", "diagnoses": "diagnosis",
            "pathways": "pathway", "expressions": "location",
            "gene_expressions": "gene",
        }
        
        while queue and node_count < max_nodes:
            ntype, nid, current_depth = queue.pop(0)
            if current_depth >= depth:
                continue
            
            neighbors = query_engine.get_neighbors(ntype, nid)
            
            for neighbor_type_key, neighbor_list in neighbors.items():
                neighbor_node_type = type_map.get(neighbor_type_key, neighbor_type_key)
                
                for neighbor in neighbor_list:
                    neighbor_node_id = f"{neighbor_node_type}_{neighbor['id']}"
                    
                    if neighbor_node_id in visited:
                        source_id = f"{ntype}_{nid}"
                        if G.has_node(source_id) and G.has_node(neighbor_node_id):
                            relation = neighbor.get("relation", "")
                            is_ess = bool(neighbor.get("is_essential"))
                            if not G.has_edge(source_id, neighbor_node_id):
                                G.add_edge(source_id, neighbor_node_id, relation=relation, is_essential=is_ess)
                        continue
                    
                    if node_count >= max_nodes:
                        break
                    
                    n_label = neighbor.get("name") or neighbor.get("symbol") or neighbor.get("organ", "?")
                    G.add_node(neighbor_node_id, label=n_label, node_type=neighbor_node_type, **neighbor)
                    visited.add(neighbor_node_id)
                    node_count += 1
                    
                    source_id = f"{ntype}_{nid}"
                    relation = neighbor.get("relation", "")
                    is_ess = bool(neighbor.get("is_essential"))
                    G.add_edge(source_id, neighbor_node_id, relation=relation, is_essential=is_ess)
                    
                    queue.append((neighbor_node_type, neighbor["id"], current_depth + 1))
        
        # Layout im Worker berechnen
        if len(G.nodes) > 0:
            pos = nx.spring_layout(G, k=3.0, iterations=50, scale=400)
            for nid in G.nodes:
                G.nodes[nid]["_pos"] = pos.get(nid, (0, 0))
        
        return G


class GraphNode(QGraphicsEllipseItem):
    """Einzelner Knoten im Graphen."""
    
    def __init__(self, node_id, label, node_type, x, y, radius=25, data=None):
        super().__init__(-radius, -radius, radius * 2, radius * 2)
        self.node_id = node_id
        self.label = label
        self.node_type = node_type
        self.data = data or {}
        self.radius = radius
        self.connected_edges = []
        
        # Farbe nach Typ
        color = QColor(NODE_COLORS.get(node_type, "#9E9E9E"))
        self.setBrush(QBrush(color))
        self.setPen(QPen(color.darker(130), 2))
        
        # Pfad-Status hervorheben
        if node_type == "pathway" and data:
            status = data.get("status", "unbekannt")
            status_color = STATUS_COLORS.get(status, "#9E9E9E")
            self.setPen(QPen(QColor(status_color), 3))
        
        # Text-Label
        self._text = QGraphicsTextItem(label, self)
        self._text.setDefaultTextColor(QColor("#1e1e2e"))
        font = QFont("Segoe UI", 8)
        font.setBold(True)
        self._text.setFont(font)
        # Text zentrieren
        br = self._text.boundingRect()
        self._text.setPos(-br.width() / 2, -br.height() / 2)
        
        # Interaktion
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCursor(Qt.PointingHandCursor)
        self.setAcceptHoverEvents(True)
        
        self.setPos(x, y)
        self.setToolTip(f"{node_type}: {label}\n{self._format_tooltip()}")
    
    def _format_tooltip(self):
        parts = []
        skip = ("id", "external_id", "_pos", "is_center", "node_type", "label")
        for k, v in self.data.items():
            if k in skip:
                continue
            try:
                if v:
                    parts.append(f"{k}: {v}")
            except (ValueError, TypeError):
                continue
        return "\n".join(parts[:5])
    
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for edge in self.connected_edges:
                edge.update_position()
        return super().itemChange(change, value)
    
    def hoverEnterEvent(self, event):
        self.setPen(QPen(QColor("#f5c2e7"), 3))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        color = QColor(NODE_COLORS.get(self.node_type, "#9E9E9E"))
        if self.node_type == "pathway" and self.data:
            status = self.data.get("status", "unbekannt")
            self.setPen(QPen(QColor(STATUS_COLORS.get(status, "#9E9E9E")), 3))
        else:
            self.setPen(QPen(color.darker(130), 2))
        super().hoverLeaveEvent(event)


class GraphEdge(QGraphicsLineItem):
    """Kante zwischen zwei Knoten."""
    
    def __init__(self, source_node, target_node, relation="", is_essential=False):
        super().__init__()
        self.source_node = source_node
        self.target_node = target_node
        self.relation = relation
        self.is_essential = is_essential
        
        color = QColor("#f38ba8") if is_essential else QColor("#585b70")
        width = 2.5 if is_essential else 1.5
        self.setPen(QPen(color, width))
        
        if relation:
            self.setToolTip(relation)
        
        self.setZValue(-1)  # Kanten hinter Knoten
        
        source_node.connected_edges.append(self)
        target_node.connected_edges.append(self)
        
        self.update_position()
    
    def update_position(self):
        self.setLine(
            self.source_node.pos().x(), self.source_node.pos().y(),
            self.target_node.pos().x(), self.target_node.pos().y()
        )


class KnowledgeGraphView(QGraphicsView):
    """Interaktive Graph-Ansicht mit Zoom/Pan."""
    
    node_selected = Signal(str, int, dict)  # node_type, node_id, data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        
        self._nodes = {}  # node_id -> GraphNode
        self._edges = []
        self._zoom = 1.0
    
    def wheelEvent(self, event: QWheelEvent):
        """Zoom mit Mausrad."""
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self._zoom *= factor
        if 0.1 < self._zoom < 10:
            self.scale(factor, factor)
        else:
            self._zoom /= factor
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        item = self.itemAt(event.pos())
        if isinstance(item, GraphNode):
            parts = item.node_id.split("_", 1)
            if len(parts) == 2:
                self.node_selected.emit(parts[0], int(parts[1]), item.data)
        elif isinstance(item, QGraphicsTextItem) and isinstance(item.parentItem(), GraphNode):
            node = item.parentItem()
            parts = node.node_id.split("_", 1)
            if len(parts) == 2:
                self.node_selected.emit(parts[0], int(parts[1]), node.data)
    
    def load_graph(self, nx_graph):
        """Laedt einen networkx-Graphen und visualisiert ihn.
        
        Erwartet vorberechnete Positionen in _pos Attribut der Knoten.
        """
        self._scene.clear()
        self._nodes.clear()
        self._edges.clear()
        
        if len(nx_graph.nodes) == 0:
            return
        
        # Knoten erstellen (Positionen aus Worker)
        for node_id, data in nx_graph.nodes(data=True):
            x, y = data.get("_pos", (0, 0))
            label = data.get("label", node_id)
            node_type = data.get("node_type", "unknown")
            
            # Kuerzen wenn noetig
            display_label = label[:12] + ".." if len(label) > 14 else label
            
            node = GraphNode(node_id, display_label, node_type,
                           x * 1.5, y * 1.5, radius=30, data=data)
            self._scene.addItem(node)
            self._nodes[node_id] = node
        
        # Kanten erstellen
        for u, v, data in nx_graph.edges(data=True):
            if u in self._nodes and v in self._nodes:
                edge = GraphEdge(
                    self._nodes[u], self._nodes[v],
                    relation=data.get("relation", ""),
                    is_essential=bool(data.get("is_essential"))
                )
                self._scene.addItem(edge)
                self._edges.append(edge)
        
        # Ansicht anpassen
        self.fitInView(self._scene.sceneRect().adjusted(-50, -50, 50, 50),
                      Qt.KeepAspectRatio)
    
    def highlight_center(self, center_type, center_id):
        """Hebt den zentralen Knoten hervor."""
        center_node_id = f"{center_type}_{center_id}"
        if center_node_id in self._nodes:
            self._nodes[center_node_id].setScale(1.4)
            self._nodes[center_node_id].setBrush(QBrush(QColor("#f5c2e7")))
    
    def highlight_pathways(self, pathway_ids):
        """Hebt bestimmte Pfade hervor."""
        for node_id, node in self._nodes.items():
            if node.node_type == "pathway":
                nid = int(node_id.split("_")[1])
                if nid in pathway_ids:
                    node.setBrush(QBrush(QColor("#f5c2e7")))
                    node.setScale(1.3)
                else:
                    color = QColor(NODE_COLORS.get("pathway", "#4FC3F7"))
                    node.setBrush(QBrush(color))
                    node.setScale(1.0)
    
    def highlight_genes(self, gene_symbols, color_hex="#a6e3a1"):
        """Hebt bestimmte Gene hervor."""
        for node_id, node in self._nodes.items():
            if node.node_type == "gene":
                if node.data.get("symbol") in gene_symbols:
                    node.setBrush(QBrush(QColor(color_hex)))
                    node.setScale(1.3)
                else:
                    node.setBrush(QBrush(QColor(NODE_COLORS["gene"])))
                    node.setScale(1.0)
    
    def reset_highlights(self):
        """Setzt alle Hervorhebungen zurueck."""
        for node_id, node in self._nodes.items():
            color = QColor(NODE_COLORS.get(node.node_type, "#9E9E9E"))
            node.setBrush(QBrush(color))
            node.setScale(1.0)


class GraphExplorer(QWidget):
    """Tab 1: Graph-Explorer mit Lazy-Loading Nachbarschafts-Navigation."""
    
    node_selected = Signal(str, int, dict)
    
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self._nav_stack = []  # Breadcrumb-Navigation
        self._worker_thread = None
        self._worker = None
        self._pending_center = None  # (type, id) fuer Hervorhebung
        self._setup_ui()
        self._load_overview()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Toolbar Zeile 1
        toolbar = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Knoten suchen...")
        self.search_input.returnPressed.connect(self._on_search)
        toolbar.addWidget(self.search_input, 3)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Alle", "Pfade", "Gene", "Orte", "Zellen", "Messwerte", "Diagnosen"])
        toolbar.addWidget(self.filter_combo)
        
        toolbar.addWidget(QLabel("Tiefe:"))
        self.depth_spin = QSpinBox()
        self.depth_spin.setRange(1, 3)
        self.depth_spin.setValue(1)
        self.depth_spin.setToolTip("Nachbarschafts-Tiefe (1-3 Hops)")
        toolbar.addWidget(self.depth_spin)
        
        toolbar.addWidget(QLabel("Max:"))
        self.max_spin = QSpinBox()
        self.max_spin.setRange(10, 1000)
        self.max_spin.setValue(200)
        self.max_spin.setSingleStep(50)
        self.max_spin.setToolTip("Maximale Knotenanzahl")
        toolbar.addWidget(self.max_spin)
        
        layout.addLayout(toolbar)
        
        # Toolbar Zeile 2: Navigation
        nav_bar = QHBoxLayout()
        
        btn_overview = QPushButton("Uebersicht")
        btn_overview.clicked.connect(self._load_overview)
        nav_bar.addWidget(btn_overview)
        
        btn_back = QPushButton("Zurueck")
        btn_back.clicked.connect(self._go_back)
        nav_bar.addWidget(btn_back)
        
        btn_refresh = QPushButton("Aktualisieren")
        btn_refresh.clicked.connect(self._refresh_current)
        nav_bar.addWidget(btn_refresh)
        
        btn_fit = QPushButton("Einpassen")
        btn_fit.clicked.connect(self._fit_view)
        nav_bar.addWidget(btn_fit)
        
        self.breadcrumb = QLabel("Uebersicht")
        self.breadcrumb.setObjectName("subtitle")
        nav_bar.addWidget(self.breadcrumb, 1)
        
        self.node_count_label = QLabel("")
        nav_bar.addWidget(self.node_count_label)
        
        layout.addLayout(nav_bar)
        
        # Legende
        legend = QHBoxLayout()
        for node_type, color in NODE_COLORS.items():
            label_names = {"pathway": "Pfad", "location": "Ort", "cell": "Zelle",
                          "gene": "Gen", "measurement": "Messwert", "diagnosis": "Diagnose"}
            lbl = QLabel(f"  {label_names.get(node_type, node_type)}  ")
            lbl.setStyleSheet(f"background-color: {color}; color: #1e1e2e; border-radius: 3px; padding: 2px 6px; font-size: 11px;")
            legend.addWidget(lbl)
        legend.addStretch()
        layout.addLayout(legend)
        
        # Graph-View
        self.graph_view = KnowledgeGraphView()
        self.graph_view.node_selected.connect(self._on_node_selected)
        layout.addWidget(self.graph_view)
    
    def _start_worker(self, task, args, center=None):
        """Startet Graph-Berechnung im Hintergrund-Thread."""
        # Alten Worker und Thread sauber aufraemen
        if self._worker_thread and self._worker_thread.isRunning():
            self._worker_thread.quit()
            self._worker_thread.wait(2000)
        # Kein manuelles deleteLater auf _worker -- das uebernimmt
        # finished.connect(deleteLater) weiter unten. Doppeltes deleteLater
        # bei schnellem Doppelklick fuehrt zu Segfault.
        self._worker = None
        if self._worker_thread:
            self._worker_thread.deleteLater()
            self._worker_thread = None

        self._pending_center = center
        self.node_count_label.setText("Lade...")

        self._worker_thread = QThread()
        self._worker = GraphWorker(task, args)
        self._worker.moveToThread(self._worker_thread)
        self._worker_thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_graph_ready)
        self._worker.finished.connect(self._worker_thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker_thread.finished.connect(self._worker_thread.deleteLater)
        self._worker_thread.start()
    
    def _on_graph_ready(self, nx_graph):
        """Callback: Graph ist berechnet, jetzt rendern (im GUI-Thread)."""
        self.graph_view.load_graph(nx_graph)
        if self._pending_center:
            self.graph_view.highlight_center(*self._pending_center)
        self._update_count()
    
    def _load_overview(self):
        """Laedt die Uebersicht (vollstaendig bei kleinen Graphen, sonst nur Pfade)."""
        self._nav_stack.clear()
        self.breadcrumb.setText("Uebersicht (alle Knoten)")
        self._start_worker("overview", {"max_nodes": self.max_spin.value()})
    
    def _on_node_selected(self, node_type, node_id, data):
        """Reagiert auf Knoten-Selektion: Navigiere in Nachbarschaft."""
        self.node_selected.emit(node_type, node_id, data)
        self._navigate_to(node_type, node_id, data)
    
    def _navigate_to(self, node_type, node_id, data):
        """Navigiert zur Nachbarschaft eines Knotens."""
        label = data.get("name") or data.get("symbol") or data.get("organ", f"{node_type}#{node_id}")
        self._nav_stack.append((node_type, node_id, label))
        
        # Breadcrumb aktualisieren
        crumbs = " > ".join(item[2] for item in self._nav_stack[-3:])
        if len(self._nav_stack) > 3:
            crumbs = "... > " + crumbs
        self.breadcrumb.setText(crumbs)
        
        # Nachbarschaft im Worker laden
        depth = self.depth_spin.value()
        max_nodes = self.max_spin.value()
        self._start_worker("neighborhood", {
            "center_type": node_type, "center_id": node_id,
            "depth": depth, "max_nodes": max_nodes
        }, center=(node_type, node_id))
    
    def _go_back(self):
        """Geht einen Schritt zurueck."""
        if len(self._nav_stack) > 1:
            self._nav_stack.pop()
            prev = self._nav_stack[-1]
            self._nav_stack.pop()  # wird von _navigate_to wieder hinzugefuegt
            self._navigate_to(prev[0], prev[1], {"name": prev[2]})
        else:
            self._load_overview()
    
    def _refresh_current(self):
        """Aktualisiert die aktuelle Ansicht."""
        if self._nav_stack:
            prev = self._nav_stack[-1]
            self._nav_stack.pop()
            self._navigate_to(prev[0], prev[1], {"name": prev[2]})
        else:
            self._load_overview()
    
    def _fit_view(self):
        self.graph_view.fitInView(
            self.graph_view.scene().sceneRect().adjusted(-50, -50, 50, 50),
            Qt.KeepAspectRatio
        )
    
    def _on_search(self):
        text = self.search_input.text().strip()
        if not text:
            self.graph_view.reset_highlights()
            self.node_count_label.setText("")
            return
        from engine.query import GraphQuery
        query = GraphQuery(self.conn)
        results = query.search_nodes(text)

        # Filter anwenden
        filter_map = {
            "Pfade": "pathway", "Gene": "gene", "Orte": "location",
            "Zellen": "cell", "Messwerte": "measurement", "Diagnosen": "diagnosis",
        }
        selected_filter = self.filter_combo.currentText()
        if selected_filter != "Alle" and selected_filter in filter_map:
            target_type = filter_map[selected_filter]
            results = [r for r in results if r.get("_node_type") == target_type]

        if not results:
            self.node_count_label.setText(f"Keine Treffer fuer '{text}'")
            return

        # Immer zum ersten Treffer navigieren (zeigt alle Farben/Typen)
        r = results[0]
        if len(results) > 1:
            self.node_count_label.setText(f"{len(results)} Treffer -- zeige #{1}")
        self._navigate_to(r["_node_type"], r["id"], r)
    
    def _update_count(self):
        count = len(self.graph_view._nodes)
        edges = len(self.graph_view._edges)
        self.node_count_label.setText(f"{count} Knoten, {edges} Kanten")
    
    def refresh(self):
        self._refresh_current()
