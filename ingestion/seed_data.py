"""Seed-Daten: Haemolyse/Milz/Antikoerper-Szenario.

Demonstriert den Knowledge Graph mit klinisch relevantem Beispiel:
- Erythrozyten-Membranintegritaet
- Erythrozyten-Abbau (Haemolyse)
- Milzfiltration
- Fruehe B-Zell-Differenzierung
- Antikoerper-Produktion
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    get_connection, init_db, insert_pathway, insert_location,
    insert_cell_type, insert_gene, insert_measurement, insert_diagnosis,
    link_pathway_location, link_pathway_cell, link_gene_pathway,
    link_measurement_pathway, link_measurement_location,
    link_pathway_diagnosis, link_gene_expression, set_pathway_status,
    insert_signature, link_signature_measurement,
)


def seed_haemolyse(conn):
    """Fuellt die DB mit dem Haemolyse-Szenario."""
    
    # === Funktionspfade ===
    p_membran = insert_pathway(conn, "Erythrozyten-Membranintegritaet",
        description="Strukturelle Stabilitaet der Erythrozyten-Membran",
        output="Stabile bikonkave Erythrozyten",
        time_dimension="chronisch")
    
    p_haemolyse = insert_pathway(conn, "Erythrozyten-Abbau (Haemolyse)",
        description="Physiologischer Abbau gealterter Erythrozyten",
        output="Freies Haemoglobin -> Bilirubin",
        time_dimension="akut")
    
    p_milz = insert_pathway(conn, "Milzfiltration",
        description="Filtration und Qualitaetskontrolle von Blutzellen",
        output="Entfernung defekter Zellen",
        time_dimension="akut")
    
    p_bcell = insert_pathway(conn, "Fruehe B-Zell-Differenzierung",
        description="Reifung von Pro-B zu Pre-B Zellen im Knochenmark",
        output="Funktionale Pre-B-Zellen",
        time_dimension="chronisch")
    
    p_antibody = insert_pathway(conn, "Antikoerper-Produktion",
        description="Sekretion von Immunglobulinen durch Plasmazellen",
        output="IgG, IgM, IgA Antikoerper",
        time_dimension="beide")
    
    # === Koerperorte ===
    l_milz_rp = insert_location(conn, "Milz", "Rote Pulpa",
        circulation_type="offen", immune_role="Filtration")
    l_milz_wp = insert_location(conn, "Milz", "Weisse Pulpa",
        circulation_type="geschlossen", immune_role="B-Zell-Aktivierung")
    l_knochenmark = insert_location(conn, "Knochenmark", "",
        circulation_type="sinusoidal", immune_role="Haematopoese")
    l_blut = insert_location(conn, "Peripheres Blut", "",
        circulation_type="geschlossen", immune_role="Transport")
    l_leber = insert_location(conn, "Leber", "Kupffer-Zellen",
        circulation_type="portal", immune_role="Haemoglobin-Abbau")
    
    # === Zelltypen ===
    c_ery = insert_cell_type(conn, "Erythrozyt",
        lineage="myeloisch", maturation_stage="terminal",
        lifespan="120 Tage", mobility="passiv")
    c_makro = insert_cell_type(conn, "Makrophage",
        lineage="myeloisch", maturation_stage="terminal",
        lifespan="Monate", mobility="resident+mobil")
    c_prob = insert_cell_type(conn, "Pro-B-Zelle",
        lineage="lymphoid", maturation_stage="frueh",
        lifespan="Tage", mobility="resident")
    c_preb = insert_cell_type(conn, "Pre-B-Zelle",
        lineage="lymphoid", maturation_stage="intermediar",
        lifespan="Tage", mobility="resident")
    c_plasma = insert_cell_type(conn, "Plasmazelle",
        lineage="lymphoid", maturation_stage="terminal",
        lifespan="Tage-Jahre", mobility="resident")
    
    # === Gene/Proteine ===
    # Membran-Gene (essentiell fuer Ery-Membran)
    g_ank1 = insert_gene(conn, "ANK1", "Ankyrin-1",
        function_type="strukturell", redundancy_degree="keine")
    g_slc4a1 = insert_gene(conn, "SLC4A1", "Band-3-Protein",
        function_type="strukturell", redundancy_degree="keine")
    g_spta1 = insert_gene(conn, "SPTA1", "Alpha-Spectrin",
        function_type="strukturell", redundancy_degree="niedrig")
    g_sptb = insert_gene(conn, "SPTB", "Beta-Spectrin",
        function_type="strukturell", redundancy_degree="keine")
    g_epb42 = insert_gene(conn, "EPB42", "Protein 4.2",
        function_type="strukturell", redundancy_degree="niedrig")
    
    # Haemolyse-Gene
    g_hp = insert_gene(conn, "HP", "Haptoglobin",
        function_type="metabolisch", redundancy_degree="niedrig")
    g_hmox1 = insert_gene(conn, "HMOX1", "Haemoxygenase-1",
        function_type="metabolisch", redundancy_degree="niedrig")
    
    # B-Zell-Gene (essentiell fuer B-Zell-Diff)
    g_blnk = insert_gene(conn, "BLNK", "B-Zell-Linker-Protein",
        function_type="signal", redundancy_degree="keine")
    g_cd19 = insert_gene(conn, "CD19", "CD19-Antigen",
        function_type="signal", redundancy_degree="keine")
    g_pax5 = insert_gene(conn, "PAX5", "Paired-Box-5",
        function_type="regulatorisch", redundancy_degree="keine")
    
    # Globale Gene (in mehreren Pfaden)
    g_notch2 = insert_gene(conn, "NOTCH2", "Notch-Rezeptor-2",
        function_type="signal", redundancy_degree="niedrig")
    
    # === Messwerte ===
    m_hb = insert_measurement(conn, "Haemoglobin", unit="g/dL",
        ref_range_low=12.0, ref_range_high=16.0, measurement_site="Blut")
    m_hapto = insert_measurement(conn, "Haptoglobin", unit="mg/dL",
        ref_range_low=30.0, ref_range_high=200.0, measurement_site="Blut")
    m_ldh = insert_measurement(conn, "LDH", unit="U/L",
        ref_range_low=120.0, ref_range_high=246.0, measurement_site="Blut")
    m_bili = insert_measurement(conn, "Bilirubin (indirekt)", unit="mg/dL",
        ref_range_low=0.0, ref_range_high=1.0, measurement_site="Blut")
    m_reti = insert_measurement(conn, "Retikulozyten", unit="%",
        ref_range_low=0.5, ref_range_high=2.5, measurement_site="Blut")
    m_igg = insert_measurement(conn, "IgG", unit="mg/dL",
        ref_range_low=700.0, ref_range_high=1600.0, measurement_site="Blut")
    m_bcell = insert_measurement(conn, "B-Zell-Zahl (CD19+)", unit="/uL",
        ref_range_low=100.0, ref_range_high=500.0, measurement_site="Blut")
    
    # === Diagnosen ===
    d_hs = insert_diagnosis(conn, "Hereditaere Sphaerozytose",
        description="Erblicher Defekt der Erythrozyten-Membran",
        icd_code="D58.0")
    d_aiha = insert_diagnosis(conn, "Autoimmunhaemolytische Anaemie",
        description="Antikoerper-vermittelte Erythrozyten-Zerstoerung",
        icd_code="D59.1")
    d_agamma = insert_diagnosis(conn, "Agammaglobulinaemie",
        description="Fehlen von Immunglobulinen",
        icd_code="D80.0")
    
    # === Verknuepfungen ===
    
    # Pfad -> Orte
    link_pathway_location(conn, p_membran, l_blut)
    link_pathway_location(conn, p_membran, l_knochenmark, "entsteht_in")
    link_pathway_location(conn, p_haemolyse, l_milz_rp)
    link_pathway_location(conn, p_haemolyse, l_leber)
    link_pathway_location(conn, p_milz, l_milz_rp)
    link_pathway_location(conn, p_milz, l_milz_wp)
    link_pathway_location(conn, p_bcell, l_knochenmark)
    link_pathway_location(conn, p_antibody, l_milz_wp)
    link_pathway_location(conn, p_antibody, l_knochenmark)
    
    # Pfad -> Zelltypen
    link_pathway_cell(conn, p_membran, c_ery)
    link_pathway_cell(conn, p_haemolyse, c_ery, "Substrat")
    link_pathway_cell(conn, p_haemolyse, c_makro, "Effektor")
    link_pathway_cell(conn, p_milz, c_makro, "Effektor")
    link_pathway_cell(conn, p_bcell, c_prob)
    link_pathway_cell(conn, p_bcell, c_preb)
    link_pathway_cell(conn, p_antibody, c_plasma)
    
    # Gene -> Pfade (mit is_essential)
    link_gene_pathway(conn, g_ank1, p_membran, "strukturell_essentiell", True)
    link_gene_pathway(conn, g_slc4a1, p_membran, "strukturell_essentiell", True)
    link_gene_pathway(conn, g_spta1, p_membran, "strukturell_essentiell", True)
    link_gene_pathway(conn, g_sptb, p_membran, "strukturell_essentiell", True)
    link_gene_pathway(conn, g_epb42, p_membran, "strukturell_essentiell", True)
    link_gene_pathway(conn, g_hp, p_haemolyse, "metabolisch", False)
    link_gene_pathway(conn, g_hmox1, p_haemolyse, "metabolisch", True)
    link_gene_pathway(conn, g_blnk, p_bcell, "signal_essentiell", True)
    link_gene_pathway(conn, g_cd19, p_bcell, "signal_essentiell", True)
    link_gene_pathway(conn, g_pax5, p_bcell, "regulatorisch_essentiell", True)
    link_gene_pathway(conn, g_notch2, p_bcell, "signal", False)
    link_gene_pathway(conn, g_notch2, p_milz, "signal_essentiell", True)
    
    # Messwerte -> Pfade
    link_measurement_pathway(conn, m_hb, p_membran)
    link_measurement_pathway(conn, m_hb, p_haemolyse)
    link_measurement_pathway(conn, m_hapto, p_haemolyse, "sinkt_bei_aktivierung")
    link_measurement_pathway(conn, m_ldh, p_haemolyse, "steigt_bei_aktivierung")
    link_measurement_pathway(conn, m_bili, p_haemolyse, "steigt_bei_aktivierung")
    link_measurement_pathway(conn, m_reti, p_membran, "kompensation")
    link_measurement_pathway(conn, m_igg, p_antibody)
    link_measurement_pathway(conn, m_bcell, p_bcell)
    
    # Messwerte -> Orte
    link_measurement_location(conn, m_hapto, l_leber, "produziert_in")
    link_measurement_location(conn, m_hb, l_blut)
    link_measurement_location(conn, m_bcell, l_blut)
    
    # Pfade -> Diagnosen
    link_pathway_diagnosis(conn, p_membran, d_hs)
    link_pathway_diagnosis(conn, p_haemolyse, d_hs)
    link_pathway_diagnosis(conn, p_haemolyse, d_aiha)
    link_pathway_diagnosis(conn, p_bcell, d_agamma)
    link_pathway_diagnosis(conn, p_antibody, d_agamma)
    
    # Gen-Expression
    link_gene_expression(conn, g_ank1, l_knochenmark, "hoch")
    link_gene_expression(conn, g_slc4a1, l_knochenmark, "hoch")
    link_gene_expression(conn, g_blnk, l_knochenmark, "hoch")
    link_gene_expression(conn, g_notch2, l_milz_wp, "hoch")
    link_gene_expression(conn, g_notch2, l_knochenmark, "mittel")
    link_gene_expression(conn, g_hp, l_leber, "hoch")
    
    # === Messwert-Signaturen ===
    
    # Haemolyse-Signatur
    sig_haemo = insert_signature(conn, "Haemolyse-Signatur",
        description="Klassisches Muster fuer intravaskulaere oder extravaskulaere Haemolyse",
        icd_codes="D55-D59")
    link_signature_measurement(conn, sig_haemo, m_hapto, "niedrig", 1.0)
    link_signature_measurement(conn, sig_haemo, m_ldh, "hoch", 0.8)
    link_signature_measurement(conn, sig_haemo, m_bili, "hoch", 0.7)
    link_signature_measurement(conn, sig_haemo, m_reti, "hoch", 0.6)
    link_signature_measurement(conn, sig_haemo, m_hb, "niedrig", 0.5)
    
    # B-Zell-Defizienz-Signatur
    sig_bcell = insert_signature(conn, "B-Zell-Defizienz-Signatur",
        description="Muster fuer Stoerungen der B-Zell-Entwicklung oder Antikoerper-Produktion",
        icd_codes="D80")
    link_signature_measurement(conn, sig_bcell, m_igg, "niedrig", 1.0)
    link_signature_measurement(conn, sig_bcell, m_bcell, "niedrig", 0.9)
    
    print(f"Seed-Daten geladen: {conn.execute('SELECT COUNT(*) FROM functional_pathways').fetchone()[0]} Pfade, "
          f"{conn.execute('SELECT COUNT(*) FROM genes_proteins').fetchone()[0]} Gene, "
          f"{conn.execute('SELECT COUNT(*) FROM measurements').fetchone()[0]} Messwerte")


if __name__ == "__main__":
    from config import DB_PATH, ensure_dirs
    ensure_dirs()
    conn = get_connection(DB_PATH)
    init_db(conn)
    seed_haemolyse(conn)
    conn.close()
