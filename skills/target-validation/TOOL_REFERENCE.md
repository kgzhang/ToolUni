# Target Validation - Tool Reference

Verified tool parameters, known corrections, fallback chains, and modality-specific tool guidance.

---

## Known Parameter Corrections

| Tool | WRONG Parameter | CORRECT Parameter |
|------|-----------------|-------------------|
| `ensembl_lookup_gene` | `id` | `gene_id` (+ `species="homo_sapiens"` REQUIRED) |
| `Reactome_map_uniprot_to_pathways` | `uniprot_id` | `id` |
| `ensembl_get_xrefs` | `gene_id` | `id` |
| `GTEx_get_median_gene_expression` | `gencode_id` only | `gencode_id` + `operation="median"` |
| `OpenTargets_*` | `ensemblID` (uppercase) | `ensemblId` (camelCase) |
| `OpenTargets_get_publications_*` | `ensemblId` | `entityId` |
| `OpenTargets_get_associated_drugs_by_target_ensemblID` | `ensemblId` only | `ensemblId` + `size` (REQUIRED) |
| `MyGene_query_genes` | `q` | `query` |
| `PubMed_search_articles` | returns `{articles: [...]}` | returns **plain list** of dicts |
| `UniProt_get_function_by_accession` | returns dict | returns **list of strings** |
| `HPA_get_rna_expression_by_source` | `ensembl_id` | `gene_name` + `source_type` + `source_name` (ALL required) |
| `alphafold_get_prediction` | `uniprot_accession` | `qualifier` |
| `drugbank_get_safety_*` | simple params | `query`, `case_sensitive`, `exact_match`, `limit` (ALL required) |

---

## Verified Tool Parameters (Quick Reference)

| Tool | Parameters | Notes |
|------|-----------|-------|
| `ensembl_lookup_gene` | `gene_id`, `species` | species="homo_sapiens" REQUIRED; response wrapped in `{status, data, url, content_type}` |
| `OpenTargets_get_*_by_ensemblID` | `ensemblId` | camelCase, NOT ensemblID |
| `OpenTargets_get_publications_by_target_ensemblID` | `entityId` | NOT ensemblId |
| `OpenTargets_get_associated_drugs_by_target_ensemblID` | `ensemblId`, `size` | size is REQUIRED |
| `OpenTargets_target_disease_evidence` | `efoId`, `ensemblId` | Both REQUIRED |
| `GTEx_get_median_gene_expression` | `operation`, `gencode_id` | operation="median" REQUIRED |
| `HPA_get_rna_expression_by_source` | `gene_name`, `source_type`, `source_name` | ALL 3 required |
| `PubMed_search_articles` | `query`, `limit` | Returns plain list, NOT {articles:[]} |
| `UniProt_get_function_by_accession` | `accession` | Returns list of strings |
| `alphafold_get_prediction` | `qualifier` | NOT uniprot_accession |
| `drugbank_get_safety_*` | `query`, `case_sensitive`, `exact_match`, `limit` | ALL required |
| `STRING_get_protein_interactions` | `protein_ids`, `species` | protein_ids is array; species=9606 |
| `Reactome_map_uniprot_to_pathways` | `id` | NOT uniprot_id |
| `ChEMBL_get_target_activities` | `target_chembl_id__exact` | Note double underscore |
| `search_clinical_trials` | `query_term` | REQUIRED parameter |
| `gnomad_get_gene_constraints` | `gene_symbol` | NOT gene_id |
| `DepMap_get_gene_dependencies` | `gene_symbol` | NOT gene_id |
| `BindingDB_get_ligands_by_uniprot` | `uniprot`, `affinity_cutoff` | affinity in nM |
| `Pharos_get_target` | `gene` or `uniprot` | Both optional but need one |

---

## Phase-by-Phase Tool Lists

### Phase 0: Target Disambiguation

| Tool | Purpose | Required Parameters |
|------|---------|---------------------|
| `MyGene_query_genes` | Initial ID resolution | `query` |
| `UniProt_get_entry_by_accession` | Protein details | `accession` |
| `ensembl_lookup_gene` | Ensembl ID + version | `gene_id`, `species="homo_sapiens"` |
| `ensembl_get_xrefs` | Cross-references | `id` |
| `OpenTargets_get_target_id_description_by_name` | OT target info | `name` |
| `ChEMBL_search_targets` | ChEMBL target ID | `query` |
| `UniProt_get_function_by_accession` | Function summary | `accession` |
| `UniProt_get_alternative_names_by_accession` | Collision detection | `accession` |
| `GPCRdb_get_protein` | GPCR detection | `protein` (format: `symbol_human`) |

### Phase 1: Open Targets Foundation

