"""HGNC Gen-ID Normalisierung."""
import csv
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import insert_data_source


def import_hgnc(conn, filepath: str) -> int:
    """Importiert HGNC Gen-Daten: Nur protein-coding genes, Status=Approved.
    
    Erstellt/aktualisiert genes_proteins mit external_id = HGNC:xxx.
    Nutzt INSERT OR IGNORE da Duplikate moeglich.
    """
    count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row.get("status") != "Approved":
                continue
            if row.get("locus_group") != "protein-coding gene":
                continue
            
            symbol = row.get("symbol", "").strip()
            name = row.get("name", "").strip()
            hgnc_id = row.get("hgnc_id", "").strip()
            
            if not symbol:
                continue
            
            conn.execute(
                "INSERT OR IGNORE INTO genes_proteins "
                "(symbol, name, external_id) VALUES (?, ?, ?)",
                (symbol, name, hgnc_id)
            )
            count += 1
            
            # Batch-Commit alle 5000 Zeilen
            if count % 5000 == 0:
                conn.commit()
    
    conn.commit()
    insert_data_source(conn, "hgnc", filepath, "", "", count)
    return count
