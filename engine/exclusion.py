"""Ausschlusslogik: Intakte Pfade schliessen essenzielle Gene aus.

Kernprinzip:
- Ein intakter Pfad beweist, dass alle seine essenziellen Gene funktionieren.
- Wenn ein Gen NUR in intakten Pfaden essentiell ist, kann es nicht die Ursache sein.
- Gene die auch in gestoerten/unbekannten Pfaden essentiell sind, bleiben Kandidaten.
- Globale Gene (essentiell in mehreren Pfaden) werden nur ausgeschlossen wenn ALLE
  ihre Pfade intakt sind.
"""
import sqlite3
from collections import defaultdict
from typing import List, Dict, Set, Tuple, Optional


class ExclusionEngine:
    """Fuehrt Ausschlussanalyse auf dem Knowledge Graph durch."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
    
    def get_pathway_status(self) -> Dict[int, dict]:
        """Liefert alle Pfade mit Status."""
        rows = self.conn.execute(
            "SELECT id, name, status FROM functional_pathways"
        ).fetchall()
        return {r["id"]: dict(r) for r in rows}
    
    def get_essential_genes_for_pathway(self, pathway_id: int) -> List[dict]:
        """Liefert alle essenziellen Gene eines Pfads."""
        rows = self.conn.execute("""
            SELECT gp.id, gp.symbol, gp.name, gp.function_type, gp.redundancy_degree,
                   gpw.relation
            FROM genes_proteins gp
            JOIN gene_pathways gpw ON gp.id = gpw.gene_id
            WHERE gpw.pathway_id = ? AND gpw.is_essential = 1
        """, (pathway_id,)).fetchall()
        return [dict(r) for r in rows]
    
    def get_all_pathways_for_gene(self, gene_id: int) -> List[dict]:
        """Liefert alle Pfade in denen ein Gen essentiell ist."""
        rows = self.conn.execute("""
            SELECT fp.id, fp.name, fp.status, gpw.is_essential, gpw.relation
            FROM functional_pathways fp
            JOIN gene_pathways gpw ON fp.id = gpw.pathway_id
            WHERE gpw.gene_id = ? AND gpw.is_essential = 1
        """, (gene_id,)).fetchall()
        return [dict(r) for r in rows]
    
    def _load_all_gene_pathway_mappings(self) -> Dict[int, List[dict]]:
        """Laedt ALLE Gen-Pathway-Mappings in einer einzigen Query.

        Vermeidet N+1 Queries (eine pro Gen) in run_exclusion().
        Returns: Dict gene_id -> Liste von Pathway-Dicts
        """
        rows = self.conn.execute("""
            SELECT gp.id as gene_id, gp.symbol, gp.name, gp.function_type, gp.redundancy_degree,
                   fp.id as pathway_id, fp.name as pathway_name, fp.status
            FROM genes_proteins gp
            JOIN gene_pathways gpw ON gp.id = gpw.gene_id
            JOIN functional_pathways fp ON fp.id = gpw.pathway_id
            WHERE gpw.is_essential = 1
        """).fetchall()

        mapping = defaultdict(list)
        for r in rows:
            mapping[r["gene_id"]].append({
                "id": r["pathway_id"],
                "name": r["pathway_name"],
                "status": r["status"],
            })
        return mapping

    def run_exclusion(self) -> dict:
        """Fuehrt die Ausschlussanalyse durch.

        Returns:
            dict mit:
            - excluded_genes: Liste von Genen die ausgeschlossen werden koennen
            - candidate_genes: Liste von Genen die Kandidaten bleiben
            - reasoning: Erklaerungen fuer jede Entscheidung
            - intact_pathways: Anzahl intakter Pfade
            - total_genes_analyzed: Gesamtzahl analysierter Gene
        """
        pathways = self.get_pathway_status()
        intact_ids = {pid for pid, p in pathways.items() if p["status"] == "intakt"}
        disturbed_ids = {pid for pid, p in pathways.items() if p["status"] == "gestoert"}

        # Alle Gene sammeln die in mindestens einem Pfad essentiell sind
        all_essential_genes = self.conn.execute("""
            SELECT DISTINCT gp.id, gp.symbol, gp.name, gp.function_type, gp.redundancy_degree
            FROM genes_proteins gp
            JOIN gene_pathways gpw ON gp.id = gpw.gene_id
            WHERE gpw.is_essential = 1
        """).fetchall()

        # Alle Gen-Pathway-Mappings in EINER Query laden (statt N+1)
        gene_pathway_map = self._load_all_gene_pathway_mappings()

        excluded = []
        candidates = []
        reasoning = []

        for gene_row in all_essential_genes:
            gene = dict(gene_row)
            gene_id = gene["id"]

            # Alle Pfade in denen dieses Gen essentiell ist (aus Bulk-Lookup)
            gene_pathways = gene_pathway_map.get(gene_id, [])
            pathway_ids = {p["id"] for p in gene_pathways}

            # Pruefen: Sind ALLE Pfade dieses Gens intakt?
            all_intact = pathway_ids.issubset(intact_ids)
            # Hat das Gen mindestens einen gestoerten Pfad?
            has_disturbed = bool(pathway_ids & disturbed_ids)
            # Nicht-intakte Pfade
            non_intact = pathway_ids - intact_ids

            pathway_names = {p["id"]: p["name"] for p in gene_pathways}

            if all_intact and len(intact_ids & pathway_ids) > 0:
                excluded.append(gene)
                intact_names = [pathway_names[pid] for pid in pathway_ids & intact_ids]
                reasoning.append({
                    "gene": gene["symbol"],
                    "decision": "ausgeschlossen",
                    "reason": f"Alle {len(pathway_ids)} Pfade intakt: {', '.join(intact_names)}",
                    "confidence": "hoch" if len(pathway_ids) > 1 else "mittel",
                })
            else:
                candidates.append(gene)
                intact_names = [pathway_names[pid] for pid in pathway_ids & intact_ids]
                non_intact_names = [pathway_names[pid] for pid in non_intact]
                reason_parts = []
                if intact_names:
                    reason_parts.append(f"Intakt: {', '.join(intact_names)}")
                if non_intact_names:
                    reason_parts.append(f"Nicht intakt: {', '.join(non_intact_names)}")
                reasoning.append({
                    "gene": gene["symbol"],
                    "decision": "kandidat",
                    "reason": "; ".join(reason_parts) or "Kein Pfad als intakt markiert",
                    "confidence": "hoch" if has_disturbed else "niedrig",
                })

        return {
            "excluded_genes": excluded,
            "candidate_genes": candidates,
            "reasoning": reasoning,
            "intact_pathways": len(intact_ids),
            "disturbed_pathways": len(disturbed_ids),
            "total_genes_analyzed": len(all_essential_genes),
        }
    
    def get_exclusion_for_gene(self, gene_symbol: str) -> Optional[dict]:
        """Prueft den Ausschlussstatus eines einzelnen Gens."""
        row = self.conn.execute(
            "SELECT id FROM genes_proteins WHERE symbol = ?", (gene_symbol,)
        ).fetchone()
        if not row:
            return None
        
        gene_id = row["id"]
        result = self.run_exclusion()
        
        for r in result["reasoning"]:
            if r["gene"] == gene_symbol:
                return r
        return None


class ProbabilisticExclusionEngine(ExclusionEngine):
    """Erweiterte Ausschlusslogik mit Konfidenzwerten.
    
    Statt binaer (ausgeschlossen/kandidat) berechnet diese Engine
    einen Konfidenzwert 0.0-1.0 fuer jeden Gen-Ausschluss.
    
    Faktoren:
    - Pfad-Evidenz: Wie sicher ist der Pfad-Status? (intakt=1.0, gestoert=0.0, unbekannt=0.5)
    - Redundanz: Gene mit hoher Redundanz sind weniger verdaechtig
    - Multi-Pfad-Evidenz: Gene in mehreren intakten Pfaden haben staerkere Ausschluss-Evidenz
    - Essentialitaet: Nicht-essentielle Gene in einem Pfad koennten trotz Defekt kompensiert werden
    """
    
    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn)
        # Pfad-Status -> Konfidenz-Mapping
        self.status_confidence = {
            "intakt": 0.95,      # 95% sicher dass der Pfad funktioniert
            "gestoert": 0.05,    # 5% (fast sicher gestoert)
            "unbekannt": 0.50,   # Keine Information
        }
        # Redundanz -> Modifikator (hohe Redundanz = Gen weniger verdaechtig)
        self.redundancy_modifier = {
            "keine": 1.0,    # Kein Backup -> voll verdaechtig wenn Pfad gestoert
            "niedrig": 0.85,
            "mittel": 0.6,
            "hoch": 0.3,     # Viel Backup -> weniger verdaechtig
        }
    
    def run_probabilistic_exclusion(self) -> dict:
        """Fuehrt probabilistische Ausschlussanalyse durch.

        Returns:
            dict mit:
            - gene_scores: Liste von {gene, exclusion_confidence, factors}
            - summary: Zusammenfassung
        """
        pathways = self.get_pathway_status()

        # Alle essenziellen Gene
        all_essential_genes = self.conn.execute("""
            SELECT DISTINCT gp.id, gp.symbol, gp.name, gp.function_type, gp.redundancy_degree
            FROM genes_proteins gp
            JOIN gene_pathways gpw ON gp.id = gpw.gene_id
            WHERE gpw.is_essential = 1
        """).fetchall()

        # Alle Gen-Pathway-Mappings in EINER Query laden (statt N+1)
        gene_pathway_map = self._load_all_gene_pathway_mappings()

        gene_scores = []

        for gene_row in all_essential_genes:
            gene = dict(gene_row)
            gene_id = gene["id"]

            # Alle Pfade in denen das Gen essentiell ist (aus Bulk-Lookup)
            gene_pathways = gene_pathway_map.get(gene_id, [])
            
            if not gene_pathways:
                continue
            
            # === Faktor 1: Pfad-Evidenz ===
            # Fuer jeden Pfad: wie sicher ist es dass der Pfad intakt ist?
            pathway_confidences = []
            for p in gene_pathways:
                status = p.get("status", "unbekannt")
                conf = self.status_confidence.get(status, 0.5)
                pathway_confidences.append({
                    "pathway": p["name"],
                    "status": status,
                    "confidence": conf,
                })
            
            # Kombinierte Pfad-Evidenz: Alle Pfade muessen intakt sein fuer Ausschluss
            # P(alle intakt) = Produkt der Einzelwahrscheinlichkeiten
            combined_pathway_conf = 1.0
            for pc in pathway_confidences:
                combined_pathway_conf *= pc["confidence"]
            
            # === Faktor 2: Redundanz ===
            redundancy = gene.get("redundancy_degree", "mittel")
            redundancy_mod = self.redundancy_modifier.get(redundancy, 0.6)
            
            # === Faktor 3: Multi-Pfad-Staerkung ===
            # Mehr intakte Pfade = staerkere Evidenz
            n_pathways = len(gene_pathways)
            n_intact = sum(1 for pc in pathway_confidences if pc["status"] == "intakt")
            multi_pathway_bonus = min(1.0, 0.7 + 0.1 * n_intact) if n_intact > 0 else 0.5
            
            # === Gesamt-Score ===
            # Exclusion Confidence: Wie sicher sind wir dass das Gen NICHT die Ursache ist?
            exclusion_confidence = combined_pathway_conf * multi_pathway_bonus
            
            # Verdachts-Score: Umkehrung + Redundanz-Gewichtung
            # Niedrige Redundanz = hoeherer Verdacht bei gestoerten Pfaden
            suspicion_score = (1.0 - exclusion_confidence) * redundancy_mod
            
            gene_scores.append({
                "gene_id": gene_id,
                "symbol": gene["symbol"],
                "name": gene.get("name", ""),
                "function_type": gene.get("function_type", ""),
                "redundancy": redundancy,
                "exclusion_confidence": round(exclusion_confidence, 3),
                "suspicion_score": round(suspicion_score, 3),
                "n_pathways": n_pathways,
                "n_intact": n_intact,
                "pathway_details": pathway_confidences,
                "factors": {
                    "pathway_evidence": round(combined_pathway_conf, 3),
                    "redundancy_modifier": redundancy_mod,
                    "multi_pathway_bonus": round(multi_pathway_bonus, 2),
                },
            })
        
        # Sortieren: hoechster Verdacht zuerst
        gene_scores.sort(key=lambda x: x["suspicion_score"], reverse=True)
        
        # Kategorisierung
        high_exclusion = [g for g in gene_scores if g["exclusion_confidence"] >= 0.8]
        moderate = [g for g in gene_scores if 0.3 <= g["exclusion_confidence"] < 0.8]
        suspects = [g for g in gene_scores if g["exclusion_confidence"] < 0.3]
        
        return {
            "gene_scores": gene_scores,
            "high_exclusion": high_exclusion,
            "moderate_exclusion": moderate,
            "suspects": suspects,
            "summary": {
                "total_analyzed": len(gene_scores),
                "high_exclusion_count": len(high_exclusion),
                "moderate_count": len(moderate),
                "suspect_count": len(suspects),
            },
        }
    
    def set_status_confidence(self, status: str, confidence: float):
        """Erlaubt Anpassung der Status-Konfidenz."""
        self.status_confidence[status] = max(0.0, min(1.0, confidence))
