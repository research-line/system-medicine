# System-Medizin

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19429347.svg)](https://doi.org/10.5281/zenodo.19429347)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://doc.qt.io/qtforpython/)

A **functional-pathway-centric medical knowledge graph** with exclusion logic for differential diagnosis support.

> **Research tool only.** This is not a clinical decision support system and must not be used for medical decisions.

> **Note on project status:** We are currently unable to actively develop this software and concept further due to time constraints. We would be happy if someone picks this up and are glad to support anyone who does. Feel free to fork, open issues, or reach out.

## What is System-Medizin?

System-Medizin models the human body as a network of **functional pathways** (biological processes) linked through genes, proteins, laboratory values, anatomical locations, cell types, and clinical diagnoses. Instead of isolated symptom matching, the graph-based approach enables:

- **Exclusion Logic:** If a functional pathway is demonstrated intact (via normal lab markers), all genes essential for that pathway can be excluded as primary disease causes.
- **Probabilistic Analysis:** Confidence scores for gene exclusion based on pathway evidence, redundancy, and multi-pathway reinforcement.
- **Pattern Detection:** Automatic recognition of known measurement signatures (e.g., hemolysis, lupus, sepsis, Cushing's).
- **Diagnostic Queries:** From abnormal measurements via suspect pathways to candidate genes and recommended follow-up tests.

## Data Coverage (v0.4)

| Category | Count |
|----------|-------|
| Functional Pathways | 51 |
| Laboratory Parameters | 151 |
| Genes/Proteins | 70 |
| Diagnoses | 68 |
| Measurement Signatures | 42 |
| Body Locations | 28 |
| Cell Types | 25 |
| Graph Edges | 696 |

**Covered domains:** Hematology, Hepatology, Nephrology, Endocrinology (Thyroid, HPA axis, Gonads, PTH), Immunology (Complement, T-cells, NK-cells, IgE/Allergy), Cardiology, Oncology markers, Blood gas analysis, Rheumatology, Hemostasis (incl. Thrombophilia, Fibrinolysis), Pulmonology, Gastroenterology (IBD, Celiac, Pancreatic insufficiency), Infectiology (Hepatitis serology), Autoimmunology (Hashimoto, Graves', PBC, AIH), Urine diagnostics, Neurology markers, Osteology, Copper metabolism, Allergology.

## Getting Started

### Requirements

- Python 3.10+
- Windows / Linux / macOS

### Installation

```bash
git clone https://github.com/um-bruch/system-medicine.git
cd system-medicine
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

On Windows you can also double-click `START.bat`.

On first launch a **Setup Wizard** appears. Click "Load Demo Data" to populate all data panels (hemolysis scenario, clinical lab panels, extended systems).

## Architecture

```
system-medicine/
  main.py              # Entry point
  config.py            # Paths, data sources, colors
  database.py          # SQLite schema, CRUD helpers
  engine/
    exclusion.py       # Binary + probabilistic exclusion logic
    query.py           # Graph traversal, diagnostic queries, pattern detection
    reasoning.py       # Human-readable explanations
  gui/
    app.py             # Main window (4 tabs)
    theme.py           # Dark theme stylesheet
    setup_wizard.py    # First-run wizard with demo data
    graph_view.py      # NetworkX graph explorer
    exclusion_panel.py # Exclusion analysis (binary + probabilistic)
    data_panel.py      # Diagnostic query + data browser
  ingestion/
    manager.py         # Download orchestration
    downloader.py      # HTTP downloads with caching
    manifest.py        # Data source manifest
    hgnc.py            # HGNC gene nomenclature parser
    uberon.py          # Uberon anatomy ontology parser
    cell_ontology.py   # Cell Ontology parser
    uniprot.py         # UniProt protein data parser
    reactome.py        # Reactome pathway data parser
    gene_ontology.py   # Gene Ontology parser
    seed_data.py       # Demo/seed data (hemolysis scenario)
  paper/               # Methodology paper (EN + DE PDFs)
  data/                # Runtime data (DB, cache) -- in .gitignore
```

## Features

| Tab | Function |
|-----|----------|
| **Graph Explorer** | Interactive visualization of the knowledge graph with NetworkX |
| **Exclusion Analysis** | Set pathway status, run binary + probabilistic gene exclusion |
| **Diagnostic Query** | Enter abnormal measurements, identify suspect pathways and genes, pattern detection |
| **Data Browser** | Browse all DB tables including measurement signatures |

## Data Sources

This tool integrates exclusively **public, open-access** biological databases:

- [Reactome](https://reactome.org/) -- Pathway data (CC BY 4.0)
- [Gene Ontology](http://geneontology.org/) -- Biological process annotations (CC BY 4.0)
- [UniProt](https://www.uniprot.org/) -- Protein data (CC BY 4.0)
- [HGNC](https://www.genenames.org/) -- Gene nomenclature (CC0)
- [Uberon](http://uberon.github.io/) -- Anatomy ontology (CC BY 3.0)
- [Cell Ontology](https://obophenotype.github.io/cell-ontology/) -- Cell type ontology (CC BY 4.0)

## Methodology

The formal exclusion model (binary and probabilistic variants), assumptions, limitations, and validation framework are described in the accompanying concept paper:

> Geiger, L. (2026). *Functional Pathway-Centric Medical Knowledge Graph with Exclusion Logic for Rare Disease Differential Diagnosis.* See `paper/` directory.

## Contributing

Contributions are welcome! Areas where help is especially valued:

- **Pathway expansion:** Adding new functional pathways with gene/measurement links
- **OMIM/HPO integration:** Connecting disease-gene associations from OMIM and phenotype data from HPO
- **Benchmark cases:** Curating validated rare-disease cases for systematic evaluation
- **Pathway weight calibration:** Data-driven calibration of exclusion confidence weights

Please open an issue first to discuss larger changes.

## License

MIT License -- see [LICENSE](LICENSE).

## Disclaimer

This software is a **research prototype** for exploring pathway-centric exclusion logic. It is **not validated for clinical use** and must not be used for medical diagnosis or treatment decisions. Always consult qualified healthcare professionals.

> ⚠️ **Rechtlicher Hinweis / Legal Notice**
>
> Dieses Projekt ist **kein Medizinprodukt** im Sinne der MDR (EU) 2017/745 / IVDR (EU) 2017/746. Es ist **nicht klinisch validiert**, **nicht durch BfArM oder eine Benannte Stelle geprüft**, **nicht zertifiziert**. Es verarbeitet Daten ausschließlich zu Forschungs- und Softwareentwicklungszwecken. Eine klinische oder diagnostische Nutzung ist ausdrücklich **nicht** die Zweckbestimmung. Entscheidungen über Diagnose und Therapie bleiben qualifizierten Fachpersonen vorbehalten.
>
> This project is **not a medical device** within the meaning of MDR (EU) 2017/745 / IVDR (EU) 2017/746. It is **not clinically validated**, **not approved by BfArM or any Notified Body**, **not certified**. Data is processed exclusively for research and software development purposes. Clinical or diagnostic use is explicitly **not** the intended purpose. Decisions about diagnosis and therapy remain reserved for qualified professionals.
>
> Unentgeltliche Open-Source-Schenkung (§§ 516 ff. BGB). Haftung auf Vorsatz und grobe Fahrlässigkeit beschränkt (§ 521 BGB). Nutzung auf eigenes Risiko. / Unpaid open-source donation. Liability limited to intent and gross negligence. Use at own risk.
