# System-Medizin Prototyp

Funktionspfad-zentrierter medizinischer Knowledge Graph mit Ausschlusslogik.

## Was ist System-Medizin?

System-Medizin modelliert den menschlichen Koerper als Netzwerk von **Funktionspfaden** (biologische Prozesse), die ueber Gene, Proteine, Koerperorte und Messwerte miteinander verknuepft sind. Statt isolierter Symptombetrachtung ermoeglicht der Graph-Ansatz:

- **Ausschlusslogik:** Intakte Pfade beweisen, dass ihre essenziellen Gene funktionieren -- diese Gene koennen als Ursache ausgeschlossen werden.
- **Probabilistische Analyse:** Konfidenzwerte fuer Gen-Ausschluss basierend auf Pfad-Evidenz, Redundanz und Multi-Pfad-Staerkung.
- **Pattern-Detection:** Automatische Erkennung bekannter Messwert-Signaturen (z.B. Haemolyse-Muster).
- **Diagnose-Queries:** Von auffaelligen Messwerten ueber Verdachtspfade zu Kandidatengenen und empfohlenen Zusatztests.

## Installation

```bash
pip install -r requirements.txt
```

## Starten

```bash
python main.py
```

Oder unter Windows: `START.bat` doppelklicken.

Beim ersten Start erscheint ein Setup-Wizard. Ueber "Demo-Daten laden" wird ein Haemolyse-Szenario mit Beispieldaten angelegt.

## Architektur

```
prototype/
  main.py              # Einstiegspunkt
  config.py             # Pfade, Datenquellen, Farben
  database.py           # SQLite-Schema, CRUD-Helpers
  START.bat             # Windows-Starter
  engine/
    exclusion.py        # Binaere + probabilistische Ausschlusslogik
    query.py            # Graph-Traversal, Diagnose-Queries, Pattern-Detection
    reasoning.py        # Menschenlesbare Erklaerungen
  gui/
    app.py              # Hauptfenster (4 Tabs)
    theme.py            # Dark-Theme Stylesheet
    setup_wizard.py     # Erststart-Assistent mit Demo-Daten
    graph_view.py       # NetworkX Graph-Explorer
    exclusion_panel.py  # Ausschluss-Analyse (binaer + probabilistisch)
    data_panel.py       # Diagnose-Query + Daten-Browser
  ingestion/
    manager.py          # Download-Orchestrierung
    downloader.py       # HTTP-Downloads mit Caching
    manifest.py         # Datenquellen-Manifest
    hgnc.py             # HGNC Gen-Nomenklatur Parser
    uberon.py           # Uberon Anatomie-Ontologie Parser
    cell_ontology.py    # Cell Ontology Parser
    uniprot.py          # UniProt Protein-Daten Parser
    reactome.py         # Reactome Pathway-Daten Parser
    gene_ontology.py    # Gene Ontology Parser
    seed_data.py        # Demo-/Seed-Daten (Haemolyse-Szenario)
  data/                 # Laufzeitdaten (DB, Cache) - in .gitignore
```

## Features

| Tab | Funktion |
|-----|----------|
| **Graph-Explorer** | Interaktive Visualisierung des Knowledge Graphs mit NetworkX |
| **Ausschluss-Analyse** | Pfad-Status setzen, binaere + probabilistische Gen-Ausschlussanalyse |
| **Diagnose-Query** | Auffaellige Messwerte eingeben, Verdachtspfade und -gene ermitteln, Pattern-Detection |
| **Daten-Browser** | Alle DB-Tabellen durchsuchen inkl. measurement_signatures |
