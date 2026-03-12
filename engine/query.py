"""Graph-Traversal und Abfragen auf dem Knowledge Graph.

Ermoeglicht:
- Nachbarschaftsabfragen (was ist mit X verbunden?)
- Pfad-Analysen (welche Pfade sind von Gen Y betroffen?)
- Diagnose-Queries (Symptome -> Verdachtspfade -> Gene)
- Pattern-Detection (Messwert-Signaturen erkennen)
"""
import sqlite3
from typing import List, Dict, Optional, Set, Tuple


class GraphQuery:
    """Abfrage-Engine fuer den Knowledge Graph."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
    
    def get_neighbors(self, node_type: str, node_id: int) -> Dict[str, List[dict]]:
        """Liefert alle Nachbarn eines Knotens, gruppiert nach Typ."""
        neighbors = {}
        
        if node_type == "pathway":
            # Orte
            neighbors["locations"] = [dict(r) for r in self.conn.execute("""
                SELECT bl.*, pl.relation FROM body_locations bl
                JOIN pathway_locations pl ON bl.id = pl.location_id
                WHERE pl.pathway_id = ?
            """, (node_id,)).fetchall()]
            # Zelltypen
            neighbors["cells"] = [dict(r) for r in self.conn.execute("""
                SELECT ct.*, pc.relation FROM cell_types ct
                JOIN pathway_cells pc ON ct.id = pc.cell_type_id
                WHERE pc.pathway_id = ?
            """, (node_id,)).fetchall()]
            # Gene
            neighbors["genes"] = [dict(r) for r in self.conn.execute("""
                SELECT gp.*, gpw.relation, gpw.is_essential FROM genes_proteins gp
                JOIN gene_pathways gpw ON gp.id = gpw.gene_id
                WHERE gpw.pathway_id = ?
            """, (node_id,)).fetchall()]
            # Messwerte
            neighbors["measurements"] = [dict(r) for r in self.conn.execute("""
                SELECT m.*, mp.relation FROM measurements m
                JOIN measurement_pathways mp ON m.id = mp.measurement_id
                WHERE mp.pathway_id = ?
            """, (node_id,)).fetchall()]
            # Diagnosen
            neighbors["diagnoses"] = [dict(r) for r in self.conn.execute("""
                SELECT d.*, pd.relation FROM diagnoses d
                JOIN pathway_diagnoses pd ON d.id = pd.diagnosis_id
                WHERE pd.pathway_id = ?
            """, (node_id,)).fetchall()]
            
        elif node_type == "gene":
            neighbors["pathways"] = [dict(r) for r in self.conn.execute("""
                SELECT fp.*, gpw.relation, gpw.is_essential FROM functional_pathways fp
                JOIN gene_pathways gpw ON fp.id = gpw.pathway_id
                WHERE gpw.gene_id = ?
            """, (node_id,)).fetchall()]
            neighbors["expressions"] = [dict(r) for r in self.conn.execute("""
                SELECT bl.*, ge.expression_level FROM body_locations bl
                JOIN gene_expressions ge ON bl.id = ge.location_id
                WHERE ge.gene_id = ?
            """, (node_id,)).fetchall()]
            
        elif node_type == "location":
            neighbors["pathways"] = [dict(r) for r in self.conn.execute("""
                SELECT fp.*, pl.relation FROM functional_pathways fp
                JOIN pathway_locations pl ON fp.id = pl.pathway_id
                WHERE pl.location_id = ?
            """, (node_id,)).fetchall()]
            neighbors["measurements"] = [dict(r) for r in self.conn.execute("""
                SELECT m.*, ml.relation FROM measurements m
                JOIN measurement_locations ml ON m.id = ml.measurement_id
                WHERE ml.location_id = ?
            """, (node_id,)).fetchall()]
            neighbors["gene_expressions"] = [dict(r) for r in self.conn.execute("""
                SELECT gp.*, ge.expression_level FROM genes_proteins gp
                JOIN gene_expressions ge ON gp.id = ge.gene_id
                WHERE ge.location_id = ?
            """, (node_id,)).fetchall()]
            
        elif node_type == "measurement":
            neighbors["pathways"] = [dict(r) for r in self.conn.execute("""
                SELECT fp.*, mp.relation FROM functional_pathways fp
                JOIN measurement_pathways mp ON fp.id = mp.pathway_id
                WHERE mp.measurement_id = ?
            """, (node_id,)).fetchall()]
            neighbors["locations"] = [dict(r) for r in self.conn.execute("""
                SELECT bl.*, ml.relation FROM body_locations bl
                JOIN measurement_locations ml ON bl.id = ml.location_id
                WHERE ml.measurement_id = ?
            """, (node_id,)).fetchall()]
            
        elif node_type == "diagnosis":
            neighbors["pathways"] = [dict(r) for r in self.conn.execute("""
                SELECT fp.*, pd.relation FROM functional_pathways fp
                JOIN pathway_diagnoses pd ON fp.id = pd.pathway_id
                WHERE pd.diagnosis_id = ?
            """, (node_id,)).fetchall()]
            
        elif node_type == "cell":
            neighbors["pathways"] = [dict(r) for r in self.conn.execute("""
                SELECT fp.*, pc.relation FROM functional_pathways fp
                JOIN pathway_cells pc ON fp.id = pc.pathway_id
                WHERE pc.cell_type_id = ?
            """, (node_id,)).fetchall()]
        
        return neighbors
    
    def diagnose_from_measurements(self, abnormal_measurements: List[Dict],
                                    intact_pathways: List[int] = None) -> dict:
        """Diagnose-Query: Auffaellige Messwerte + intakte Pfade -> Verdacht.
        
        Args:
            abnormal_measurements: Liste von {"name": str, "value": float, "direction": "hoch"|"niedrig"}
            intact_pathways: Liste von Pathway-IDs die als intakt gelten
            
        Returns:
            dict mit suspect_pathways, suspect_genes, suggested_tests, reasoning
        """
        intact_pathways = intact_pathways or []
        
        # Betroffene Pfade finden
        affected_pathway_ids = set()
        measurement_pathway_map = {}
        
        for am in abnormal_measurements:
            rows = self.conn.execute("""
                SELECT mp.pathway_id, fp.name as pathway_name, mp.relation
                FROM measurement_pathways mp
                JOIN functional_pathways fp ON fp.id = mp.pathway_id
                JOIN measurements m ON m.id = mp.measurement_id
                WHERE m.name = ?
            """, (am["name"],)).fetchall()
            
            for r in rows:
                pid = r["pathway_id"]
                affected_pathway_ids.add(pid)
                if pid not in measurement_pathway_map:
                    measurement_pathway_map[pid] = {
                        "pathway_name": r["pathway_name"],
                        "measurements": [],
                    }
                measurement_pathway_map[pid]["measurements"].append({
                    "name": am["name"],
                    "value": am.get("value"),
                    "direction": am.get("direction", ""),
                    "relation": r["relation"],
                })
        
        # Intakte Pfade ausschliessen
        suspect_pathway_ids = affected_pathway_ids - set(intact_pathways)
        
        # Verdachtsgene aus nicht-intakten betroffenen Pfaden
        suspect_genes = []
        seen_genes = set()
        for pid in suspect_pathway_ids:
            rows = self.conn.execute("""
                SELECT gp.id, gp.symbol, gp.name, gp.function_type,
                       gpw.is_essential, gpw.relation
                FROM genes_proteins gp
                JOIN gene_pathways gpw ON gp.id = gpw.gene_id
                WHERE gpw.pathway_id = ? AND gpw.is_essential = 1
            """, (pid,)).fetchall()
            for r in rows:
                if r["id"] not in seen_genes:
                    seen_genes.add(r["id"])
                    gene = dict(r)
                    gene["from_pathway"] = measurement_pathway_map.get(pid, {}).get("pathway_name", "")
                    suspect_genes.append(gene)
        
        # Test-Vorschlaege: Messwerte die mit Verdachtspfaden verknuepft sind
        # aber noch nicht gemessen wurden
        measured_names = {am["name"] for am in abnormal_measurements}
        suggested_tests = []
        for pid in suspect_pathway_ids:
            rows = self.conn.execute("""
                SELECT m.name, m.unit, m.measurement_site, mp.relation
                FROM measurements m
                JOIN measurement_pathways mp ON m.id = mp.measurement_id
                WHERE mp.pathway_id = ?
            """, (pid,)).fetchall()
            for r in rows:
                if r["name"] not in measured_names:
                    suggested_tests.append(dict(r))
                    measured_names.add(r["name"])  # Duplikate vermeiden
        
        return {
            "suspect_pathways": [
                {**measurement_pathway_map[pid], "pathway_id": pid}
                for pid in suspect_pathway_ids if pid in measurement_pathway_map
            ],
            "excluded_pathways": [
                {**measurement_pathway_map[pid], "pathway_id": pid, "reason": "intakt markiert"}
                for pid in (affected_pathway_ids & set(intact_pathways))
                if pid in measurement_pathway_map
            ],
            "suspect_genes": suspect_genes,
            "suggested_tests": suggested_tests,
        }
    
    def get_pathways_for_diagnosis(self, diagnosis_name: str) -> List[dict]:
        """Liefert alle Pfade die mit einer Diagnose verknuepft sind."""
        rows = self.conn.execute("""
            SELECT fp.*, pd.relation
            FROM functional_pathways fp
            JOIN pathway_diagnoses pd ON fp.id = pd.pathway_id
            JOIN diagnoses d ON d.id = pd.diagnosis_id
            WHERE d.name = ?
        """, (diagnosis_name,)).fetchall()
        return [dict(r) for r in rows]
    
    def search_nodes(self, query: str) -> List[dict]:
        """Sucht Knoten ueber alle Tabellen nach Name/Symbol."""
        results = []
        query_like = f"%{query}%"
        
        for table, name_col, node_type in [
            ("functional_pathways", "name", "pathway"),
            ("body_locations", "organ", "location"),
            ("cell_types", "name", "cell"),
            ("genes_proteins", "symbol", "gene"),
            ("measurements", "name", "measurement"),
            ("diagnoses", "name", "diagnosis"),
        ]:
            rows = self.conn.execute(
                f"SELECT * FROM {table} WHERE {name_col} LIKE ?",
                (query_like,)
            ).fetchall()
            for r in rows:
                d = dict(r)
                d["_node_type"] = node_type
                results.append(d)
        
        # Auch Gen-Namen durchsuchen (Duplikate via ID vermeiden)
        seen_ids = {(r["_node_type"], r["id"]) for r in results}
        rows = self.conn.execute(
            "SELECT * FROM genes_proteins WHERE name LIKE ?",
            (query_like,)
        ).fetchall()
        for r in rows:
            if ("gene", r["id"]) not in seen_ids:
                d = dict(r)
                d["_node_type"] = "gene"
                results.append(d)
                seen_ids.add(("gene", r["id"]))
        
        return results
    
    def detect_patterns(self, abnormal_measurements: List[Dict]) -> List[dict]:
        """Erkennt Messwert-Muster/Signaturen in den auffaelligen Messwerten.
        
        Args:
            abnormal_measurements: Liste von {"name": str, "value": float, "direction": "hoch"|"niedrig"}
            
        Returns:
            Liste von erkannten Signaturen mit Match-Score
        """
        # Alle definierten Signaturen laden
        signatures = self.conn.execute(
            "SELECT * FROM measurement_signatures"
        ).fetchall()
        
        if not signatures:
            return []
        
        # Eingabe-Map: name -> direction
        input_map = {}
        for am in abnormal_measurements:
            input_map[am["name"]] = am.get("direction", "")
        
        detected = []
        
        for sig in signatures:
            sig = dict(sig)
            sig_id = sig["id"]
            
            # Signatur-Komponenten laden
            components = self.conn.execute("""
                SELECT sc.*, m.name as measurement_name, m.unit
                FROM signature_components sc
                JOIN measurements m ON m.id = sc.measurement_id
                WHERE sc.signature_id = ?
            """, (sig_id,)).fetchall()
            
            if not components:
                continue
            
            # Match berechnen
            total_weight = sum(c["weight"] for c in components)
            matched_weight = 0.0
            matched_components = []
            unmatched_components = []
            
            for comp in components:
                comp = dict(comp)
                meas_name = comp["measurement_name"]
                expected_dir = comp["expected_direction"]
                
                if meas_name in input_map:
                    actual_dir = input_map[meas_name]
                    if actual_dir == expected_dir:
                        matched_weight += comp["weight"]
                        comp["matched"] = True
                        comp["match_type"] = "voll"
                        matched_components.append(comp)
                    else:
                        comp["matched"] = False
                        comp["match_type"] = f"erwartet {expected_dir}, ist {actual_dir}"
                        unmatched_components.append(comp)
                else:
                    comp["matched"] = False
                    comp["match_type"] = "nicht gemessen"
                    unmatched_components.append(comp)
            
            match_score = matched_weight / total_weight if total_weight > 0 else 0.0
            
            # Nur Signaturen mit mindestens 30% Match anzeigen
            if match_score >= 0.3:
                detected.append({
                    "signature_name": sig["name"],
                    "description": sig.get("description", ""),
                    "icd_codes": sig.get("icd_codes", ""),
                    "match_score": round(match_score, 2),
                    "matched_components": matched_components,
                    "unmatched_components": unmatched_components,
                    "total_components": len(components),
                    "matched_count": len(matched_components),
                })
        
        # Sortieren nach Match-Score
        detected.sort(key=lambda x: x["match_score"], reverse=True)
        return detected
    
    def build_networkx_graph(self):
        """Baut einen networkx-Graphen fuer Visualisierung."""
        import networkx as nx
        
        G = nx.Graph()
        
        # Alle Knoten hinzufuegen
        from database import get_all_nodes, get_all_edges
        nodes = get_all_nodes(self.conn)
        edges = get_all_edges(self.conn)
        
        for node_type, node_list in nodes.items():
            for node in node_list:
                node_id = f"{node_type}_{node['id']}"
                label = node.get("name") or node.get("symbol") or node.get("organ", "")
                G.add_node(node_id, label=label, node_type=node_type, **node)
        
        for edge in edges:
            src = f"{edge['source_type']}_{edge['source_id']}"
            tgt = f"{edge['target_type']}_{edge['target_id']}"
            G.add_edge(src, tgt, relation=edge["relation"],
                      is_essential=edge.get("is_essential"))
        
        return G
