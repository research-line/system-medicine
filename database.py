"""Datenbank-Schema und CRUD fuer den System-Medizin Knowledge Graph.

Zentrale Entitaeten: Funktionspfade, Koerperorte, Zelltypen,
Gene/Proteine, Messwerte/Tests, Diagnosen.
Kanten bilden biologische Abhaengigkeiten ab.
"""
import sqlite3
import json
import os
from datetime import datetime

from config import DB_PATH


def get_connection(db_path=None, check_same_thread=True):
    conn = sqlite3.connect(db_path or DB_PATH,
                           check_same_thread=check_same_thread)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn):
    """Erstellt alle Tabellen falls nicht vorhanden."""
    conn.executescript("""
    -- Knoten-Tabellen
    CREATE TABLE IF NOT EXISTS functional_pathways (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        output TEXT,
        time_dimension TEXT CHECK(time_dimension IN ('akut','chronisch','beide')),
        status TEXT DEFAULT 'unbekannt'
            CHECK(status IN ('intakt','gestoert','unbekannt')),
        external_id TEXT
    );

    CREATE TABLE IF NOT EXISTS body_locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        organ TEXT NOT NULL,
        subcompartment TEXT,
        circulation_type TEXT,
        immune_role TEXT,
        external_id TEXT,
        UNIQUE(organ, subcompartment)
    );

    CREATE TABLE IF NOT EXISTS cell_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        lineage TEXT,
        maturation_stage TEXT,
        lifespan TEXT,
        mobility TEXT,
        external_id TEXT
    );

    CREATE TABLE IF NOT EXISTS genes_proteins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL UNIQUE,
        name TEXT,
        function_type TEXT CHECK(function_type IN
            ('strukturell','regulatorisch','signal','metabolisch')),
        redundancy_degree TEXT CHECK(redundancy_degree IN
            ('hoch','mittel','niedrig','keine')),
        external_id TEXT
    );

    CREATE TABLE IF NOT EXISTS measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        loinc_code TEXT,
        measurement_site TEXT,
        time_reference TEXT,
        unit TEXT,
        ref_range_low REAL,
        ref_range_high REAL,
        sensitivity TEXT,
        specificity TEXT,
        external_id TEXT
    );

    CREATE TABLE IF NOT EXISTS diagnoses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        icd_code TEXT,
        external_id TEXT
    );

    -- Kanten-Tabellen
    CREATE TABLE IF NOT EXISTS pathway_locations (
        pathway_id INTEGER REFERENCES functional_pathways(id) ON DELETE CASCADE,
        location_id INTEGER REFERENCES body_locations(id) ON DELETE CASCADE,
        relation TEXT DEFAULT 'laeuft_in',
        PRIMARY KEY (pathway_id, location_id)
    );

    CREATE TABLE IF NOT EXISTS pathway_cells (
        pathway_id INTEGER REFERENCES functional_pathways(id) ON DELETE CASCADE,
        cell_type_id INTEGER REFERENCES cell_types(id) ON DELETE CASCADE,
        relation TEXT DEFAULT 'benoetigt',
        PRIMARY KEY (pathway_id, cell_type_id)
    );

    CREATE TABLE IF NOT EXISTS gene_pathways (
        gene_id INTEGER REFERENCES genes_proteins(id) ON DELETE CASCADE,
        pathway_id INTEGER REFERENCES functional_pathways(id) ON DELETE CASCADE,
        relation TEXT DEFAULT 'moduliert',
        is_essential INTEGER DEFAULT 0,
        PRIMARY KEY (gene_id, pathway_id)
    );

    CREATE TABLE IF NOT EXISTS measurement_pathways (
        measurement_id INTEGER REFERENCES measurements(id) ON DELETE CASCADE,
        pathway_id INTEGER REFERENCES functional_pathways(id) ON DELETE CASCADE,
        relation TEXT DEFAULT 'misst_output_von',
        PRIMARY KEY (measurement_id, pathway_id)
    );

    CREATE TABLE IF NOT EXISTS measurement_locations (
        measurement_id INTEGER REFERENCES measurements(id) ON DELETE CASCADE,
        location_id INTEGER REFERENCES body_locations(id) ON DELETE CASCADE,
        relation TEXT DEFAULT 'repraesentiert_aktivitaet_in',
        PRIMARY KEY (measurement_id, location_id)
    );

    CREATE TABLE IF NOT EXISTS pathway_diagnoses (
        pathway_id INTEGER REFERENCES functional_pathways(id) ON DELETE CASCADE,
        diagnosis_id INTEGER REFERENCES diagnoses(id) ON DELETE CASCADE,
        relation TEXT DEFAULT 'stoerung_fuehrt_zu',
        PRIMARY KEY (pathway_id, diagnosis_id)
    );

    CREATE TABLE IF NOT EXISTS gene_expressions (
        gene_id INTEGER REFERENCES genes_proteins(id) ON DELETE CASCADE,
        location_id INTEGER REFERENCES body_locations(id) ON DELETE CASCADE,
        expression_level TEXT DEFAULT 'normal',
        PRIMARY KEY (gene_id, location_id)
    );

    -- Datenquellen-Tracking
    CREATE TABLE IF NOT EXISTS data_sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        url TEXT,
        version TEXT,
        download_date TEXT,
        sha256 TEXT,
        record_count INTEGER DEFAULT 0
    );

    -- Messwert-Signaturen (Pattern-basierte Diagnose)
    CREATE TABLE IF NOT EXISTS measurement_signatures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        icd_codes TEXT
    );

    CREATE TABLE IF NOT EXISTS signature_components (
        signature_id INTEGER REFERENCES measurement_signatures(id) ON DELETE CASCADE,
        measurement_id INTEGER REFERENCES measurements(id) ON DELETE CASCADE,
        expected_direction TEXT CHECK(expected_direction IN ('hoch','niedrig','normal')),
        weight REAL DEFAULT 1.0,
        PRIMARY KEY (signature_id, measurement_id)
    );

    CREATE INDEX IF NOT EXISTS idx_sig_components ON signature_components(signature_id);

    -- Indizes
    CREATE INDEX IF NOT EXISTS idx_pathways_external ON functional_pathways(external_id);
    CREATE INDEX IF NOT EXISTS idx_locations_organ ON body_locations(organ);
    CREATE INDEX IF NOT EXISTS idx_genes_symbol ON genes_proteins(symbol);
    CREATE INDEX IF NOT EXISTS idx_genes_external ON genes_proteins(external_id);
    CREATE INDEX IF NOT EXISTS idx_cells_external ON cell_types(external_id);
    CREATE INDEX IF NOT EXISTS idx_locations_external ON body_locations(external_id);
    CREATE INDEX IF NOT EXISTS idx_measurements_external ON measurements(external_id);
    CREATE INDEX IF NOT EXISTS idx_diagnoses_external ON diagnoses(external_id);
    """)
    conn.commit()


