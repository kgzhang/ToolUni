---
name: target-validation
description: Comprehensive computational validation of drug targets for early-stage drug discovery. Evaluates targets across 5 dimensions using 60+ ToolUniverse tools with evidence grading (T1-T4), quantitative scoring (0-100), and matplotlib visualizations. Produces comprehensive report with GO/NO-GO recommendation. Use for target validation, druggability assessment, or target prioritization.
---

# Drug Target Validation Pipeline

Validate drug target hypotheses using multi-dimensional computational evidence before committing to wet-lab work. Produces a quantitative Target Validation Score (0-100) with priority tier classification and GO/NO-GO recommendation.

## Key Principles

1. **Target disambiguation FIRST** - Resolve ALL identifiers before analysis
2. **Foundation layer** - Query Open Targets aggregator first
3. **Evidence grading** - Grade all evidence as T1 (clinical proof) to T4 (computational prediction)
4. **Disease-specific** - Tailor analysis to disease context when provided
5. **Quantitative scoring** - Every dimension scored numerically (0-100 composite)
6. **Negative results documented** - "No data" is data; empty sections are failures
7. **Visual reports** - Matplotlib graphs replace ASCII visualizations

## When to Use

Apply when users ask about:
- "Is [target] a good drug target for [disease]?"
- Target validation, druggability assessment, or target prioritization
- Safety risks of modulating a target
- GO/NO-GO recommendation for a target

**Not for**: general target biology (`tooluniverse-target-research`), drug compound profiling (`tooluniverse-drug-research`), variant interpretation (`tooluniverse-variant-interpretation`)

---

## Quick Start

**Command Line**:
```bash
cd skills/target-validation/scripts
uv run python run_validation.py TARGET [--output-dir DIR] [--disease DISEASE]
```

**Examples**:
- `uv run python run_validation.py STING --output-dir ./results`
- `uv run python run_validation.py EGFR --disease "non-small cell lung cancer"`
- `uv run python run_validation.py KRAS --modality "small molecule"`

---

## Workflow

```
Phase 0: Disambiguation → Phase 1: Foundation → Phases 2-7: Collection
    → Phases 8-12: Scoring → Visualization → Report Generation
```

| Phase | Purpose | Key Tools |
|-------|---------|-----------|
| 0 | Resolve all IDs | UniProt, MyGene, Ensembl, ChEMBL |
| 1 | Foundation data | Open Targets (11 endpoints) |
| 2-7 | Collection | UniProt, PDB, STRING, GTEx, gnomAD |
| 8-12 | Scoring | Composite calculation |
| - | Visualization | Matplotlib figures |
| - | Report | Markdown with embedded figures |

---

## Scoring Overview

**Total: 0-100 points** across 5 dimensions:

| Dimension | Max | Components |
|-----------|-----|------------|
| Disease Association | 30 | Genetic (10) + Literature (10) + Pathway (10) |
| Druggability | 25 | Structure (10) + Chemical matter (10) + Target class (5) |
| Safety Profile | 20 | Expression (5) + Genetic validation (10) + ADRs (5) |
| Clinical Precedent | 15 | Based on highest clinical stage |
| Validation Evidence | 10 | Publications (4) + PPI (3) + Structures (3) |

**Priority Tiers**:
- 80-100: Tier 1 (GO)
- 60-79: Tier 2 (CONDITIONAL GO)
- 40-59: Tier 3 (CAUTION)
- 0-39: Tier 4 (NO-GO)

---

## Evidence Grading

| Tier | Symbol | Criteria |
|------|--------|----------|
| T1 | ★★★ | Clinical proof, FDA-approved drug, mechanistic study |
| T2 | ★★ | Functional study (knockdown, clinical trial) |
| T3 | ★ | Association (GWAS, screen hit, correlation) |
| T4 | ☆ | Mention (review, text-mined, prediction) |

---

## Phase Details

### Phase 0: Target Disambiguation (ALWAYS FIRST)

