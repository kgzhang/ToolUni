# Target Validation Skill Integration Design

**Date**: 2026-03-17
**Author**: Claude Code
**Status**: Design Complete

---

## Overview

This document defines the design for integrating two existing ToolUniverse skills:
- `tooluniverse-target-research`: Comprehensive biological target intelligence gathering
- `tooluniverse-drug-target-validation`: Quantitative target validation scoring

The integrated skill `target-validation` provides one-stop target assessment from biological intelligence to validation decisions.

---

## Design Requirements Summary

| Requirement | Decision |
|-------------|----------|
| Use Case | Full assessment - one-stop for all needs |
| Disease Parameter | Auto-discover from target associations |
| Scoring System | Preserve full quantitative scoring (0-100) |
| Report Structure | Integrated/fused report with logical flow |
| Modality Support | Support small molecule, antibody, PROTAC specific assessment |
| Advanced Features | Safety deep analysis + Structured JSON output + Experimental recommendations |

---

## Skill Metadata

```yaml
name: tooluniverse-target-validation
description: Comprehensive target validation assistant - from biological intelligence to validation decisions in one assessment. Integrates protein information, disease associations, druggability, safety, and clinical data to generate quantitative scoring (0-100) with GO/NO-GO recommendations. Auto-discovers disease associations, supports multi-modality assessment (small molecule/antibody/PROTAC), outputs integrated report and structured data. Use for target validation, prioritization, competitive analysis.

trigger:
  - Target validation, druggability assessment, target prioritization
  - "Is X a good drug target?"
  - Comprehensive target profiling with decision support

not_for:
  - Simple protein lookup → tooluniverse-target-research
  - Drug compound profiling → tooluniverse-drug-research
  - Variant interpretation → tooluniverse-variant-interpretation
  - Disease research → tooluniverse-disease-research
```

---

## Input Parameters

| Parameter | Required | Type | Description | Example |
|-----------|----------|------|-------------|---------|
| **target** | Yes | string | Gene symbol, protein name, or UniProt ID | `EGFR`, `P00533`, `KRAS` |
| **modality** | No | string | Preferred therapeutic modality | `small molecule`, `antibody`, `PROTAC`, `all` (default) |
| **disease** | No | string | Disease context for targeted analysis | `Non-small cell lung cancer` |
| **output_format** | No | string | Output format preference | `markdown` (default), `json`, `both` |

### Auto-Discovered Disease Handling

When disease parameter is not provided:
1. Query Open Targets for top associated diseases by association score
2. Select top 3 diseases for parallel evaluation
3. Generate comparative validation scores
4. Report highest score as primary recommendation

### Modality-Specific Analysis

| Modality | Focus Areas |
|----------|-------------|
| `small molecule` | Binding pockets, tractability buckets 1-7, oral drug-likeness |
| `antibody` | Surface accessibility, epitope mapping, cell surface expression |
| `PROTAC` | Ligandability, E3 ligase recruitment, degradation potential |
| `all` | Calculate scores for each modality, report all |

---

## Workflow Phases

### Stage 1: Foundation (Phases 0-2)

| Phase | Name | Purpose | Key Tools |
|-------|------|---------|-----------|
| **0** | Target Disambiguation | Resolve all identifiers, detect GPCR/special classes | `MyGene_query_genes`, `UniProt_id_mapping`, `GPCRdb_get_protein` |
| **1** | Open Targets Foundation | Baseline data for all subsequent phases | `OpenTargets_get_diseases_phenotypes_by_target_ensemblId`, `OpenTargets_get_target_tractability_by_ensemblId`, `OpenTargets_get_target_safety_profile_by_ensemblId` |
| **2** | Core Identity | Protein names, function, subcellular location | `UniProt_get_entry_by_accession`, `UniProt_get_function_by_accession` |

### Stage 2: Biological Intelligence (Phases 3-7)

