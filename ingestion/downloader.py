"""HTTP-Downloader mit Fortschritt und Hash-Verifikation."""
import hashlib
import os
import gzip
import shutil
import time
from typing import Optional, Callable
import requests


def download_file(url: str, dest_path: str, 
                  progress_callback: Optional[Callable] = None,
                  expected_sha256: Optional[str] = None,
                  max_retries: int = 3) -> dict:
    """Laedt eine Datei herunter mit Fortschrittsanzeige.
    
    Args:
        url: Download-URL
        dest_path: Ziel-Dateipfad
        progress_callback: Optional callback(downloaded_bytes, total_bytes)
        expected_sha256: Erwarteter SHA256-Hash zur Verifikation
        max_retries: Maximale Wiederholungsversuche
        
    Returns:
        dict mit path, size, sha256, duration
    """
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    for attempt in range(max_retries):
        try:
            start_time = time.time()
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            total = int(response.headers.get("content-length", 0))
            downloaded = 0
            sha256 = hashlib.sha256()
            
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    sha256.update(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total)
            
            duration = time.time() - start_time
            file_hash = sha256.hexdigest()
            
            if expected_sha256 and file_hash != expected_sha256:
                raise ValueError(
                    f"Hash-Mismatch: erwartet {expected_sha256}, "
                    f"erhalten {file_hash}"
                )
            
            return {
                "path": dest_path,
                "size": downloaded,
                "sha256": file_hash,
                "duration": duration,
            }
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                time.sleep(wait)
            else:
                raise


def decompress_gzip(gz_path: str, dest_path: Optional[str] = None) -> str:
    """Entpackt eine .gz Datei."""
    if dest_path is None:
        dest_path = gz_path.rsplit(".gz", 1)[0]
    with gzip.open(gz_path, "rb") as f_in:
        with open(dest_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    return dest_path


def compute_sha256(filepath: str) -> str:
    """Berechnet SHA256-Hash einer Datei."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()
