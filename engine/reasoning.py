"""Erklaerungsgenerierung fuer Ausschluss- und Diagnose-Ergebnisse.

Wandelt rohe Analyse-Ergebnisse in menschenlesbare Erklaerungen um.
"""
from typing import List, Dict


def explain_exclusion(result: dict) -> str:
    """Generiert menschenlesbare Erklaerung fuer Ausschluss-Ergebnis."""
    lines = []
    lines.append(f"=== Ausschluss-Analyse ===")
    lines.append(f"Intakte Pfade: {result['intact_pathways']}")
    lines.append(f"Gestoerte Pfade: {result['disturbed_pathways']}")
    lines.append(f"Analysierte Gene: {result['total_genes_analyzed']}")
    lines.append("")
    
    if result["excluded_genes"]:
        lines.append(f"AUSGESCHLOSSEN ({len(result['excluded_genes'])} Gene):")
        for gene in result["excluded_genes"]:
            reasoning = next(
                (r for r in result["reasoning"] if r["gene"] == gene["symbol"]), None
            )
            reason = reasoning["reason"] if reasoning else ""
            conf = reasoning.get("confidence", "") if reasoning else ""
            lines.append(f"  X {gene['symbol']} ({gene['name']}) - {reason} [{conf}]")
        lines.append("")
    
    if result["candidate_genes"]:
        lines.append(f"KANDIDATEN ({len(result['candidate_genes'])} Gene):")
        for gene in result["candidate_genes"]:
            reasoning = next(
                (r for r in result["reasoning"] if r["gene"] == gene["symbol"]), None
            )
            reason = reasoning["reason"] if reasoning else ""
            conf = reasoning.get("confidence", "") if reasoning else ""
            lines.append(f"  ? {gene['symbol']} ({gene['name']}) - {reason} [{conf}]")
    
    return "\n".join(lines)


def explain_diagnosis_query(result: dict) -> str:
    """Generiert Erklaerung fuer Diagnose-Query-Ergebnis."""
    lines = []
    lines.append("=== Diagnose-Query ===")
    lines.append("")
    
    if result["suspect_pathways"]:
        lines.append("VERDAECHTIGE PFADE:")
        for sp in result["suspect_pathways"]:
            lines.append(f"  ! {sp['pathway_name']}")
            for m in sp["measurements"]:
                direction = f" ({m['direction']})" if m.get("direction") else ""
                lines.append(f"    - {m['name']}{direction}: {m['relation']}")
        lines.append("")
    
    if result["excluded_pathways"]:
        lines.append("AUSGESCHLOSSENE PFADE (intakt):")
        for ep in result["excluded_pathways"]:
            lines.append(f"  V {ep['pathway_name']} - {ep['reason']}")
        lines.append("")
    
    if result["suspect_genes"]:
        lines.append("VERDACHTSGENE:")
        for g in result["suspect_genes"]:
            ess = " [essentiell]" if g.get("is_essential") else ""
            lines.append(f"  -> {g['symbol']} ({g['name']}){ess}")
            if g.get("from_pathway"):
                lines.append(f"    aus Pfad: {g['from_pathway']}")
        lines.append("")
    
    if result["suggested_tests"]:
        lines.append("VORGESCHLAGENE TESTS:")
        for t in result["suggested_tests"]:
            unit = f" [{t['unit']}]" if t.get("unit") else ""
            site = f" ({t['measurement_site']})" if t.get("measurement_site") else ""
            lines.append(f"  + {t['name']}{unit}{site}")
    
    return "\n".join(lines)


def generate_patient_summary(exclusion_result: dict, diagnosis_result: dict = None) -> str:
    """Generiert zusammenfassenden Bericht."""
    lines = []
    lines.append("=" * 60)
    lines.append("SYSTEM-MEDIZIN ANALYSEBERICHT")
    lines.append("=" * 60)
    lines.append("")
    
    # Ausschluss-Zusammenfassung
    n_excl = len(exclusion_result.get("excluded_genes", []))
    n_cand = len(exclusion_result.get("candidate_genes", []))
    total = n_excl + n_cand
    
    if total > 0:
        pct = (n_excl / total) * 100
        lines.append(f"Genanalyse: {n_excl}/{total} Gene ausgeschlossen ({pct:.0f}%)")
        lines.append(f"Verbleibende Kandidaten: {n_cand}")
    
    if exclusion_result.get("candidate_genes"):
        lines.append("")
        lines.append("Prioritaere Kandidaten:")
        for g in exclusion_result["candidate_genes"]:
            lines.append(f"  - {g['symbol']}: {g.get('name', '')}")
    
    if diagnosis_result:
        lines.append("")
        lines.append("-" * 40)
        if diagnosis_result.get("suspect_genes"):
            lines.append("Diagnosespezifische Verdachtsgene:")
            for g in diagnosis_result["suspect_genes"]:
                lines.append(f"  - {g['symbol']}")
        
        if diagnosis_result.get("suggested_tests"):
            lines.append("")
            lines.append("Empfohlene Zusatztests:")
            for t in diagnosis_result["suggested_tests"]:
                lines.append(f"  - {t['name']}")
    
    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


