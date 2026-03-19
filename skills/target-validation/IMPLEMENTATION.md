# Target Validation - Implementation Guide

This document provides workflow guidance and references to implementation scripts.

---

## Script Structure

```
scripts/
├── pipeline_core.py          # Base classes, utilities, scoring logic
├── phase0_disambiguation.py  # Phase 0: Target ID resolution
├── phase1_opentargets.py     # Phase 1: Open Targets foundation
├── phases2_7_data_collection.py  # Phases 2-7: Data collection
├── phases8_12_scoring.py     # Phases 8-12: Scoring
├── visualization.py          # Matplotlib figure generation
├── report_generator.py       # Report generation
└── run_validation.py         # Orchestrator
```

---

## Usage

### Command Line

```bash
cd skills/target-validation/scripts
uv run python run_validation.py TARGET [--output-dir DIR] [--disease DISEASE]
```

### Python API

**See**: [scripts/run_validation.py](scripts/run_validation.py) for the `TargetValidationOrchestrator` class.

---

## Phase Overview

### Phase 0: Target Disambiguation

**Script**: `phase0_disambiguation.py`

**Purpose**: Resolve target query to all identifiers.

**Output**:
- Standard gene symbol
- UniProt accession
- Ensembl ID (versioned)
- Entrez Gene ID
- ChEMBL target ID
- Aliases for collision detection

**Key Parameters**:
- `UniProt_search_entries`: Use `gene:{target} AND organism_id:9606`
- `OpenTargets_multi_entity_search_by_query_string`: Use `queryString`
- `ensembl_lookup_gene`: Use `gene_id` with `species="homo_sapiens"`

---

### Phase 1: Open Targets Foundation

**Script**: `phase1_opentargets.py`

**Purpose**: Query comprehensive aggregator for baseline data.

**Endpoints Queried**:
- Diseases, Tractability, Safety, Interactions, GO terms
- Mouse models, Probes, Drugs, Classes, Homologues, Publications

**CRITICAL**: Publications endpoint uses `entityId` NOT `ensemblId`

---

### Phases 2-7: Data Collection

**Script**: `phases2_7_data_collection.py`

| Phase | Data Type | Tools |
|-------|-----------|-------|
| 2 | Core Identity | UniProt entry, function, localization |
| 3 | Structure | PDB, AlphaFold, InterPro domains |
| 4 | Pathways | Reactome, WikiPathways, GO |
| 5 | PPIs | STRING, IntAct |
| 6 | Expression | GTEx, HPA |
| 7 | Genetics | gnomAD, ClinVar, GWAS |

**Minimum Requirements**:
- PPIs: >= 20 interactors OR documented explanation
- Expression: Top 10 tissues with TPM values
- Pathways: >= 10 pathways OR explanation

---

### Phases 8-12: Scoring

**Script**: `phases8_12_scoring.py`

| Phase | Dimension | Max Points |
|-------|-----------|------------|
| 8 | Disease Association | 30 |
| 9 | Druggability | 25 |
| 10 | Safety | 20 |
| 11 | Clinical Precedent | 15 |
| 12 | Validation Evidence | 10 |

**Priority Tiers**:
- 80-100: Tier 1 (GO)
- 60-79: Tier 2 (CONDITIONAL GO)
- 40-59: Tier 3 (CAUTION)
- 0-39: Tier 4 (NO-GO)

---

## Visualization Module

**Script**: `visualization.py`

Generates matplotlib figures:

| Figure | File | Description |
|--------|------|-------------|
| Validation Score | `validation_score.png` | Bar chart with tier gauge |
| Disease Associations | `disease_associations.png` | Evidence tier bar chart |
| Tissue Expression | `tissue_expression.png` | Expression heatmap |
| Clinical Timeline | `clinical_timeline.png` | Drug development timeline |
| Safety Dashboard | `safety_dashboard.png` | Multi-panel safety indicators |

---

## Report Generator

**Script**: `report_generator.py`

Generates comprehensive markdown report following REPORT_TEMPLATE.md structure:

1. Executive Summary with scorecard
2. Part A: Target Intelligence (Sections 1-7)
3. Part B: Validation Assessment (Sections 8-13)
4. Part C: Synthesis & Recommendations (Sections 14-17)
5. Appendices

Embeds matplotlib visualizations at appropriate locations.

---

## Critical Parameter Corrections

See [TOOL_REFERENCE.md](TOOL_REFERENCE.md) for complete parameter corrections.

Key corrections:

| Tool | WRONG | CORRECT |
|------|-------|---------|
| `OpenTargets_*` | `ensemblID` | `ensemblId` |
| `OpenTargets_publications` | `ensemblId` | `entityId` |
| `GTEx_get_median_gene_expression` | `operation="median"` | `operation="get_median_gene_expression"` |
| `gnomad_get_gene_constraints` | `gene_id` | `gene_symbol` |
| `gwas_get_snps_for_gene` | `gene` | `mapped_gene` |
| `STRING_get_protein_interactions` | single ID | `protein_ids` (list) |

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
├── phase0_disambiguation.json      # Phase 0 intermediate
├── phase1_opentargets.json         # Phase 1 intermediate
├── phases2-7_data_collection.json  # Phases 2-7 intermediate
└── phases8-12_scoring.json         # Phases 8-12 intermediate
```

---

## Error Handling

All scripts implement fallback chains:

```
Primary Tool → Fallback 1 → Fallback 2 → Document in Data Gaps
```

Failed tool calls are documented in:
- `warnings` list in phase results
- `tool_calls` list with status
- Final report Data Gaps section

---

## Testing

Run individual phases for testing:

```bash
uv run python phase0_disambiguation.py EGFR --output-dir ./test
uv run python phase1_opentargets.py --ids-file ./test/phase0_disambiguation.json --output-dir ./test
```

---

## Reference Files

- [SKILL.md](SKILL.md) - Skill documentation and workflow
- [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md) - Report structure template
- [TOOL_REFERENCE.md](TOOL_REFERENCE.md) - Complete tool reference
- [SCORING_CRITERIA.md](SCORING_CRITERIA.md) - Detailed scoring matrices