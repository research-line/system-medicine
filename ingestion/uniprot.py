"""UniProt Swiss-Prot Human -> genes_proteins."""
import csv
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import insert_data_source, add_external_reference


def import_uniprot(conn, filepath: str) -> int:
    """Importiert UniProt-Daten in genes_proteins.
    
    TSV mit Entry, Gene Names, Protein names, Gene Ontology IDs.
    Aktualisiert bestehende Gene (von HGNC) mit UniProt-Accession als external_id,
    oder fuegt neue ein.
    """
    count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            accession = row.get("Entry", "").strip()
            gene_names = row.get("Gene Names", row.get("Gene names", "")).strip()
            protein_name = row.get("Protein names", "").strip()
            
            if not accession or not gene_names:
                continue
            
            # Erstes Gen-Symbol extrahieren (oft space-getrennt)
            symbol = gene_names.split()[0].strip()
            
            # Protein-Name kuerzen
            if protein_name and "(" in protein_name:
                protein_name = protein_name.split("(")[0].strip()
            if len(protein_name) > 200:
                protein_name = protein_name[:200]
            
            # Pruefen ob Gen schon existiert (von HGNC)
            existing = conn.execute(
                "SELECT id FROM genes_proteins WHERE symbol = ?", (symbol,)
            ).fetchone()
            
            if existing:
                gene_id = existing[0]
            else:
                conn.execute(
                    "INSERT OR IGNORE INTO genes_proteins "
                    "(symbol, name, external_id) VALUES (?, ?, ?)",
                    (symbol, protein_name, f"UniProt:{accession}")
                )
                row = conn.execute(
                    "SELECT id FROM genes_proteins WHERE symbol = ?", (symbol,)
                ).fetchone()
                gene_id = row[0] if row else None

            # External Reference fuer Multi-Source-Lookup (BUG-10 Fix):
            # Statt external_id zu ueberschreiben (was HGNC-ID verliert),
            # wird die UniProt-Accession als separate Referenz gespeichert.
            if gene_id:
                add_external_reference(conn, "gene", gene_id, "uniprot",
                                       f"UniProt:{accession}")

            count += 1
            
            if count % 5000 == 0:
                conn.commit()
    
    insert_data_source(conn, "uniprot_human", filepath, "", "", count)
    conn.commit()
    return count
