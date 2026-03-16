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
    
    # Batch-Commit: Alle Inserts/Links oben sind ohne Einzel-Commit,
    # daher hier am Ende des Seed-Batches einmal committen.
    conn.commit()

    print(f"Seed-Daten geladen: {conn.execute('SELECT COUNT(*) FROM functional_pathways').fetchone()[0]} Pfade, "
          f"{conn.execute('SELECT COUNT(*) FROM genes_proteins').fetchone()[0]} Gene, "
          f"{conn.execute('SELECT COUNT(*) FROM measurements').fetchone()[0]} Messwerte")


def seed_clinical_panels(conn):
    """Erweitert die DB mit umfassenden klinischen Laborpanels.

    Deckt ab: Blutbild, Leber, Niere, Elektrolyte, Eisen, Schilddruese,
    Entzuendung, Gerinnung, Lipide, Diabetes, Herz, Pankreas, Vitamine.
    """

    # === Funktionspfade ===
    p_erythro = insert_pathway(conn, "Erythropoese",
        description="Bildung roter Blutkoerperchen im Knochenmark",
        output="Reife Erythrozyten", time_dimension="chronisch")
    p_granulo = insert_pathway(conn, "Granulopoese",
        description="Bildung von Granulozyten",
        output="Reife Granulozyten", time_dimension="chronisch")
    p_thrombo = insert_pathway(conn, "Thrombopoese",
        description="Bildung von Thrombozyten aus Megakaryozyten",
        output="Funktionale Thrombozyten", time_dimension="chronisch")
    p_hepato = insert_pathway(conn, "Hepatozellulaere Integritaet",
        description="Strukturelle und funktionelle Integritaet der Hepatozyten",
        output="Intakte Leberzellfunktion", time_dimension="chronisch")
    p_cholestase = insert_pathway(conn, "Gallensaeure-Metabolismus",
        description="Synthese, Sekretion und enterohepatischer Kreislauf",
        output="Gallefluss und Bilirubin-Konjugation", time_dimension="akut")
    p_albumin = insert_pathway(conn, "Albumin-Synthese",
        description="Hepatische Produktion von Serumalbumin",
        output="Albumin", time_dimension="chronisch")
    p_gerinnung = insert_pathway(conn, "Gerinnungskaskade",
        description="Plasmatische Gerinnung (intrinsisch + extrinsisch)",
        output="Haemostase", time_dimension="akut")
    p_gfr = insert_pathway(conn, "Glomerulaere Filtration",
        description="Filtration des Blutplasmas im Glomerulus",
        output="Primaerharn", time_dimension="chronisch")
    p_tubulus = insert_pathway(conn, "Tubulaere Rueckresorption",
        description="Selektive Rueckresorption von Elektrolyten und Wasser",
        output="Elektrolyt-Homoeoastase", time_dimension="akut")
    p_thyroid = insert_pathway(conn, "Hypothalamus-Hypophysen-Schilddruesen-Achse",
        description="TSH-gesteuerte Schilddruesenhormon-Synthese",
        output="fT3, fT4", time_dimension="chronisch")
    p_eisen = insert_pathway(conn, "Eisenstoffwechsel",
        description="Aufnahme, Transport und Speicherung von Eisen",
        output="Bioverfuegbares Eisen", time_dimension="chronisch")
    p_akutephase = insert_pathway(conn, "Akute-Phase-Reaktion",
        description="Hepatische Synthese von Akute-Phase-Proteinen",
        output="CRP, Fibrinogen", time_dimension="akut")
    p_lipid = insert_pathway(conn, "Lipid-Metabolismus",
        description="Synthese, Transport und Abbau von Lipoproteinen",
        output="LDL, HDL, Triglyzeride", time_dimension="chronisch")
    p_glukose = insert_pathway(conn, "Glukose-Homoeoastase",
        description="Insulin/Glukagon-gesteuerter Blutzuckerspiegel",
        output="Normoglykaemie", time_dimension="beide")
    p_myokard = insert_pathway(conn, "Myokard-Integritaet",
        description="Strukturelle Integritaet des Herzmuskels",
        output="Kontraktile Funktion", time_dimension="akut")
    p_pankreas = insert_pathway(conn, "Pankreatische Exokrine Funktion",
        description="Sekretion von Verdauungsenzymen",
        output="Lipase, Amylase", time_dimension="akut")

    # === Koerperorte ===
    l_leber_hep = insert_location(conn, "Leber", "Hepatozyten",
        circulation_type="portal", immune_role="Metabolismus")
    l_niere_glom = insert_location(conn, "Niere", "Glomerulus",
        circulation_type="kapillaer", immune_role="Filtration")
    l_niere_tub = insert_location(conn, "Niere", "Tubulus",
        circulation_type="kapillaer", immune_role="Rueckresorption")
    l_schilddruese = insert_location(conn, "Schilddruese", "",
        circulation_type="kapillaer", immune_role="Hormonproduktion")
    l_pankreas_endo = insert_location(conn, "Pankreas", "Langerhans-Inseln",
        circulation_type="kapillaer", immune_role="Hormonproduktion")
    l_pankreas_exo = insert_location(conn, "Pankreas", "Exokrin",
        circulation_type="kapillaer", immune_role="Enzymsynthese")
    l_myokard = insert_location(conn, "Myokard", "",
        circulation_type="koronar", immune_role="keine")
    l_gefaess = insert_location(conn, "Gefaessendothel", "",
        circulation_type="systemisch", immune_role="Haemostase")

    # Bestehende Orte referenzieren
    def _get_loc(organ, sub=""):
        r = conn.execute("SELECT id FROM body_locations WHERE organ=? AND subcompartment=?",
                         (organ, sub)).fetchone()
        return r[0] if r else insert_location(conn, organ, sub)
    l_blut = _get_loc("Peripheres Blut")
    l_km = _get_loc("Knochenmark")

    # === Zelltypen ===
    c_hepatozyt = insert_cell_type(conn, "Hepatozyt",
        lineage="endoderm", maturation_stage="terminal", lifespan="200-300 Tage")
    c_thyreozyt = insert_cell_type(conn, "Thyreozyt",
        lineage="endoderm", maturation_stage="terminal", lifespan="Jahre")
    c_betazelle = insert_cell_type(conn, "Beta-Zelle",
        lineage="endoderm", maturation_stage="terminal", lifespan="Jahre")
    c_kardiomyozyt = insert_cell_type(conn, "Kardiomyozyt",
        lineage="mesoderm", maturation_stage="terminal", lifespan="Jahrzehnte")
    c_thrombozyt = insert_cell_type(conn, "Thrombozyt",
        lineage="myeloisch", maturation_stage="terminal", lifespan="8-12 Tage")
    c_neutrophil = insert_cell_type(conn, "Neutrophiler Granulozyt",
        lineage="myeloisch", maturation_stage="terminal", lifespan="Stunden-Tage")
    c_podozyt = insert_cell_type(conn, "Podozyt",
        lineage="mesoderm", maturation_stage="terminal", lifespan="Jahre")

    # === ~65 neue Messwerte ===

    # Blutbild
    m_ery = insert_measurement(conn, "Erythrozyten", unit="/pL",
        ref_range_low=4.0, ref_range_high=5.5, measurement_site="Blut")
    m_leuko = insert_measurement(conn, "Leukozyten", unit="/nL",
        ref_range_low=4.0, ref_range_high=10.0, measurement_site="Blut")
    m_thrombo = insert_measurement(conn, "Thrombozyten", unit="/nL",
        ref_range_low=150.0, ref_range_high=400.0, measurement_site="Blut")
    m_hkt = insert_measurement(conn, "Haematokrit", unit="%",
        ref_range_low=36.0, ref_range_high=48.0, measurement_site="Blut")
    m_mcv = insert_measurement(conn, "MCV", unit="fL",
        ref_range_low=80.0, ref_range_high=96.0, measurement_site="Blut")
    m_mch = insert_measurement(conn, "MCH", unit="pg",
        ref_range_low=27.0, ref_range_high=34.0, measurement_site="Blut")
    m_mchc = insert_measurement(conn, "MCHC", unit="g/dL",
        ref_range_low=32.0, ref_range_high=36.0, measurement_site="Blut")
    m_neutro = insert_measurement(conn, "Neutrophile", unit="%",
        ref_range_low=40.0, ref_range_high=75.0, measurement_site="Blut")
    m_lympho = insert_measurement(conn, "Lymphozyten", unit="%",
        ref_range_low=20.0, ref_range_high=45.0, measurement_site="Blut")
    m_eosino = insert_measurement(conn, "Eosinophile", unit="%",
        ref_range_low=1.0, ref_range_high=5.0, measurement_site="Blut")

    # Leber
    m_alt = insert_measurement(conn, "ALT (GPT)", unit="U/L",
        ref_range_low=0.0, ref_range_high=35.0, measurement_site="Blut")
    m_ast = insert_measurement(conn, "AST (GOT)", unit="U/L",
        ref_range_low=0.0, ref_range_high=35.0, measurement_site="Blut")
    m_ggt = insert_measurement(conn, "GGT", unit="U/L",
        ref_range_low=0.0, ref_range_high=55.0, measurement_site="Blut")
    m_ap = insert_measurement(conn, "Alkalische Phosphatase", unit="U/L",
        ref_range_low=35.0, ref_range_high=105.0, measurement_site="Blut")
    m_albumin = insert_measurement(conn, "Albumin", unit="g/dL",
        ref_range_low=3.5, ref_range_high=5.0, measurement_site="Blut")
    m_bili_dir = insert_measurement(conn, "Bilirubin (direkt)", unit="mg/dL",
        ref_range_low=0.0, ref_range_high=0.3, measurement_site="Blut")
    m_che = insert_measurement(conn, "Cholinesterase", unit="kU/L",
        ref_range_low=5.3, ref_range_high=12.9, measurement_site="Blut")

    # Niere
    m_krea = insert_measurement(conn, "Kreatinin", unit="mg/dL",
        ref_range_low=0.6, ref_range_high=1.2, measurement_site="Blut")
    m_harnstoff = insert_measurement(conn, "Harnstoff", unit="mg/dL",
        ref_range_low=10.0, ref_range_high=50.0, measurement_site="Blut")
    m_gfr_m = insert_measurement(conn, "GFR (geschaetzt)", unit="mL/min",
        ref_range_low=90.0, ref_range_high=120.0, measurement_site="Blut")
    m_harnsaeure = insert_measurement(conn, "Harnsaeure", unit="mg/dL",
        ref_range_low=2.4, ref_range_high=5.7, measurement_site="Blut")
    m_cysc = insert_measurement(conn, "Cystatin C", unit="mg/L",
        ref_range_low=0.53, ref_range_high=0.95, measurement_site="Blut")

    # Elektrolyte
    m_na = insert_measurement(conn, "Natrium", unit="mmol/L",
        ref_range_low=135.0, ref_range_high=145.0, measurement_site="Blut")
    m_k = insert_measurement(conn, "Kalium", unit="mmol/L",
        ref_range_low=3.5, ref_range_high=5.0, measurement_site="Blut")
    m_ca = insert_measurement(conn, "Calcium", unit="mmol/L",
        ref_range_low=2.1, ref_range_high=2.6, measurement_site="Blut")
    m_phos = insert_measurement(conn, "Phosphat", unit="mmol/L",
        ref_range_low=0.81, ref_range_high=1.45, measurement_site="Blut")
    m_mg = insert_measurement(conn, "Magnesium", unit="mmol/L",
        ref_range_low=0.75, ref_range_high=1.05, measurement_site="Blut")
    m_cl = insert_measurement(conn, "Chlorid", unit="mmol/L",
        ref_range_low=96.0, ref_range_high=106.0, measurement_site="Blut")

    # Eisen
    m_eisen = insert_measurement(conn, "Eisen", unit="ug/dL",
        ref_range_low=60.0, ref_range_high=170.0, measurement_site="Blut")
    m_ferritin = insert_measurement(conn, "Ferritin", unit="ng/mL",
        ref_range_low=15.0, ref_range_high=150.0, measurement_site="Blut")
    m_transferrin = insert_measurement(conn, "Transferrin", unit="mg/dL",
        ref_range_low=200.0, ref_range_high=360.0, measurement_site="Blut")
    m_tsat = insert_measurement(conn, "Transferrinsaettigung", unit="%",
        ref_range_low=16.0, ref_range_high=45.0, measurement_site="Blut")

    # Schilddruese
    m_tsh = insert_measurement(conn, "TSH", unit="mIU/L",
        ref_range_low=0.27, ref_range_high=4.2, measurement_site="Blut")
    m_ft3 = insert_measurement(conn, "fT3", unit="pg/mL",
        ref_range_low=2.0, ref_range_high=4.4, measurement_site="Blut")
    m_ft4 = insert_measurement(conn, "fT4", unit="ng/dL",
        ref_range_low=0.93, ref_range_high=1.7, measurement_site="Blut")

    # Entzuendung
    m_crp = insert_measurement(conn, "CRP", unit="mg/L",
        ref_range_low=0.0, ref_range_high=5.0, measurement_site="Blut")
    m_bsg = insert_measurement(conn, "BSG", unit="mm/h",
        ref_range_low=0.0, ref_range_high=20.0, measurement_site="Blut")
    m_pct = insert_measurement(conn, "Procalcitonin", unit="ng/mL",
        ref_range_low=0.0, ref_range_high=0.5, measurement_site="Blut")
    m_il6 = insert_measurement(conn, "IL-6", unit="pg/mL",
        ref_range_low=0.0, ref_range_high=7.0, measurement_site="Blut")

    # Gerinnung
    m_inr = insert_measurement(conn, "Quick/INR", unit="INR",
        ref_range_low=0.85, ref_range_high=1.15, measurement_site="Blut")
    m_ptt = insert_measurement(conn, "PTT", unit="sec",
        ref_range_low=25.0, ref_range_high=38.0, measurement_site="Blut")
    m_ddimer = insert_measurement(conn, "D-Dimere", unit="mg/L",
        ref_range_low=0.0, ref_range_high=0.5, measurement_site="Blut")
    m_fibrinogen = insert_measurement(conn, "Fibrinogen", unit="mg/dL",
        ref_range_low=200.0, ref_range_high=400.0, measurement_site="Blut")

    # Lipide
    m_chol = insert_measurement(conn, "Cholesterin gesamt", unit="mg/dL",
        ref_range_low=0.0, ref_range_high=200.0, measurement_site="Blut")
    m_hdl = insert_measurement(conn, "HDL-Cholesterin", unit="mg/dL",
        ref_range_low=40.0, ref_range_high=60.0, measurement_site="Blut")
    m_ldl = insert_measurement(conn, "LDL-Cholesterin", unit="mg/dL",
        ref_range_low=0.0, ref_range_high=130.0, measurement_site="Blut")
    m_trigly = insert_measurement(conn, "Triglyzeride", unit="mg/dL",
        ref_range_low=0.0, ref_range_high=150.0, measurement_site="Blut")

    # Diabetes
    m_glukose = insert_measurement(conn, "Glukose (nuechtern)", unit="mg/dL",
        ref_range_low=70.0, ref_range_high=100.0, measurement_site="Blut")
    m_hba1c = insert_measurement(conn, "HbA1c", unit="%",
        ref_range_low=4.0, ref_range_high=5.6, measurement_site="Blut")
    m_insulin = insert_measurement(conn, "Insulin", unit="uU/mL",
        ref_range_low=2.6, ref_range_high=24.9, measurement_site="Blut")
    m_cpeptid = insert_measurement(conn, "C-Peptid", unit="ng/mL",
        ref_range_low=1.1, ref_range_high=4.4, measurement_site="Blut")

    # Herzmarker
    m_trop = insert_measurement(conn, "Troponin I", unit="ng/L",
        ref_range_low=0.0, ref_range_high=14.0, measurement_site="Blut")
    m_ck = insert_measurement(conn, "CK", unit="U/L",
        ref_range_low=0.0, ref_range_high=170.0, measurement_site="Blut")
    m_ckmb = insert_measurement(conn, "CK-MB", unit="U/L",
        ref_range_low=0.0, ref_range_high=24.0, measurement_site="Blut")
    m_bnp = insert_measurement(conn, "NT-proBNP", unit="pg/mL",
        ref_range_low=0.0, ref_range_high=125.0, measurement_site="Blut")

    # Pankreas
    m_lipase = insert_measurement(conn, "Lipase", unit="U/L",
        ref_range_low=0.0, ref_range_high=60.0, measurement_site="Blut")
    m_amylase = insert_measurement(conn, "Amylase", unit="U/L",
        ref_range_low=28.0, ref_range_high=100.0, measurement_site="Blut")

    # Vitamine
    m_b12 = insert_measurement(conn, "Vitamin B12", unit="pg/mL",
        ref_range_low=200.0, ref_range_high=900.0, measurement_site="Blut")
    m_folsaeure = insert_measurement(conn, "Folsaeure", unit="ng/mL",
        ref_range_low=3.1, ref_range_high=17.5, measurement_site="Blut")
    m_vitd = insert_measurement(conn, "25-OH-Vitamin D", unit="ng/mL",
        ref_range_low=30.0, ref_range_high=70.0, measurement_site="Blut")

    # Immunglobuline (IgG existiert bereits)
    m_iga = insert_measurement(conn, "IgA", unit="mg/dL",
        ref_range_low=70.0, ref_range_high=400.0, measurement_site="Blut")
    m_igm = insert_measurement(conn, "IgM", unit="mg/dL",
        ref_range_low=40.0, ref_range_high=230.0, measurement_site="Blut")

    # Gesamtprotein
    m_gew = insert_measurement(conn, "Gesamteiweiss", unit="g/dL",
        ref_range_low=6.0, ref_range_high=8.0, measurement_site="Blut")

    # === Diagnosen ===
    d_eisen = insert_diagnosis(conn, "Eisenmangelanaemie",
        description="Anaemie durch Eisenmangel", icd_code="D50.9")
    d_hypo = insert_diagnosis(conn, "Hypothyreose",
        description="Unterfunktion der Schilddruese", icd_code="E03.9")
    d_hyper = insert_diagnosis(conn, "Hyperthyreose",
        description="Ueberfunktion der Schilddruese", icd_code="E05.9")
    d_dm2 = insert_diagnosis(conn, "Diabetes mellitus Typ 2",
        description="Insulinresistenz", icd_code="E11.9")
    d_acs = insert_diagnosis(conn, "Akutes Koronarsyndrom",
        description="Akute Myokardischaemie", icd_code="I21.9")
    d_cni = insert_diagnosis(conn, "Chronische Niereninsuffizienz",
        description="Progrediente GFR-Abnahme", icd_code="N18.9")
    d_hep = insert_diagnosis(conn, "Hepatitis",
        description="Entzuendung der Leber", icd_code="K75.9")
    d_zirrhose = insert_diagnosis(conn, "Leberzirrhose",
        description="Chronischer Leberumbau", icd_code="K74.6")
    d_pankreatitis = insert_diagnosis(conn, "Akute Pankreatitis",
        description="Akute Entzuendung der Bauchspeicheldruese", icd_code="K85.9")
    d_thrombopenie = insert_diagnosis(conn, "Thrombozytopenie",
        description="Verminderte Thrombozyten", icd_code="D69.6")
    d_dic = insert_diagnosis(conn, "Disseminierte intravasale Koagulopathie",
        description="Verbrauchskoagulopathie", icd_code="D65")
    d_dyslipid = insert_diagnosis(conn, "Dyslipidaemie",
        description="Stoerung des Lipidstoffwechsels", icd_code="E78.5")
    d_vitd = insert_diagnosis(conn, "Vitamin-D-Mangel",
        description="25-OH-Vitamin D < 20 ng/mL", icd_code="E55.9")

    # === Pfad <-> Ort ===
    link_pathway_location(conn, p_erythro, l_km)
    link_pathway_location(conn, p_erythro, l_blut, "output_in")
    link_pathway_location(conn, p_granulo, l_km)
    link_pathway_location(conn, p_thrombo, l_km)
    link_pathway_location(conn, p_hepato, l_leber_hep)
    link_pathway_location(conn, p_cholestase, l_leber_hep)
    link_pathway_location(conn, p_albumin, l_leber_hep)
    link_pathway_location(conn, p_gerinnung, l_leber_hep, "synthese_in")
    link_pathway_location(conn, p_gerinnung, l_gefaess, "aktivierung_in")
    link_pathway_location(conn, p_gfr, l_niere_glom)
    link_pathway_location(conn, p_tubulus, l_niere_tub)
    link_pathway_location(conn, p_thyroid, l_schilddruese)
    link_pathway_location(conn, p_eisen, l_leber_hep, "speicherung_in")
    link_pathway_location(conn, p_eisen, l_km, "verbrauch_in")
    link_pathway_location(conn, p_akutephase, l_leber_hep)
    link_pathway_location(conn, p_lipid, l_leber_hep)
    link_pathway_location(conn, p_glukose, l_pankreas_endo)
    link_pathway_location(conn, p_myokard, l_myokard)
    link_pathway_location(conn, p_pankreas, l_pankreas_exo)

    # === Pfad <-> Zelltyp ===
    link_pathway_cell(conn, p_hepato, c_hepatozyt)
    link_pathway_cell(conn, p_cholestase, c_hepatozyt)
    link_pathway_cell(conn, p_albumin, c_hepatozyt)
    link_pathway_cell(conn, p_gerinnung, c_thrombozyt, "Aktivierung")
    link_pathway_cell(conn, p_gfr, c_podozyt)
    link_pathway_cell(conn, p_thyroid, c_thyreozyt)
    link_pathway_cell(conn, p_glukose, c_betazelle)
    link_pathway_cell(conn, p_myokard, c_kardiomyozyt)
    link_pathway_cell(conn, p_thrombo, c_thrombozyt)
    link_pathway_cell(conn, p_granulo, c_neutrophil)
    link_pathway_cell(conn, p_akutephase, c_hepatozyt)

    # === Messwert <-> Pfad ===
    # Blutbild
    link_measurement_pathway(conn, m_ery, p_erythro)
    link_measurement_pathway(conn, m_hkt, p_erythro)
    link_measurement_pathway(conn, m_mcv, p_erythro)
    link_measurement_pathway(conn, m_mch, p_erythro)
    link_measurement_pathway(conn, m_mchc, p_erythro)
    link_measurement_pathway(conn, m_leuko, p_granulo)
    link_measurement_pathway(conn, m_neutro, p_granulo)
    link_measurement_pathway(conn, m_lympho, p_granulo)
    link_measurement_pathway(conn, m_eosino, p_granulo)
    link_measurement_pathway(conn, m_thrombo, p_thrombo)
    # Hb -> Erythropoese + Eisen
    m_hb_r = conn.execute("SELECT id FROM measurements WHERE name='Haemoglobin'").fetchone()
    if m_hb_r:
        link_measurement_pathway(conn, m_hb_r[0], p_erythro)
        link_measurement_pathway(conn, m_hb_r[0], p_eisen, "benoetigt_eisen")
    # Leber
    link_measurement_pathway(conn, m_alt, p_hepato, "steigt_bei_schaedigung")
    link_measurement_pathway(conn, m_ast, p_hepato, "steigt_bei_schaedigung")
    link_measurement_pathway(conn, m_ggt, p_hepato, "steigt_bei_schaedigung")
    link_measurement_pathway(conn, m_ggt, p_cholestase, "steigt_bei_stauung")
    link_measurement_pathway(conn, m_ap, p_cholestase, "steigt_bei_stauung")
    link_measurement_pathway(conn, m_bili_dir, p_cholestase, "steigt_bei_stauung")
    link_measurement_pathway(conn, m_albumin, p_albumin, "sinkt_bei_insuffizienz")
    link_measurement_pathway(conn, m_che, p_hepato, "sinkt_bei_insuffizienz")
    link_measurement_pathway(conn, m_gew, p_albumin)
    # Niere
    link_measurement_pathway(conn, m_krea, p_gfr, "steigt_bei_funktionsverlust")
    link_measurement_pathway(conn, m_harnstoff, p_gfr, "steigt_bei_funktionsverlust")
    link_measurement_pathway(conn, m_gfr_m, p_gfr, "sinkt_bei_funktionsverlust")
    link_measurement_pathway(conn, m_harnsaeure, p_gfr)
    link_measurement_pathway(conn, m_cysc, p_gfr, "steigt_bei_funktionsverlust")
    # Elektrolyte
    for m in [m_na, m_k, m_ca, m_phos, m_mg, m_cl]:
        link_measurement_pathway(conn, m, p_tubulus)
    # Eisen
    link_measurement_pathway(conn, m_eisen, p_eisen)
    link_measurement_pathway(conn, m_ferritin, p_eisen, "speicherparameter")
    link_measurement_pathway(conn, m_transferrin, p_eisen, "transportparameter")
    link_measurement_pathway(conn, m_tsat, p_eisen)
    link_measurement_pathway(conn, m_mcv, p_eisen, "sinkt_bei_eisenmangel")
    link_measurement_pathway(conn, m_mch, p_eisen, "sinkt_bei_eisenmangel")
    # Schilddruese
    link_measurement_pathway(conn, m_tsh, p_thyroid, "regulationsparameter")
    link_measurement_pathway(conn, m_ft3, p_thyroid, "effektorhormon")
    link_measurement_pathway(conn, m_ft4, p_thyroid, "effektorhormon")
    # Entzuendung
    link_measurement_pathway(conn, m_crp, p_akutephase, "steigt_bei_aktivierung")
    link_measurement_pathway(conn, m_bsg, p_akutephase, "steigt_bei_aktivierung")
    link_measurement_pathway(conn, m_pct, p_akutephase, "steigt_bei_bakteriell")
    link_measurement_pathway(conn, m_il6, p_akutephase, "zytokin_trigger")
    link_measurement_pathway(conn, m_fibrinogen, p_akutephase, "steigt_bei_aktivierung")
    # Gerinnung
    link_measurement_pathway(conn, m_inr, p_gerinnung, "extrinsisch")
    link_measurement_pathway(conn, m_ptt, p_gerinnung, "intrinsisch")
    link_measurement_pathway(conn, m_ddimer, p_gerinnung, "fibrinolyse_marker")
    link_measurement_pathway(conn, m_fibrinogen, p_gerinnung, "substrat")
    link_measurement_pathway(conn, m_thrombo, p_gerinnung, "zellulaere_haemostase")
    # Lipide
    link_measurement_pathway(conn, m_chol, p_lipid)
    link_measurement_pathway(conn, m_hdl, p_lipid, "protektiv")
    link_measurement_pathway(conn, m_ldl, p_lipid, "atherogen")
    link_measurement_pathway(conn, m_trigly, p_lipid)
    # Diabetes
    link_measurement_pathway(conn, m_glukose, p_glukose)
    link_measurement_pathway(conn, m_hba1c, p_glukose, "langzeitparameter")
    link_measurement_pathway(conn, m_insulin, p_glukose, "regulationshormon")
    link_measurement_pathway(conn, m_cpeptid, p_glukose, "sekretionsmarker")
    # Herz
    link_measurement_pathway(conn, m_trop, p_myokard, "steigt_bei_nekrose")
    link_measurement_pathway(conn, m_ck, p_myokard, "steigt_bei_schaedigung")
    link_measurement_pathway(conn, m_ckmb, p_myokard, "herzspezifisch")
    link_measurement_pathway(conn, m_bnp, p_myokard, "steigt_bei_herzinsuffizienz")
    # Pankreas
    link_measurement_pathway(conn, m_lipase, p_pankreas, "steigt_bei_entzuendung")
    link_measurement_pathway(conn, m_amylase, p_pankreas, "steigt_bei_entzuendung")
    # Vitamine -> Erythropoese
    link_measurement_pathway(conn, m_b12, p_erythro, "cofaktor")
    link_measurement_pathway(conn, m_folsaeure, p_erythro, "cofaktor")
    link_measurement_pathway(conn, m_vitd, p_tubulus, "calcium_regulation")
    # Ig -> bestehenden Antikoerper-Pfad
    p_ab_r = conn.execute(
        "SELECT id FROM functional_pathways WHERE name='Antikoerper-Produktion'").fetchone()
    if p_ab_r:
        link_measurement_pathway(conn, m_iga, p_ab_r[0])
        link_measurement_pathway(conn, m_igm, p_ab_r[0])

    # === Pfad <-> Diagnose ===
    link_pathway_diagnosis(conn, p_eisen, d_eisen)
    link_pathway_diagnosis(conn, p_erythro, d_eisen)
    link_pathway_diagnosis(conn, p_thyroid, d_hypo)
    link_pathway_diagnosis(conn, p_thyroid, d_hyper)
    link_pathway_diagnosis(conn, p_glukose, d_dm2)
    link_pathway_diagnosis(conn, p_myokard, d_acs)
    link_pathway_diagnosis(conn, p_gfr, d_cni)
    link_pathway_diagnosis(conn, p_tubulus, d_cni)
    link_pathway_diagnosis(conn, p_hepato, d_hep)
    link_pathway_diagnosis(conn, p_hepato, d_zirrhose)
    link_pathway_diagnosis(conn, p_albumin, d_zirrhose)
    link_pathway_diagnosis(conn, p_gerinnung, d_zirrhose)
    link_pathway_diagnosis(conn, p_cholestase, d_zirrhose)
    link_pathway_diagnosis(conn, p_pankreas, d_pankreatitis)
    link_pathway_diagnosis(conn, p_thrombo, d_thrombopenie)
    link_pathway_diagnosis(conn, p_gerinnung, d_dic)
    link_pathway_diagnosis(conn, p_thrombo, d_dic)
    link_pathway_diagnosis(conn, p_lipid, d_dyslipid)

    # === Signaturen ===
    sig_leber = insert_signature(conn, "Leberzellschaden-Signatur",
        description="Hepatozellulaere Schaedigung", icd_codes="K70-K77")
    link_signature_measurement(conn, sig_leber, m_alt, "hoch", 1.0)
    link_signature_measurement(conn, sig_leber, m_ast, "hoch", 0.9)
    link_signature_measurement(conn, sig_leber, m_ggt, "hoch", 0.7)
    link_signature_measurement(conn, sig_leber, m_bili_dir, "hoch", 0.6)
    link_signature_measurement(conn, sig_leber, m_albumin, "niedrig", 0.5)
    link_signature_measurement(conn, sig_leber, m_che, "niedrig", 0.5)

    sig_chole = insert_signature(conn, "Cholestase-Signatur",
        description="Gallenstauung", icd_codes="K80-K83")
    link_signature_measurement(conn, sig_chole, m_ggt, "hoch", 1.0)
    link_signature_measurement(conn, sig_chole, m_ap, "hoch", 0.9)
    link_signature_measurement(conn, sig_chole, m_bili_dir, "hoch", 0.8)
    link_signature_measurement(conn, sig_chole, m_alt, "hoch", 0.4)

    sig_niere = insert_signature(conn, "Niereninsuffizienz-Signatur",
        description="Nierenfunktionsstoerung", icd_codes="N17-N19")
    link_signature_measurement(conn, sig_niere, m_krea, "hoch", 1.0)
    link_signature_measurement(conn, sig_niere, m_harnstoff, "hoch", 0.8)
    link_signature_measurement(conn, sig_niere, m_gfr_m, "niedrig", 0.9)
    link_signature_measurement(conn, sig_niere, m_k, "hoch", 0.6)
    link_signature_measurement(conn, sig_niere, m_phos, "hoch", 0.5)
    link_signature_measurement(conn, sig_niere, m_ca, "niedrig", 0.4)

    sig_hypo = insert_signature(conn, "Hypothyreose-Signatur",
        description="Schilddruesenunterfunktion", icd_codes="E03")
    link_signature_measurement(conn, sig_hypo, m_tsh, "hoch", 1.0)
    link_signature_measurement(conn, sig_hypo, m_ft4, "niedrig", 0.9)
    link_signature_measurement(conn, sig_hypo, m_ft3, "niedrig", 0.7)
    link_signature_measurement(conn, sig_hypo, m_chol, "hoch", 0.4)

    sig_eisen = insert_signature(conn, "Eisenmangel-Signatur",
        description="Eisenmangelanaemie", icd_codes="D50")
    link_signature_measurement(conn, sig_eisen, m_ferritin, "niedrig", 1.0)
    link_signature_measurement(conn, sig_eisen, m_eisen, "niedrig", 0.9)
    link_signature_measurement(conn, sig_eisen, m_transferrin, "hoch", 0.7)
    link_signature_measurement(conn, sig_eisen, m_tsat, "niedrig", 0.8)
    link_signature_measurement(conn, sig_eisen, m_mcv, "niedrig", 0.6)
    link_signature_measurement(conn, sig_eisen, m_mch, "niedrig", 0.5)
    if m_hb_r:
        link_signature_measurement(conn, sig_eisen, m_hb_r[0], "niedrig", 0.5)

    sig_inflam = insert_signature(conn, "Akute-Entzuendung-Signatur",
        description="Akute Entzuendungsreaktion", icd_codes="R65")
    link_signature_measurement(conn, sig_inflam, m_crp, "hoch", 1.0)
    link_signature_measurement(conn, sig_inflam, m_leuko, "hoch", 0.8)
    link_signature_measurement(conn, sig_inflam, m_neutro, "hoch", 0.7)
    link_signature_measurement(conn, sig_inflam, m_pct, "hoch", 0.9)
    link_signature_measurement(conn, sig_inflam, m_bsg, "hoch", 0.6)

    sig_acs = insert_signature(conn, "ACS-Signatur",
        description="Akutes Koronarsyndrom", icd_codes="I21")
    link_signature_measurement(conn, sig_acs, m_trop, "hoch", 1.0)
    link_signature_measurement(conn, sig_acs, m_ck, "hoch", 0.7)
    link_signature_measurement(conn, sig_acs, m_ckmb, "hoch", 0.8)
    link_signature_measurement(conn, sig_acs, m_bnp, "hoch", 0.5)

    sig_dm = insert_signature(conn, "Diabetes-Signatur",
        description="Diabetes mellitus", icd_codes="E11")
    link_signature_measurement(conn, sig_dm, m_glukose, "hoch", 1.0)
    link_signature_measurement(conn, sig_dm, m_hba1c, "hoch", 0.9)

    sig_dic = insert_signature(conn, "DIC-Signatur",
        description="Verbrauchskoagulopathie", icd_codes="D65")
    link_signature_measurement(conn, sig_dic, m_ddimer, "hoch", 1.0)
    link_signature_measurement(conn, sig_dic, m_fibrinogen, "niedrig", 0.8)
    link_signature_measurement(conn, sig_dic, m_thrombo, "niedrig", 0.9)
    link_signature_measurement(conn, sig_dic, m_ptt, "hoch", 0.7)
    link_signature_measurement(conn, sig_dic, m_inr, "hoch", 0.6)

    conn.commit()
    n = lambda t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"Klinische Panels geladen: {n('functional_pathways')} Pfade, "
          f"{n('measurements')} Messwerte, {n('diagnoses')} Diagnosen, "
          f"{n('measurement_signatures')} Signaturen")


if __name__ == "__main__":
    from config import DB_PATH, ensure_dirs
    ensure_dirs()
    conn = get_connection(DB_PATH)
    init_db(conn)
    seed_haemolyse(conn)
    seed_clinical_panels(conn)
    conn.close()
