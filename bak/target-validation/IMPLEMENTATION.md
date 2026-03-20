# Target Validation - Implementation Guide

This document provides workflow guidance and references to implementation scripts.

---

## Recent Updates (Optimization)

### Issue Fixes

1. **Phase 0 Disambiguation**: Now uses OpenTargets as PRIMARY source, then supplements from other databases (fixes `UniProt_search_entries` not found error)

2. **Report Content**: Added text summaries explaining the data in each section (instead of raw JSON blocks)

3. **Report Generation**: Supports sub-report generation to avoid context limits

4. **Safety Visualization**: Simplified to only show key tissue expression bar chart

5. **Report Sections**: Clearly defined 14 sections, removed subjective Part D (Synthesis & Recommendations)

6. **Factual Data Basis**: All content based on existing factual data from databases

---

## Script Structure

```
scripts/
├── pipeline_core.py          # Base classes, utilities, scoring logic
├── phase0_disambiguation.py  # Phase 0: Target ID resolution (OpenTargets primary)
├── phase1_opentargets.py     # Phase 1: Open Targets foundation
├── phases2_7_data_collection.py  # Phases 2-7: Data collection
├── phases8_12_scoring.py     # Phases 8-12: Scoring
├── visualization.py          # Matplotlib figure generation
├── report_generator.py       # Report generation with text summaries
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

### Phase 0: Target Disambiguation (UPDATED)

**Script**: `phase0_disambiguation.py`

**Purpose**: Resolve target query to all identifiers using OpenTargets as PRIMARY source.

**NEW Order of Operations**:
1. OpenTargets search - Get target name, Ensembl ID (PRIMARY)
2. MyGene query - Supplement with Entrez, name
3. UniProt ID mapping - Get UniProt accession
4. Ensembl lookup - Get versioned ID
5. ChEMBL search - Get ChEMBL target ID
6. UniProt synonyms - Get aliases

**Output**:
- Standard gene symbol
- UniProt accession
- Ensembl ID (versioned)
- Entrez Gene ID
- ChEMBL target ID
- Aliases for collision detection
- raw_data dict for reporting

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

| Phase | Data Type | Tools | Minimum |
|-------|-----------|-------|---------|
| 2 | Core Identity | UniProt entry, function, localization | Full entry |
| 3 | Structure | PDB, AlphaFold, InterPro domains | >=5 PDB OR AlphaFold |
| 4 | Pathways | Reactome, WikiPathways, GO | >=10 pathways |
| 5 | PPIs | STRING, IntAct | >=20 interactors |
| 6 | Expression | GTEx, HPA | Top 10 tissues with TPM |
| 7 | Genetics | gnomAD, ClinVar, GWAS | All 4 constraint scores |

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
- 80-100: Tier 1 (Strong validation)
- 60-79: Tier 2 (Good validation)
- 40-59: Tier 3 (Moderate validation)
- 0-39: Tier 4 (Limited validation)

---

## Visualization Module

**Script**: `visualization.py`

Generates matplotlib figures:

| Figure | File | Description |
|--------|------|-------------|
| Validation Score | `validation_score.png` | Bar chart with tier gauge |
| Disease Associations | `disease_associations.png` | Evidence tier bar chart |
| Tissue Expression | `tissue_expression.png` | Expression bar chart |
| Clinical Timeline | `clinical_timeline.png` | Drug development timeline |
| Safety Dashboard | `safety_dashboard.png` | **Critical tissue expression bar chart only** |

**Note**: Safety visualization simplified per optimization requirements.

---

## Report Generator

**Script**: `report_generator.py`

Generates comprehensive markdown report with:

1. **Text summaries** explaining the data (not raw JSON)
2. **Factual data basis** for all content
3. **14 sections** across 3 parts:
   - Part A: Executive Summary (Section 1)
   - Part B: Target Intelligence (Sections 2-8)
   - Part C: Validation Assessment (Sections 9-14)

**Note**: Part D (Synthesis & Recommendations) removed for factual data focus.

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
├── sub_reports/                    # Optional sub-report files
│   ├── target_intelligence.md
│   └── validation_assessment.md
└── phase*.json                     # Intermediate files with data
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
- Final report data completeness section

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