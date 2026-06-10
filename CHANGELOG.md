# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Added Unicode character support configuration (`glyphtounicode`) to English and German LaTeX source papers to fix rendering/copying artifacts in compiled PDFs.
- Added `CHANGELOG.md` for project history and release tracking.

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