# --- Probabilistische Analyse ---

def _confidence_bar(value, width=10):
    """Erzeugt ASCII-Konfidenzbalken."""
    filled = int(value * width)
    empty = width - filled
    return f"[{'#' * filled}{'.' * empty}]"


def explain_probabilistic_exclusion(result: dict) -> str:
    """Generiert Erklaerung fuer probabilistische Ausschluss-Ergebnis."""
    lines = []
    lines.append("=== Probabilistische Ausschluss-Analyse ===")
    s = result["summary"]
    lines.append(f"Analysierte Gene: {s['total_analyzed']}")
    lines.append(f"Hohe Ausschluss-Konfidenz (>=80%): {s['high_exclusion_count']}")
    lines.append(f"Moderate Konfidenz (30-80%): {s['moderate_count']}")
    lines.append(f"Verdaechtig (<30%): {s['suspect_count']}")
    lines.append("")
    
    if result["suspects"]:
        lines.append("VERDAECHTIGE GENE (hoher Verdacht):")
        for g in result["suspects"]:
            bar = _confidence_bar(g["suspicion_score"])
            lines.append(f"  {bar} {g['symbol']} ({g['name']})")
            lines.append(f"      Verdacht: {g['suspicion_score']*100:.0f}% | "
                        f"Ausschluss: {g['exclusion_confidence']*100:.0f}% | "
                        f"Redundanz: {g['redundancy']}")
            for pd in g["pathway_details"]:
                lines.append(f"      - {pd['pathway']}: {pd['status']} ({pd['confidence']*100:.0f}%)")
        lines.append("")
    
    if result["moderate_exclusion"]:
        lines.append("MODERATE KONFIDENZ:")
        for g in result["moderate_exclusion"]:
            bar = _confidence_bar(g["exclusion_confidence"])
            lines.append(f"  {bar} {g['symbol']}: Ausschluss {g['exclusion_confidence']*100:.0f}%")
        lines.append("")
    
    if result["high_exclusion"]:
        lines.append("HOHE AUSSCHLUSS-KONFIDENZ:")
        for g in result["high_exclusion"]:
            bar = _confidence_bar(g["exclusion_confidence"])
            lines.append(f"  {bar} {g['symbol']}: Ausschluss {g['exclusion_confidence']*100:.0f}%")
    
    return "\n".join(lines)


# --- Pattern-Detection ---

def explain_pattern_detection(patterns: list) -> str:
    """Generiert Erklaerung fuer erkannte Messwert-Muster."""
    if not patterns:
        return "Keine bekannten Messwert-Muster erkannt."
    
    lines = []
    lines.append("=== Erkannte Messwert-Signaturen ===")
    lines.append("")
    
    for p in patterns:
        score_pct = p["match_score"] * 100
        bar = _confidence_bar(p["match_score"])
        lines.append(f"{bar} {p['signature_name']} ({score_pct:.0f}% Match)")
        
        if p.get("description"):
            lines.append(f"  {p['description']}")
        if p.get("icd_codes"):
            lines.append(f"  ICD: {p['icd_codes']}")
        
        lines.append(f"  Treffer: {p['matched_count']}/{p['total_components']} Komponenten")
        
        if p["matched_components"]:
            lines.append("  Uebereinstimmende Messwerte:")
            for c in p["matched_components"]:
                lines.append(f"    + {c['measurement_name']} ({c['expected_direction']})")
        
        if p["unmatched_components"]:
            lines.append("  Fehlende/abweichende Messwerte:")
            for c in p["unmatched_components"]:
                lines.append(f"    - {c['measurement_name']}: {c['match_type']}")
        
        lines.append("")
    
    return "\n".join(lines)