**Purpose**: Resolve target to ALL identifiers.

**Output**: symbol, uniprot, ensembl, ensembl_versioned, entrez, chembl_target, aliases

**Key Parameter Corrections**:
- `OpenTargets_multi_entity_search`: Use `queryString` (not `query`)
- `ensembl_lookup_gene`: Use `gene_id` with `species="homo_sapiens"`

---

### Phase 1: Open Targets Foundation (ALWAYS SECOND)

**Purpose**: Query comprehensive aggregator for baseline data.

**11 Endpoints**: diseases, tractability, safety, interactions, go_terms, mouse_models, probes, drugs, classes, homologues, publications

**CRITICAL**: Publications uses `entityId` NOT `ensemblId`

---

### Phases 2-7: Data Collection

| Phase | Data | Minimum |
|-------|------|---------|
| 2 | Core Identity | UniProt entry |
| 3 | Structure | >=5 PDB OR AlphaFold |
| 4 | Pathways | >=10 pathways |
| 5 | PPIs | >=20 interactors |
| 6 | Expression | Top 10 tissues with TPM |
| 7 | Genetics | All 4 constraint scores |

**Fallback Chains**:
- Expression: GTEx (versioned) → GTEx (unversioned) → HPA
- PPIs: STRING → IntAct → BioGRID
- Constraints: gnomAD → OpenTargets

---

### Phases 8-12: Scoring

See [SCORING_CRITERIA.md](SCORING_CRITERIA.md) for detailed scoring rules.

---

## Visualization Module

Generates 5 matplotlib figures:

| Figure | Description |
|--------|-------------|
| `validation_score.png` | Bar chart with tier gauge |
| `disease_associations.png` | Evidence tier bar chart |
| `tissue_expression.png` | Expression heatmap |
| `clinical_timeline.png` | Drug development timeline |
| `safety_dashboard.png` | Multi-panel safety indicators |

---

## Output Files

```
output_dir/
├── TARGET_validation_report.md     # Comprehensive markdown report
├── TARGET_validation_results.json  # Structured JSON data
├── figures/                        # Matplotlib visualizations
│   ├── validation_score.png
│   ├── disease_associations.png
│   ├── tissue_expression.png
│   ├── clinical_timeline.png
│   └── safety_dashboard.png
└── phase*.json                     # Intermediate files
```

---

## Critical Parameter Corrections

See [TOOL_REFERENCE.md](TOOL_REFERENCE.md) for complete reference.

| Tool | WRONG | CORRECT |
|------|-------|---------|
| `OpenTargets_*` | `ensemblID` | `ensemblId` |
| `OpenTargets_publications` | `ensemblId` | `entityId` |
| `GTEx_get_median_gene_expression` | `operation="median"` | `operation="get_median_gene_expression"` |
| `gnomad_get_gene_constraints` | `gene_id` | `gene_symbol` |
| `gwas_get_snps_for_gene` | `gene` | `mapped_gene` |
| `STRING_get_protein_interactions` | single ID | `protein_ids` (list) |

---

## Completeness Checklist

- [ ] All identifiers resolved (UniProt, Ensembl, Entrez, ChEMBL)
- [ ] Open Targets foundation data queried (11 endpoints)
- [ ] PPIs: >= 20 interactors OR documented explanation
- [ ] Expression: Top 10 tissues with TPM values OR "unavailable"
- [ ] Diseases: Top 10 associations with scores
- [ ] Constraints: All 4 gnomAD scores OR "unavailable"
- [ ] Evidence grading applied (T1-T4)
- [ ] Safety flags documented
- [ ] Validation roadmap provided
- [ ] All visualizations generated

---

## Reference Files

- [IMPLEMENTATION.md](IMPLEMENTATION.md) - Implementation guide
- [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md) - Report structure template
- [TOOL_REFERENCE.md](TOOL_REFERENCE.md) - Complete tool reference
- [SCORING_CRITERIA.md](SCORING_CRITERIA.md) - Detailed scoring matrices