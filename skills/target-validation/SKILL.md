---
name: target-validation
description: Comprehensive target validation assistant - from biological intelligence to validation decisions in one assessment. Integrates protein information, disease associations, druggability, safety, and clinical data to generate quantitative scoring (0-100) with GO/NO-GO recommendations. Auto-discovers disease associations, supports multi-modality assessment (small molecule/antibody/PROTAC), outputs integrated report and structured data. Use for target validation, prioritization, competitive analysis.
---

# Target Validation Pipeline

Validate drug target hypotheses using multi-dimensional computational evidence before committing to wet-lab work. Produces a quantitative Target Validation Score (0-100) with priority tier classification and GO/NO-GO recommendation.

## Key Principles

1. **Report-first** - Create report file FIRST, then populate progressively
2. **Target disambiguation FIRST** - Resolve all identifiers before analysis
3. **Evidence grading** - Grade all evidence as T1 (clinical proof) to T4 (computational)
4. **Auto disease discovery** - Automatically identify top associated diseases
5. **Modality-aware** - Consider small molecule vs antibody vs PROTAC tractability
6. **Safety-first** - Prominently flag safety concerns early
7. **Quantitative scoring** - Every dimension scored numerically (0-100 composite)
8. **Negative results documented** - "No data" is data; empty sections are failures
9. **Source references** - Every statement must cite tool/database
10. **English-first queries** - Always use English terms in tool calls; respond in user's language

---

## When to Use This Skill

**Triggers**:
- "Is [target] a good drug target?"
- Target validation, druggability assessment, or target prioritization
- Safety risks of modulating a target
- Chemical starting points for target validation
- GO/NO-GO recommendation for a target

**Use Cases**:
1. **Full Target Assessment**: Comprehensive evaluation from biology to validation decision
2. **Disease-Specific Validation**: Assess target suitability for specific indication
3. **Modality Selection**: Compare tractability across small molecule/antibody/PROTAC
4. **Competitive Analysis**: Understand clinical landscape and differentiation opportunities
5. **Risk Assessment**: Identify safety liabilities and mitigation strategies

**Not for** (use other skills):
- General target biology only → `tooluniverse-target-research`
- Drug compound profiling → `tooluniverse-drug-research`
- Variant interpretation → `tooluniverse-variant-interpretation`
- Disease research → `tooluniverse-disease-research`

---

## Input Parameters

| Parameter | Required | Type | Description | Example |
|-----------|----------|------|-------------|---------|
| **target** | Yes | string | Gene symbol, protein name, or UniProt ID | `EGFR`, `P00533`, `KRAS` |
| **modality** | No | string | Preferred therapeutic modality | `small molecule`, `antibody`, `PROTAC`, `all` (default) |
| **disease** | No | string | Disease context for targeted analysis | `Non-small cell lung cancer` |
| **output_format** | No | string | Output format preference | `markdown` (default), `json`, `both` |

---

## Workflow Overview

```
Stage 1: Foundation
Phase 0: Target Disambiguation → Phase 1: Open Targets Foundation → Phase 2: Core Identity

Stage 2: Biological Intelligence
Phase 3: Structure & Domains → Phase 4: Function & Pathways → Phase 5: Protein Interactions
Phase 6: Expression Profile → Phase 7: Genetic Variation

Stage 3: Validation Assessment
Phase 8: Disease Scoring → Phase 9: Druggability → Phase 10: Safety Deep Analysis
Phase 11: Clinical Precedent → Phase 12: Literature Intelligence

Stage 4: Synthesis
Phase 13: Composite Scoring → Phase 14: Validation Roadmap

Output: Integrated Report + Structured JSON
```

---

## Stage 1: Foundation

### Phase 0: Target Disambiguation (ALWAYS FIRST)

Resolve target to ALL identifiers before any analysis.

**Tools**:
- `MyGene_query_genes` - Get initial IDs (Ensembl, UniProt, Entrez)
- `ensembl_lookup_gene` - Get versioned Ensembl ID (species="homo_sapiens" REQUIRED)
- `ensembl_get_xrefs` - Cross-references (HGNC, etc.)
- `OpenTargets_get_target_id_description_by_name` - Verify OT target
- `ChEMBL_search_targets` - Get ChEMBL target ID
- `UniProt_get_function_by_accession` - Function summary
- `UniProt_get_alternative_names_by_accession` - Collision detection
- `GPCRdb_get_protein` - Detect if GPCR for specialized handling

