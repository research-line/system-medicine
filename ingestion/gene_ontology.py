"""Gene Ontology: Biologische Prozesse als Pfad-Ergaenzung."""
import csv
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion import parse_obo
from database import insert_data_source


def import_go_terms(conn, filepath: str) -> int:
    """Importiert GO:BP Terme als ergaenzende Pfade.
    
    Filtert nach namespace 'biological_process'.
    """
    terms = parse_obo(filepath)
    count = 0
    
    for term in terms:
        if term["namespace"] != "biological_process":
            continue
        
        name = term["name"]
        term_id = term["id"]
        description = term.get("def", "")
        
        if not name or not term_id.startswith("GO:"):
            continue
        
        conn.execute(
            "INSERT OR IGNORE INTO functional_pathways "
            "(name, description, external_id) VALUES (?, ?, ?)",
            (name, description[:500] if description else "", term_id)
        )
        count += 1
        
        if count % 2000 == 0:
            conn.commit()
    
    conn.commit()
    insert_data_source(conn, "gene_ontology", filepath, "", "", count)
    return count


def import_go_annotations(conn, filepath: str) -> int:
    """Importiert GO-Annotationen (Gen -> GO:BP Term).
    
    GAF Format: Tab-separiert, !-Kommentare.
    Spalte 2: Gen-Symbol (DB_Object_Symbol)
    Spalte 4: GO-ID
    Spalte 8: Aspect (P=biological_process)
    
    Performance: Lookup-Dicts statt pro-Zeile SQL-Queries.
    """
    count = 0
    
    # Lookup-Dicts im Speicher aufbauen
    gene_lookup = {}  # symbol -> gene_db_id
    for row in conn.execute("SELECT id, symbol FROM genes_proteins").fetchall():
        gene_lookup[row["symbol"]] = row["id"]
    
    pathway_lookup = {}  # go_id -> pathway_db_id
    for row in conn.execute(
        "SELECT id, external_id FROM functional_pathways WHERE external_id LIKE 'GO:%'"
    ).fetchall():
        pathway_lookup[row["external_id"]] = row["id"]
    
    batch = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("!"):
                continue
            
            parts = line.strip().split("\t")
            if len(parts) < 9:
                continue
            
            symbol = parts[2]
            go_id = parts[4]
            aspect = parts[8]
            
            # Nur biological_process
            if aspect != "P":
                continue
            
            gene_id = gene_lookup.get(symbol)
            if not gene_id:
                continue
            
            pathway_id = pathway_lookup.get(go_id)
            if not pathway_id:
                continue
            
            batch.append((gene_id, pathway_id, "annotiert"))
            count += 1
            
            if len(batch) >= 5000:
                conn.executemany(
                    "INSERT OR IGNORE INTO gene_pathways "
                    "(gene_id, pathway_id, relation) VALUES (?, ?, ?)",
                    batch
                )
                conn.commit()
                batch.clear()
    
    if batch:
        conn.executemany(
            "INSERT OR IGNORE INTO gene_pathways "
            "(gene_id, pathway_id, relation) VALUES (?, ?, ?)",
            batch
        )
    conn.commit()
    insert_data_source(conn, "go_annotations", filepath, "", "", count)
    return count
