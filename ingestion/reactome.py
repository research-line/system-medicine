"""Reactome Pathway-Datenbank."""
import csv
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import insert_data_source


def import_reactome_pathways(conn, filepath: str) -> int:
    """Importiert Reactome-Pfade in functional_pathways.
    
    TSV ohne Header: pathway_id, pathway_name, species
    Filtert nach Homo sapiens.
    """
    count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if len(row) < 3:
                continue
            pathway_id, name, species = row[0], row[1], row[2]
            
            if species != "Homo sapiens":
                continue
            
            conn.execute(
                "INSERT OR IGNORE INTO functional_pathways "
                "(name, external_id) VALUES (?, ?)",
                (name, f"Reactome:{pathway_id}")
            )
            count += 1
            
            if count % 1000 == 0:
                conn.commit()
    
    conn.commit()
    insert_data_source(conn, "reactome_pathways", filepath, "", "", count)
    return count


def import_reactome_uniprot(conn, filepath: str) -> int:
    """Importiert UniProt-Reactome Zuordnungen in gene_pathways.
    
    TSV ohne Header: uniprot_id, reactome_id, url, pathway_name, evidence, species
    Filtert nach Homo sapiens. Verknuepft Gene mit Pfaden.
    
    Performance: Lookup-Dicts statt pro-Zeile SQL-Queries.
    """
    count = 0
    
    # Lookup-Dicts im Speicher aufbauen (statt pro Zeile DB-Query)
    gene_lookup = {}  # uniprot_id -> gene_db_id
    for row in conn.execute(
        "SELECT id, external_id FROM genes_proteins WHERE external_id IS NOT NULL"
    ).fetchall():
        ext = row["external_id"]
        if ext and ext.startswith("UniProt:"):
            uid = ext.split(":", 1)[1].split(";")[0].strip()
            gene_lookup[uid] = row["id"]
    
    pathway_lookup = {}  # reactome_id -> pathway_db_id
    for row in conn.execute(
        "SELECT id, external_id FROM functional_pathways WHERE external_id IS NOT NULL"
    ).fetchall():
        ext = row["external_id"]
        if ext and ext.startswith("Reactome:"):
            rid = ext.split(":", 1)[1].strip()
            pathway_lookup[rid] = row["id"]
    
    batch = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if len(row) < 6:
                continue
            
            uniprot_id = row[0]
            reactome_id = row[1]
            species = row[5]
            
            if species != "Homo sapiens":
                continue
            
            gene_id = gene_lookup.get(uniprot_id)
            if not gene_id:
                continue
            
            pathway_id = pathway_lookup.get(reactome_id)
            if not pathway_id:
                continue
            
            batch.append((gene_id, pathway_id, "beteiligt"))
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
    insert_data_source(conn, "reactome_uniprot", filepath, "", "", count)
    return count
