"""Cell Ontology -> cell_types."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion import parse_obo
from database import insert_data_source


def import_cell_ontology(conn, filepath: str) -> int:
    """Importiert Cell Ontology in cell_types.
    
    Importiert alle CL-Terme. Lineage wird aus is_a extrahiert.
    """
    terms = parse_obo(filepath)
    count = 0
    
    # Index aufbauen fuer Eltern-Lookup
    id_to_name = {t["id"]: t["name"] for t in terms}
    
    for term in terms:
        name = term["name"]
        term_id = term["id"]
        
        if not name or not term_id.startswith("CL:"):
            continue
        
        # Lineage: erster is_a Parent
        lineage = ""
        if term["is_a"]:
            parent_id = term["is_a"][0]
            lineage = id_to_name.get(parent_id, parent_id)
        
        conn.execute(
            "INSERT OR IGNORE INTO cell_types "
            "(name, lineage, external_id) VALUES (?, ?, ?)",
            (name, lineage, term_id)
        )
        count += 1
        
        if count % 1000 == 0:
            conn.commit()
    
    conn.commit()
    insert_data_source(conn, "cell_ontology", filepath, "", "", count)
    return count
