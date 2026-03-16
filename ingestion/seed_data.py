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


def seed_expanded_systems(conn):
    """Erweitert die DB mit zusaetzlichen medizinischen Systemen.

    Neue Bereiche: Immunologie, Endokrinologie erweitert, Onkologie-Marker,
    Blutgasanalyse, Rheumatologie, Haemostase erweitert, Infektiologie,
    Nephrologie erweitert, Pneumologie, Neurologie-Marker.
    """

    # === Hilfsfunktion: bestehende Entitaet nachschlagen ===
    def _get_loc(organ, sub=""):
        r = conn.execute("SELECT id FROM body_locations WHERE organ=? AND subcompartment=?",
                         (organ, sub)).fetchone()
        return r[0] if r else insert_location(conn, organ, sub)

    def _get_meas(name):
        r = conn.execute("SELECT id FROM measurements WHERE name=?", (name,)).fetchone()
        return r[0] if r else None

    def _get_pathway(name):
        r = conn.execute("SELECT id FROM functional_pathways WHERE name=?", (name,)).fetchone()
        return r[0] if r else None

    # Bestehende Orte referenzieren
    l_blut = _get_loc("Peripheres Blut")
    l_km = _get_loc("Knochenmark")
    l_leber_hep = _get_loc("Leber", "Hepatozyten")
    l_niere_glom = _get_loc("Niere", "Glomerulus")
    l_niere_tub = _get_loc("Niere", "Tubulus")

    # === Neue Koerperorte ===
    l_nebenniere = insert_location(conn, "Nebenniere", "Rinde",
        circulation_type="kapillaer", immune_role="Hormonproduktion")
    l_hypophyse = insert_location(conn, "Hypophyse", "",
        circulation_type="portal", immune_role="Hormonregulation")
    l_lunge_alv = insert_location(conn, "Lunge", "Alveolen",
        circulation_type="kapillaer", immune_role="Gasaustausch")
    l_gelenk = insert_location(conn, "Gelenk", "Synovia",
        circulation_type="kapillaer", immune_role="keine")
    l_thymus = insert_location(conn, "Thymus", "",
        circulation_type="kapillaer", immune_role="T-Zell-Reifung")
    l_darm = insert_location(conn, "Duenndarm", "Mukosa",
        circulation_type="mesenterial", immune_role="Absorption")
    l_gefaess = _get_loc("Gefaessendothel")
    l_milz_wp = _get_loc("Milz", "Weisse Pulpa")
    l_hypothalamus = insert_location(conn, "Hypothalamus", "",
        circulation_type="portal", immune_role="Neuroendokrin")
    l_prostata = insert_location(conn, "Prostata", "",
        circulation_type="kapillaer", immune_role="keine")
    l_kolon = insert_location(conn, "Kolon", "Mukosa",
        circulation_type="mesenterial", immune_role="Barriere")

    # === Neue Zelltypen ===
    c_tlymph = insert_cell_type(conn, "T-Lymphozyt",
        lineage="lymphoid", maturation_stage="terminal",
        lifespan="Wochen-Jahre", mobility="mobil")
    c_nk = insert_cell_type(conn, "NK-Zelle",
        lineage="lymphoid", maturation_stage="terminal",
        lifespan="Wochen", mobility="mobil")
    c_nnr = insert_cell_type(conn, "Nebennierenrindenzelle",
        lineage="mesoderm", maturation_stage="terminal",
        lifespan="Jahre", mobility="resident")
    c_alveo2 = insert_cell_type(conn, "Alveolarzelle Typ II",
        lineage="endoderm", maturation_stage="terminal",
        lifespan="Monate", mobility="resident")
    c_osteoblast = insert_cell_type(conn, "Osteoblast",
        lineage="mesoderm", maturation_stage="intermediar",
        lifespan="Monate", mobility="resident")
    c_osteoklast = insert_cell_type(conn, "Osteoklast",
        lineage="myeloisch", maturation_stage="terminal",
        lifespan="Wochen", mobility="resident")
    c_dendritisch = insert_cell_type(conn, "Dendritische Zelle",
        lineage="myeloisch", maturation_stage="terminal",
        lifespan="Tage-Wochen", mobility="mobil")
    c_enterozyt = insert_cell_type(conn, "Enterozyt",
        lineage="endoderm", maturation_stage="terminal",
        lifespan="3-5 Tage", mobility="resident")
    c_gonadotroph = insert_cell_type(conn, "Gonadotrophe Zelle",
        lineage="endoderm", maturation_stage="terminal",
        lifespan="Jahre", mobility="resident")

    # === Neue Funktionspfade (15) ===
    p_komplement = insert_pathway(conn, "Komplement-Kaskade",
        description="Klassischer, alternativer und Lektin-Weg der Komplementaktivierung",
        output="Membranangriffskomplex (MAC), Opsonisierung",
        time_dimension="akut")
    p_tcell = insert_pathway(conn, "T-Zell-Immunantwort",
        description="Aktivierung und Differenzierung von T-Lymphozyten",
        output="Zytotoxische T-Zellen, T-Helfer-Zellen",
        time_dimension="beide")
    p_nkcell = insert_pathway(conn, "NK-Zell-Aktivierung",
        description="Erkennung und Lyse virusinfizierter/tumoroeser Zellen",
        output="Perforin/Granzym-vermittelte Zelllyse",
        time_dimension="akut")
    p_hpa = insert_pathway(conn, "Hypothalamus-Hypophysen-Nebennieren-Achse",
        description="CRH/ACTH-gesteuerte Cortisol-Synthese",
        output="Cortisol",
        time_dimension="beide")
    p_gonadal = insert_pathway(conn, "Gonadotrope Achse",
        description="GnRH/FSH/LH-gesteuerte Gonadenfunktion",
        output="Testosteron, Estradiol",
        time_dimension="chronisch")
    p_pth = insert_pathway(conn, "Calcium-Phosphat-Homoeoastase",
        description="PTH-gesteuerte Calcium/Phosphat-Regulation",
        output="Calcium-Spiegel, Knochenmineralisation",
        time_dimension="chronisch")
    p_haem = insert_pathway(conn, "Haem-Biosynthese",
        description="Achtstufige Synthese von Haem aus Glycin und Succinyl-CoA",
        output="Haem (Protoporphyrin IX + Fe2+)",
        time_dimension="chronisch")
    p_purin = insert_pathway(conn, "Purin-Metabolismus",
        description="Synthese und Abbau von Purin-Nukleotiden zu Harnsaeure",
        output="Harnsaeure",
        time_dimension="chronisch")
    p_dnarep = insert_pathway(conn, "DNA-Reparatur",
        description="Mismatch-Repair, Nukleotid-Exzision, Doppelstrangbruch-Reparatur",
        output="Genomische Integritaet",
        time_dimension="chronisch")
    p_apoptose = insert_pathway(conn, "Apoptose-Regulation",
        description="Intrinsischer und extrinsischer Apoptose-Weg",
        output="Programmierter Zelltod",
        time_dimension="akut")
    p_raas = insert_pathway(conn, "Renin-Angiotensin-Aldosteron-System",
        description="Blutdruck- und Volumenregulation",
        output="Angiotensin II, Aldosteron",
        time_dimension="beide")
    p_surfactant = insert_pathway(conn, "Surfactant-Produktion",
        description="Synthese von pulmonalem Surfactant",
        output="Surfactant-Phospholipide, SP-A/B/C/D",
        time_dimension="chronisch")
    p_b12abs = insert_pathway(conn, "Vitamin-B12-Absorption",
        description="Intrinsic-Factor-abhaengige Aufnahme im Ileum",
        output="Bioverfuegbares Cobalamin",
        time_dimension="chronisch")
    p_vwf = insert_pathway(conn, "Primaere Haemostase",
        description="Thrombozytenadhäsion und -aggregation via vWF/GPIb",
        output="Plättchenthrombus",
        time_dimension="akut")
    p_ifn = insert_pathway(conn, "Interferon-Signalweg",
        description="Typ-I/II/III Interferon-Produktion und -Signalisierung",
        output="Antiviraler Zustand",
        time_dimension="akut")

    # === Neue Gene/Proteine (30+) ===

    # Komplement
    g_c3 = insert_gene(conn, "C3", "Komplement-Faktor C3",
        function_type="metabolisch", redundancy_degree="keine")
    g_c4 = insert_gene(conn, "C4A", "Komplement-Faktor C4A",
        function_type="metabolisch", redundancy_degree="niedrig")
    g_c1q = insert_gene(conn, "C1QA", "Komplement C1q Untereinheit A",
        function_type="metabolisch", redundancy_degree="keine")

    # T-Zell-Immunantwort
    g_cd4 = insert_gene(conn, "CD4", "CD4-Antigen",
        function_type="signal", redundancy_degree="keine")
    g_cd8a = insert_gene(conn, "CD8A", "CD8-Antigen Alpha-Kette",
        function_type="signal", redundancy_degree="keine")
    g_zap70 = insert_gene(conn, "ZAP70", "Zeta-Kette-assoziierte Proteinkinase 70",
        function_type="signal", redundancy_degree="keine")
    g_lck = insert_gene(conn, "LCK", "Lymphozyten-spezifische Proteintyrosinkinase",
        function_type="signal", redundancy_degree="keine")

    # NK-Zellen
    g_prf1 = insert_gene(conn, "PRF1", "Perforin-1",
        function_type="strukturell", redundancy_degree="keine")
    g_klrk1 = insert_gene(conn, "KLRK1", "NKG2D-Rezeptor",
        function_type="signal", redundancy_degree="niedrig")

    # HPA-Achse
    g_cyp11a1 = insert_gene(conn, "CYP11A1", "Cholesterol-Seitenkettenspaltungsenzym",
        function_type="metabolisch", redundancy_degree="keine")
    g_cyp11b1 = insert_gene(conn, "CYP11B1", "Steroid-11-beta-Hydroxylase",
        function_type="metabolisch", redundancy_degree="keine")
    g_pomc = insert_gene(conn, "POMC", "Proopiomelanocortin",
        function_type="regulatorisch", redundancy_degree="keine")

    # Gonadal
    g_cyp19a1 = insert_gene(conn, "CYP19A1", "Aromatase",
        function_type="metabolisch", redundancy_degree="keine")
    g_fshr = insert_gene(conn, "FSHR", "FSH-Rezeptor",
        function_type="signal", redundancy_degree="keine")

    # PTH / Calcium
    g_pth = insert_gene(conn, "PTH", "Parathormon",
        function_type="regulatorisch", redundancy_degree="keine")
    g_casr = insert_gene(conn, "CASR", "Calcium-Sensing-Rezeptor",
        function_type="signal", redundancy_degree="keine")

    # Haem-Biosynthese
    g_alas2 = insert_gene(conn, "ALAS2", "5-Aminolaevulinat-Synthase 2",
        function_type="metabolisch", redundancy_degree="keine")
    g_hmbs = insert_gene(conn, "HMBS", "Hydroxymethylbilan-Synthase",
        function_type="metabolisch", redundancy_degree="keine")
    g_urod = insert_gene(conn, "UROD", "Uroporphyrinogen-Decarboxylase",
        function_type="metabolisch", redundancy_degree="keine")

    # Purin-Metabolismus
    g_xdh = insert_gene(conn, "XDH", "Xanthin-Dehydrogenase/Oxidase",
        function_type="metabolisch", redundancy_degree="keine")
    g_hprt1 = insert_gene(conn, "HPRT1", "Hypoxanthin-Guanin-Phosphoribosyltransferase",
        function_type="metabolisch", redundancy_degree="keine")

    # DNA-Reparatur / Apoptose
    g_tp53 = insert_gene(conn, "TP53", "Tumorsuppressor p53",
        function_type="regulatorisch", redundancy_degree="keine")
    g_brca1 = insert_gene(conn, "BRCA1", "Breast Cancer Type 1 Susceptibility Protein",
        function_type="regulatorisch", redundancy_degree="keine")
    g_mlh1 = insert_gene(conn, "MLH1", "MutL-Homolog 1",
        function_type="regulatorisch", redundancy_degree="niedrig")
    g_bcl2 = insert_gene(conn, "BCL2", "B-Zell-Lymphom 2",
        function_type="regulatorisch", redundancy_degree="niedrig")
    g_bax = insert_gene(conn, "BAX", "BCL2-assoziiertes X-Protein",
        function_type="regulatorisch", redundancy_degree="niedrig")

    # RAAS
    g_ren = insert_gene(conn, "REN", "Renin",
        function_type="metabolisch", redundancy_degree="keine")
    g_ace = insert_gene(conn, "ACE", "Angiotensin-Converting-Enzyme",
        function_type="metabolisch", redundancy_degree="niedrig")
    g_agt = insert_gene(conn, "AGT", "Angiotensinogen",
        function_type="metabolisch", redundancy_degree="keine")

    # Surfactant
    g_sftpb = insert_gene(conn, "SFTPB", "Surfactant-Protein B",
        function_type="strukturell", redundancy_degree="keine")
    g_sftpc = insert_gene(conn, "SFTPC", "Surfactant-Protein C",
        function_type="strukturell", redundancy_degree="niedrig")

    # B12-Absorption
    g_gif = insert_gene(conn, "GIF", "Intrinsic Factor",
        function_type="metabolisch", redundancy_degree="keine")
    g_cubn = insert_gene(conn, "CUBN", "Cubilin",
        function_type="signal", redundancy_degree="keine")

    # Primaere Haemostase
    g_vwf = insert_gene(conn, "VWF", "Von-Willebrand-Faktor",
        function_type="strukturell", redundancy_degree="keine")
    g_gp1ba = insert_gene(conn, "GP1BA", "Glykoprotein Ib Alpha",
        function_type="signal", redundancy_degree="keine")

    # Interferon
    g_ifnar1 = insert_gene(conn, "IFNAR1", "Interferon-Alpha/Beta-Rezeptor 1",
        function_type="signal", redundancy_degree="keine")
    g_stat1 = insert_gene(conn, "STAT1", "Signal Transducer and Activator of Transcription 1",
        function_type="signal", redundancy_degree="keine")

    # Gerinnungsfaktoren (erweitert)
    g_f8 = insert_gene(conn, "F8", "Gerinnungsfaktor VIII",
        function_type="metabolisch", redundancy_degree="keine")
    g_f9 = insert_gene(conn, "F9", "Gerinnungsfaktor IX",
        function_type="metabolisch", redundancy_degree="keine")

    # === Neue Messwerte (~35 neue) ===

    # Immunologie
    m_ige = insert_measurement(conn, "IgE", unit="IU/mL",
        ref_range_low=0.0, ref_range_high=150.0, measurement_site="Blut")
    m_c3 = insert_measurement(conn, "Komplement C3", unit="mg/dL",
        ref_range_low=90.0, ref_range_high=180.0, measurement_site="Blut")
    m_c4 = insert_measurement(conn, "Komplement C4", unit="mg/dL",
        ref_range_low=10.0, ref_range_high=40.0, measurement_site="Blut")
    m_cd4cd8 = insert_measurement(conn, "CD4/CD8-Ratio", unit="Ratio",
        ref_range_low=1.0, ref_range_high=3.5, measurement_site="Blut")
    m_cd4abs = insert_measurement(conn, "CD4+ T-Zellen (absolut)", unit="/uL",
        ref_range_low=500.0, ref_range_high=1500.0, measurement_site="Blut")
    m_nk = insert_measurement(conn, "NK-Zellen (CD56+)", unit="/uL",
        ref_range_low=90.0, ref_range_high=600.0, measurement_site="Blut")
    m_ana = insert_measurement(conn, "ANA-Titer", unit="Titer",
        ref_range_low=0.0, ref_range_high=1.0, measurement_site="Blut")
    m_rf = insert_measurement(conn, "Rheumafaktor", unit="IU/mL",
        ref_range_low=0.0, ref_range_high=14.0, measurement_site="Blut")
    m_antidsdna = insert_measurement(conn, "Anti-dsDNA-Antikoerper", unit="IU/mL",
        ref_range_low=0.0, ref_range_high=25.0, measurement_site="Blut")
    m_anca = insert_measurement(conn, "ANCA", unit="Titer",
        ref_range_low=0.0, ref_range_high=1.0, measurement_site="Blut")

    # Tumormarker
    m_cea = insert_measurement(conn, "CEA", unit="ng/mL",
        ref_range_low=0.0, ref_range_high=5.0, measurement_site="Blut")
    m_psa = insert_measurement(conn, "PSA", unit="ng/mL",
        ref_range_low=0.0, ref_range_high=4.0, measurement_site="Blut")
    m_afp = insert_measurement(conn, "AFP", unit="ng/mL",
        ref_range_low=0.0, ref_range_high=10.0, measurement_site="Blut")
    m_ca199 = insert_measurement(conn, "CA 19-9", unit="U/mL",
        ref_range_low=0.0, ref_range_high=37.0, measurement_site="Blut")
    m_ca153 = insert_measurement(conn, "CA 15-3", unit="U/mL",
        ref_range_low=0.0, ref_range_high=30.0, measurement_site="Blut")
    m_hcg = insert_measurement(conn, "Beta-HCG", unit="mIU/mL",
        ref_range_low=0.0, ref_range_high=5.0, measurement_site="Blut")
    m_calcitonin = insert_measurement(conn, "Kalzitonin", unit="pg/mL",
        ref_range_low=0.0, ref_range_high=10.0, measurement_site="Blut")
    m_ldhratio = insert_measurement(conn, "Freie Leichtketten Ratio", unit="Ratio",
        ref_range_low=0.26, ref_range_high=1.65, measurement_site="Blut")

    # Blutgasanalyse
    m_ph = insert_measurement(conn, "pH (arteriell)", unit="",
        ref_range_low=7.35, ref_range_high=7.45, measurement_site="Blut")
    m_pco2 = insert_measurement(conn, "pCO2", unit="mmHg",
        ref_range_low=35.0, ref_range_high=45.0, measurement_site="Blut")
    m_po2 = insert_measurement(conn, "pO2", unit="mmHg",
        ref_range_low=75.0, ref_range_high=100.0, measurement_site="Blut")
    m_bicarb = insert_measurement(conn, "Bikarbonat", unit="mmol/L",
        ref_range_low=22.0, ref_range_high=26.0, measurement_site="Blut")
    m_laktat = insert_measurement(conn, "Laktat", unit="mmol/L",
        ref_range_low=0.5, ref_range_high=1.5, measurement_site="Blut")

    # Erweiterte Gerinnung
    m_thrombinzeit = insert_measurement(conn, "Thrombin-Zeit", unit="sec",
        ref_range_low=15.0, ref_range_high=20.0, measurement_site="Blut")
    m_vwf_ag = insert_measurement(conn, "Von-Willebrand-Faktor-Antigen", unit="%",
        ref_range_low=50.0, ref_range_high=160.0, measurement_site="Blut")
    m_faktor8 = insert_measurement(conn, "Faktor-VIII-Aktivitaet", unit="%",
        ref_range_low=50.0, ref_range_high=150.0, measurement_site="Blut")

    # Hormone
    m_cortisol = insert_measurement(conn, "Cortisol (morgens)", unit="ug/dL",
        ref_range_low=6.2, ref_range_high=19.4, measurement_site="Blut")
    m_acth = insert_measurement(conn, "ACTH", unit="pg/mL",
        ref_range_low=7.2, ref_range_high=63.3, measurement_site="Blut")
    m_pthorm = insert_measurement(conn, "Parathormon (PTH)", unit="pg/mL",
        ref_range_low=15.0, ref_range_high=65.0, measurement_site="Blut")
    m_testosteron = insert_measurement(conn, "Testosteron", unit="ng/dL",
        ref_range_low=280.0, ref_range_high=1100.0, measurement_site="Blut")
    m_estradiol = insert_measurement(conn, "Estradiol", unit="pg/mL",
        ref_range_low=10.0, ref_range_high=40.0, measurement_site="Blut")
    m_fsh = insert_measurement(conn, "FSH", unit="mIU/mL",
        ref_range_low=1.5, ref_range_high=12.4, measurement_site="Blut")
    m_lh = insert_measurement(conn, "LH", unit="mIU/mL",
        ref_range_low=1.7, ref_range_high=8.6, measurement_site="Blut")
    m_prolaktin = insert_measurement(conn, "Prolaktin", unit="ng/mL",
        ref_range_low=4.0, ref_range_high=15.0, measurement_site="Blut")
    m_igf1 = insert_measurement(conn, "IGF-1", unit="ng/mL",
        ref_range_low=115.0, ref_range_high=355.0, measurement_site="Blut")
    m_aldosteron = insert_measurement(conn, "Aldosteron", unit="ng/dL",
        ref_range_low=3.0, ref_range_high=16.0, measurement_site="Blut")
    m_renin = insert_measurement(conn, "Renin (aktiv)", unit="uIU/mL",
        ref_range_low=2.8, ref_range_high=39.9, measurement_site="Blut")

    # Metabolite
    m_ammoniak = insert_measurement(conn, "Ammoniak", unit="umol/L",
        ref_range_low=19.0, ref_range_high=60.0, measurement_site="Blut")
    m_homocystein = insert_measurement(conn, "Homozystein", unit="umol/L",
        ref_range_low=5.0, ref_range_high=15.0, measurement_site="Blut")
    m_porpho = insert_measurement(conn, "Porphobilinogen (Urin)", unit="umol/L",
        ref_range_low=0.0, ref_range_high=8.8, measurement_site="Urin")
    m_osmol = insert_measurement(conn, "Osmolalitaet (Serum)", unit="mosm/kg",
        ref_range_low=275.0, ref_range_high=295.0, measurement_site="Blut")

    # === Neue Diagnosen (20+) ===
    d_sle = insert_diagnosis(conn, "Systemischer Lupus Erythematodes",
        description="Systemische Autoimmunerkrankung mit Multi-Organ-Beteiligung",
        icd_code="M32.9")
    d_ra = insert_diagnosis(conn, "Rheumatoide Arthritis",
        description="Chronische Autoimmun-Polyarthritis",
        icd_code="M06.9")
    d_gicht = insert_diagnosis(conn, "Gicht",
        description="Harnsaeure-Kristallarthropathie",
        icd_code="M10.9")
    d_addison = insert_diagnosis(conn, "Morbus Addison",
        description="Primaere Nebennierenrindeninsuffizienz",
        icd_code="E27.1")
    d_cushing = insert_diagnosis(conn, "Cushing-Syndrom",
        description="Hyperkortisolismus",
        icd_code="E24.9")
    d_hyperpt = insert_diagnosis(conn, "Primaerer Hyperparathyreoidismus",
        description="Ueberfunktion der Nebenschilddruesen",
        icd_code="E21.0")
    d_hypopt = insert_diagnosis(conn, "Hypoparathyreoidismus",
        description="Unterfunktion der Nebenschilddruesen",
        icd_code="E20.9")
    d_crc = insert_diagnosis(conn, "Kolorektales Karzinom",
        description="Maligner Tumor des Dickdarms",
        icd_code="C18.9")
    d_prostataca = insert_diagnosis(conn, "Prostatakarzinom",
        description="Maligner Tumor der Prostata",
        icd_code="C61")
    d_hcc = insert_diagnosis(conn, "Hepatozellulaeres Karzinom",
        description="Primaerer Leberkrebs",
        icd_code="C22.0")
    d_pancreaca = insert_diagnosis(conn, "Pankreaskarzinom",
        description="Maligner Tumor der Bauchspeicheldruese",
        icd_code="C25.9")
    d_myelom = insert_diagnosis(conn, "Multiples Myelom",
        description="Maligne Plasmazellneoplasie",
        icd_code="C90.0")
    d_porphyrie = insert_diagnosis(conn, "Akute intermittierende Porphyrie",
        description="Haem-Biosynthese-Stoerung",
        icd_code="E80.2")
    d_haemophA = insert_diagnosis(conn, "Haemophilie A",
        description="Faktor-VIII-Mangel",
        icd_code="D66")
    d_vws = insert_diagnosis(conn, "Von-Willebrand-Syndrom",
        description="Stoerung der primaeren Haemostase",
        icd_code="D68.0")
    d_sepsis = insert_diagnosis(conn, "Sepsis",
        description="Lebensbedrohliche Organdysfunktion durch Infektion",
        icd_code="A41.9")
    d_ards = insert_diagnosis(conn, "ARDS",
        description="Akutes Atemnotsyndrom des Erwachsenen",
        icd_code="J80")
    d_metsyn = insert_diagnosis(conn, "Metabolisches Syndrom",
        description="Kombination: Adipositas, Hypertonie, Dyslipidaemie, Insulinresistenz",
        icd_code="E88.81")
    d_megaloblast = insert_diagnosis(conn, "Megaloblastische Anaemie",
        description="B12/Folsaeuremangel-Anaemie",
        icd_code="D51.9")
    d_haemophB = insert_diagnosis(conn, "Haemophilie B",
        description="Faktor-IX-Mangel",
        icd_code="D67")
    d_immundefekt = insert_diagnosis(conn, "Primaerer Immundefekt",
        description="Angeborene Stoerung der Immunabwehr",
        icd_code="D84.9")
    d_resp_azidose = insert_diagnosis(conn, "Respiratorische Azidose",
        description="CO2-Retention mit pH-Abfall",
        icd_code="E87.2")
    d_resp_alkalose = insert_diagnosis(conn, "Respiratorische Alkalose",
        description="Hyperventilation mit pH-Anstieg",
        icd_code="E87.3")
    d_leberenzephalopathie = insert_diagnosis(conn, "Hepatische Enzephalopathie",
        description="ZNS-Dysfunktion bei Leberversagen",
        icd_code="K72.9")
    d_hypogonadismus = insert_diagnosis(conn, "Hypogonadismus",
        description="Unterfunktion der Gonaden",
        icd_code="E29.1")

    # === Pfad <-> Ort ===
    link_pathway_location(conn, p_komplement, l_blut)
    link_pathway_location(conn, p_komplement, l_leber_hep, "synthese_in")
    link_pathway_location(conn, p_tcell, l_thymus)
    link_pathway_location(conn, p_tcell, l_milz_wp, "aktivierung_in")
    link_pathway_location(conn, p_tcell, l_blut, "zirkulation_in")
    link_pathway_location(conn, p_nkcell, l_blut)
    link_pathway_location(conn, p_nkcell, l_km, "reifung_in")
    link_pathway_location(conn, p_hpa, l_hypothalamus, "regulation_in")
    link_pathway_location(conn, p_hpa, l_hypophyse, "regulation_in")
    link_pathway_location(conn, p_hpa, l_nebenniere)
    link_pathway_location(conn, p_gonadal, l_hypophyse, "regulation_in")
    link_pathway_location(conn, p_gonadal, l_hypothalamus, "regulation_in")
    link_pathway_location(conn, p_pth, l_niere_tub, "wirkung_in")
    link_pathway_location(conn, p_pth, l_darm, "wirkung_in")
    link_pathway_location(conn, p_haem, l_km)
    link_pathway_location(conn, p_haem, l_leber_hep, "auch_in")
    link_pathway_location(conn, p_purin, l_leber_hep)
    link_pathway_location(conn, p_purin, l_niere_tub, "ausscheidung_in")
    link_pathway_location(conn, p_dnarep, l_km)
    link_pathway_location(conn, p_apoptose, l_km)
    link_pathway_location(conn, p_raas, l_niere_glom, "renin_aus")
    link_pathway_location(conn, p_raas, l_nebenniere, "aldosteron_aus")
    link_pathway_location(conn, p_surfactant, l_lunge_alv)
    link_pathway_location(conn, p_b12abs, l_darm)
    link_pathway_location(conn, p_vwf, l_gefaess)
    link_pathway_location(conn, p_ifn, l_blut)

    # === Pfad <-> Zelltyp ===
    link_pathway_cell(conn, p_komplement, c_dendritisch, "Aktivierung")
    link_pathway_cell(conn, p_tcell, c_tlymph)
    link_pathway_cell(conn, p_tcell, c_dendritisch, "Praesentation")
    link_pathway_cell(conn, p_nkcell, c_nk)
    link_pathway_cell(conn, p_hpa, c_nnr)
    link_pathway_cell(conn, p_gonadal, c_gonadotroph)
    link_pathway_cell(conn, p_pth, c_osteoblast, "Wirkung")
    link_pathway_cell(conn, p_pth, c_osteoklast, "Wirkung")
    link_pathway_cell(conn, p_surfactant, c_alveo2)
    link_pathway_cell(conn, p_b12abs, c_enterozyt)

    # === Gene -> Pfade (mit is_essential) ===
    link_gene_pathway(conn, g_c3, p_komplement, "zentral", True)
    link_gene_pathway(conn, g_c4, p_komplement, "klassisch", True)
    link_gene_pathway(conn, g_c1q, p_komplement, "initiator", True)
    link_gene_pathway(conn, g_cd4, p_tcell, "korezeptor", True)
    link_gene_pathway(conn, g_cd8a, p_tcell, "korezeptor", True)
    link_gene_pathway(conn, g_zap70, p_tcell, "signaltransduktion", True)
    link_gene_pathway(conn, g_lck, p_tcell, "signaltransduktion", True)
    link_gene_pathway(conn, g_prf1, p_nkcell, "effektor", True)
    link_gene_pathway(conn, g_klrk1, p_nkcell, "aktivierung", True)
    link_gene_pathway(conn, g_cyp11a1, p_hpa, "steroidogenese", True)
    link_gene_pathway(conn, g_cyp11b1, p_hpa, "cortisol_synthese", True)
    link_gene_pathway(conn, g_pomc, p_hpa, "acth_vorlaeufer", True)
    link_gene_pathway(conn, g_cyp19a1, p_gonadal, "aromatisierung", True)
    link_gene_pathway(conn, g_fshr, p_gonadal, "signaltransduktion", True)
    link_gene_pathway(conn, g_pth, p_pth, "hormon", True)
    link_gene_pathway(conn, g_casr, p_pth, "sensor", True)
    link_gene_pathway(conn, g_alas2, p_haem, "geschwindigkeitslimitierend", True)
    link_gene_pathway(conn, g_hmbs, p_haem, "essentiell", True)
    link_gene_pathway(conn, g_urod, p_haem, "essentiell", True)
    link_gene_pathway(conn, g_xdh, p_purin, "endschritt", True)
    link_gene_pathway(conn, g_hprt1, p_purin, "recycling", True)
    link_gene_pathway(conn, g_tp53, p_dnarep, "waechterfunktion", True)
    link_gene_pathway(conn, g_brca1, p_dnarep, "doppelstrangbruch", True)
    link_gene_pathway(conn, g_mlh1, p_dnarep, "mismatch_repair", True)
    link_gene_pathway(conn, g_tp53, p_apoptose, "aktivator", True)
    link_gene_pathway(conn, g_bcl2, p_apoptose, "inhibitor", False)
    link_gene_pathway(conn, g_bax, p_apoptose, "effektor", True)
    link_gene_pathway(conn, g_ren, p_raas, "initiator", True)
    link_gene_pathway(conn, g_ace, p_raas, "konversion", True)
    link_gene_pathway(conn, g_agt, p_raas, "substrat", True)
    link_gene_pathway(conn, g_sftpb, p_surfactant, "essentiell", True)
    link_gene_pathway(conn, g_sftpc, p_surfactant, "essentiell", True)
    link_gene_pathway(conn, g_gif, p_b12abs, "intrinsic_factor", True)
    link_gene_pathway(conn, g_cubn, p_b12abs, "rezeptor", True)
    link_gene_pathway(conn, g_vwf, p_vwf, "adhäsion", True)
    link_gene_pathway(conn, g_gp1ba, p_vwf, "rezeptor", True)
    link_gene_pathway(conn, g_ifnar1, p_ifn, "rezeptor", True)
    link_gene_pathway(conn, g_stat1, p_ifn, "signaltransduktion", True)

    # Gerinnungsfaktoren -> bestehende Gerinnungskaskade
    p_gerinnung = _get_pathway("Gerinnungskaskade")
    if p_gerinnung:
        link_gene_pathway(conn, g_f8, p_gerinnung, "intrinsisch_essentiell", True)
        link_gene_pathway(conn, g_f9, p_gerinnung, "intrinsisch_essentiell", True)

    # === Messwert <-> Pfad ===
    # Komplement
    link_measurement_pathway(conn, m_c3, p_komplement)
    link_measurement_pathway(conn, m_c4, p_komplement)
    # T-Zell
    link_measurement_pathway(conn, m_cd4cd8, p_tcell, "differentialmarker")
    link_measurement_pathway(conn, m_cd4abs, p_tcell, "quantitativ")
    # NK-Zell
    link_measurement_pathway(conn, m_nk, p_nkcell)
    # HPA
    link_measurement_pathway(conn, m_cortisol, p_hpa, "output")
    link_measurement_pathway(conn, m_acth, p_hpa, "regulationsparameter")
    # Gonadal
    link_measurement_pathway(conn, m_testosteron, p_gonadal, "output_maennlich")
    link_measurement_pathway(conn, m_estradiol, p_gonadal, "output_weiblich")
    link_measurement_pathway(conn, m_fsh, p_gonadal, "regulationsparameter")
    link_measurement_pathway(conn, m_lh, p_gonadal, "regulationsparameter")
    link_measurement_pathway(conn, m_prolaktin, p_gonadal, "inhibitorisch")
    # PTH
    link_measurement_pathway(conn, m_pthorm, p_pth, "output")
    m_ca = _get_meas("Calcium")
    m_phos = _get_meas("Phosphat")
    if m_ca:
        link_measurement_pathway(conn, m_ca, p_pth, "reguliert_durch")
    if m_phos:
        link_measurement_pathway(conn, m_phos, p_pth, "reguliert_durch")
    m_vitd = _get_meas("25-OH-Vitamin D")
    if m_vitd:
        link_measurement_pathway(conn, m_vitd, p_pth, "moduliert_durch")
    # Haem
    link_measurement_pathway(conn, m_porpho, p_haem, "intermediat")
    m_hb_r = _get_meas("Haemoglobin")
    if m_hb_r:
        link_measurement_pathway(conn, m_hb_r, p_haem, "endprodukt")
    # Purin
    m_harns = _get_meas("Harnsaeure")
    if m_harns:
        link_measurement_pathway(conn, m_harns, p_purin, "endprodukt")
    # Blutgas -> Surfactant/RAAS
    link_measurement_pathway(conn, m_po2, p_surfactant, "gasaustausch")
    link_measurement_pathway(conn, m_pco2, p_surfactant, "gasaustausch")
    link_measurement_pathway(conn, m_ph, p_raas, "reguliert_mit")
    link_measurement_pathway(conn, m_bicarb, p_raas)
    link_measurement_pathway(conn, m_renin, p_raas, "regulationsparameter")
    link_measurement_pathway(conn, m_aldosteron, p_raas, "output")
    # RAAS -> Elektrolyte
    m_na = _get_meas("Natrium")
    m_k = _get_meas("Kalium")
    if m_na:
        link_measurement_pathway(conn, m_na, p_raas, "reguliert_durch_aldosteron")
    if m_k:
        link_measurement_pathway(conn, m_k, p_raas, "reguliert_durch_aldosteron")
    # Primaere Haemostase
    link_measurement_pathway(conn, m_vwf_ag, p_vwf)
    link_measurement_pathway(conn, m_thrombinzeit, p_vwf, "zeitparameter")
    # Gerinnungsfaktoren
    if p_gerinnung:
        link_measurement_pathway(conn, m_faktor8, p_gerinnung, "intrinsisch")
        link_measurement_pathway(conn, m_thrombinzeit, p_gerinnung, "endstrecke")
    # B12-Absorption
    m_b12 = _get_meas("Vitamin B12")
    if m_b12:
        link_measurement_pathway(conn, m_b12, p_b12abs, "output")
    link_measurement_pathway(conn, m_homocystein, p_b12abs, "steigt_bei_mangel")
    # Interferon
    link_measurement_pathway(conn, m_nk, p_ifn, "aktiviert_durch")
    m_leuko = _get_meas("Leukozyten")
    if m_leuko:
        link_measurement_pathway(conn, m_leuko, p_ifn, "moduliert")
    # Autoimmun -> Komplement
    link_measurement_pathway(conn, m_ana, p_komplement, "autoimmun_marker")
    link_measurement_pathway(conn, m_antidsdna, p_komplement, "autoimmun_marker")
    link_measurement_pathway(conn, m_rf, p_komplement, "autoimmun_marker")
    # Ammoniak -> Leber
    p_hepato = _get_pathway("Hepatozellulaere Integritaet")
    if p_hepato:
        link_measurement_pathway(conn, m_ammoniak, p_hepato, "steigt_bei_versagen")
    # Laktat -> Energiestoffwechsel (allgemein: mehrere Pfade)
    link_measurement_pathway(conn, m_laktat, p_surfactant, "hypoxie_marker")
    # Tumormarker -> DNA-Reparatur/Apoptose
    link_measurement_pathway(conn, m_cea, p_dnarep, "tumormarker")
    link_measurement_pathway(conn, m_psa, p_dnarep, "tumormarker")
    link_measurement_pathway(conn, m_afp, p_apoptose, "tumormarker")
    link_measurement_pathway(conn, m_ca199, p_apoptose, "tumormarker")
    link_measurement_pathway(conn, m_ca153, p_apoptose, "tumormarker")
    link_measurement_pathway(conn, m_ldhratio, p_apoptose, "plasmazellmarker")
    # IGF-1 -> Gonadal (Wachstumshormone)
    link_measurement_pathway(conn, m_igf1, p_gonadal, "wachstumsfaktor")

    # === Pfad <-> Diagnose ===
    link_pathway_diagnosis(conn, p_komplement, d_sle)
    link_pathway_diagnosis(conn, p_tcell, d_sle)
    link_pathway_diagnosis(conn, p_tcell, d_immundefekt)
    link_pathway_diagnosis(conn, p_nkcell, d_immundefekt)
    link_pathway_diagnosis(conn, p_komplement, d_ra)
    link_pathway_diagnosis(conn, p_purin, d_gicht)
    link_pathway_diagnosis(conn, p_hpa, d_addison)
    link_pathway_diagnosis(conn, p_hpa, d_cushing)
    link_pathway_diagnosis(conn, p_pth, d_hyperpt)
    link_pathway_diagnosis(conn, p_pth, d_hypopt)
    link_pathway_diagnosis(conn, p_haem, d_porphyrie)
    link_pathway_diagnosis(conn, p_dnarep, d_crc)
    link_pathway_diagnosis(conn, p_dnarep, d_prostataca)
    link_pathway_diagnosis(conn, p_apoptose, d_crc)
    link_pathway_diagnosis(conn, p_apoptose, d_hcc)
    link_pathway_diagnosis(conn, p_apoptose, d_pancreaca)
    link_pathway_diagnosis(conn, p_apoptose, d_myelom)
    link_pathway_diagnosis(conn, p_raas, d_crc)  # Renale Beteiligung moeglich
    link_pathway_diagnosis(conn, p_surfactant, d_ards)
    link_pathway_diagnosis(conn, p_b12abs, d_megaloblast)
    link_pathway_diagnosis(conn, p_vwf, d_vws)
    link_pathway_diagnosis(conn, p_ifn, d_sepsis)
    link_pathway_diagnosis(conn, p_gonadal, d_hypogonadismus)
    # Gerinnungskaskade -> Haemophilie
    if p_gerinnung:
        link_pathway_diagnosis(conn, p_gerinnung, d_haemophA)
        link_pathway_diagnosis(conn, p_gerinnung, d_haemophB)
    # Blutgas -> Azidose/Alkalose
    link_pathway_diagnosis(conn, p_surfactant, d_resp_azidose)
    link_pathway_diagnosis(conn, p_surfactant, d_resp_alkalose)
    # Ammoniak -> Leberenzephalopathie
    if p_hepato:
        link_pathway_diagnosis(conn, p_hepato, d_leberenzephalopathie)
    # Metabolisches Syndrom -> mehrere Pfade
    p_lipid = _get_pathway("Lipid-Metabolismus")
    p_glukose = _get_pathway("Glukose-Homoeoastase")
    if p_lipid:
        link_pathway_diagnosis(conn, p_lipid, d_metsyn)
    if p_glukose:
        link_pathway_diagnosis(conn, p_glukose, d_metsyn)
    link_pathway_diagnosis(conn, p_raas, d_metsyn)

    # === Gen-Expressionen ===
    link_gene_expression(conn, g_c3, l_leber_hep, "hoch")
    link_gene_expression(conn, g_cd4, l_thymus, "hoch")
    link_gene_expression(conn, g_cd8a, l_thymus, "hoch")
    link_gene_expression(conn, g_prf1, l_blut, "hoch")
    link_gene_expression(conn, g_cyp11a1, l_nebenniere, "hoch")
    link_gene_expression(conn, g_cyp11b1, l_nebenniere, "hoch")
    link_gene_expression(conn, g_pomc, l_hypophyse, "hoch")
    link_gene_expression(conn, g_pth, l_blut, "mittel")
    link_gene_expression(conn, g_alas2, l_km, "hoch")
    link_gene_expression(conn, g_tp53, l_km, "hoch")
    link_gene_expression(conn, g_brca1, l_km, "hoch")
    link_gene_expression(conn, g_ren, l_niere_glom, "hoch")
    link_gene_expression(conn, g_sftpb, l_lunge_alv, "hoch")
    link_gene_expression(conn, g_gif, l_darm, "hoch")
    link_gene_expression(conn, g_vwf, l_gefaess, "hoch")
    link_gene_expression(conn, g_f8, l_leber_hep, "hoch")
    link_gene_expression(conn, g_f9, l_leber_hep, "hoch")
    link_gene_expression(conn, g_stat1, l_blut, "mittel")

    # === Neue Messwert-Signaturen (12+) ===

    # Lupus-Signatur
    sig_lupus = insert_signature(conn, "Lupus-Signatur",
        description="Systemischer Lupus Erythematodes", icd_codes="M32")
    link_signature_measurement(conn, sig_lupus, m_ana, "hoch", 1.0)
    link_signature_measurement(conn, sig_lupus, m_antidsdna, "hoch", 0.9)
    link_signature_measurement(conn, sig_lupus, m_c3, "niedrig", 0.8)
    link_signature_measurement(conn, sig_lupus, m_c4, "niedrig", 0.7)
    m_bsg = _get_meas("BSG")
    if m_bsg:
        link_signature_measurement(conn, sig_lupus, m_bsg, "hoch", 0.5)

    # Gicht-Signatur
    sig_gicht = insert_signature(conn, "Gicht-Signatur",
        description="Hyperurikaemie/Gicht", icd_codes="M10")
    if m_harns:
        link_signature_measurement(conn, sig_gicht, m_harns, "hoch", 1.0)
    m_crp = _get_meas("CRP")
    if m_crp:
        link_signature_measurement(conn, sig_gicht, m_crp, "hoch", 0.6)
    if m_leuko:
        link_signature_measurement(conn, sig_gicht, m_leuko, "hoch", 0.5)

    # Cushing-Signatur
    sig_cushing = insert_signature(conn, "Cushing-Signatur",
        description="Hyperkortisolismus", icd_codes="E24")
    link_signature_measurement(conn, sig_cushing, m_cortisol, "hoch", 1.0)
    link_signature_measurement(conn, sig_cushing, m_acth, "hoch", 0.7)
    m_glukose = _get_meas("Glukose (nuechtern)")
    if m_glukose:
        link_signature_measurement(conn, sig_cushing, m_glukose, "hoch", 0.5)
    if m_k:
        link_signature_measurement(conn, sig_cushing, m_k, "niedrig", 0.4)

    # Addison-Signatur
    sig_addison = insert_signature(conn, "Addison-Signatur",
        description="Nebennierenrindeninsuffizienz", icd_codes="E27.1")
    link_signature_measurement(conn, sig_addison, m_cortisol, "niedrig", 1.0)
    link_signature_measurement(conn, sig_addison, m_acth, "hoch", 0.9)
    if m_na:
        link_signature_measurement(conn, sig_addison, m_na, "niedrig", 0.7)
    if m_k:
        link_signature_measurement(conn, sig_addison, m_k, "hoch", 0.7)
    link_signature_measurement(conn, sig_addison, m_aldosteron, "niedrig", 0.6)

    # Hyperparathyreoidismus-Signatur
    sig_hyperpt = insert_signature(conn, "Hyperparathyreoidismus-Signatur",
        description="Primaerer Hyperparathyreoidismus", icd_codes="E21.0")
    link_signature_measurement(conn, sig_hyperpt, m_pthorm, "hoch", 1.0)
    if m_ca:
        link_signature_measurement(conn, sig_hyperpt, m_ca, "hoch", 0.9)
    if m_phos:
        link_signature_measurement(conn, sig_hyperpt, m_phos, "niedrig", 0.7)
    m_ap = _get_meas("Alkalische Phosphatase")
    if m_ap:
        link_signature_measurement(conn, sig_hyperpt, m_ap, "hoch", 0.5)

    # Metabolisches-Syndrom-Signatur
    sig_metsyn = insert_signature(conn, "Metabolisches-Syndrom-Signatur",
        description="Metabolisches Syndrom", icd_codes="E88.81")
    if m_glukose:
        link_signature_measurement(conn, sig_metsyn, m_glukose, "hoch", 0.8)
    m_trigly = _get_meas("Triglyzeride")
    m_hdl = _get_meas("HDL-Cholesterin")
    m_hba1c = _get_meas("HbA1c")
    if m_trigly:
        link_signature_measurement(conn, sig_metsyn, m_trigly, "hoch", 0.8)
    if m_hdl:
        link_signature_measurement(conn, sig_metsyn, m_hdl, "niedrig", 0.7)
    if m_hba1c:
        link_signature_measurement(conn, sig_metsyn, m_hba1c, "hoch", 0.6)
    m_insulin = _get_meas("Insulin")
    if m_insulin:
        link_signature_measurement(conn, sig_metsyn, m_insulin, "hoch", 0.7)

    # Sepsis-Signatur
    sig_sepsis = insert_signature(conn, "Sepsis-Signatur",
        description="Sepsis/SIRS", icd_codes="A41")
    m_pct = _get_meas("Procalcitonin")
    if m_crp:
        link_signature_measurement(conn, sig_sepsis, m_crp, "hoch", 0.8)
    if m_pct:
        link_signature_measurement(conn, sig_sepsis, m_pct, "hoch", 1.0)
    if m_leuko:
        link_signature_measurement(conn, sig_sepsis, m_leuko, "hoch", 0.7)
    link_signature_measurement(conn, sig_sepsis, m_laktat, "hoch", 0.9)
    m_thrombo = _get_meas("Thrombozyten")
    if m_thrombo:
        link_signature_measurement(conn, sig_sepsis, m_thrombo, "niedrig", 0.6)

    # Haemophilie-A-Signatur
    sig_haemA = insert_signature(conn, "Haemophilie-A-Signatur",
        description="Faktor-VIII-Mangel", icd_codes="D66")
    link_signature_measurement(conn, sig_haemA, m_faktor8, "niedrig", 1.0)
    m_ptt = _get_meas("PTT")
    if m_ptt:
        link_signature_measurement(conn, sig_haemA, m_ptt, "hoch", 0.9)
    m_inr = _get_meas("Quick/INR")
    if m_inr:
        link_signature_measurement(conn, sig_haemA, m_inr, "normal", 0.6)

    # Von-Willebrand-Signatur
    sig_vws = insert_signature(conn, "Von-Willebrand-Signatur",
        description="Von-Willebrand-Syndrom", icd_codes="D68.0")
    link_signature_measurement(conn, sig_vws, m_vwf_ag, "niedrig", 1.0)
    link_signature_measurement(conn, sig_vws, m_faktor8, "niedrig", 0.7)
    if m_ptt:
        link_signature_measurement(conn, sig_vws, m_ptt, "hoch", 0.6)

    # Megaloblastische-Anaemie-Signatur
    sig_megalo = insert_signature(conn, "Megaloblastische-Anaemie-Signatur",
        description="B12/Folsaeuremangelanaemie", icd_codes="D51")
    m_b12_r = _get_meas("Vitamin B12")
    m_mcv = _get_meas("MCV")
    m_folsaeure = _get_meas("Folsaeure")
    if m_b12_r:
        link_signature_measurement(conn, sig_megalo, m_b12_r, "niedrig", 1.0)
    if m_mcv:
        link_signature_measurement(conn, sig_megalo, m_mcv, "hoch", 0.9)
    link_signature_measurement(conn, sig_megalo, m_homocystein, "hoch", 0.8)
    if m_folsaeure:
        link_signature_measurement(conn, sig_megalo, m_folsaeure, "niedrig", 0.7)
    m_ldh = _get_meas("LDH")
    if m_ldh:
        link_signature_measurement(conn, sig_megalo, m_ldh, "hoch", 0.5)

    # Porphyrie-Signatur
    sig_porphyrie = insert_signature(conn, "Porphyrie-Signatur",
        description="Akute intermittierende Porphyrie", icd_codes="E80.2")
    link_signature_measurement(conn, sig_porphyrie, m_porpho, "hoch", 1.0)
    if m_na:
        link_signature_measurement(conn, sig_porphyrie, m_na, "niedrig", 0.5)

    # Hyperthyreose-Signatur (fehlte noch!)
    sig_hyper_thy = insert_signature(conn, "Hyperthyreose-Signatur",
        description="Schilddruesenueberfunktion", icd_codes="E05")
    m_tsh = _get_meas("TSH")
    m_ft3 = _get_meas("fT3")
    m_ft4 = _get_meas("fT4")
    if m_tsh:
        link_signature_measurement(conn, sig_hyper_thy, m_tsh, "niedrig", 1.0)
    if m_ft4:
        link_signature_measurement(conn, sig_hyper_thy, m_ft4, "hoch", 0.9)
    if m_ft3:
        link_signature_measurement(conn, sig_hyper_thy, m_ft3, "hoch", 0.7)
    m_chol = _get_meas("Cholesterin gesamt")
    if m_chol:
        link_signature_measurement(conn, sig_hyper_thy, m_chol, "niedrig", 0.3)

    # Respiratorische-Azidose-Signatur
    sig_resp_azid = insert_signature(conn, "Respiratorische-Azidose-Signatur",
        description="CO2-Retention", icd_codes="E87.2")
    link_signature_measurement(conn, sig_resp_azid, m_ph, "niedrig", 1.0)
    link_signature_measurement(conn, sig_resp_azid, m_pco2, "hoch", 0.9)
    link_signature_measurement(conn, sig_resp_azid, m_bicarb, "hoch", 0.5)
    link_signature_measurement(conn, sig_resp_azid, m_po2, "niedrig", 0.7)

    # Hepatische-Enzephalopathie-Signatur
    sig_hep_enz = insert_signature(conn, "Hepatische-Enzephalopathie-Signatur",
        description="Leberversagen mit ZNS-Beteiligung", icd_codes="K72.9")
    link_signature_measurement(conn, sig_hep_enz, m_ammoniak, "hoch", 1.0)
    m_albumin = _get_meas("Albumin")
    m_inr2 = _get_meas("Quick/INR")
    if m_albumin:
        link_signature_measurement(conn, sig_hep_enz, m_albumin, "niedrig", 0.7)
    if m_inr2:
        link_signature_measurement(conn, sig_hep_enz, m_inr2, "hoch", 0.6)

    # Immundefekt-Signatur
    sig_immundef = insert_signature(conn, "Immundefekt-Signatur",
        description="Primaerer/sekundaerer Immundefekt", icd_codes="D84")
    link_signature_measurement(conn, sig_immundef, m_cd4abs, "niedrig", 1.0)
    link_signature_measurement(conn, sig_immundef, m_cd4cd8, "niedrig", 0.7)
    m_igg = _get_meas("IgG")
    if m_igg:
        link_signature_measurement(conn, sig_immundef, m_igg, "niedrig", 0.8)
    if m_leuko:
        link_signature_measurement(conn, sig_immundef, m_leuko, "niedrig", 0.5)

    conn.commit()
    n = lambda t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"Erweiterte Systeme geladen: {n('functional_pathways')} Pfade, "
          f"{n('genes_proteins')} Gene, {n('measurements')} Messwerte, "
          f"{n('diagnoses')} Diagnosen, {n('measurement_signatures')} Signaturen, "
          f"{n('body_locations')} Orte, {n('cell_types')} Zelltypen")


