"""Manifest-Verwaltung: Trackt Download-Status und Versionen."""
import json
import os
from datetime import datetime
from typing import Optional


class Manifest:
    """Verwaltet manifest.json fuer Download-Tracking."""
    
    def __init__(self, manifest_path: str):
        self.path = manifest_path
        self.data = self._load()
    
    def _load(self) -> dict:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"sources": {}, "last_update": None}
    
    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def is_downloaded(self, source_name: str) -> bool:
        return source_name in self.data["sources"]
    
    def get_source_info(self, source_name: str) -> Optional[dict]:
        return self.data["sources"].get(source_name)
    
    def mark_downloaded(self, source_name: str, url: str, 
                       sha256: str, size: int, record_count: int = 0):
        self.data["sources"][source_name] = {
            "url": url,
            "sha256": sha256,
            "size": size,
            "record_count": record_count,
            "downloaded_at": datetime.now().isoformat(),
        }
        self.data["last_update"] = datetime.now().isoformat()
        self.save()
    
    def mark_imported(self, source_name: str, record_count: int):
        if source_name in self.data["sources"]:
            self.data["sources"][source_name]["imported"] = True
            self.data["sources"][source_name]["record_count"] = record_count
            self.data["sources"][source_name]["imported_at"] = datetime.now().isoformat()
            self.save()
    
    def get_all_sources(self) -> dict:
        return self.data["sources"]
    
    def needs_update(self, source_name: str, max_age_days: int = 30) -> bool:
        info = self.get_source_info(source_name)
        if not info:
            return True
        downloaded = datetime.fromisoformat(info["downloaded_at"])
        age = (datetime.now() - downloaded).days
        return age > max_age_days