# --- CRUD Helpers ---

def insert_pathway(conn, name, description="", output="",
                   time_dimension="beide", status="unbekannt"):
    conn.execute(
        "INSERT OR IGNORE INTO functional_pathways "
        "(name, description, output, time_dimension, status) VALUES (?,?,?,?,?)",
        (name, description, output, time_dimension, status))
    conn.commit()
    return conn.execute(
        "SELECT id FROM functional_pathways WHERE name=?", (name,)).fetchone()[0]


def insert_location(conn, organ, subcompartment="", circulation_type="",
                    immune_role=""):
    conn.execute(
        "INSERT OR IGNORE INTO body_locations "
        "(organ, subcompartment, circulation_type, immune_role) VALUES (?,?,?,?)",
        (organ, subcompartment, circulation_type, immune_role))
    conn.commit()
    return conn.execute(
        "SELECT id FROM body_locations WHERE organ=? AND subcompartment=?",
        (organ, subcompartment)).fetchone()[0]


def insert_cell_type(conn, name, lineage="", maturation_stage="",
                     lifespan="", mobility=""):
    conn.execute(
        "INSERT OR IGNORE INTO cell_types "
        "(name, lineage, maturation_stage, lifespan, mobility) VALUES (?,?,?,?,?)",
        (name, lineage, maturation_stage, lifespan, mobility))
    conn.commit()
    return conn.execute(
        "SELECT id FROM cell_types WHERE name=?", (name,)).fetchone()[0]


def insert_gene(conn, symbol, name="", function_type="regulatorisch",
                redundancy_degree="mittel"):
    conn.execute(
        "INSERT OR IGNORE INTO genes_proteins "
        "(symbol, name, function_type, redundancy_degree) VALUES (?,?,?,?)",
        (symbol, name, function_type, redundancy_degree))
    conn.commit()
    return conn.execute(
        "SELECT id FROM genes_proteins WHERE symbol=?", (symbol,)).fetchone()[0]


def insert_measurement(conn, name, unit="", ref_range_low=None,
                       ref_range_high=None, loinc_code="",
                       measurement_site="Blut"):
    conn.execute(
        "INSERT OR IGNORE INTO measurements "
        "(name, unit, ref_range_low, ref_range_high, loinc_code, measurement_site) "
        "VALUES (?,?,?,?,?,?)",
        (name, unit, ref_range_low, ref_range_high, loinc_code, measurement_site))
    conn.commit()
    return conn.execute(
        "SELECT id FROM measurements WHERE name=?", (name,)).fetchone()[0]


def insert_diagnosis(conn, name, description="", icd_code=""):
    conn.execute(
        "INSERT OR IGNORE INTO diagnoses "
        "(name, description, icd_code) VALUES (?,?,?)",
        (name, description, icd_code))
    conn.commit()
    return conn.execute(
        "SELECT id FROM diagnoses WHERE name=?", (name,)).fetchone()[0]


# --- Data Source CRUD ---

