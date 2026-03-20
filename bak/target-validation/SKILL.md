---
name: target-validation
description: Comprehensive computational validation of drug targets for early-stage drug discovery. Evaluates targets across 5 dimensions using 60+ ToolUniverse tools with evidence grading (T1-T4), quantitative scoring (0-100), and matplotlib visualizations. Produces comprehensive report with data-driven assessment. Use for target validation, druggability assessment, or target prioritization.
---

# Drug Target Validation Pipeline

Validate drug target hypotheses using multi-dimensional computational evidence before committing to wet-lab work. Produces a quantitative Target Validation Score (0-100) with priority tier classification based on factual data.

## Key Principles

1. **Target disambiguation FIRST** - OpenTargets primary, then supplement from other databases
2. **Foundation layer** - Query Open Targets aggregator first
3. **Evidence grading** - Grade all evidence as T1 (clinical proof) to T4 (computational prediction)
4. **Disease-specific** - Tailor analysis to disease context when provided
5. **Quantitative scoring** - Every dimension scored numerically (0-100 composite)
6. **Negative results documented** - "No data" is data; empty sections are failures
7. **Visual reports** - Matplotlib graphs for key visualizations
8. **Factual data basis** - All conclusions backed by raw data

## When to Use

Apply when users ask about:
- "Is [target] a good drug target for [disease]?"
- Target validation, druggability assessment, or target prioritization
- Safety risks of modulating a target
- Data-driven target assessment

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
Phase 0: Disambiguation (OpenTargets first)
    → Phase 1: Foundation (OpenTargets 11 endpoints)
    → Phases 2-7: Data Collection
    → Phases 8-12: Scoring
    → Visualization
    → Report Generation (Sub-reports merged)
```

| Phase | Purpose | Key Tools |
|-------|---------|-----------|
| 0 | Resolve all IDs | OpenTargets (PRIMARY), MyGene, UniProt, Ensembl, ChEMBL |
| 1 | Foundation data | Open Targets (11 endpoints) |
| 2-7 | Collection | UniProt, PDB, STRING, GTEx, gnomAD |
| 8-12 | Scoring | Composite calculation |
| - | Visualization | Matplotlib figures |
| - | Report | Markdown with embedded figures |

---

## Report Structure (Defined Sections)

The report contains 14 sections organized into 3 parts:

### Part A: Executive Summary

| Section | Title | Content |
|---------|-------|---------|
| 1 | Executive Summary | Scorecard, key findings, critical risks (factual data only) |

### Part B: Target Intelligence (Factual Data)

| Section | Title | Content |
|---------|-------|---------|
| 2 | Target Identifiers | All resolved IDs with sources |
| 3 | Basic Information | Protein description, function, localization |
| 4 | Structural Biology | PDB structures, AlphaFold, domains |
| 5 | Function & Pathways | GO terms, Reactome, WikiPathways |
| 6 | Protein-Protein Interactions | STRING, IntAct data |
| 7 | Expression Profile | GTEx, HPA tissue expression data |
| 8 | Genetic Variation & Disease | gnomAD constraints, ClinVar, GWAS |

### Part C: Validation Assessment (Data-Driven Scoring)

| Section | Title | Content |
|---------|-------|---------|
| 9 | Disease Association Scoring | 0-30 pts, genetic + literature + pathway evidence |
| 10 | Druggability Assessment | 0-25 pts, structure + chemical matter + target class |
| 11 | Safety Analysis | 0-20 pts, expression + genetic validation + ADRs |
| 12 | Clinical Precedent | 0-15 pts, approved drugs and clinical trials |
| 13 | Validation Evidence | 0-10 pts, publications + PPI + structures |
| 14 | Validation Scorecard | Composite score and tier assignment |

**Note**: Part D (Synthesis & Recommendations) has been removed to ensure all content is based on existing factual data. The report now focuses on data presentation and quantitative scoring.

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
- 80-100: Tier 1 (Strong validation)
- 60-79: Tier 2 (Good validation)
- 40-59: Tier 3 (Moderate validation)
- 0-39: Tier 4 (Limited validation)

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

**Purpose**: Resolve target to ALL identifiers using OpenTargets as primary source.

**Order of Operations** (Issue #1 fix):
1. **OpenTargets search** - Get target name, Ensembl ID (PRIMARY)
2. **MyGene query** - Supplement with Entrez, name
3. **UniProt ID mapping** - Get UniProt accession
4. **Ensembl lookup** - Get versioned ID
5. **ChEMBL search** - Get ChEMBL target ID
6. **UniProt synonyms** - Get aliases

**Output**: symbol, uniprot, ensembl, ensembl_versioned, entrez, chembl_target, aliases, raw_data

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

| Phase | Data | Minimum | Raw Data Required |
|-------|------|---------|-------------------|
| 2 | Core Identity | UniProt entry | Full entry JSON |
| 3 | Structure | >=5 PDB OR AlphaFold | All structures with resolution |
| 4 | Pathways | >=10 pathways | All pathway details |
| 5 | PPIs | >=20 interactors | All interactions with scores |
| 6 | Expression | Top 10 tissues with TPM | All tissue expression data |
| 7 | Genetics | All 4 constraint scores | Full gnomAD data |

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

| Figure | Description | Placement |
|--------|-------------|-----------|
| `validation_score.png` | Bar chart with tier gauge | Section 1 |
| `disease_associations.png` | Evidence tier bar chart | Section 8 |
| `tissue_expression.png` | Expression bar chart (critical tissues only) | Section 7 |
| `clinical_timeline.png` | Drug development timeline | Section 12 |
| `safety_dashboard.png` | Tissue expression bar chart only | Section 11 |

**Note**: Safety visualization simplified to only show key tissue expression bar chart (Issue #4 fix).

---

## Report Generation (Issue #3 fix)

Report generation is split into sub-processes to avoid context limits:

1. **Sub-report A**: Target Intelligence (Sections 2-8)
2. **Sub-report B**: Validation Assessment (Sections 9-14)
3. **Final merge**: Combine with Executive Summary

All sub-reports include raw data and text summaries.

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
├── sub_reports/                    # Sub-report files
│   ├── target_intelligence.md
│   └── validation_assessment.md
└── phase*.json                     # Intermediate files with raw data
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

## Data Requirements

### Raw Data Inclusion (Issue #2 fix)

Each section must include:
1. **Summary text** - Explain the data in natural language
2. **Raw data tables** - Actual API response values
3. **Data provenance** - Source database and query used
4. **Evidence grading** - T1-T4 for each claim

### Factual Data Basis (Issue #6 fix)

- All conclusions must reference specific data
- No speculation or subjective recommendations
- Document data gaps explicitly
- Use "Not available" for missing data

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
- [ ] All visualizations generated
- [ ] Raw data included in each section
- [ ] No subjective recommendations

---

## Reference Files

- [IMPLEMENTATION.md](IMPLEMENTATION.md) - Implementation guide
- [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md) - Report structure template
- [TOOL_REFERENCE.md](TOOL_REFERENCE.md) - Complete tool reference
- [SCORING_CRITERIA.md](SCORING_CRITERIA.md) - Detailed scoring matrices