# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.7.1] - 2026-07-26

### Added
- Added German README documentation (`README_de.md`) and badge link in `README.md`.
- Added GFM LLM callout box (`> [!NOTE]`) to `README.md` and `README_de.md` for AI/LLM discovery.
- Added visual Mermaid architecture flowchart diagram to `README.md` and `README_de.md`.
- Added PEP 621 `pyproject.toml` specification with Pytest configuration (`pythonpath = "."`) for direct test suite discovery.

### Changed
- Updated `llms.txt` and `README.md` Last-checked metadata timestamp (2026-07-26).

## [0.7.0] - 2026-07-11

### Added
- Added a GitHub Actions smoke-test workflow for Python 3.10, 3.11, and 3.12.
- Added in-memory core smoke tests for database schema setup, exclusion logic, probabilistic ranking, and measurement-to-pathway queries.
- Added Unicode character support configuration (`glyphtounicode`) to English and German LaTeX source papers to fix rendering/copying artifacts in compiled PDFs.
- Added `CHANGELOG.md` for project history and release tracking.

### Changed
- Published the June paper-maintenance set as Zenodo v0.7 without a clinical-validation claim.
- Carried forward the evaluation-gate ledger, AI-disclosure hardening, English register maintenance, and German terminology/umlaut cleanup.
- Normalized the Zenodo related repository to `https://github.com/um-bruch/system-medicine`.

## [0.6.0] - 2026-05-10

### Changed
- Updated DOI metadata and badges to reference the Zenodo Concept DOI `10.5281/zenodo.19429347`.
- Enhanced `README.md` and `llms.txt` with structured branding and discovery metadata.

## [0.5.0] - 2026-05-01

### Added
- Added methodology paper LaTeX source and compiled PDF variants (English, German, and Combined).
- Restructured repository layout to separate codebase (`engine/`, `gui/`, `ingestion/`) from publications (`paper/`).

## [0.4.0] - 2026-04-15

### Added
- Expanded biological coverage to 51 functional pathways, 151 laboratory parameters, 70 genes/proteins, and 68 clinical diagnoses.
- Implemented measurement signature detection engine for hematology, hepatology, endocrinology, and pulmonology.

## [0.3.0] - 2026-03-30

### Added
- Implemented probabilistic pathway exclusion logic in `engine/exclusion.py`.
- Added NetworkX graph explorer panel to PySide6 GUI.

## [0.2.0] - 2026-03-10

### Added
- Added public-data ingestion modules for HGNC, Uberon, Cell Ontology, UniProt, and Reactome.
- Designed SQLite database schema and CRUD helpers in `database.py`.

## [0.1.0] - 2026-02-15

### Added
- Initial proof-of-concept release with binary exclusion analysis logic and mock hemolysis dataset.