| Phase | Name | Purpose | Key Tools |
|-------|------|---------|-----------|
| **3** | Structure & Domains | PDB structures, AlphaFold, domain architecture | `UniProt_get_entry_by_accession` (PDB xrefs), `alphafold_get_prediction`, `InterPro_get_protein_domains`, `ProteinsPlus_predict_binding_sites` |
| **4** | Function & Pathways | GO terms, pathway involvement | `Reactome_map_uniprot_to_pathways`, `GO_get_annotations_for_gene`, `kegg_get_gene_info` |
| **5** | Protein Interactions | PPI network, complexes | `STRING_get_protein_interactions`, `intact_get_interactions`, `intact_get_complex_details` |
| **6** | Expression Profile | Tissue/cell type expression, specificity | `GTEx_get_median_gene_expression`, `HPA_get_comprehensive_gene_details`, `CELLxGENE_get_expression_data` |
| **7** | Genetic Variation | gnomAD constraints, ClinVar, disease mutations | `gnomad_get_gene_constraints`, `clinvar_search_variants`, `DisGeNET_search_gene`, `civic_get_variants_by_gene` |

### Stage 3: Validation Assessment (Phases 8-12)

| Phase | Name | Purpose | Key Tools |
|-------|------|---------|-----------|
| **8** | Disease Association Scoring | Quantify target-disease links (0-30 pts) | `OpenTargets_target_disease_evidence`, `gwas_get_snps_for_gene`, `gnomad_get_gene_constraints` |
| **9** | Druggability Assessment | Structure, chemical matter, target class (0-25 pts) | `OpenTargets_get_target_tractability`, `Pharos_get_target`, `BindingDB_get_ligands_by_uniprot`, `DGIdb_get_gene_druggability` |
| **10** | Safety Deep Analysis | Expression selectivity, KO phenotypes, ADRs (0-20 pts) | `OpenTargets_get_target_safety_profile`, `OpenTargets_get_biological_mouse_models`, `FDA_get_adverse_reactions`, `OpenTargets_get_target_homologues` |
| **11** | Clinical Precedent | Approved drugs, clinical trials (0-15 pts) | `OpenTargets_get_associated_drugs`, `search_clinical_trials`, `FDA_get_mechanism_of_action`, `drugbank_get_targets_by_drug_name` |
| **12** | Literature Intelligence | Publication metrics, key papers, trends | `PubMed_search_articles`, `EuropePMC_search_articles`, `PubTator3_LiteratureSearch`, `openalex_search_works` |

### Stage 4: Synthesis (Phases 13-14)

| Phase | Name | Purpose | Output |
|-------|------|---------|--------|
| **13** | Composite Scoring | Calculate total score (0-100), assign tier, generate GO/NO-GO | Tier 1-4, recommendation |
| **14** | Validation Roadmap | Recommended experiments, tool compounds, biomarkers | Actionable next steps |

---

## Scoring System

### Composite Score (0-100 Points)

| Dimension | Max Points | Sub-dimensions |
|-----------|------------|----------------|
| **Disease Association** | 30 | Genetic (10) + Literature (10) + Pathway (10) |
| **Druggability** | 25 | Structure (10) + Chemical matter (10) + Target class (5) |
| **Safety Profile** | 20 | Expression (5) + Genetic validation (10) + ADRs (5) |
| **Clinical Precedent** | 15 | Based on highest clinical stage |
| **Validation Evidence** | 10 | Functional studies (5) + Disease models (5) |

### Modality-Specific Adjustments

| Modality | Bonus/Adjustment |
|----------|------------------|
| Small Molecule | +2 for high-res co-crystal; focus on oral tractability |
| Antibody | +2 for surface accessibility; assess extracellular domain |
| PROTAC | +2 for known ligand binders; assess linker sites |
| All | Report all scores, highlight best |

### Priority Tiers

| Score | Tier | Recommendation |
|-------|------|----------------|
| 80-100 | Tier 1 | GO - Highly validated, proceed with confidence |
| 60-79 | Tier 2 | CONDITIONAL GO - Needs focused validation |
| 40-59 | Tier 3 | CAUTION - Significant validation required |
| 0-39 | Tier 4 | NO-GO - Consider alternatives |

### Evidence Grading (T1-T4)

| Tier | Criteria | Examples |
|------|----------|----------|
| T1 | Direct mechanistic, human clinical proof | FDA-approved drug, patient mutation |
| T2 | Functional studies, model organism | siRNA phenotype, mouse KO |
| T3 | Association, screen hits, computational | GWAS hit, DepMap essentiality |
| T4 | Mention, review, predicted | Review article, database annotation |

---

## Report Structure

### Integrated Report Outline

