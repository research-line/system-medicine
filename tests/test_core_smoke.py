import sqlite3

from database import (
    init_db,
    insert_diagnosis,
    insert_gene,
    insert_measurement,
    insert_pathway,
    link_gene_pathway,
    link_measurement_pathway,
    link_pathway_diagnosis,
)
from engine.exclusion import ExclusionEngine, ProbabilisticExclusionEngine
from engine.query import GraphQuery


def _memory_graph():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    init_db(conn)

    intact = insert_pathway(conn, "Copper transport", status="intakt")
    disturbed = insert_pathway(conn, "Hemolysis response", status="gestoert")
    excluded_gene = insert_gene(conn, "ATP7B", "ATPase copper transporting beta")
    candidate_gene = insert_gene(conn, "HBB", "Hemoglobin subunit beta")

    link_gene_pathway(conn, excluded_gene, intact, is_essential=True)
    link_gene_pathway(conn, candidate_gene, disturbed, is_essential=True)

    bilirubin = insert_measurement(conn, "Bilirubin", unit="mg/dL")
    ldh = insert_measurement(conn, "LDH", unit="U/L")
    anemia = insert_diagnosis(conn, "Hemolytic anemia")
    link_measurement_pathway(conn, bilirubin, disturbed)
    link_measurement_pathway(conn, ldh, disturbed)
    link_pathway_diagnosis(conn, disturbed, anemia)
    conn.commit()
    return conn, intact, disturbed


def test_exclusion_engine_classifies_intact_and_disturbed_pathways():
    conn, _, _ = _memory_graph()

    result = ExclusionEngine(conn).run_exclusion()

    assert result["intact_pathways"] == 1
    assert result["disturbed_pathways"] == 1
    assert {gene["symbol"] for gene in result["excluded_genes"]} == {"ATP7B"}
    assert {gene["symbol"] for gene in result["candidate_genes"]} == {"HBB"}
    assert ExclusionEngine(conn).get_exclusion_for_gene("HBB")["decision"] == "kandidat"


def test_graph_query_keeps_intact_pathways_out_of_measurement_diagnosis():
    conn, _, disturbed = _memory_graph()

    query = GraphQuery(conn)
    result = query.diagnose_from_measurements(
        [{"name": "Bilirubin", "value": 3.1, "direction": "hoch"}],
        intact_pathways=[],
    )

    assert result["suspect_pathways"][0]["pathway_id"] == disturbed
    assert {gene["symbol"] for gene in result["suspect_genes"]} == {"HBB"}
    assert [test["name"] for test in result["suggested_tests"]] == ["LDH"]
    assert query.get_pathways_for_diagnosis("Hemolytic anemia")[0]["id"] == disturbed


def test_probabilistic_engine_produces_ranked_scores():
    conn, _, _ = _memory_graph()

    result = ProbabilisticExclusionEngine(conn).run_probabilistic_exclusion()

    assert result["summary"]["total_analyzed"] == 2
    symbols_by_suspicion = [score["symbol"] for score in result["gene_scores"]]
    assert symbols_by_suspicion[0] == "HBB"
    assert "ATP7B" in {score["symbol"] for score in result["moderate_exclusion"]}