**Output**: Table of verified identifiers (Gene Symbol, Ensembl, UniProt, Entrez, ChEMBL, HGNC) plus protein function and target class.

### Phase 1: Open Targets Foundation

Populates baseline data for all subsequent phases.

**Tools**:
- `OpenTargets_get_diseases_phenotypes_by_target_ensemblId` - Disease associations (for auto-discovery)
- `OpenTargets_get_target_tractability_by_ensemblId` - Tractability assessment
- `OpenTargets_get_target_safety_profile_by_ensemblId` - Safety liabilities
- `OpenTargets_get_target_interactions_by_ensemblId` - PPI network
- `OpenTargets_get_target_gene_ontology_by_ensemblId` - GO annotations
- `OpenTargets_get_publications_by_target_ensemblId` - Literature
- `OpenTargets_get_biological_mouse_models_by_ensemblId` - KO phenotypes
- `OpenTargets_get_chemical_probes_by_target_ensemblId` - Chemical probes
- `OpenTargets_get_associated_drugs_by_target_ensemblId` - Known drugs

**Auto Disease Discovery**: If no disease provided, extract top 3 diseases by association score for parallel evaluation.

### Phase 2: Core Identity

**Tools**:
- `UniProt_get_entry_by_accession` - Complete protein entry
- `UniProt_get_function_by_accession` - Functional description
- `UniProt_get_recommended_name_by_accession` - Recommended name
- `UniProt_get_alternative_names_by_accession` - Synonyms
- `UniProt_get_subcellular_location_by_accession` - Localization
- `MyGene_get_gene_annotation` - Gene annotation

**Populates**: Sections 1-3 (Identifiers, Basic Information, Function)

---

## Stage 2: Biological Intelligence

### Phase 3: Structure & Domains

Use 3-step structure search chain (do NOT rely solely on PDB text search):
1. UniProt PDB cross-references (most reliable)
2. Sequence-based PDB search (catches missing annotations)
3. AlphaFold (always check)
4. Domain architecture

**Tools**:
- `UniProt_get_entry_by_accession` - PDB cross-references
- `get_protein_metadata_by_pdb_id` - PDB metadata
- `PDB_search_similar_structures` - Sequence-based search
- `alphafold_get_prediction` - AlphaFold structure
- `alphafold_get_summary` - pLDDT confidence
- `InterPro_get_protein_domains` - Domain architecture
- `ProteinsPlus_predict_binding_sites` - Druggable pockets

**GPCR targets**: Also query `GPCRdb_get_structures` for active/inactive state data.

### Phase 4: Function & Pathways

**Tools**:
- `GO_get_annotations_for_gene` - GO terms
- `Reactome_map_uniprot_to_pathways` - Reactome pathways (param: `id`, NOT `uniprot_id`)
- `kegg_get_gene_info` - KEGG pathways
- `WikiPathways_search` - WikiPathways
- `enrichr_gene_enrichment_analysis` - Enrichment analysis

### Phase 5: Protein Interactions

**Tools**:
- `STRING_get_protein_interactions` - Predicted + experimental PPIs
- `intact_get_interactions` - Experimentally validated interactions
- `intact_get_complex_details` - Protein complexes
- `BioGRID_get_interactions` - Literature-curated interactions

**Minimum**: 20 interactors OR documented explanation.

### Phase 6: Expression Profile

GTEx with versioned ID fallback + HPA as backup.

**Tools**:
- `GTEx_get_median_gene_expression` - Tissue expression (requires `operation="median"`)
- `HPA_get_rna_expression_by_source` - HPA RNA expression
- `HPA_get_comprehensive_gene_details_by_ensembl_id` - Comprehensive HPA data
- `HPA_get_subcellular_location` - Protein localization
- `HPA_get_cancer_prognostics_by_gene` - Cancer prognostics
- `CELLxGENE_get_expression_data` - Single-cell expression

### Phase 7: Genetic Variation & Disease

**Tools**:
- `gnomad_get_gene_constraints` - Constraint scores (pLI, LOEUF, missense Z, pRec)
- `clinvar_search_variants` - Clinical variants
- `OpenTargets_get_diseases_phenotypes_by_target_ensembl` - Disease associations
- `DisGeNET_search_gene` - Curated gene-disease associations
- `civic_get_variants_by_gene` - Clinical variants (CIViC)
- `cBioPortal_get_mutations` - Cancer mutations