| Tool | Purpose | Required Parameters |
|------|---------|---------------------|
| `OpenTargets_get_diseases_phenotypes_by_target_ensemblId` | Disease associations | `ensemblId` |
| `OpenTargets_get_target_tractability_by_ensemblId` | Tractability | `ensemblId` |
| `OpenTargets_get_target_safety_profile_by_ensemblId` | Safety liabilities | `ensemblId` |
| `OpenTargets_get_target_interactions_by_ensemblId` | PPI network | `ensemblId` |
| `OpenTargets_get_target_gene_ontology_by_ensemblId` | GO annotations | `ensemblId` |
| `OpenTargets_get_publications_by_target_ensemblId` | Literature | `entityId` |
| `OpenTargets_get_biological_mouse_models_by_ensemblId` | KO phenotypes | `ensemblId` |
| `OpenTargets_get_chemical_probes_by_target_ensemblId` | Chemical probes | `ensemblId` |
| `OpenTargets_get_associated_drugs_by_target_ensemblId` | Known drugs | `ensemblId`, `size` |

### Phase 3: Structure & Domains

| Tool | Purpose | Required Parameters |
|------|---------|---------------------|
| `UniProt_get_entry_by_accession` | PDB cross-references | `accession` |
| `get_protein_metadata_by_pdb_id` | PDB metadata | `pdb_id` |
| `PDB_search_similar_structures` | Sequence-based search | `sequence`, `identity_cutoff` |
| `alphafold_get_prediction` | AlphaFold structure | `qualifier` |
| `alphafold_get_summary` | pLDDT confidence | `qualifier` |
| `InterPro_get_protein_domains` | Domain architecture | `uniprot_accession` |
| `ProteinsPlus_predict_binding_sites` | Pocket detection | `pdb_id` |
| `GPCRdb_get_structures` | GPCR structures | `protein` |

### Phase 4: Function & Pathways

| Tool | Purpose | Required Parameters |
|------|---------|---------------------|
| `GO_get_annotations_for_gene` | GO terms | `gene_id` |
| `Reactome_map_uniprot_to_pathways` | Reactome pathways | `id` (NOT `uniprot_id`) |
| `kegg_get_gene_info` | KEGG pathways | `gene_id` |
| `WikiPathways_search` | WikiPathways | `query` |
| `enrichr_gene_enrichment_analysis` | Enrichment | `gene_list` |

### Phase 5: Protein Interactions

| Tool | Purpose | Required Parameters |
|------|---------|---------------------|
| `STRING_get_protein_interactions` | PPI network | `protein_ids` (list), `species=9606` |
| `intact_get_interactions` | Experimental PPI | `identifier` (UniProt accession) |
| `intact_get_complex_details` | Complexes | `complex_ac` |
| `BioGRID_get_interactions` | Literature PPI | `gene_symbol` |

### Phase 6: Expression Profile

| Tool | Purpose | Required Parameters |
|------|---------|---------------------|
| `GTEx_get_median_gene_expression` | Tissue expression | `gencode_id`, `operation="median"` |
| `HPA_get_rna_expression_by_source` | HPA RNA | `gene_name`, `source_type`, `source_name` |
| `HPA_get_comprehensive_gene_details_by_ensembl_id` | Comprehensive HPA | `ensembl_id` |
| `HPA_get_subcellular_location` | Localization | `ensembl_id` |
| `HPA_get_cancer_prognostics_by_gene` | Cancer prognostics | `gene_name` |
| `CELLxGENE_get_expression_data` | Single-cell | `gene` |

### Phase 7: Genetic Variation

| Tool | Purpose | Required Parameters |
|------|---------|---------------------|
| `gnomad_get_gene_constraints` | Constraint scores | `gene_symbol` |
| `clinvar_search_variants` | Clinical variants | `gene` |
| `DisGeNET_search_gene` | Gene-disease | `gene`, `limit` |
| `civic_get_variants_by_gene` | CIViC variants | `gene_symbol` |
| `cBioPortal_get_mutations` | Cancer mutations | `gene_symbol` |

### Phase 8: Disease Association Scoring

| Tool | Purpose | Required Parameters |
|------|---------|---------------------|
| `OpenTargets_target_disease_evidence` | Detailed evidence | `efoId`, `ensemblId` |
| `OpenTargets_get_evidence_by_datasource` | Evidence by source | `ensemblId`, `efoId`, `datasource` |
| `gwas_get_snps_for_gene` | GWAS SNPs | `gene` |
| `gwas_search_studies` | GWAS studies | `query` |

### Phase 9: Druggability Assessment

| Tool | Purpose | Required Parameters |
|------|---------|---------------------|
| `OpenTargets_get_target_tractability_by_ensemblId` | Tractability | `ensemblId` |
| `OpenTargets_get_target_classes_by_ensemblId` | Target class | `ensemblId` |
| `Pharos_get_target` | TDL classification | `gene` or `uniprot` |
| `DGIdb_get_gene_druggability` | Druggability | `genes` |
| `BindingDB_get_ligands_by_uniprot` | Ligands | `uniprot`, `affinity_cutoff` |
| `PubChem_search_assays_by_target_gene` | HTS assays | `gene_symbol` |
| `ChEMBL_get_target_activities` | Bioactivity | `target_chembl_id__exact` |

