"""Ingestion-Modul: Download und Import biologischer Datenquellen."""

def parse_obo(filepath):
    """Parst eine OBO-Datei und liefert eine Liste von Term-Dicts.
    
    Jeder Term hat: id, name, namespace, def, is_a (Liste), relationship (Liste).
    """
    terms = []
    current = None
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "[Term]":
                if current:
                    terms.append(current)
                current = {"id": "", "name": "", "namespace": "", "def": "",
                           "is_a": [], "relationship": [], "is_obsolete": False}
            elif current is not None:
                if line.startswith("id: "):
                    current["id"] = line[4:]
                elif line.startswith("name: "):
                    current["name"] = line[6:]
                elif line.startswith("namespace: "):
                    current["namespace"] = line[11:]
                elif line.startswith("def: "):
                    current["def"] = line[5:].split('"')[1] if '"' in line else line[5:]
                elif line.startswith("is_a: "):
                    current["is_a"].append(line[6:].split("!")[0].strip())
                elif line.startswith("relationship: "):
                    current["relationship"].append(line[14:])
                elif line == "is_obsolete: true":
                    current["is_obsolete"] = True
        if current:
            terms.append(current)
    return [t for t in terms if not t["is_obsolete"]]