**Required**: All 4 constraint scores (pLI, LOEUF, missense Z, pRec).

---

## Stage 3: Validation Assessment

### Phase 8: Disease Association Scoring (0-30 pts)

Quantify target-disease association from genetic, literature, and pathway evidence.

**Sub-scores**:
- Genetic evidence (0-10): GWAS, rare variants, somatic mutations
- Literature evidence (0-10): Publication count and quality
- Pathway evidence (0-10): OpenTargets association score

**Tools**:
- `OpenTargets_target_disease_evidence` - Detailed evidence
- `OpenTargets_get_evidence_by_datasource` - Evidence by source
- `gwas_get_snps_for_gene` - GWAS associations
- `gwas_search_studies` - GWAS studies

### Phase 9: Druggability Assessment (0-25 pts)

Assess whether the target is amenable to therapeutic intervention.

**Sub-scores**:
- Structural tractability (0-10): Structure quality, binding pockets
- Chemical matter (0-10): Known compounds, bioactivity data
- Target class bonus (0-5): Validated target family

**Tools**:
- `OpenTargets_get_target_tractability_by_ensemblId` - Tractability buckets
- `OpenTargets_get_target_classes_by_ensemblId` - Target classification
- `Pharos_get_target` - TDL: Tclin > Tchem > Tbio > Tdark
- `DGIdb_get_gene_druggability` - Druggability categories
- `alphafold_get_prediction` / `alphafold_get_summary` - Structure prediction
- `ProteinsPlus_predict_binding_sites` - Pocket detection
- `OpenTargets_get_chemical_probes_by_target_ensemblId` - Chemical probes

### Phase 10: Safety Deep Analysis (0-20 pts)

Comprehensive safety assessment from multiple sources.

**Sub-scores**:
- Tissue expression selectivity (0-5): Expression in critical tissues
- Genetic validation (0-10): Knockout phenotypes, human genetics
- Known adverse events (0-5): Safety signals from modulators

**Tools**:
- `OpenTargets_get_target_safety_profile_by_ensemblId` - Safety liabilities
- `GTEx_get_median_gene_expression` - Tissue expression
- `HPA_get_comprehensive_gene_details_by_ensembl_id` - HPA data
- `OpenTargets_get_biological_mouse_models_by_ensemblId` - KO phenotypes
- `FDA_get_adverse_reactions_by_drug_name` - ADRs from approved drugs
- `FDA_get_boxed_warning_info_by_drug_name` - Black box warnings
- `OpenTargets_get_target_homologues_by_ensemblId` - Paralog risks

**Critical tissues**: heart, liver, kidney, brain, bone marrow.

### Phase 11: Clinical Precedent (0-15 pts)

Assess clinical validation from approved drugs and clinical trials.

**Tools**:
- `OpenTargets_get_associated_drugs_by_target_ensemblId` - Known drugs
- `FDA_get_mechanism_of_action_by_drug_name` - FDA MoA
- `FDA_get_indications_by_drug_name` - FDA indications
- `drugbank_get_targets_by_drug_name_or_drugbank_id` - DrugBank targets
- `search_clinical_trials` - Clinical trials
- `ChEMBL_search_mechanisms` - Drug mechanisms

### Phase 12: Literature Intelligence

Comprehensive collision-aware literature analysis.

**Tools**:
- `PubMed_search_articles` - PubMed search
- `EuropePMC_search_articles` - Broader coverage
- `PubTator3_LiteratureSearch` - Literature search
- `openalex_search_works` - Citation metrics
- `OpenTargets_get_publications_by_target_ensemblId` - OT publications

**Collision detection**: Search gene symbol in title; if >20% off-topic, add filters (AND protein OR gene).

---

## Stage 4: Synthesis

### Phase 13: Composite Scoring

Calculate total score (0-100), assign tier, generate GO/NO-GO.

**Score Calculation**:
```
Total = Disease (0-30) + Druggability (0-25) + Safety (0-20) + Clinical (0-15) + Validation (0-10)
```