### Phase 10: Safety Deep Analysis

| Tool | Purpose | Required Parameters |
|------|---------|---------------------|
| `OpenTargets_get_target_safety_profile_by_ensemblId` | Safety liabilities | `ensemblId` |
| `OpenTargets_get_biological_mouse_models_by_ensemblId` | KO phenotypes | `ensemblId` |
| `OpenTargets_get_target_homologues_by_ensemblId` | Paralogs | `ensemblId` |
| `FDA_get_adverse_reactions_by_drug_name` | ADRs | `drug_name` |
| `FDA_get_boxed_warning_info_by_drug_name` | Black box | `drug_name` |

### Phase 11: Clinical Precedent

| Tool | Purpose | Required Parameters |
|------|---------|---------------------|
| `OpenTargets_get_associated_drugs_by_target_ensemblId` | Known drugs | `ensemblId`, `size` |
| `search_clinical_trials` | Clinical trials | `query_term` |
| `FDA_get_mechanism_of_action_by_drug_name` | MoA | `drug_name` |
| `FDA_get_indications_by_drug_name` | Indications | `drug_name` |
| `drugbank_get_targets_by_drug_name_or_drugbank_id` | DrugBank | `query`, `case_sensitive`, `exact_match`, `limit` |

### Phase 12: Literature Intelligence

| Tool | Purpose | Required Parameters |
|------|---------|---------------------|
| `PubMed_search_articles` | PubMed search | `query`, `limit` |
| `EuropePMC_search_articles` | EuropePMC | `query`, `limit` |
| `PubTator3_LiteratureSearch` | PubTator3 | `keyword` |
| `openalex_search_works` | Citation metrics | `search` |

---

## Fallback Chains

| Primary Tool | Fallback 1 | Fallback 2 | If All Fail |
|--------------|------------|------------|-------------|
| `OpenTargets_get_diseases_phenotypes_*` | `CTD_get_gene_diseases` | PubMed search | Note in report |
| `GTEx_get_median_gene_expression` (versioned) | GTEx (unversioned) | `HPA_search_genes_by_query` | Document gap |
| `ChEMBL_get_target_activities` | `BindingDB_get_ligands_by_uniprot` | `DGIdb_get_gene_info` | Note in report |
| `gnomad_get_gene_constraints` | `OpenTargets_get_target_constraint_info_*` | - | Note as unavailable |
| `Reactome_map_uniprot_to_pathways` | `OpenTargets_get_target_gene_ontology_*` | - | Use GO only |
| `STRING_get_protein_interactions` | `intact_get_interactions` | `OpenTargets interactions` | Note in report |
| `ProteinsPlus_predict_binding_sites` | `alphafold_get_prediction` | Literature pockets | Note as limited |

---

## Modality-Specific Tool Focus

### Small Molecule
- **Emphasize**: binding pockets, ChEMBL compounds, Lipinski compliance
- **Key tractability**: OpenTargets SM tractability bucket
- **Structure**: co-crystal structures with small molecule ligands
- **Chemical matter**: IC50/Ki/Kd data from ChEMBL/BindingDB

### Antibody
- **Emphasize**: extracellular domains, cell surface expression, glycosylation
- **Key tractability**: OpenTargets AB tractability bucket
- **Structure**: ectodomain structures, epitope mapping
- **Expression**: surface expression in disease vs normal tissue

### PROTAC
- **Emphasize**: intracellular targets, surface lysines, E3 ligase proximity
- **Key tractability**: OpenTargets PROTAC tractability
- **Structure**: full-length structures for linker design
- **Chemical matter**: known binders + E3 ligase binders

---

## Response Format Handling

Three formats tools may return:
- **Standard**: `{status: "success", data: [...]}`
- **Direct list**: `[...]` without wrapper
- **Direct dict**: `{field1: ..., field2: ...}` without status

Handle all three with `isinstance()` checks in implementation.

---

## GTEx Versioned ID Fallback

GTEx often requires versioned Ensembl IDs. If `ENSG00000123456` returns empty, try `ENSG00000123456.{version}` from `ensembl_lookup_gene`.

```python
# Fallback logic
if ids['ensembl']:
    gene_info = tu.tools.ensembl_lookup_gene(gene_id=ids['ensembl'], species="homo_sapiens")
    if gene_info and gene_info.get('version'):
        ids['ensembl_versioned'] = f"{ids['ensembl']}.{gene_info['version']}"
```

---

## SOAP Tools

Some tools require `operation` parameter for SOAP services:
- `GPCRdb_get_protein` - requires `operation="get_protein"`
- `GPCRdb_get_structures` - requires `operation="get_structures"`
- `GPCRdb_get_ligands` - requires `operation="get_ligands"`
- `DisGeNET_search_gene` - requires `operation="search_gene"`

Always include `operation` parameter when calling SOAP-based tools.