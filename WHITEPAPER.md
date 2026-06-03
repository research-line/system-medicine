# Functional Pathway-Centric Medical Knowledge Graph with Exclusion Logic
## A System-Medicine Architecture for Differential Diagnosis Support

> **Note:** The authoritative technical description is in the current LaTeX paper package (`paper/SystemMedicine_v2_en.tex`). This whitepaper provides a high-level overview.

**Author:** Lukas Geiger, Independent Researcher, Bernau, Germany
**Date:** March 2026
**Status:** DRAFT -- Concept Paper v0.4
**Prototype:** Available at [github.com/um-bruch/system-medicine](https://github.com/um-bruch/system-medicine)

---

## Abstract

We present the design and prototype implementation of a functional pathway-centric medical knowledge graph intended to support differential diagnosis. Standard clinical decision support systems organize knowledge around diagnoses, symptoms, or genes as primary entities. In contrast, the proposed system uses *biological functional pathways* as its central organizing principle, linking genes, proteins, laboratory values, anatomical locations, cell types, and clinical diagnoses as secondary annotations. This architecture enables a novel form of *exclusion reasoning*: if a functional pathway is demonstrated to be intact (via normal laboratory markers and absence of relevant symptoms), all genes essential and sufficient for that pathway can be excluded as primary causes of disease in the current patient. The system is implemented as a SQLite-backed prototype with a graphical interface, integrating public data sources (Reactome, Gene Ontology, UniProt, HGNC, Uberon, Cell Ontology). The current prototype covers 51 functional pathways, 151 laboratory parameters, 70 genes, 68 clinical diagnoses, and 42 measurement signatures spanning hematology, hepatology, nephrology, endocrinology, immunology (including allergology), cardiology, oncology markers, blood gas analysis, rheumatology, hemostasis (including thrombophilia and fibrinolysis), pulmonology, gastroenterology (IBD, celiac disease), infectiology (hepatitis serology), autoimmunology (thyroid, PBC, AIH), urine diagnostics, neurology markers, osteology, copper metabolism, and allergology. We describe the formal exclusion model, its assumptions and limitations, and propose a validation framework. The system is positioned as a research tool for exploring the pathway-centric paradigm, not as a clinical decision support system.

**Keywords:** knowledge graph, differential diagnosis, functional pathways, exclusion reasoning, system medicine, Reactome, Gene Ontology, biomarker

---

## 1. Introduction and Motivation

Differential diagnosis in complex, multi-system diseases frequently fails not from lack of data but from the inability to systematically integrate heterogeneous evidence. A patient with abnormal laboratory values may have hundreds of candidate genetic causes; current clinical tools largely present these as ranked lists without exploiting the logical structure of *excluded* possibilities.

The central observation motivating this work is: **if a biological functional pathway is demonstrably intact, then all genes that are both necessary and sufficient for that pathway can be excluded as primary causes of dysfunction.** This transforms positive evidence (intact pathway) into negative diagnostic constraints (excluded genes), potentially reducing the candidate space substantially before differential diagnosis is applied.

Existing systems (PhenoTips, OMIM, ClinVar, Phenomizer) organize knowledge around genes, phenotypes, or diseases as primary nodes. Pathway databases (Reactome, KEGG, WikiPathways) organize around biochemical reactions but are not designed for clinical exclusion reasoning. The proposed system bridges this gap.

---

## 2. Problem Statement and Formal Hypothesis

### 2.1 Formal Problem Statement

Let $\mathcal{P} = \{p_1, \ldots, p_n\}$ be the set of biological functional pathways for a given patient context.
Let $\mathcal{G}$ be the set of candidate genes.
Let $\mathcal{E}(p_i) \subseteq \mathcal{G}$ be the set of genes *essential* to pathway $p_i$.
Let $s(p_i) \in \{0, 1\}$ be the observed pathway status: 1 = intact, 0 = disrupted or unknown.

**Exclusion Rule (binary):** If $s(p_i) = 1$, then $\forall g \in \mathcal{E}(p_i)$: gene $g$ is *excluded* as a primary cause.

**Exclusion Score (probabilistic):** For a gene $g$, the exclusion confidence is:
$$\text{excl}(g) = \prod_{i: g \in \mathcal{E}(p_i)} c(p_i) \cdot b(g)$$
where $c(p_i) \in [0,1]$ is the pathway status confidence (intact: 0.95, unknown: 0.50, disrupted: 0.05), and $b(g) \in [0,1]$ is a multi-pathway bonus factor:
$$b(g) = \min(1.0,\; 0.7 + 0.1 \cdot |\{p_i : g \in \mathcal{E}(p_i) \wedge s(p_i) = 1\}|)$$
The *suspicion score* incorporates gene redundancy:
$$\text{susp}(g) = (1 - \text{excl}(g)) \cdot r(g)$$
where $r(g) \in \{1.0, 0.85, 0.6, 0.3\}$ maps the gene's redundancy degree (none, low, medium, high).

**Research question:** Does the pathway-centric exclusion model reduce the candidate gene space significantly compared to symptom-only filtering, measured against known genetic diagnoses?

### 2.2 Core Hypothesis

> *Pathway-status-based exclusion logic systematically reduces the candidate gene set for complex rare disease cases by at least 30% relative to phenotype-only filtering, when evaluated on a curated benchmark dataset.*

This is a specific, falsifiable hypothesis. The 30% threshold is set as a minimal clinically meaningful reduction; a null result (< 10% reduction) would indicate that the exclusion logic adds little diagnostic value beyond existing tools.

---

## 3. System Architecture

### 3.1 Data Model

The central entity is the **FunctionalPathway** node, defined by:
- `pathway_id` (Reactome stable ID or internal ID)
- `description` (free text)
- `primary_output` (e.g., "IgG stability", "erythrocyte membrane integrity")
- `temporal_class` (acute / chronic)

Connected entities (with edge types):
- **BodyLocation** (Uberon): OCCURS_IN
- **CellType** (Cell Ontology): EXECUTED_BY
- **Gene/Protein** (HGNC/UniProt): REQUIRES (essential), MODULATES (modulatory)
- **MeasurementType** (laboratory values): MONITORED_BY
- **ClinicalDiagnosis** (ICD-10): IMPAIRED_IN

### 3.2 Implementation

The prototype uses **SQLite** as the backend, with relational tables simulating a graph structure through association tables. A dedicated **Graph Explorer** (NetworkX-based) visualizes the subgraph for selected pathways.

**Note on graph database choice:** The current SQLite implementation enables rapid prototyping but introduces known limitations for deep graph traversal (see Section 6.2). A production system would use Neo4j or a comparable native graph database. The prototype demonstrates the conceptual model; performance comparisons with graph-native backends are planned.

### 3.3 Data Sources

| Source | Entity Type | Integration Status |
|--------|-------------|-------------------|
| Reactome | Pathways, reactions | Partial (top-level pathways) |
| Gene Ontology (GO) | Molecular functions | Partial |
| UniProt | Proteins, gene associations | Partial |
| HGNC | Gene nomenclature | Integrated |
| Uberon | Anatomical locations | Integrated |
| Cell Ontology | Cell types | Integrated |
| KEGG | Pathway maps | Planned |
| OMIM / HPO | Disease-gene associations | Planned |

### 3.4 Data Coverage (v0.4)

The prototype includes curated seed data spanning multiple medical domains:

| Category | Count | Examples |
|----------|-------|---------|
| Functional pathways | 51 | Complement cascade, HPA axis, heme biosynthesis, RAAS, DNA repair, apoptosis regulation |
| Laboratory parameters | 151 | Complete blood count, liver/kidney panels, coagulation, lipids, thyroid, iron, tumor markers, blood gas, hormones, complement, autoimmune markers |
| Genes/proteins | 70 | Structural (ANK1, VWF), signaling (CD4, ZAP70, STAT1), metabolic (CYP11A1, ALAS2), regulatory (TP53, BRCA1) |
| Clinical diagnoses | 68 | Rare (porphyria, hemophilia), common (diabetes, CKD), autoimmune (SLE, RA), oncological (CRC, HCC) |
| Measurement signatures | 42 | Hemolysis, sepsis, Cushing, Addison, lupus, metabolic syndrome, respiratory acidosis |
| Body locations | 28 | Including adrenal, hypothalamus, pituitary, alveoli, thymus, synovium |
| Cell types | 25 | Including T-lymphocytes, NK cells, osteoblasts, alveolar type II cells, dendritic cells |

The data model supports 7 edge types with 192 measurement-pathway links, 77 gene-pathway links (with essentiality flags), and 99 pathway-diagnosis associations.

---

## 4. Exclusion Logic: Assumptions and Limitations

### 4.1 Independence Assumption

The binary exclusion model assumes that pathways are *functionally independent*: an intact pathway $p_i$ excludes its essential genes regardless of the status of other pathways. This assumption is **known to be false** in many biological contexts:

- Many genes participate in multiple pathways (*pleiotropy*). A gene excluded via pathway $p_i$ may still be causative via a different pathway $p_j$ that is not assessed.
- Compensatory mechanisms can maintain measured pathway outputs even when an essential gene is partially dysfunctional.
- The binary status $s(p_i) \in \{0, 1\}$ is a simplification; real pathway activity exists on a continuum.

**Correction in the probabilistic model:** The weight $w_i$ is intended to partially capture uncertainty, but is currently assigned heuristically. A data-driven method for estimating $w_i$ from pathway redundancy and measurement reliability is needed.

### 4.2 Essentiality Definition

"Essential gene" is defined operationally as a gene annotated in Reactome as *required* for at least one reaction in the pathway. This definition is conservative and should be refined using curated essentiality databases (e.g., DepMap, CRISPR essentiality screens).

### 4.3 Weighting Factors

The weighting factors $w_i$ in the probabilistic model are currently assigned manually for the demo scenario. A principled estimation method—calibrating weights against diagnostic accuracy in training cases—is required before the system can be evaluated fairly.

---

## 5. Related Work

### 5.1 Phenotype-Driven Diagnosis Support

Phenomizer (Kohler et al., 2009) and PhenoTips (Girdea et al., 2013) match patient phenotypes (HPO terms) to disease databases. These systems excel at symptom-to-disease matching but do not exploit pathway integrity as exclusion evidence.

### 5.2 Pathway Analysis in Genomics

GSEA (Subramanian et al., 2005) and similar tools identify dysregulated pathways from expression data. They work at the population level and require omics data not typically available in clinical settings. The proposed system works with individual patient laboratory values.

### 5.3 Graph-Based Clinical Reasoning

Knowledge graphs for clinical decision support have been explored in several contexts, including clinical KGs from electronic health records (Rotmensch et al., 2017), large-scale biomedical KGs like Hetionet (Himmelstein et al., 2017), and LLM-augmented systems such as ESCARGOT (Matsumoto et al., 2025) and HealthGenie (Gao et al., 2025). The distinction of the present approach is the use of pathway status as a *first-class constraint* in exclusion reasoning, rather than as a background annotation.

### 5.4 Comparison Summary

| System | Primary Organizer | Exclusion Logic | Clinical Data Integration |
|--------|-------------------|-----------------|--------------------------|
| Phenomizer | HPO phenotypes | None | Phenotypes only |
| PhenoTips | Patient phenotypes + genes | None | Phenotypes, genotype |
| GSEA/KEGG tools | Pathways | None | Omics data |
| **Proposed** | Functional pathways | Explicit | Lab values + phenotypes |

---

## 6. Evaluation Framework

### 6.1 Benchmark Dataset

A validation study requires a curated benchmark of confirmed genetic diagnoses where:
1. Patient laboratory profiles are available at the time of initial presentation (before genetic diagnosis)
2. The genetic diagnosis is confirmed (variant + phenotype + functional study)
3. The patient's pathway status can be retrospectively reconstructed from laboratory data

**Target:** 20--50 cases from rare disease registries (EURORDIS, OMIM clinical synopsis, published case series). The demo hemolysis scenario provides proof-of-concept only.

### 6.2 Primary Metric

**Candidate reduction rate (CRR):**
$$\text{CRR} = 1 - \frac{|\mathcal{G}_{\text{after exclusion}}|}{|\mathcal{G}_{\text{before exclusion}}|}$$

A CRR > 0.30 (30% reduction) is set as the primary success criterion (see Section 2.2 hypothesis).

**Safety constraint:** The confirmed causal gene must not be excluded (false exclusion rate = 0 is required for clinical applicability; any false exclusion in the benchmark invalidates the model).

### 6.3 Secondary Metrics

- Rank improvement: position of the correct gene in the ranked candidate list after exclusion filtering
- Coverage: percentage of benchmark cases where at least one pathway can be assessed from available laboratory data
- Comparison: CRR vs. standard HPO-only filtering

### 6.4 Comparison with Clinical Tools

The system should be benchmarked against at least one existing tool (Phenomizer or similar) on the same case set. Without this comparison, the added value of the pathway-centric approach cannot be established.

---

## 7. Limitations and Open Questions

1. **SQLite vs. graph database:** The prototype uses SQLite for simplicity. Scalability to full Reactome (>2000 pathways, >10,000 reactions) requires performance testing; a graph database backend (Neo4j) is recommended for production use.

2. **Binary pathway status:** Real pathway function is continuous. A measurement-based continuous pathway score would be more informative but requires calibrated reference ranges.

3. **Weighting factors:** The probabilistic model's weights $w_i$ are currently heuristic. Learning these from training data is required for validated probabilistic exclusion.

4. **Data completeness:** Not all pathways have adequate Reactome coverage. Orphan pathways, tissue-specific metabolism, and recently characterized mechanisms may not be represented.

5. **Independence assumption violations:** Pleiotropic genes and compensatory mechanisms limit the reliability of exclusion claims. Conservative thresholds and explicit uncertainty communication are essential.

6. **No clinical integration:** The system is a research tool, not a certified clinical decision support system. Clinical integration would require regulatory compliance (MDR, FDA 510(k)) and prospective validation.

---

## 8. Conclusion

The functional pathway-centric knowledge graph represents a structurally distinct approach to differential diagnosis support, exploiting pathway-status evidence as explicit diagnostic constraints. The prototype implementation demonstrates feasibility across all core components: data ingestion, graph modeling, exclusion reasoning, and visualization, now spanning 51 pathways with 151 laboratory parameters, 70 genes, 68 diagnoses, and 42 diagnostic signatures. The core hypothesis—that pathway exclusion reduces the candidate gene space by ≥ 30% without false exclusions—is testable and constitutes the primary empirical target for future work.

Key open tasks before academic publication:
1. Curated benchmark dataset (20–50 cases from rare disease registries)
2. Data-driven calibration of pathway weights $w_i$ via grid search on training cases
3. Integration of OMIM/HPO disease-gene associations for comprehensive gene coverage
4. Benchmarking against Phenomizer on the same case set
5. Performance evaluation of SQLite vs. Neo4j backends at full Reactome scale
6. Sensitivity analysis: robustness of CRR under parameter variation ($w_i \pm 0.2$)
7. Explicit failure mode documentation (pleiotropy, measurement masking, tissue-specific essentiality)

---

## References

- Amberger, J.S. et al. (2019). OMIM.org: leveraging knowledge across phenotype-gene relationships. *Nucleic Acids Research*, 47(D1), D1038--D1043.
- Ashburner, M. et al. (2000). Gene Ontology: tool for the unification of biology. *Nature Genetics*, 25(1), 25--29.
- Braschi, B. et al. (2019). Genenames.org: the HGNC and VGNC resources in 2019. *Nucleic Acids Research*, 47(D1), D786--D792.
- Diehl, A.D. et al. (2016). The Cell Ontology 2016: enhanced content, modularization, and ontology interoperability. *J Biomed Semantics*, 7(1), 44.
- Fabregat, A. et al. (2018). The Reactome Pathway Knowledgebase. *Nucleic Acids Research*, 46(D1), D649--D655.
- Gao, F. et al. (2025). HealthGenie: A Knowledge-Driven LLM Framework for Tailored Dietary Guidance. *CIKM '25*, 6639--6643.
- Girdea, M. et al. (2013). PhenoTips: patient phenotyping software for clinical and research use. *Human Mutation*, 34(8), 1057--1065.
- Himmelstein, D.S. et al. (2017). Systematic integration of biomedical knowledge prioritizes drugs for repurposing. *eLife*, 6, e26726.
- HL7 International (2023). FHIR Release 5. https://hl7.org/fhir/R5/
- Kanehisa, M. et al. (2023). KEGG for taxonomy-based analysis of pathways and genomes. *Nucleic Acids Research*, 51(D1), D587--D592.
- Kohler, S. et al. (2009). Clinical diagnostics in human genetics with semantic similarity searches in ontologies. *Am J Hum Genet*, 85(4), 457--464.
- Matsumoto, N. et al. (2025). ESCARGOT: an AI agent leveraging LLMs, dynamic graph of thoughts, and biomedical KGs. *Bioinformatics*, 41(2).
- Mungall, C.J. et al. (2012). Uberon, an integrative multi-species anatomy ontology. *Genome Biology*, 13(1), R5.
- Robinson, P.N. et al. (2008). The Human Phenotype Ontology. *Am J Hum Genet*, 83(5), 610--615.
- Rotmensch, M. et al. (2017). Learning a health knowledge graph from electronic medical records. *Scientific Reports*, 7(1), 5994.
- Subramanian, A. et al. (2005). Gene set enrichment analysis: A knowledge-based approach. *PNAS*, 102(43), 15545--15550.
- The UniProt Consortium (2023). UniProt: the Universal Protein Knowledgebase in 2023. *Nucleic Acids Research*, 51(D1), D523--D531.
