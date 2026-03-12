# Functional Pathway-Centric Medical Knowledge Graph with Exclusion Logic
## A System-Medicine Architecture for Differential Diagnosis Support

**Author:** Lukas Geiger, Independent Researcher, Bernau, Germany
**Date:** March 2026
**Status:** DRAFT — Concept Paper v0.1
**Prototype:** Available at [github.com/lukisch] (link TODO)

---

## Abstract

We present the design and prototype implementation of a functional pathway-centric medical knowledge graph intended to support differential diagnosis. Standard clinical decision support systems organize knowledge around diagnoses, symptoms, or genes as primary entities. In contrast, the proposed system uses *biological functional pathways* as its central organizing principle, linking genes, proteins, laboratory values, anatomical locations, cell types, and clinical diagnoses as secondary annotations. This architecture enables a novel form of *exclusion reasoning*: if a functional pathway is demonstrated to be intact (via normal laboratory markers and absence of relevant symptoms), all genes essential and sufficient for that pathway can be excluded as primary causes of disease in the current patient. The system is implemented as a SQLite-backed prototype with a graphical interface, integrating public data sources (Reactome, Gene Ontology, UniProt, HGNC, Uberon, Cell Ontology). We describe the formal exclusion model, its assumptions and limitations, and propose a validation framework. The system is positioned as a research tool for exploring the pathway-centric paradigm, not as a clinical decision support system.

**Keywords:** knowledge graph, differential diagnosis, functional pathways, exclusion reasoning, system medicine, Reactome, Gene Ontology

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
$$\text{excl}(g) = 1 - \prod_{i: g \in \mathcal{E}(p_i)} (1 - s(p_i) \cdot w_i)$$
where $w_i \in [0,1]$ is a pathway-specific weight encoding data completeness and pathway redundancy.

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
| OMIM / HPO | Disease-gene associations | %TODO: not yet integrated |

---

## 4. Exclusion Logic: Assumptions and Limitations

### 4.1 Independence Assumption

The binary exclusion model assumes that pathways are *functionally independent*: an intact pathway $p_i$ excludes its essential genes regardless of the status of other pathways. This assumption is **known to be false** in many biological contexts:

- Many genes participate in multiple pathways (*pleiotropy*). A gene excluded via pathway $p_i$ may still be causative via a different pathway $p_j$ that is not assessed.
- Compensatory mechanisms can maintain measured pathway outputs even when an essential gene is partially dysfunctional.
- The binary status $s(p_i) \in \{0, 1\}$ is a simplification; real pathway activity exists on a continuum.

**Correction in the probabilistic model:** The weight $w_i$ is intended to partially capture uncertainty, but is currently assigned heuristically. A data-driven method for estimating $w_i$ from pathway redundancy and measurement reliability is needed.

### 4.2 Essentiality Definition

"Essential gene" is defined operationally as a gene annotated in Reactome as *required* for at least one reaction in the pathway. This definition is conservative (includes genes with modulatory roles) and should be refined using curated essentiality databases (%TODO: DepMap, CRISPR essentiality screens).

### 4.3 Weighting Factors

The weighting factors $w_i$ in the probabilistic model are currently assigned manually for the demo scenario. A principled estimation method—calibrating weights against diagnostic accuracy in training cases—is required before the system can be evaluated fairly.

---

## 5. Related Work

### 5.1 Phenotype-Driven Diagnosis Support

Phenomizer \citep{%TODO_Kohler2009} and PhenoTips \citep{%TODO_Girdea2013} match patient phenotypes (HPO terms) to disease databases. These systems excel at symptom-to-disease matching but do not exploit pathway integrity as exclusion evidence.

### 5.2 Pathway Analysis in Genomics

GSEA \citep{%TODO_Subramanian2005} and similar tools identify dysregulated pathways from expression data. They work at the population level and require omics data not typically available in clinical settings. The proposed system works with individual patient laboratory values.

### 5.3 Graph-Based Clinical Reasoning

Knowledge graphs for clinical decision support have been explored in several contexts (%TODO: cite KG-based CDSSs). The distinction of the present approach is the use of pathway status as a *first-class constraint* in exclusion reasoning, rather than as a background annotation.

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

**Target:** 20–50 cases from rare disease registries (%TODO: EURORDIS, OMIM clinical synopsis, published case series). The demo Haemolyse scenario provides proof-of-concept only.

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

The functional pathway-centric knowledge graph represents a structurally distinct approach to differential diagnosis support, exploiting pathway-status evidence as explicit diagnostic constraints. The prototype implementation demonstrates feasibility across all core components: data ingestion, graph modeling, exclusion reasoning, and visualization. The core hypothesis—that pathway exclusion reduces the candidate gene space by ≥ 30% without false exclusions—is testable and constitutes the primary empirical target for future work.

Key open tasks before academic publication:
1. Curated benchmark dataset (20–50 cases)
2. Data-driven calibration of pathway weights $w_i$
3. Integration of OMIM/HPO disease-gene associations
4. Benchmarking against Phenomizer on the same case set
5. Performance evaluation of SQLite vs. Neo4j backends

---

## References

%TODO: Replace all %TODO_* placeholders with complete bibliographic entries.

<!--
Suggested references (verify before use):
- Köhler et al. (2009). Clinical diagnostics in human genetics with semantic similarity searches in ontologies. Am J Hum Genet.
- Girdea et al. (2013). PhenoTips: patient phenotyping software for clinical and research use. Hum Mutat.
- Subramanian et al. (2005). Gene set enrichment analysis: A knowledge-based approach. PNAS.
- Fabregat et al. (2018). The Reactome Pathway Knowledgebase. Nucleic Acids Res.
- Ashburner et al. (2000). Gene Ontology: tool for the unification of biology. Nat Genet.
- Robinson et al. (2008). The Human Phenotype Ontology. Am J Hum Genet.
- The UniProt Consortium (2023). UniProt: the Universal Protein Knowledgebase. Nucleic Acids Res.
-->
