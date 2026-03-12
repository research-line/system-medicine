"""Konfiguration fuer System-Medizin Prototyp."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "system_medizin.db")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
MANIFEST_PATH = os.path.join(DATA_DIR, "manifest.json")

# Datenquellen
DATA_SOURCES = {
    "reactome_pathways": {
        "url": "https://reactome.org/download/current/ReactomePathways.txt",
        "format": "tsv",
    },
    "reactome_uniprot": {
        "url": "https://reactome.org/download/current/UniProt2Reactome_All_Levels.txt",
        "format": "tsv",
    },
    "gene_ontology": {
        "url": "https://purl.obolibrary.org/obo/go/go-basic.obo",
        "format": "obo",
    },
    "go_annotations": {
        "url": "http://geneontology.org/gene-associations/goa_human.gaf.gz",
        "format": "gaf_gz",
    },
    "uberon": {
        "url": "https://purl.obolibrary.org/obo/uberon/basic.obo",
        "format": "obo",
    },
    "cell_ontology": {
        "url": "https://purl.obolibrary.org/obo/cl/cl-basic.obo",
        "format": "obo",
    },
    "uniprot_human": {
        "url": "https://rest.uniprot.org/uniprotkb/stream?query=(organism_id:9606)+AND+(reviewed:true)&format=tsv&fields=accession,gene_names,protein_name,go_id",
        "format": "tsv",
    },
    "hgnc": {
        "url": "https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt",
        "format": "tsv",
    },
}

# Import-Reihenfolge
IMPORT_ORDER = ["hgnc", "uberon", "cell_ontology", "uniprot_human", "reactome_pathways", "reactome_uniprot", "gene_ontology", "go_annotations"]

# Farben fuer Graph-Visualisierung
NODE_COLORS = {
    "pathway": "#4FC3F7",   # Blau
    "location": "#81C784",  # Gruen
    "cell": "#FFB74D",      # Orange
    "gene": "#E57373",      # Rot
    "measurement": "#BA68C8",  # Lila
    "diagnosis": "#FFD54F",    # Gelb
}

# Pfad-Status Farben
STATUS_COLORS = {
    "intakt": "#4CAF50",
    "gestoert": "#F44336",
    "unbekannt": "#9E9E9E",
}

def ensure_dirs():
    """Erstellt noetige Verzeichnisse."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)