def seed_expanded_v2(conn):
    """Erweitert die DB mit weiteren klinisch wichtigen Bereichen (v0.4).

    Neue Bereiche: Gastroenterologie, Knochenmetabolismus, Thrombophilie,
    Allergologie, Autoimmun-Schilddruese, Kupfer-Metabolismus, Fibrinolyse,
    Hepatitis-Serologie, Urindiagnostik, Neurologie-Marker, Haematologie erweitert.
    """

    # === Hilfsfunktionen ===
    def _get_loc(organ, sub=""):
        r = conn.execute("SELECT id FROM body_locations WHERE organ=? AND subcompartment=?",
                         (organ, sub)).fetchone()
        return r[0] if r else insert_location(conn, organ, sub)

    def _get_meas(name):
        r = conn.execute("SELECT id FROM measurements WHERE name=?", (name,)).fetchone()
        return r[0] if r else None

    def _get_pathway(name):
        r = conn.execute("SELECT id FROM functional_pathways WHERE name=?", (name,)).fetchone()
        return r[0] if r else None

    def _get_gene(symbol):
        r = conn.execute("SELECT id FROM genes_proteins WHERE symbol=?", (symbol,)).fetchone()
        return r[0] if r else None

    # Bestehende Orte
    l_blut = _get_loc("Peripheres Blut")
    l_km = _get_loc("Knochenmark")
    l_leber_hep = _get_loc("Leber", "Hepatozyten")
    l_niere_tub = _get_loc("Niere", "Tubulus")
    l_niere_glom = _get_loc("Niere", "Glomerulus")
    l_darm = _get_loc("Duenndarm", "Mukosa")
    l_schilddruese = _get_loc("Schilddruese")
    l_lunge_alv = _get_loc("Lunge", "Alveolen")
    l_gelenk = _get_loc("Gelenk", "Synovia")
    l_gefaess = _get_loc("Gefaessendothel")
    l_kolon = _get_loc("Kolon", "Mukosa")

    # === Neue Koerperorte ===
    l_knochen = insert_location(conn, "Knochen", "Trabekulaer",
        circulation_type="sinusoidal", immune_role="keine")
    l_haut = insert_location(conn, "Haut", "Dermis",
        circulation_type="kapillaer", immune_role="Barriere")
    l_gallenwege = insert_location(conn, "Gallenwege", "Intrahepatisch",
        circulation_type="portal", immune_role="keine")
    l_magen = insert_location(conn, "Magen", "Mukosa",
        circulation_type="mesenterial", immune_role="Sekretion")
    l_niere_sammel = insert_location(conn, "Niere", "Sammelrohr",
        circulation_type="kapillaer", immune_role="Konzentration")
    l_gehirn = insert_location(conn, "Gehirn", "Kortex",
        circulation_type="kapillaer", immune_role="Blut-Hirn-Schranke")

    # === Neue Zelltypen ===
    c_mastzelle = insert_cell_type(conn, "Mastzelle",
        lineage="myeloisch", maturation_stage="terminal",
        lifespan="Wochen-Monate", mobility="resident")
    c_eosinophil = insert_cell_type(conn, "Eosinophiler Granulozyt",
        lineage="myeloisch", maturation_stage="terminal",
        lifespan="8-12 Tage", mobility="mobil")
    c_kupffer = insert_cell_type(conn, "Kupffer-Zelle",
        lineage="myeloisch", maturation_stage="terminal",
        lifespan="Monate", mobility="resident")
    c_cholangiozyt = insert_cell_type(conn, "Cholangiozyt",
        lineage="endoderm", maturation_stage="terminal",
        lifespan="Monate", mobility="resident")

    # === Neue Funktionspfade (15) ===

    p_knochen = insert_pathway(conn, "Knochenmetabolismus",
        description="Osteoblast/Osteoklast-Balance, RANK/RANKL/OPG-System",
        output="Knochenmineralisation und -resorption",
        time_dimension="chronisch")
    p_fibrinolyse = insert_pathway(conn, "Fibrinolyse",
        description="Plasminogen-Aktivierung und Fibrin-Abbau",
        output="Aufgeloeste Fibrin-Thromben",
        time_dimension="akut")
    p_gi_barriere = insert_pathway(conn, "GI-Barrierefunktion",
        description="Intestinale Epithelintegritaet und mukosale Immunabwehr",
        output="Intakte Darmbarriere",
        time_dimension="chronisch")
    p_kupfer = insert_pathway(conn, "Kupfer-Metabolismus",
        description="Aufnahme (CTR1), hepatischer Transport (ATP7B), Ausscheidung",
        output="Kupfer-Homoeoastase, Coeruloplasmin",
        time_dimension="chronisch")
    p_hepcidin = insert_pathway(conn, "Hepcidin-Ferroportin-Achse",
        description="Hepcidin-regulierte Eisen-Freisetzung aus Enterozyten und Makrophagen",
        output="Eisen-Homoeoastase",
        time_dimension="chronisch")
    p_allergie = insert_pathway(conn, "IgE-vermittelte Immunantwort",
        description="Mastzell-Degranulation durch IgE-Kreuzvernetzung",
        output="Histamin, Leukotriene, Prostaglandine",
        time_dimension="akut")
    p_thyroid_auto = insert_pathway(conn, "Schilddruesen-Autoimmunitaet",
        description="Autoimmune Destruktion/Stimulation von Thyreozyten",
        output="Anti-TPO, Anti-Tg, TRAK",
        time_dimension="chronisch")
    p_hepatitis_immun = insert_pathway(conn, "Virale Hepatitis-Immunantwort",
        description="Antikoerper-basierte Immunantwort gegen Hepatitis-Viren",
        output="Anti-HBs, Anti-HCV",
        time_dimension="chronisch")
    p_thrombophilie = insert_pathway(conn, "Natuerliche Antikoagulation",
        description="Antithrombin, Protein C/S, Fibrinolyse als Gegengewicht zur Gerinnung",
        output="Regulierte Haemostase",
        time_dimension="chronisch")
    p_urin_konz = insert_pathway(conn, "Renale Konzentration",
        description="ADH-abhaengige Wasserrueckresorption im Sammelrohr",
        output="Konzentrierter Endharn",
        time_dimension="akut")
    p_vitd_aktiv = insert_pathway(conn, "Vitamin-D-Aktivierung",
        description="25-OH-D -> 1,25-Dihydroxy-D via renaler 1-alpha-Hydroxylase",
        output="Aktives Calcitriol (1,25(OH)2D)",
        time_dimension="chronisch")
    p_epo = insert_pathway(conn, "Erythropoietin-Regulation",
        description="Renale EPO-Synthese bei Hypoxie, Stimulation der Erythropoese",
        output="Erythropoietin",
        time_dimension="chronisch")
    p_gi_absorption = insert_pathway(conn, "Intestinale Naehrstoffabsorption",
        description="Enzymatische Verdauung und Resorption von Naehrstoffen",
        output="Aminosaeuren, Glukose, Fettsaeuren, Vitamine",
        time_dimension="chronisch")
    p_bilirubin = insert_pathway(conn, "Bilirubin-Konjugation",
        description="Hepatische Konjugation von indirektem Bilirubin zu direktem Bilirubin",
        output="Konjugiertes Bilirubin",
        time_dimension="akut")
    p_muskel = insert_pathway(conn, "Muskelzell-Integritaet",
        description="Strukturelle und metabolische Integritaet der Skelettmuskulatur",
        output="Kontraktile Funktion",
        time_dimension="akut")

    # === Neue Gene/Proteine (20) ===

    # Knochen
    g_runx2 = insert_gene(conn, "RUNX2", "Runt-related Transcription Factor 2",
        function_type="regulatorisch", redundancy_degree="keine")
    g_tnfsf11 = insert_gene(conn, "TNFSF11", "RANKL (Receptor Activator of NF-kB Ligand)",
        function_type="signal", redundancy_degree="keine")
    g_tnfrsf11b = insert_gene(conn, "TNFRSF11B", "Osteoprotegerin (OPG)",
        function_type="signal", redundancy_degree="niedrig")

    # Fibrinolyse
    g_plg = insert_gene(conn, "PLG", "Plasminogen",
        function_type="metabolisch", redundancy_degree="keine")
    g_plat = insert_gene(conn, "PLAT", "Gewebeplasminogenaktivator (tPA)",
        function_type="metabolisch", redundancy_degree="niedrig")
    g_serpine1 = insert_gene(conn, "SERPINE1", "Plasminogen-Aktivator-Inhibitor 1 (PAI-1)",
        function_type="regulatorisch", redundancy_degree="niedrig")

    # Kupfer
    g_atp7b = insert_gene(conn, "ATP7B", "Wilson-ATPase (Kupfertransporter)",
        function_type="metabolisch", redundancy_degree="keine")
    g_cp = insert_gene(conn, "CP", "Coeruloplasmin",
        function_type="metabolisch", redundancy_degree="niedrig")

    # Hepcidin
    g_hamp = insert_gene(conn, "HAMP", "Hepcidin",
        function_type="regulatorisch", redundancy_degree="keine")
    g_slc40a1 = insert_gene(conn, "SLC40A1", "Ferroportin",
        function_type="metabolisch", redundancy_degree="keine")
    g_hfe = insert_gene(conn, "HFE", "Hereditaere Haemochromatose Protein",
        function_type="regulatorisch", redundancy_degree="keine")

    # Allergie
    g_fcer1a = insert_gene(conn, "FCER1A", "Hochaffiner IgE-Rezeptor Alpha",
        function_type="signal", redundancy_degree="keine")
    g_kit = insert_gene(conn, "KIT", "Mastzell-Stammzellfaktor-Rezeptor",
        function_type="signal", redundancy_degree="keine")

    # Thrombophilie
    g_serpinc1 = insert_gene(conn, "SERPINC1", "Antithrombin III",
        function_type="regulatorisch", redundancy_degree="keine")
    g_proc = insert_gene(conn, "PROC", "Protein C",
        function_type="regulatorisch", redundancy_degree="keine")
    g_pros1 = insert_gene(conn, "PROS1", "Protein S",
        function_type="regulatorisch", redundancy_degree="niedrig")
    g_f5 = insert_gene(conn, "F5", "Gerinnungsfaktor V (Leiden bei Mutation)",
        function_type="metabolisch", redundancy_degree="keine")

    # Vitamin D
    g_cyp27b1 = insert_gene(conn, "CYP27B1", "1-alpha-Hydroxylase",
        function_type="metabolisch", redundancy_degree="keine")
    g_vdr = insert_gene(conn, "VDR", "Vitamin-D-Rezeptor",
        function_type="signal", redundancy_degree="keine")

    # EPO
    g_epo = insert_gene(conn, "EPO", "Erythropoietin",
        function_type="regulatorisch", redundancy_degree="keine")

    # === Neue Messwerte (~40) ===

    # Urindiagnostik
    m_uprot = insert_measurement(conn, "Protein (Urin-Streifentest)", unit="mg/dL",
        ref_range_low=0.0, ref_range_high=15.0, measurement_site="Urin")
    m_ugluk = insert_measurement(conn, "Glukose (Urin)", unit="mg/dL",
        ref_range_low=0.0, ref_range_high=15.0, measurement_site="Urin")
    m_ublut = insert_measurement(conn, "Blut (Urin)", unit="Ery/uL",
        ref_range_low=0.0, ref_range_high=5.0, measurement_site="Urin")
    m_uleuko = insert_measurement(conn, "Leukozyten (Urin)", unit="/uL",
        ref_range_low=0.0, ref_range_high=10.0, measurement_site="Urin")
    m_mikroalb = insert_measurement(conn, "Mikroalbumin (Urin)", unit="mg/L",
        ref_range_low=0.0, ref_range_high=20.0, measurement_site="Urin")
    m_uacr = insert_measurement(conn, "Albumin-Kreatinin-Ratio (Urin)", unit="mg/g",
        ref_range_low=0.0, ref_range_high=30.0, measurement_site="Urin")
    m_uosmo = insert_measurement(conn, "Osmolalitaet (Urin)", unit="mosm/kg",
        ref_range_low=300.0, ref_range_high=900.0, measurement_site="Urin")

    # Autoimmun-Schilddruese
    m_antitpo = insert_measurement(conn, "Anti-TPO-Antikoerper", unit="IU/mL",
        ref_range_low=0.0, ref_range_high=34.0, measurement_site="Blut")
    m_trak = insert_measurement(conn, "TSH-Rezeptor-Antikoerper (TRAK)", unit="IU/L",
        ref_range_low=0.0, ref_range_high=1.75, measurement_site="Blut")
    m_antitg = insert_measurement(conn, "Anti-Thyreoglobulin-Antikoerper", unit="IU/mL",
        ref_range_low=0.0, ref_range_high=115.0, measurement_site="Blut")

    # Rheumatologie erweitert
    m_anticcP = insert_measurement(conn, "Anti-CCP-Antikoerper", unit="U/mL",
        ref_range_low=0.0, ref_range_high=17.0, measurement_site="Blut")
    m_hlab27 = insert_measurement(conn, "HLA-B27", unit="pos/neg",
        ref_range_low=0.0, ref_range_high=0.0, measurement_site="Blut")

    # Gastroenterologie
    m_calprotectin = insert_measurement(conn, "Calprotectin (Stuhl)", unit="ug/g",
        ref_range_low=0.0, ref_range_high=50.0, measurement_site="Stuhl")
    m_elastase_stuhl = insert_measurement(conn, "Pankreas-Elastase (Stuhl)", unit="ug/g",
        ref_range_low=200.0, ref_range_high=1000.0, measurement_site="Stuhl")
    m_ttg_iga = insert_measurement(conn, "Transglutaminase-IgA (tTG-IgA)", unit="U/mL",
        ref_range_low=0.0, ref_range_high=10.0, measurement_site="Blut")
    m_ifobt = insert_measurement(conn, "iFOBT (Stuhl)", unit="ng/mL",
        ref_range_low=0.0, ref_range_high=100.0, measurement_site="Stuhl")

    # Hepatitis-Serologie
    m_hbsag = insert_measurement(conn, "HBsAg", unit="pos/neg",
        ref_range_low=0.0, ref_range_high=0.0, measurement_site="Blut")
    m_antihbs = insert_measurement(conn, "Anti-HBs", unit="mIU/mL",
        ref_range_low=10.0, ref_range_high=1000.0, measurement_site="Blut")
    m_antihbc = insert_measurement(conn, "Anti-HBc (gesamt)", unit="pos/neg",
        ref_range_low=0.0, ref_range_high=0.0, measurement_site="Blut")
    m_antihcv = insert_measurement(conn, "Anti-HCV", unit="pos/neg",
        ref_range_low=0.0, ref_range_high=0.0, measurement_site="Blut")

    # Thrombophilie
    m_atiii = insert_measurement(conn, "Antithrombin III", unit="%",
        ref_range_low=80.0, ref_range_high=120.0, measurement_site="Blut")
    m_protc = insert_measurement(conn, "Protein C (Aktivitaet)", unit="%",
        ref_range_low=70.0, ref_range_high=140.0, measurement_site="Blut")
    m_prots = insert_measurement(conn, "Protein S (frei)", unit="%",
        ref_range_low=60.0, ref_range_high=130.0, measurement_site="Blut")
    m_apcr = insert_measurement(conn, "APC-Resistenz (Faktor-V-Leiden-Screening)", unit="Ratio",
        ref_range_low=2.0, ref_range_high=4.0, measurement_site="Blut")

    # Kupfer
    m_coeruloplasmin = insert_measurement(conn, "Coeruloplasmin", unit="mg/dL",
        ref_range_low=20.0, ref_range_high=60.0, measurement_site="Blut")
    m_kupfer = insert_measurement(conn, "Kupfer (Serum)", unit="ug/dL",
        ref_range_low=70.0, ref_range_high=140.0, measurement_site="Blut")
    m_kupfer_urin = insert_measurement(conn, "Kupfer (24h-Urin)", unit="ug/24h",
        ref_range_low=15.0, ref_range_high=60.0, measurement_site="Urin")

    # Allergologie
    m_tryptase = insert_measurement(conn, "Tryptase", unit="ug/L",
        ref_range_low=0.0, ref_range_high=11.4, measurement_site="Blut")
    m_gesamt_ige = insert_measurement(conn, "Gesamt-IgE", unit="IU/mL",
        ref_range_low=0.0, ref_range_high=100.0, measurement_site="Blut")

    # Haematologie erweitert
    m_epo_lvl = insert_measurement(conn, "Erythropoietin (EPO)", unit="mIU/mL",
        ref_range_low=4.3, ref_range_high=29.0, measurement_site="Blut")
    m_stfr = insert_measurement(conn, "Loeslicher Transferrin-Rezeptor (sTfR)", unit="mg/L",
        ref_range_low=0.76, ref_range_high=1.76, measurement_site="Blut")
    m_hepcidin = insert_measurement(conn, "Hepcidin", unit="ng/mL",
        ref_range_low=1.0, ref_range_high=20.0, measurement_site="Blut")
    m_dat = insert_measurement(conn, "Direkter Antiglobulin-Test (DAT)", unit="pos/neg",
        ref_range_low=0.0, ref_range_high=0.0, measurement_site="Blut")

    # Neurologie
    m_s100b = insert_measurement(conn, "S-100B", unit="ug/L",
        ref_range_low=0.0, ref_range_high=0.105, measurement_site="Blut")
    m_nse = insert_measurement(conn, "NSE (Neuron-spezifische Enolase)", unit="ug/L",
        ref_range_low=0.0, ref_range_high=16.3, measurement_site="Blut")

    # Leber/Autoimmun erweitert
    m_ama = insert_measurement(conn, "Anti-Mitochondrien-Antikoerper (AMA)", unit="Titer",
        ref_range_low=0.0, ref_range_high=1.0, measurement_site="Blut")
    m_sma = insert_measurement(conn, "Anti-Smooth-Muscle-Antikoerper (SMA)", unit="Titer",
        ref_range_low=0.0, ref_range_high=1.0, measurement_site="Blut")

    # Sonstiges
    m_myoglobin = insert_measurement(conn, "Myoglobin", unit="ug/L",
        ref_range_low=25.0, ref_range_high=72.0, measurement_site="Blut")
    m_a1at = insert_measurement(conn, "Alpha-1-Antitrypsin", unit="g/L",
        ref_range_low=0.9, ref_range_high=2.0, measurement_site="Blut")
    m_b2m = insert_measurement(conn, "Beta-2-Mikroglobulin", unit="mg/L",
        ref_range_low=0.8, ref_range_high=2.2, measurement_site="Blut")

    # === Neue Diagnosen (25+) ===

    d_crohn = insert_diagnosis(conn, "Morbus Crohn",
        description="Chronisch-entzuendliche Darmerkrankung, transmural", icd_code="K50.9")
    d_colitis = insert_diagnosis(conn, "Colitis Ulcerosa",
        description="Chronisch-entzuendliche Darmerkrankung, nur Mukosa", icd_code="K51.9")
    d_zoeliakie = insert_diagnosis(conn, "Zoeliakie",
        description="Autoimmune Glutenenteropathie", icd_code="K90.0")
    d_haemochrom = insert_diagnosis(conn, "Haemochromatose",
        description="Eisenueberladungserkrankung", icd_code="E83.1")
    d_wilson = insert_diagnosis(conn, "Morbus Wilson",
        description="Kupferspeicherkrankheit durch ATP7B-Defekt", icd_code="E83.0")
    d_thalassaemie = insert_diagnosis(conn, "Thalassaemie",
        description="Quantitative Haemoglobin-Synthesetoerung", icd_code="D56.9")
    d_polycythaemie = insert_diagnosis(conn, "Polycythaemia vera",
        description="Myeloproliferative Neoplasie mit Erythrozytose", icd_code="D45")
    d_mds = insert_diagnosis(conn, "Myelodysplastisches Syndrom",
        description="Klonale Stammzellerkrankung mit ineffektiver Haematopoese", icd_code="D46.9")
    d_cll = insert_diagnosis(conn, "Chronisch-lymphatische Leukaemie",
        description="Indolentes B-Zell-Lymphom", icd_code="C91.1")
    d_nephrotisch = insert_diagnosis(conn, "Nephrotisches Syndrom",
        description="Proteinurie > 3.5g/d, Hypoalbuminaemie, Oedeme", icd_code="N04.9")
    d_lungenembolie = insert_diagnosis(conn, "Lungenembolie",
        description="Thrombotischer Verschluss einer Pulmonalarterie", icd_code="I26.9")
    d_tvt = insert_diagnosis(conn, "Tiefe Venenthrombose",
        description="Thrombose in tiefen Bein-/Beckenvenen", icd_code="I80.2")
    d_herzinsuff = insert_diagnosis(conn, "Herzinsuffizienz",
        description="Unzureichende Herzpumpfunktion", icd_code="I50.9")
    d_hashimoto = insert_diagnosis(conn, "Hashimoto-Thyreoiditis",
        description="Autoimmune Schilddruesenzerstoerung", icd_code="E06.3")
    d_basedow = insert_diagnosis(conn, "Morbus Basedow",
        description="Autoimmune Schilddruesenueberfunktion durch TRAK", icd_code="E05.0")
    d_dm1 = insert_diagnosis(conn, "Diabetes mellitus Typ 1",
        description="Autoimmune Beta-Zell-Zerstoerung", icd_code="E10.9")
    d_osteoporose = insert_diagnosis(conn, "Osteoporose",
        description="Systemische Skeletterkrankung mit Knochenmasseverlust", icd_code="M81.0")
    d_aih = insert_diagnosis(conn, "Autoimmunhepatitis",
        description="Autoimmune Leberentzuendung", icd_code="K75.4")
    d_pbc = insert_diagnosis(conn, "Primaer biliaere Cholangitis",
        description="Autoimmune Gallengangszerstoerung", icd_code="K74.3")
    d_anaphylaxie = insert_diagnosis(conn, "Anaphylaxie",
        description="Systemische IgE-vermittelte Sofortreaktion", icd_code="T78.2")
    d_a1at_mangel = insert_diagnosis(conn, "Alpha-1-Antitrypsin-Mangel",
        description="Protease-Inhibitor-Mangel mit Lungen/Leberbeteiligung", icd_code="E88.0")
    d_rhabdomyolyse = insert_diagnosis(conn, "Rhabdomyolyse",
        description="Akuter Skelettmuskelzerfall", icd_code="M62.82")
    d_hepb = insert_diagnosis(conn, "Hepatitis B",
        description="Virale Leberentzuendung durch HBV", icd_code="B18.1")
    d_hepc = insert_diagnosis(conn, "Hepatitis C",
        description="Virale Leberentzuendung durch HCV", icd_code="B18.2")
    d_aps = insert_diagnosis(conn, "Antiphospholipid-Syndrom",
        description="Autoimmune Thrombophilie", icd_code="D68.6")
    d_morbus_bechterew = insert_diagnosis(conn, "Morbus Bechterew",
        description="Axiale Spondyloarthritis, HLA-B27-assoziiert", icd_code="M45.0")
    d_pankreasinsuff = insert_diagnosis(conn, "Exokrine Pankreasinsuffizienz",
        description="Unzureichende Verdauungsenzym-Produktion", icd_code="K86.81")

    # === Pfad <-> Ort ===
    link_pathway_location(conn, p_knochen, l_knochen)
    link_pathway_location(conn, p_knochen, l_km, "stammzellen_aus")
    link_pathway_location(conn, p_fibrinolyse, l_blut)
    link_pathway_location(conn, p_fibrinolyse, l_gefaess)
    link_pathway_location(conn, p_gi_barriere, l_darm)
    link_pathway_location(conn, p_gi_barriere, l_kolon)
    link_pathway_location(conn, p_kupfer, l_leber_hep)
    link_pathway_location(conn, p_kupfer, l_darm, "absorption_in")
    link_pathway_location(conn, p_kupfer, l_gallenwege, "exkretion_in")
    link_pathway_location(conn, p_hepcidin, l_leber_hep, "synthese_in")
    link_pathway_location(conn, p_hepcidin, l_darm, "wirkung_in")
    link_pathway_location(conn, p_allergie, l_haut)
    link_pathway_location(conn, p_allergie, l_blut)
    link_pathway_location(conn, p_allergie, l_lunge_alv)
    link_pathway_location(conn, p_thyroid_auto, l_schilddruese)
    link_pathway_location(conn, p_hepatitis_immun, l_leber_hep)
    link_pathway_location(conn, p_thrombophilie, l_leber_hep, "synthese_in")
    link_pathway_location(conn, p_thrombophilie, l_gefaess, "wirkung_in")
    link_pathway_location(conn, p_urin_konz, l_niere_sammel)
    link_pathway_location(conn, p_vitd_aktiv, l_niere_tub)
    link_pathway_location(conn, p_epo, l_niere_tub, "synthese_in")
    link_pathway_location(conn, p_epo, l_km, "wirkung_in")
    link_pathway_location(conn, p_gi_absorption, l_darm)
    link_pathway_location(conn, p_gi_absorption, l_magen, "vorverdauung")
    link_pathway_location(conn, p_bilirubin, l_leber_hep)
    link_pathway_location(conn, p_muskel, l_blut, "marker_in")

    # === Pfad <-> Zelltyp ===
    c_osteoblast = conn.execute("SELECT id FROM cell_types WHERE name='Osteoblast'").fetchone()
    c_osteoklast = conn.execute("SELECT id FROM cell_types WHERE name='Osteoklast'").fetchone()
    c_enterozyt = conn.execute("SELECT id FROM cell_types WHERE name='Enterozyt'").fetchone()
    c_hepatozyt = conn.execute("SELECT id FROM cell_types WHERE name='Hepatozyt'").fetchone()
    c_thyreozyt = conn.execute("SELECT id FROM cell_types WHERE name='Thyreozyt'").fetchone()

    if c_osteoblast:
        link_pathway_cell(conn, p_knochen, c_osteoblast[0])
    if c_osteoklast:
        link_pathway_cell(conn, p_knochen, c_osteoklast[0])
    link_pathway_cell(conn, p_allergie, c_mastzelle)
    link_pathway_cell(conn, p_allergie, c_eosinophil)
    if c_enterozyt:
        link_pathway_cell(conn, p_gi_barriere, c_enterozyt[0])
        link_pathway_cell(conn, p_gi_absorption, c_enterozyt[0])
        link_pathway_cell(conn, p_hepcidin, c_enterozyt[0], "Wirkung")
    if c_hepatozyt:
        link_pathway_cell(conn, p_kupfer, c_hepatozyt[0])
        link_pathway_cell(conn, p_hepcidin, c_hepatozyt[0], "Synthese")
        link_pathway_cell(conn, p_thrombophilie, c_hepatozyt[0], "Synthese")
        link_pathway_cell(conn, p_bilirubin, c_hepatozyt[0])
    if c_thyreozyt:
        link_pathway_cell(conn, p_thyroid_auto, c_thyreozyt[0])
    link_pathway_cell(conn, p_hepatitis_immun, c_kupffer)
    link_pathway_cell(conn, p_bilirubin, c_kupffer, "Quelle")

    # === Gene -> Pfade ===
    link_gene_pathway(conn, g_runx2, p_knochen, "osteoblast_differenzierung", True)
    link_gene_pathway(conn, g_tnfsf11, p_knochen, "osteoklast_aktivierung", True)
    link_gene_pathway(conn, g_tnfrsf11b, p_knochen, "osteoklast_hemmung", True)
    link_gene_pathway(conn, g_plg, p_fibrinolyse, "substrat", True)
    link_gene_pathway(conn, g_plat, p_fibrinolyse, "aktivator", True)
    link_gene_pathway(conn, g_serpine1, p_fibrinolyse, "inhibitor", False)
    link_gene_pathway(conn, g_atp7b, p_kupfer, "transporter", True)
    link_gene_pathway(conn, g_cp, p_kupfer, "oxidase", True)
    link_gene_pathway(conn, g_hamp, p_hepcidin, "regulator", True)
    link_gene_pathway(conn, g_slc40a1, p_hepcidin, "target", True)
    link_gene_pathway(conn, g_hfe, p_hepcidin, "sensor", True)
    link_gene_pathway(conn, g_fcer1a, p_allergie, "rezeptor", True)
    link_gene_pathway(conn, g_kit, p_allergie, "mastzell_ueberleben", True)
    link_gene_pathway(conn, g_serpinc1, p_thrombophilie, "antithrombin", True)
    link_gene_pathway(conn, g_proc, p_thrombophilie, "protein_c", True)
    link_gene_pathway(conn, g_pros1, p_thrombophilie, "protein_s", True)
    link_gene_pathway(conn, g_f5, p_thrombophilie, "substrat", False)
    link_gene_pathway(conn, g_cyp27b1, p_vitd_aktiv, "hydroxylase", True)
    link_gene_pathway(conn, g_vdr, p_vitd_aktiv, "rezeptor", True)
    link_gene_pathway(conn, g_epo, p_epo, "hormon", True)

    # Querverbindungen bestehender Gene
    g_tp53_id = _get_gene("TP53")
    if g_tp53_id:
        link_gene_pathway(conn, g_tp53_id, p_knochen, "tumorsuppression", False)
    g_vwf_id = _get_gene("VWF")
    if g_vwf_id:
        link_gene_pathway(conn, g_vwf_id, p_fibrinolyse, "thrombusbildung", False)

    # Gerinnungskaskade-Querverbindung
    p_gerinnung = _get_pathway("Gerinnungskaskade")
    if p_gerinnung:
        link_gene_pathway(conn, g_f5, p_gerinnung, "faktor_v", True)
        link_gene_pathway(conn, g_serpinc1, p_gerinnung, "inhibitor", False)

    # EPO -> Erythropoese
    p_erythro = _get_pathway("Erythropoese")
    if p_erythro:
        link_gene_pathway(conn, g_epo, p_erythro, "stimulation", True)

    # === Messwert <-> Pfad ===

    # Knochen
    m_ca = _get_meas("Calcium")
    m_phos = _get_meas("Phosphat")
    m_ap = _get_meas("Alkalische Phosphatase")
    m_vitd = _get_meas("25-OH-Vitamin D")
    m_pthorm = _get_meas("Parathormon (PTH)")
    if m_ca:
        link_measurement_pathway(conn, m_ca, p_knochen, "freisetzung_bei_resorption")
    if m_phos:
        link_measurement_pathway(conn, m_phos, p_knochen, "knochenumbau_marker")
    if m_ap:
        link_measurement_pathway(conn, m_ap, p_knochen, "osteoblast_marker")
    if m_vitd:
        link_measurement_pathway(conn, m_vitd, p_knochen, "regulation")
        link_measurement_pathway(conn, m_vitd, p_vitd_aktiv, "substrat")
    if m_pthorm:
        link_measurement_pathway(conn, m_pthorm, p_knochen, "regulation")

    # Fibrinolyse
    m_ddimer = _get_meas("D-Dimere")
    if m_ddimer:
        link_measurement_pathway(conn, m_ddimer, p_fibrinolyse, "abbauprodukt")

    # GI-Barriere
    link_measurement_pathway(conn, m_calprotectin, p_gi_barriere, "entzuendungsmarker")
    link_measurement_pathway(conn, m_ifobt, p_gi_barriere, "blutungsmarker")
    link_measurement_pathway(conn, m_ttg_iga, p_gi_barriere, "autoimmun_marker")

    # Kupfer
    link_measurement_pathway(conn, m_coeruloplasmin, p_kupfer, "transportprotein")
    link_measurement_pathway(conn, m_kupfer, p_kupfer, "serumspiegel")
    link_measurement_pathway(conn, m_kupfer_urin, p_kupfer, "ausscheidung")

    # Hepcidin/Eisen
    link_measurement_pathway(conn, m_hepcidin, p_hepcidin, "regulationshormon")
    link_measurement_pathway(conn, m_stfr, p_hepcidin, "eisenbedarf_marker")
    m_ferritin = _get_meas("Ferritin")
    if m_ferritin:
        link_measurement_pathway(conn, m_ferritin, p_hepcidin, "speicher_feedback")
    p_eisen = _get_pathway("Eisenstoffwechsel")
    if p_eisen:
        link_measurement_pathway(conn, m_hepcidin, p_eisen, "regulator")
        link_measurement_pathway(conn, m_stfr, p_eisen, "bedarfsmarker")
        link_measurement_pathway(conn, m_epo_lvl, p_eisen, "stimulator")

    # Allergie
    m_ige_exist = _get_meas("IgE")
    link_measurement_pathway(conn, m_tryptase, p_allergie, "mastzell_marker")
    link_measurement_pathway(conn, m_gesamt_ige, p_allergie, "sensibilisierung")
    if m_ige_exist:
        link_measurement_pathway(conn, m_ige_exist, p_allergie, "spezifisch")
    m_eosino = _get_meas("Eosinophile")
    if m_eosino:
        link_measurement_pathway(conn, m_eosino, p_allergie, "zellulaer")

    # Autoimmun-Schilddruese
    link_measurement_pathway(conn, m_antitpo, p_thyroid_auto, "destruktions_marker")
    link_measurement_pathway(conn, m_trak, p_thyroid_auto, "stimulations_marker")
    link_measurement_pathway(conn, m_antitg, p_thyroid_auto, "autoimmun_marker")
    p_thyroid = _get_pathway("Hypothalamus-Hypophysen-Schilddruesen-Achse")
    if p_thyroid:
        link_measurement_pathway(conn, m_antitpo, p_thyroid, "stoerung_marker")
        link_measurement_pathway(conn, m_trak, p_thyroid, "stimulation_marker")

    # Hepatitis
    link_measurement_pathway(conn, m_hbsag, p_hepatitis_immun, "virusantigen")
    link_measurement_pathway(conn, m_antihbs, p_hepatitis_immun, "immunitaet")
    link_measurement_pathway(conn, m_antihbc, p_hepatitis_immun, "infektionsmarker")
    link_measurement_pathway(conn, m_antihcv, p_hepatitis_immun, "hcv_marker")
    p_hepato = _get_pathway("Hepatozellulaere Integritaet")
    if p_hepato:
        link_measurement_pathway(conn, m_ama, p_hepato, "autoimmun_marker")
        link_measurement_pathway(conn, m_sma, p_hepato, "autoimmun_marker")
        link_measurement_pathway(conn, m_a1at, p_hepato, "protease_inhibitor")

    # Thrombophilie
    link_measurement_pathway(conn, m_atiii, p_thrombophilie, "antithrombin_spiegel")
    link_measurement_pathway(conn, m_protc, p_thrombophilie, "protein_c_spiegel")
    link_measurement_pathway(conn, m_prots, p_thrombophilie, "protein_s_spiegel")
    link_measurement_pathway(conn, m_apcr, p_thrombophilie, "faktor_v_leiden_screen")
    if p_gerinnung:
        link_measurement_pathway(conn, m_atiii, p_gerinnung, "inhibitor_spiegel")

    # Urindiagnostik
    link_measurement_pathway(conn, m_uprot, p_urin_konz, "proteinurie_marker")
    link_measurement_pathway(conn, m_ugluk, p_urin_konz, "glukosurie_marker")
    link_measurement_pathway(conn, m_ublut, p_urin_konz, "haematurie_marker")
    link_measurement_pathway(conn, m_uleuko, p_urin_konz, "infektion_marker")
    link_measurement_pathway(conn, m_mikroalb, p_urin_konz, "fruehmarker")
    link_measurement_pathway(conn, m_uacr, p_urin_konz, "albuminurie")
    link_measurement_pathway(conn, m_uosmo, p_urin_konz, "konzentration")
    # Urin -> GFR
    p_gfr = _get_pathway("Glomerulaere Filtration")
    if p_gfr:
        link_measurement_pathway(conn, m_mikroalb, p_gfr, "schaedigungsmarker")
        link_measurement_pathway(conn, m_uacr, p_gfr, "schaedigungsmarker")
        link_measurement_pathway(conn, m_uprot, p_gfr, "schaedigungsmarker")

    # Vitamin-D-Aktivierung
    link_measurement_pathway(conn, m_epo_lvl, p_epo, "spiegel")

    # Rheumatologie
    link_measurement_pathway(conn, m_anticcP, p_gi_barriere, "autoimmun_marker")
    m_rf = _get_meas("Rheumafaktor")
    p_komplement = _get_pathway("Komplement-Kaskade")
    if p_komplement:
        link_measurement_pathway(conn, m_anticcP, p_komplement, "ra_spezifisch")

    # GI-Absorption
    link_measurement_pathway(conn, m_elastase_stuhl, p_gi_absorption, "pankreasfunktion")
    link_measurement_pathway(conn, m_ttg_iga, p_gi_absorption, "zoeliakie_marker")
    m_b12 = _get_meas("Vitamin B12")
    m_folsaeure = _get_meas("Folsaeure")
    if m_b12:
        link_measurement_pathway(conn, m_b12, p_gi_absorption, "resorption_marker")
    if m_folsaeure:
        link_measurement_pathway(conn, m_folsaeure, p_gi_absorption, "resorption_marker")

    # Bilirubin
    m_bili = _get_meas("Bilirubin (indirekt)")
    m_bili_dir = _get_meas("Bilirubin (direkt)")
    if m_bili:
        link_measurement_pathway(conn, m_bili, p_bilirubin, "substrat")
    if m_bili_dir:
        link_measurement_pathway(conn, m_bili_dir, p_bilirubin, "produkt")

    # Muskel
    m_ck = _get_meas("CK")
    if m_ck:
        link_measurement_pathway(conn, m_ck, p_muskel, "schaedigungsmarker")
    link_measurement_pathway(conn, m_myoglobin, p_muskel, "nekrose_marker")
    m_ldh = _get_meas("LDH")
    if m_ldh:
        link_measurement_pathway(conn, m_ldh, p_muskel, "zellschaden")

    # Neurologie -> DNA-Reparatur/Apoptose (Tumormarker-Kontext)
    p_dnarep = _get_pathway("DNA-Reparatur")
    if p_dnarep:
        link_measurement_pathway(conn, m_nse, p_dnarep, "neuroendokrin_marker")
        link_measurement_pathway(conn, m_b2m, p_dnarep, "zellproliferation")

    # EPO -> Erythropoese
    if p_erythro:
        link_measurement_pathway(conn, m_epo_lvl, p_erythro, "stimulation")
        link_measurement_pathway(conn, m_stfr, p_erythro, "bedarfsmarker")

    # DAT -> Haemolyse
    p_haemolyse = _get_pathway("Erythrozyten-Abbau (Haemolyse)")
    if p_haemolyse:
        link_measurement_pathway(conn, m_dat, p_haemolyse, "autoimmun_marker")

    # === Pfad <-> Diagnose ===

    # Knochen
    link_pathway_diagnosis(conn, p_knochen, d_osteoporose)
    p_pth = _get_pathway("Calcium-Phosphat-Homoeoastase")
    if p_pth:
        link_pathway_diagnosis(conn, p_pth, d_osteoporose)
    link_pathway_diagnosis(conn, p_vitd_aktiv, d_osteoporose)

    # Fibrinolyse
    link_pathway_diagnosis(conn, p_fibrinolyse, d_lungenembolie)
    link_pathway_diagnosis(conn, p_fibrinolyse, d_tvt)
    if p_gerinnung:
        link_pathway_diagnosis(conn, p_gerinnung, d_lungenembolie)
        link_pathway_diagnosis(conn, p_gerinnung, d_tvt)

    # GI
    link_pathway_diagnosis(conn, p_gi_barriere, d_crohn)
    link_pathway_diagnosis(conn, p_gi_barriere, d_colitis)
    link_pathway_diagnosis(conn, p_gi_barriere, d_zoeliakie)
    link_pathway_diagnosis(conn, p_gi_absorption, d_zoeliakie)
    link_pathway_diagnosis(conn, p_gi_absorption, d_pankreasinsuff)

    # Kupfer
    link_pathway_diagnosis(conn, p_kupfer, d_wilson)

    # Hepcidin/Eisen
    link_pathway_diagnosis(conn, p_hepcidin, d_haemochrom)
    if p_eisen:
        link_pathway_diagnosis(conn, p_eisen, d_haemochrom)
        link_pathway_diagnosis(conn, p_eisen, d_thalassaemie)

    # Allergie
    link_pathway_diagnosis(conn, p_allergie, d_anaphylaxie)

    # Autoimmun-Schilddruese
    link_pathway_diagnosis(conn, p_thyroid_auto, d_hashimoto)
    link_pathway_diagnosis(conn, p_thyroid_auto, d_basedow)
    if p_thyroid:
        link_pathway_diagnosis(conn, p_thyroid, d_hashimoto)
        link_pathway_diagnosis(conn, p_thyroid, d_basedow)

    # Hepatitis
    link_pathway_diagnosis(conn, p_hepatitis_immun, d_hepb)
    link_pathway_diagnosis(conn, p_hepatitis_immun, d_hepc)
    if p_hepato:
        link_pathway_diagnosis(conn, p_hepato, d_aih)
        link_pathway_diagnosis(conn, p_hepato, d_hepb)
        link_pathway_diagnosis(conn, p_hepato, d_hepc)
        link_pathway_diagnosis(conn, p_hepato, d_a1at_mangel)
    p_cholestase = _get_pathway("Gallensaeure-Metabolismus")
    if p_cholestase:
        link_pathway_diagnosis(conn, p_cholestase, d_pbc)

    # Thrombophilie
    link_pathway_diagnosis(conn, p_thrombophilie, d_lungenembolie)
    link_pathway_diagnosis(conn, p_thrombophilie, d_tvt)
    link_pathway_diagnosis(conn, p_thrombophilie, d_aps)

    # Diabetes Typ 1
    p_glukose = _get_pathway("Glukose-Homoeoastase")
    if p_glukose:
        link_pathway_diagnosis(conn, p_glukose, d_dm1)

    # Herzinsuffizienz
    p_myokard = _get_pathway("Myokard-Integritaet")
    if p_myokard:
        link_pathway_diagnosis(conn, p_myokard, d_herzinsuff)

    # Nephrotisches Syndrom
    if p_gfr:
        link_pathway_diagnosis(conn, p_gfr, d_nephrotisch)
    link_pathway_diagnosis(conn, p_urin_konz, d_nephrotisch)

    # Haematologie
    if p_erythro:
        link_pathway_diagnosis(conn, p_erythro, d_thalassaemie)
        link_pathway_diagnosis(conn, p_erythro, d_polycythaemie)
        link_pathway_diagnosis(conn, p_erythro, d_mds)
    link_pathway_diagnosis(conn, p_epo, d_polycythaemie)

    # CLL
    p_bcell = _get_pathway("Fruehe B-Zell-Differenzierung")
    if p_bcell:
        link_pathway_diagnosis(conn, p_bcell, d_cll)

    # Bilirubin
    link_pathway_diagnosis(conn, p_bilirubin, d_wilson)

    # Muskel
    link_pathway_diagnosis(conn, p_muskel, d_rhabdomyolyse)

    # Morbus Bechterew -> Komplement
    if p_komplement:
        link_pathway_diagnosis(conn, p_komplement, d_morbus_bechterew)

    # A1AT -> Surfactant/Lunge
    p_surfactant = _get_pathway("Surfactant-Produktion")
    if p_surfactant:
        link_pathway_diagnosis(conn, p_surfactant, d_a1at_mangel)

    # Pankreasinsuffizienz
    p_pankreas = _get_pathway("Pankreatische Exokrine Funktion")
    if p_pankreas:
        link_pathway_diagnosis(conn, p_pankreas, d_pankreasinsuff)

    # === Gen-Expressionen ===
    link_gene_expression(conn, g_runx2, l_knochen, "hoch")
    link_gene_expression(conn, g_tnfsf11, l_knochen, "hoch")
    link_gene_expression(conn, g_plg, l_leber_hep, "hoch")
    link_gene_expression(conn, g_atp7b, l_leber_hep, "hoch")
    link_gene_expression(conn, g_cp, l_leber_hep, "hoch")
    link_gene_expression(conn, g_hamp, l_leber_hep, "hoch")
    link_gene_expression(conn, g_hfe, l_darm, "mittel")
    link_gene_expression(conn, g_fcer1a, l_haut, "hoch")
    link_gene_expression(conn, g_serpinc1, l_leber_hep, "hoch")
    link_gene_expression(conn, g_proc, l_leber_hep, "hoch")
    link_gene_expression(conn, g_cyp27b1, l_niere_tub, "hoch")
    link_gene_expression(conn, g_epo, l_niere_tub, "hoch")

    # === Neue Messwert-Signaturen (15+) ===

    # Morbus Crohn-Signatur
    sig_crohn = insert_signature(conn, "Morbus-Crohn-Signatur",
        description="Chronisch-entzuendliche Darmerkrankung", icd_codes="K50")
    link_signature_measurement(conn, sig_crohn, m_calprotectin, "hoch", 1.0)
    m_crp = _get_meas("CRP")
    if m_crp:
        link_signature_measurement(conn, sig_crohn, m_crp, "hoch", 0.7)
    m_albumin = _get_meas("Albumin")
    if m_albumin:
        link_signature_measurement(conn, sig_crohn, m_albumin, "niedrig", 0.5)
    m_bsg = _get_meas("BSG")
    if m_bsg:
        link_signature_measurement(conn, sig_crohn, m_bsg, "hoch", 0.6)

    # Zoeliakie-Signatur
    sig_zoeliakie = insert_signature(conn, "Zoeliakie-Signatur",
        description="Glutenenteropathie", icd_codes="K90.0")
    link_signature_measurement(conn, sig_zoeliakie, m_ttg_iga, "hoch", 1.0)
    m_hb = _get_meas("Haemoglobin")
    if m_hb:
        link_signature_measurement(conn, sig_zoeliakie, m_hb, "niedrig", 0.5)
    if m_ferritin:
        link_signature_measurement(conn, sig_zoeliakie, m_ferritin, "niedrig", 0.6)
    if m_b12:
        link_signature_measurement(conn, sig_zoeliakie, m_b12, "niedrig", 0.4)

    # Hashimoto-Signatur
    sig_hashimoto = insert_signature(conn, "Hashimoto-Signatur",
        description="Autoimmune Hypothyreose", icd_codes="E06.3")
    link_signature_measurement(conn, sig_hashimoto, m_antitpo, "hoch", 1.0)
    m_tsh = _get_meas("TSH")
    if m_tsh:
        link_signature_measurement(conn, sig_hashimoto, m_tsh, "hoch", 0.9)
    m_ft4 = _get_meas("fT4")
    if m_ft4:
        link_signature_measurement(conn, sig_hashimoto, m_ft4, "niedrig", 0.7)
    link_signature_measurement(conn, sig_hashimoto, m_antitg, "hoch", 0.6)

    # Morbus Basedow-Signatur
    sig_basedow = insert_signature(conn, "Morbus-Basedow-Signatur",
        description="Autoimmune Hyperthyreose", icd_codes="E05.0")
    link_signature_measurement(conn, sig_basedow, m_trak, "hoch", 1.0)
    if m_tsh:
        link_signature_measurement(conn, sig_basedow, m_tsh, "niedrig", 0.9)
    m_ft3 = _get_meas("fT3")
    if m_ft4:
        link_signature_measurement(conn, sig_basedow, m_ft4, "hoch", 0.8)
    if m_ft3:
        link_signature_measurement(conn, sig_basedow, m_ft3, "hoch", 0.7)

    # Morbus Wilson-Signatur
    sig_wilson = insert_signature(conn, "Morbus-Wilson-Signatur",
        description="Kupferspeicherkrankheit", icd_codes="E83.0")
    link_signature_measurement(conn, sig_wilson, m_coeruloplasmin, "niedrig", 1.0)
    link_signature_measurement(conn, sig_wilson, m_kupfer_urin, "hoch", 0.9)
    link_signature_measurement(conn, sig_wilson, m_kupfer, "niedrig", 0.7)
    m_alt = _get_meas("ALT (GPT)")
    if m_alt:
        link_signature_measurement(conn, sig_wilson, m_alt, "hoch", 0.5)

    # Haemochromatose-Signatur
    sig_haemochrom = insert_signature(conn, "Haemochromatose-Signatur",
        description="Eisenueberladung", icd_codes="E83.1")
    if m_ferritin:
        link_signature_measurement(conn, sig_haemochrom, m_ferritin, "hoch", 1.0)
    m_tsat = _get_meas("Transferrinsaettigung")
    if m_tsat:
        link_signature_measurement(conn, sig_haemochrom, m_tsat, "hoch", 0.9)
    m_eisen = _get_meas("Eisen")
    if m_eisen:
        link_signature_measurement(conn, sig_haemochrom, m_eisen, "hoch", 0.7)
    m_transferrin = _get_meas("Transferrin")
    if m_transferrin:
        link_signature_measurement(conn, sig_haemochrom, m_transferrin, "niedrig", 0.6)

    # Lungenembolie/TVT-Signatur
    sig_le = insert_signature(conn, "Lungenembolie/TVT-Signatur",
        description="Thromboembolische Erkrankung", icd_codes="I26,I80")
    if m_ddimer:
        link_signature_measurement(conn, sig_le, m_ddimer, "hoch", 1.0)
    m_bnp = _get_meas("NT-proBNP")
    if m_bnp:
        link_signature_measurement(conn, sig_le, m_bnp, "hoch", 0.5)
    m_trop = _get_meas("Troponin I")
    if m_trop:
        link_signature_measurement(conn, sig_le, m_trop, "hoch", 0.4)

    # Nephrotisches-Syndrom-Signatur
    sig_nephrot = insert_signature(conn, "Nephrotisches-Syndrom-Signatur",
        description="Massiver renaler Proteinverlust", icd_codes="N04")
    link_signature_measurement(conn, sig_nephrot, m_uprot, "hoch", 1.0)
    link_signature_measurement(conn, sig_nephrot, m_mikroalb, "hoch", 0.8)
    if m_albumin:
        link_signature_measurement(conn, sig_nephrot, m_albumin, "niedrig", 0.9)
    m_chol = _get_meas("Cholesterin gesamt")
    if m_chol:
        link_signature_measurement(conn, sig_nephrot, m_chol, "hoch", 0.5)

    # Anaphylaxie-Signatur
    sig_anaphylaxie = insert_signature(conn, "Anaphylaxie-Signatur",
        description="Systemische allergische Sofortreaktion", icd_codes="T78.2")
    link_signature_measurement(conn, sig_anaphylaxie, m_tryptase, "hoch", 1.0)
    link_signature_measurement(conn, sig_anaphylaxie, m_gesamt_ige, "hoch", 0.6)

    # Autoimmunhepatitis-Signatur
    sig_aih = insert_signature(conn, "Autoimmunhepatitis-Signatur",
        description="Autoimmune Leberentzuendung", icd_codes="K75.4")
    link_signature_measurement(conn, sig_aih, m_sma, "hoch", 0.9)
    if m_alt:
        link_signature_measurement(conn, sig_aih, m_alt, "hoch", 1.0)
    m_igg = _get_meas("IgG")
    if m_igg:
        link_signature_measurement(conn, sig_aih, m_igg, "hoch", 0.8)
    m_ana = _get_meas("ANA-Titer")
    if m_ana:
        link_signature_measurement(conn, sig_aih, m_ana, "hoch", 0.7)

    # PBC-Signatur
    sig_pbc = insert_signature(conn, "PBC-Signatur",
        description="Primaer biliaere Cholangitis", icd_codes="K74.3")
    link_signature_measurement(conn, sig_pbc, m_ama, "hoch", 1.0)
    m_ggt = _get_meas("GGT")
    if m_ggt:
        link_signature_measurement(conn, sig_pbc, m_ggt, "hoch", 0.8)
    if m_ap:
        link_signature_measurement(conn, sig_pbc, m_ap, "hoch", 0.7)
    m_igm = _get_meas("IgM")
    if m_igm:
        link_signature_measurement(conn, sig_pbc, m_igm, "hoch", 0.6)

    # Rhabdomyolyse-Signatur
    sig_rhabdo = insert_signature(conn, "Rhabdomyolyse-Signatur",
        description="Akuter Muskelzerfall", icd_codes="M62.82")
    if m_ck:
        link_signature_measurement(conn, sig_rhabdo, m_ck, "hoch", 1.0)
    link_signature_measurement(conn, sig_rhabdo, m_myoglobin, "hoch", 0.9)
    if m_ldh:
        link_signature_measurement(conn, sig_rhabdo, m_ldh, "hoch", 0.7)
    m_k = _get_meas("Kalium")
    if m_k:
        link_signature_measurement(conn, sig_rhabdo, m_k, "hoch", 0.5)
    m_krea = _get_meas("Kreatinin")
    if m_krea:
        link_signature_measurement(conn, sig_rhabdo, m_krea, "hoch", 0.6)

    # Thrombophilie-Screening-Signatur
    sig_thrombophilie = insert_signature(conn, "Thrombophilie-Signatur",
        description="Hereditaere Thrombophilie", icd_codes="D68")
    link_signature_measurement(conn, sig_thrombophilie, m_atiii, "niedrig", 0.8)
    link_signature_measurement(conn, sig_thrombophilie, m_protc, "niedrig", 0.8)
    link_signature_measurement(conn, sig_thrombophilie, m_prots, "niedrig", 0.7)
    link_signature_measurement(conn, sig_thrombophilie, m_apcr, "niedrig", 0.9)

    # Rheumatoide-Arthritis erweiterte Signatur
    sig_ra = insert_signature(conn, "Rheumatoide-Arthritis-Signatur",
        description="Seropositiv mit Anti-CCP", icd_codes="M06")
    if m_rf:
        link_signature_measurement(conn, sig_ra, m_rf, "hoch", 0.8)
    link_signature_measurement(conn, sig_ra, m_anticcP, "hoch", 1.0)
    if m_crp:
        link_signature_measurement(conn, sig_ra, m_crp, "hoch", 0.6)
    if m_bsg:
        link_signature_measurement(conn, sig_ra, m_bsg, "hoch", 0.5)

    # Hepatitis-B-Signatur (akut)
    sig_hepb = insert_signature(conn, "Hepatitis-B-Signatur (akut)",
        description="Akute HBV-Infektion", icd_codes="B16")
    link_signature_measurement(conn, sig_hepb, m_hbsag, "hoch", 1.0)
    link_signature_measurement(conn, sig_hepb, m_antihbc, "hoch", 0.9)
    if m_alt:
        link_signature_measurement(conn, sig_hepb, m_alt, "hoch", 0.8)
    m_bili_dir2 = _get_meas("Bilirubin (direkt)")
    if m_bili_dir2:
        link_signature_measurement(conn, sig_hepb, m_bili_dir2, "hoch", 0.5)

    # Herzinsuffizienz-Signatur
    sig_herzinsuff = insert_signature(conn, "Herzinsuffizienz-Signatur",
        description="Chronische Herzinsuffizienz", icd_codes="I50")
    if m_bnp:
        link_signature_measurement(conn, sig_herzinsuff, m_bnp, "hoch", 1.0)
    m_na = _get_meas("Natrium")
    if m_na:
        link_signature_measurement(conn, sig_herzinsuff, m_na, "niedrig", 0.5)
    m_krea2 = _get_meas("Kreatinin")
    if m_krea2:
        link_signature_measurement(conn, sig_herzinsuff, m_krea2, "hoch", 0.4)

    conn.commit()
    n = lambda t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"Expansion v2 geladen: {n('functional_pathways')} Pfade, "
          f"{n('genes_proteins')} Gene, {n('measurements')} Messwerte, "
          f"{n('diagnoses')} Diagnosen, {n('measurement_signatures')} Signaturen, "
          f"{n('body_locations')} Orte, {n('cell_types')} Zelltypen")


if __name__ == "__main__":
    from config import DB_PATH, ensure_dirs
    ensure_dirs()
    conn = get_connection(DB_PATH)
    init_db(conn)
    seed_haemolyse(conn)
    seed_clinical_panels(conn)
    seed_expanded_systems(conn)
    seed_expanded_v2(conn)
    conn.close()