def insert_data_source(conn, name, url="", version="", sha256="", record_count=0):
    """Registriert eine Datenquelle mit Metadaten."""
    conn.execute(
        "INSERT OR REPLACE INTO data_sources "
        "(name, url, version, download_date, sha256, record_count) VALUES (?,?,?,?,?,?)",
        (name, url, version, datetime.now().isoformat(), sha256, record_count))
    conn.commit()


def get_data_source(conn, name):
    """Liefert Metadaten einer Datenquelle oder None."""
    row = conn.execute(
        "SELECT * FROM data_sources WHERE name=?", (name,)).fetchone()
    return dict(row) if row else None


# --- Signature CRUD ---

def insert_signature(conn, name, description="", icd_codes=""):
    conn.execute(
        "INSERT OR IGNORE INTO measurement_signatures "
        "(name, description, icd_codes) VALUES (?,?,?)",
        (name, description, icd_codes))
    conn.commit()
    return conn.execute(
        "SELECT id FROM measurement_signatures WHERE name=?", (name,)).fetchone()[0]


def link_signature_measurement(conn, signature_id, measurement_id,
                                expected_direction="hoch", weight=1.0):
    conn.execute(
        "INSERT OR IGNORE INTO signature_components VALUES (?,?,?,?)",
        (signature_id, measurement_id, expected_direction, weight))
    conn.commit()


# --- Edge Helpers ---

def link_pathway_location(conn, pathway_id, location_id, relation="laeuft_in"):
    conn.execute(
        "INSERT OR IGNORE INTO pathway_locations VALUES (?,?,?)",
        (pathway_id, location_id, relation))
    conn.commit()


def link_pathway_cell(conn, pathway_id, cell_type_id, relation="benoetigt"):
    conn.execute(
        "INSERT OR IGNORE INTO pathway_cells VALUES (?,?,?)",
        (pathway_id, cell_type_id, relation))
    conn.commit()


def link_gene_pathway(conn, gene_id, pathway_id, relation="moduliert",
                      is_essential=False):
    conn.execute(
        "INSERT OR IGNORE INTO gene_pathways VALUES (?,?,?,?)",
        (gene_id, pathway_id, relation, int(is_essential)))
    conn.commit()


def link_measurement_pathway(conn, measurement_id, pathway_id,
                             relation="misst_output_von"):
    conn.execute(
        "INSERT OR IGNORE INTO measurement_pathways VALUES (?,?,?)",
        (measurement_id, pathway_id, relation))
    conn.commit()


def link_measurement_location(conn, measurement_id, location_id,
                              relation="repraesentiert_aktivitaet_in"):
    conn.execute(
        "INSERT OR IGNORE INTO measurement_locations VALUES (?,?,?)",
        (measurement_id, location_id, relation))
    conn.commit()


def link_pathway_diagnosis(conn, pathway_id, diagnosis_id,
                           relation="stoerung_fuehrt_zu"):
    conn.execute(
        "INSERT OR IGNORE INTO pathway_diagnoses VALUES (?,?,?)",
        (pathway_id, diagnosis_id, relation))
    conn.commit()


def link_gene_expression(conn, gene_id, location_id, level="normal"):
    conn.execute(
        "INSERT OR IGNORE INTO gene_expressions VALUES (?,?,?)",
        (gene_id, location_id, level))
    conn.commit()


def set_pathway_status(conn, pathway_id, status):
    conn.execute(
        "UPDATE functional_pathways SET status=? WHERE id=?",
        (status, pathway_id))
    conn.commit()


def get_all_nodes(conn):
    """Liefert alle Knoten gruppiert nach Typ."""
    result = {}
    for table, label in [
        ("functional_pathways", "pathway"),
        ("body_locations", "location"),
        ("cell_types", "cell"),
        ("genes_proteins", "gene"),
        ("measurements", "measurement"),
        ("diagnoses", "diagnosis"),
    ]:
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        result[label] = [dict(r) for r in rows]
    return result


def get_all_edges(conn):
    """Liefert alle Kanten."""
    edges = []
    edge_tables = [
        ("pathway_locations", "pathway_id", "location_id", "pathway", "location"),
        ("pathway_cells", "pathway_id", "cell_type_id", "pathway", "cell"),
        ("gene_pathways", "gene_id", "pathway_id", "gene", "pathway"),
        ("measurement_pathways", "measurement_id", "pathway_id", "measurement", "pathway"),
        ("measurement_locations", "measurement_id", "location_id", "measurement", "location"),
        ("pathway_diagnoses", "pathway_id", "diagnosis_id", "pathway", "diagnosis"),
        ("gene_expressions", "gene_id", "location_id", "gene", "location"),
    ]
    for table, col_a, col_b, type_a, type_b in edge_tables:
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        for r in rows:
            d = dict(r)
            edges.append({
                "source_type": type_a,
                "source_id": d[col_a],
                "target_type": type_b,
                "target_id": d[col_b],
                "relation": d.get("relation", ""),
                "is_essential": d.get("is_essential", None),
                "table": table,
            })
    return edges