```markdown
# Target Validation Report: [TARGET]

**Generated**: [Date] | **Query**: [Original query] | **Completeness**: [X/14 phases]

## Executive Summary
- Target Validation Score: [XX/100] (Tier [1-4])
- Primary Disease Association: [Disease]
- GO/NO-GO Recommendation: [Recommendation]
- Key Findings (3 bullets)
- Critical Risks

## Part A: Target Intelligence
1. Target Identifiers
2. Basic Information
3. Structural Biology
4. Function & Pathways
5. Protein-Protein Interactions
6. Expression Profile
7. Genetic Variation & Disease Associations

## Part B: Validation Assessment
8. Disease Association Scoring (0-30 pts)
9. Druggability Assessment (0-25 pts)
10. Safety Deep Analysis (0-20 pts)
11. Clinical Precedent (0-15 pts)
12. Validation Evidence (0-10 pts)
13. Validation Scorecard

## Part C: Synthesis & Recommendations
14. Validation Roadmap
15. Tool Compounds for Testing
16. Biomarker Strategy
17. Key Risks & Mitigations

## Appendices
A. Data Sources & Methodology
B. Completeness Checklist
C. Data Gaps & Limitations
D. Structured Data Export (JSON)
```

### Report Principles

1. **Report-First**: Create file with all headers first, populate progressively
2. **Evidence Grading**: Every claim graded T1-T4 with citations
3. **Completeness Audit**: Mandatory checklist before finalizing
4. **Negative Results**: "No data" explicitly documented

---

## Advanced Features

### Safety Deep Analysis

| Analysis | Sources | Output |
|----------|---------|--------|
| Off-target Profiling | STRING paralog network, ChEMBL selectivity | Potential off-targets |
| Tissue Toxicity | GTEx + HPA + OT safety | Organ risk scores |
| ADR Mining | FDA FAERS, drug labels | Known events with frequencies |
| Black Box Check | FDA boxed warnings | Regulatory history |
| Genetic Lethality | Mouse KO (IMPC), human pLI | Essentiality warnings |

### Structured JSON Output

```json
{
  "metadata": {
    "target": "EGFR",
    "uniprot_id": "P00533",
    "ensembl_id": "ENSG00000146648",
    "report_date": "2026-03-17"
  },
  "validation_score": {
    "total": 90,
    "tier": 1,
    "recommendation": "GO",
    "components": {
      "disease_association": {"score": 28, "max": 30},
      "druggability": {"score": 24, "max": 25},
      "safety": {"score": 14, "max": 20},
      "clinical_precedent": {"score": 15, "max": 15},
      "validation_evidence": {"score": 9, "max": 10}
    }
  },
  "diseases": [...],
  "modality_assessment": {...},
  "safety_flags": [...],
  "recommended_actions": [...]
}
```

### Experimental Validation Recommendations

| Gap Type | Recommendation |
|----------|----------------|
| No PPI data | Yeast-2-hybrid or AP-MS study |
| No chemical probes | SGC probe development |
| No KO phenotype | CRISPR screen in disease-relevant cells |
| Limited expression | IHC/ISH validation |

---

## Reference File Structure

| File | Content |
|------|---------|
| `SKILL.md` | Main skill definition, workflow, principles |
| `SCORING_CRITERIA.md` | Point allocations, tier definitions, examples |
| `REPORT_TEMPLATE.md` | Full template, completeness checklist |
| `TOOL_REFERENCE.md` | Verified parameters, corrections, fallbacks |
| `EVIDENCE_GRADING.md` | T1-T4 definitions, citation format |
| `IMPLEMENTATION.md` | Python code for each phase |
| `EXAMPLES.md` | Worked examples (EGFR, KRAS, novel target) |

---

## Inheritance from Source Skills

### From tooluniverse-target-research
- 9 research paths structure
- GPCR special handling
- Collision-aware literature search
- GTEx versioned ID fallback
- ClinVar SNV/CNV separation
- Evidence grading system

### From tooluniverse-drug-target-validation
- Quantitative scoring matrices
- Modality-specific tractability
- Phase-by-phase tool lists
- GO/NO-GO decision framework
- Validation roadmap generation

### New for Integrated Skill
- Auto disease discovery workflow
- Safety deep analysis procedures
- JSON output schema
- Validation experiment recommendations
- Comparative disease scoring

---

## Implementation Approach

The skill will be created using the `create-tooluniverse-skill` workflow with:
1. Test-driven development (example-based tests)
2. Implementation-agnostic design
3. Proper skill structure following ToolUniverse conventions