**Priority Tiers**:
| Score | Tier | Recommendation |
|-------|------|----------------|
| 80-100 | Tier 1 | GO - Highly validated |
| 60-79 | Tier 2 | CONDITIONAL GO |
| 40-59 | Tier 3 | CAUTION |
| 0-39 | Tier 4 | NO-GO |

### Phase 14: Validation Roadmap

Generate actionable recommendations:
1. Recommended validation experiments
2. Tool compounds for testing
3. Biomarker strategy
4. Key risks and mitigations

---

## Modality-Specific Assessment

| Modality | Focus Areas | Tractability Check |
|----------|-------------|-------------------|
| `small molecule` | Binding pockets, oral tractability buckets 1-7 | SM tractability + high-res co-crystal bonus |
| `antibody` | Surface accessibility, extracellular domain | AB tractability + cell surface expression |
| `PROTAC` | Ligandability, E3 recruitment, lysines | Known binders + intracellular location |
| `all` | Report all scores, highlight best | Compare across modalities |

---

## Evidence Grading System

| Tier | Symbol | Criteria | Examples |
|------|--------|----------|----------|
| **T1** | ⭐⭐⭐ | Direct mechanistic, human clinical proof | FDA-approved drug, crystal structure, patient mutation |
| **T2** | ⭐⭐ | Functional studies, model organism | siRNA phenotype, mouse KO, biochemical assay |
| **T3** | ⭐ | Association, screen hits, computational | GWAS hit, DepMap essentiality, expression correlation |
| **T4** | - | Mention, review, predicted | Review article, database annotation, AlphaFold |

See [EVIDENCE_GRADING.md](EVIDENCE_GRADING.md) for detailed tier definitions.

---

## Report Output

Create file: `[TARGET]_validation_report.md`

Use the full template from [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md). Key sections:
- Executive Summary (score, tier, recommendation, key findings)
- Part A: Target Intelligence (7 sections)
- Part B: Validation Assessment (6 sections)
- Part C: Synthesis & Recommendations (4 sections)
- Appendices (data sources, completeness, gaps, JSON)

---

## Tool Parameter Reference

**Critical Parameter Corrections**:

| Tool | WRONG Parameter | CORRECT Parameter |
|------|-----------------|-------------------|
| `Reactome_map_uniprot_to_pathways` | `uniprot_id` | `id` |
| `ensembl_get_xrefs` | `gene_id` | `id` |
| `GTEx_get_median_gene_expression` | `gencode_id` only | `gencode_id` + `operation="median"` |
| `OpenTargets_*` | `ensemblID` | `ensemblId` (camelCase) |
| `STRING_get_protein_interactions` | single ID | `protein_ids` (list), `species` |
| `intact_get_interactions` | gene symbol | `identifier` (UniProt accession) |
| `OpenTargets_get_associated_drugs_by_target_ensemblID` | `ensemblId` only | `ensemblId` + `size` (REQUIRED) |

See [TOOL_REFERENCE.md](TOOL_REFERENCE.md) for complete reference.

---

## Fallback Strategies

| Primary Tool | Fallback 1 | Fallback 2 |
|--------------|------------|------------|
| `ChEMBL_get_target_activities` | `GtoPdb_get_target_ligands` | `OpenTargets drugs` |
| `intact_get_interactions` | `STRING_get_protein_interactions` | `OpenTargets interactions` |
| `GO_get_annotations_for_gene` | `OpenTargets GO` | `MyGene GO` |
| `GTEx_get_median_gene_expression` | `HPA_get_rna_expression` | Document as unavailable |
| `gnomad_get_gene_constraints` | `OpenTargets constraint` | - |

**NEVER silently skip failed tools.** Document failures and fallbacks.

---

## Reference Files

| File | Contents |
|------|----------|
| [SCORING_CRITERIA.md](SCORING_CRITERIA.md) | Detailed scoring matrices, evidence grading, priority tiers |
| [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md) | Full report template with all sections |
| [TOOL_REFERENCE.md](TOOL_REFERENCE.md) | Complete tool reference with parameters |
| [EVIDENCE_GRADING.md](EVIDENCE_GRADING.md) | T1-T4 tier definitions, citation format |
| [IMPLEMENTATION.md](IMPLEMENTATION.md) | Python code for each phase |
| [EXAMPLES.md](EXAMPLES.md) | Worked examples (EGFR, KRAS, novel target) |