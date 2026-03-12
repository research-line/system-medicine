"""Ingestion-Manager: Orchestriert Downloads und Imports."""
import os
import sys
from typing import Optional, Callable, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_SOURCES, CACHE_DIR, MANIFEST_PATH, IMPORT_ORDER
from ingestion.downloader import download_file, decompress_gzip
from ingestion.manifest import Manifest


class IngestionManager:
    """Orchestriert den Download und Import aller Datenquellen."""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        self.manifest = Manifest(MANIFEST_PATH)
        self.progress_callback = progress_callback
        self._importers = {}
        self._register_importers()
    
    def _register_importers(self):
        """Registriert alle verfuegbaren Import-Funktionen."""
        from ingestion.hgnc import import_hgnc
        from ingestion.uberon import import_uberon
        from ingestion.cell_ontology import import_cell_ontology
        from ingestion.uniprot import import_uniprot
        from ingestion.reactome import import_reactome_pathways, import_reactome_uniprot
        from ingestion.gene_ontology import import_go_terms, import_go_annotations
        
        self._importers = {
            "hgnc": import_hgnc,
            "uberon": import_uberon,
            "cell_ontology": import_cell_ontology,
            "uniprot_human": import_uniprot,
            "reactome_pathways": import_reactome_pathways,
            "reactome_uniprot": import_reactome_uniprot,
            "gene_ontology": import_go_terms,
            "go_annotations": import_go_annotations,
        }
    
    def get_status(self) -> dict:
        """Liefert Status aller Datenquellen."""
        status = {}
        for name in DATA_SOURCES:
            info = self.manifest.get_source_info(name)
            if info:
                status[name] = {
                    "downloaded": True,
                    "imported": info.get("imported", False),
                    "record_count": info.get("record_count", 0),
                    "date": info.get("downloaded_at", ""),
                }
            else:
                status[name] = {"downloaded": False, "imported": False}
        return status
    
    def download_source(self, name: str) -> dict:
        """Laedt eine einzelne Datenquelle herunter."""
        if name not in DATA_SOURCES:
            raise ValueError(f"Unbekannte Datenquelle: {name}")
        
        source = DATA_SOURCES[name]
        url = source["url"]
        filename = url.split("/")[-1].split("?")[0] or f"{name}.dat"
        dest = os.path.join(CACHE_DIR, filename)
        
        result = download_file(url, dest, self.progress_callback)
        
        # Entpacken falls gz
        if source["format"] == "gaf_gz" or filename.endswith(".gz"):
            result["path"] = decompress_gzip(dest)
        
        self.manifest.mark_downloaded(
            name, url, result["sha256"], result["size"]
        )
        return result
    
    def download_all(self) -> List[dict]:
        """Laedt alle fehlenden Datenquellen herunter."""
        results = []
        for name in IMPORT_ORDER:
            if not self.manifest.is_downloaded(name):
                try:
                    result = self.download_source(name)
                    results.append({"name": name, "status": "ok", **result})
                except Exception as e:
                    results.append({"name": name, "status": "error", "error": str(e)})
        return results
    
    def get_cached_path(self, name: str) -> Optional[str]:
        """Liefert den Cache-Pfad einer heruntergeladenen Quelle."""
        source = DATA_SOURCES.get(name)
        if not source:
            return None
        url = source["url"]
        filename = url.split("/")[-1].split("?")[0] or f"{name}.dat"
        path = os.path.join(CACHE_DIR, filename)
        # Fuer gz-Dateien den entpackten Pfad
        if source["format"] == "gaf_gz" or filename.endswith(".gz"):
            path = path.rsplit(".gz", 1)[0]
        if os.path.exists(path):
            return path
        # Fallback: gz-Version
        gz_path = path + ".gz"
        if os.path.exists(gz_path):
            return gz_path
        return None
    
    def import_source(self, name: str, conn) -> int:
        """Importiert eine heruntergeladene Quelle in die DB."""
        if name not in self._importers:
            raise NotImplementedError(
                f"Importer fuer '{name}' noch nicht implementiert"
            )
        filepath = self.get_cached_path(name)
        if not filepath:
            raise FileNotFoundError(f"Cache-Datei fuer '{name}' nicht gefunden")
        count = self._importers[name](conn, filepath)
        self.manifest.mark_imported(name, count)
        return count
    
    def import_all(self, conn) -> dict:
        """Importiert alle heruntergeladenen Quellen in der richtigen Reihenfolge."""
        results = {}
        for name in IMPORT_ORDER:
            info = self.manifest.get_source_info(name)
            if info and not info.get("imported"):
                try:
                    count = self.import_source(name, conn)
                    results[name] = {"status": "ok", "count": count}
                except NotImplementedError as e:
                    results[name] = {"status": "skipped", "reason": str(e)}
                except Exception as e:
                    results[name] = {"status": "error", "error": str(e)}
        return results
    
    def register_importer(self, name: str, func: Callable):
        """Registriert eine Import-Funktion fuer eine Datenquelle."""
        self._importers[name] = func
