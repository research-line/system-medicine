"""Uberon Anatomie-Ontologie -> body_locations."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion import parse_obo
from database import insert_data_source


# Relevante Top-Level Uberon-Klassen fuer medizinische Relevanz
RELEVANT_NAMESPACES = {"uberon"}
# Nur Organe und grosse anatomische Strukturen, nicht jedes Gewebe
ORGAN_KEYWORDS = [
    "organ", "gland", "liver", "kidney", "spleen", "heart", "lung",
    "brain", "bone marrow", "thymus", "lymph node", "intestin",
    "stomach", "pancreas", "blood", "skin", "muscle", "nerve",
    "adrenal", "thyroid", "ovary", "testis", "uterus", "prostate",
    "bladder", "trachea", "esophagus", "colon", "appendix",
]


def import_uberon(conn, filepath: str) -> int:
    """Importiert Uberon-Terme in body_locations.
    
    Filtert nach medizinisch relevanten anatomischen Strukturen.
    Nur Terme mit 'organ' im is_a oder Name-Keywords.
    """
    terms = parse_obo(filepath)
    count = 0
    
    for term in terms:
        name = term["name"]
        term_id = term["id"]
        
        if not name or not term_id.startswith("UBERON:"):
            continue
        
        # Filter: nur relevante Strukturen
        name_lower = name.lower()
        is_relevant = any(kw in name_lower for kw in ORGAN_KEYWORDS)
        
        # Auch Terme die 'organ' in is_a haben
        if not is_relevant:
            for parent in term["is_a"]:
                if "organ" in parent.lower():
                    is_relevant = True
                    break
        
        if not is_relevant:
            continue
        
        # Organ = Name, Subcompartment aus Relationship extrahieren
        conn.execute(
            "INSERT OR IGNORE INTO body_locations "
            "(organ, subcompartment, external_id) VALUES (?, '', ?)",
            (name, term_id)
        )
        count += 1
        
        if count % 1000 == 0:
            conn.commit()
    
    conn.commit()
    insert_data_source(conn, "uberon", filepath, "", "", count)
    return count
