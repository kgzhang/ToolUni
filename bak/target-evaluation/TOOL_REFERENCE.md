# Target Validation - Tool Reference

Verified tool parameters, known corrections, fallback chains, and modality-specific tool guidance.

---

## CRITICAL Parameter Corrections

These corrections are ESSENTIAL for getting data. Using wrong parameters will return empty results.

| Tool | WRONG Parameter | CORRECT Parameter | Impact |
|------|-----------------|-------------------|--------|
| `UniProt_id_mapping` | `_from`, `to` | `from_db`, `to_db`, `ids` | Returns validation error |
| `Reactome_map_uniprot_to_pathways` | `id` | `uniprot_id` | Returns validation error |
| `GTEx_get_median_gene_expression` | `operation="median"` | `operation="get_median_gene_expression"` | Returns validation error |
| `ensembl_get_xrefs` | `gene_id` | `id` | Returns error |
| `OpenTargets_get_publications_by_target_ensemblId` | `ensemblId` | `entityId` | Returns empty |
| `OpenTargets_get_associated_drugs_by_target_ensemblId` | `ensemblId` only | `ensemblId` + `size` | Returns limited data |
| `OpenTargets_target_disease_evidence` | just `ensemblId` | `ensemblId` + `efoId` | Returns error |
| `STRING_get_protein_interactions` | single ID string | `protein_ids` (list), `species` | Returns error |
| `intact_get_interactions` | gene symbol | `identifier` (UniProt accession) | Returns empty |
| `HPA_get_comprehensive_gene_details_by_ensembl_id` | `ensembl_id` only | `ensembl_id` + `include_images` + `include_antibodies` + `include_expression` | Returns validation error |
| `HPA_get_rna_expression_by_source` | `ensembl_id` | `gene_name` + `source_type` + `source_name` | Returns error |
| `alphafold_get_prediction` | `uniprot_accession` | `qualifier` | Returns error |
| `ChEMBL_get_target_activities` | `target_chembl_id` | `target_chembl_id__exact` | Returns empty |
| `MyGene_query_genes` | `q` | `query` | Returns error |
| `search_clinical_trials` | `query` | `query_term` | Returns error |
| `gnomad_get_gene_constraints` | `gene_id` | `gene_symbol` | Returns error |
| `ensembl_lookup_gene` | `id` | `gene_id` + `species="homo_sapiens"` | Returns error |
| `InterPro_get_protein_domains` | `uniprot_accession` | `protein_id` | Returns validation error |
| `gwas_get_snps_for_gene` | `gene` | `mapped_gene` | Returns validation error |

---

## Response Format Handling

Tools return THREE different formats. Always handle all cases:

```python
def handle_response(result):
    if result is None:
        return None

    # Format 1: Standard wrapper with status
    if isinstance(result, dict):
        if 'status' in result:
            if result['status'] == 'error':
                return None
            return result.get('data', result.get('content', result))
        if 'data' in result:
            return result['data']
        return result  # Direct dict

    # Format 2: Direct list
    if isinstance(result, list):
        return result

    # Format 3: Other
    return result
```

### Known Response Formats by Tool

| Tool | Response Format | Notes |
|------|-----------------|-------|
| `MyGene_query_genes` | Direct list or `{data: [...]}` | Check both |
| `UniProt_get_function_by_accession` | **List of strings** | NOT dict! |
| `PubMed_search_articles` | **Direct list** | NOT `{articles: [...]}` |
| `OpenTargets_get_*` | `{data: [...]}` | Standard wrapper |
| `GTEx_get_median_gene_expression` | `{data: [...]}` | Standard wrapper |
| `gnomad_get_gene_constraints` | Direct dict | No wrapper |
| `ChEMBL_get_target_activities` | `{compounds: [...]}` or `{data: [...]}` | Check both |

---

## Phase-by-Phase Tool Reference

### Phase 0: Target Disambiguation

| Tool | Purpose | Required Parameters | Response Format |
|------|---------|---------------------|-----------------|
| `MyGene_query_genes` | Initial ID resolution | `query` (NOT `q`), `limit` | List or `{data: [...]}` |
| `UniProt_id_mapping` | UniProt ID mapping | **`from_db`**, **`to_db`**, `ids` | `{results: [...]}` |
| `ensembl_lookup_gene` | Ensembl ID + version | `gene_id` (NOT `id`), `species="homo_sapiens"` | `{status, data, ...}` |
| `ensembl_get_xrefs` | Cross-references | `id` (NOT `gene_id`) | `{status, data, ...}` |
| `ChEMBL_search_targets` | ChEMBL target ID | `query` | `{targets: [...]}` |
| `UniProt_get_function_by_accession` | Function summary | `accession` | **List of strings** |
| `UniProt_get_alternative_names_by_accession` | Synonyms | `accession` | List |
| `GPCRdb_get_protein` | GPCR detection | `operation="get_protein"`, `protein` | `{status, ...}` |

### Phase 1: Open Targets Foundation

| Tool | Purpose | Required Parameters | Notes |
|------|---------|---------------------|-------|
| `OpenTargets_get_diseases_phenotypes_by_target_ensemblId` | Disease associations | `ensemblId` | Standard |
| `OpenTargets_get_target_tractability_by_ensemblId` | Tractability | `ensemblId` | Standard |
| `OpenTargets_get_target_safety_profile_by_ensemblId` | Safety liabilities | `ensemblId` | Standard |
| `OpenTargets_get_target_interactions_by_ensemblId` | PPI network | `ensemblId` | Standard |
| `OpenTargets_get_target_gene_ontology_by_ensemblId` | GO annotations | `ensemblId` | Standard |
| `OpenTargets_get_publications_by_target_ensemblId` | Literature | **`entityId`** (NOT `ensemblId`) | CRITICAL! |
| `OpenTargets_get_biological_mouse_models_by_ensemblId` | KO phenotypes | `ensemblId` | Standard |
| `OpenTargets_get_chemical_probes_by_target_ensemblId` | Chemical probes | `ensemblId` | Standard |
| `OpenTargets_get_associated_drugs_by_target_ensemblId` | Known drugs | `ensemblId`, **`size`** | size REQUIRED |
| `OpenTargets_get_target_classes_by_ensemblId` | Target class | `ensemblId` | Standard |
| `OpenTargets_get_target_homologues_by_ensemblId` | Paralogs | `ensemblId` | Standard |
| `OpenTargets_target_disease_evidence` | Detailed evidence | **`ensemblId` + `efoId`** | BOTH required |

### Phase 3: Structure & Domains

| Tool | Purpose | Required Parameters | Notes |
|------|---------|---------------------|-------|
| `UniProt_get_entry_by_accession` | PDB cross-refs | `accession` | Contains PDB refs |
| `get_protein_metadata_by_pdb_id` | PDB metadata | `pdb_id` | Standard |
| `PDB_search_similar_structures` | Sequence-based search | `sequence`, `identity_cutoff` | Standard |
| `alphafold_get_prediction` | AlphaFold structure | **`qualifier`** | NOT `uniprot_accession` |
| `alphafold_get_summary` | pLDDT confidence | **`qualifier`** | NOT `uniprot_accession` |
| `InterPro_get_protein_domains` | Domain architecture | **`protein_id`** (NOT `uniprot_accession`) | CRITICAL! |
| `ProteinsPlus_predict_binding_sites` | Pocket detection | `pdb_id` | Standard |
| `GPCRdb_get_structures` | GPCR structures | `operation="get_structures"`, `protein` | SOAP tool |

### Phase 4: Function & Pathways

| Tool | Purpose | Required Parameters | Notes |
|------|---------|---------------------|-------|
| `GO_get_annotations_for_gene` | GO terms | `gene_id` | Standard |
| `Reactome_map_uniprot_to_pathways` | Reactome pathways | **`uniprot_id`** (NOT `id`) | CRITICAL! |
| `kegg_get_gene_info` | KEGG pathways | `gene_id` | Standard |
| `WikiPathways_search` | WikiPathways | `query` | Standard |
| `enrichr_gene_enrichment_analysis` | Enrichment | `gene_list` | Standard |

### Phase 5: Protein Interactions

| Tool | Purpose | Required Parameters | Notes |
|------|---------|---------------------|-------|
| `STRING_get_protein_interactions` | PPI network | **`protein_ids` (list)**, `species=9606` | LIST format! |
| `intact_get_interactions` | Experimental PPI | `identifier` (UniProt accession) | UniProt ID |
| `intact_get_complex_details` | Complexes | `complex_ac` | Standard |
| `BioGRID_get_interactions` | Literature PPI | `gene_symbol` | Standard |

### Phase 6: Expression Profile

| Tool | Purpose | Required Parameters | Notes |
|------|---------|---------------------|-------|
| `GTEx_get_median_gene_expression` | Tissue expression | `gencode_id`, **`operation="get_median_gene_expression"`** | BOTH required |
| `HPA_get_rna_expression_by_source` | HPA RNA | **`gene_name` + `source_type` + `source_name`** | ALL 3 required |
| `HPA_get_comprehensive_gene_details_by_ensembl_id` | Comprehensive HPA | `ensembl_id` + `include_images` + `include_antibodies` + `include_expression` | ALL 4 required |
| `HPA_get_subcellular_location` | Localization | `ensembl_id` | Standard |
| `HPA_get_cancer_prognostics_by_gene` | Cancer prognostics | `gene_name` | Standard |
| `CELLxGENE_get_expression_data` | Single-cell | `gene` | Standard |

### Phase 7: Genetic Variation

| Tool | Purpose | Required Parameters | Notes |
|------|---------|---------------------|-------|
| `gnomad_get_gene_constraints` | Constraint scores | **`gene_symbol`** | NOT `gene_id` |
| `clinvar_search_variants` | Clinical variants | `gene` | Standard |
| `DisGeNET_search_gene` | Gene-disease | `gene`, `limit`, **`operation`** | SOAP tool |
| `civic_get_variants_by_gene` | CIViC variants | `gene_symbol` | Standard |
| `cBioPortal_get_mutations` | Cancer mutations | `gene_symbol` | Standard |

### Phase 8-12: Scoring

| Tool | Purpose | Required Parameters | Notes |
|------|---------|---------------------|-------|
| `gwas_get_snps_for_gene` | GWAS SNPs | **`mapped_gene`** (NOT `gene`) | CRITICAL! |
| `gwas_search_studies` | GWAS studies | `query` | Standard |
| `Pharos_get_target` | TDL classification | `gene` or `uniprot` | Either works |
| `DGIdb_get_gene_druggability` | Druggability | `genes` | Standard |
| `BindingDB_get_ligands_by_uniprot` | Ligands | `uniprot`, `affinity_cutoff` | affinity in nM |
| `search_clinical_trials` | Clinical trials | **`query_term`** | NOT `query` |
| `FDA_get_adverse_reactions_by_drug_name` | ADRs | `drug_name` | Standard |
| `FDA_get_boxed_warning_info_by_drug_name` | Black box | `drug_name` | Standard |

---

## Unavailable Tools & Alternatives

These tools referenced in the skill may not be available in all ToolUniverse installations. Use the alternatives:

| Unavailable Tool | Alternative | Notes |
|------------------|-------------|-------|
| `OpenTargets_get_diseases_phenotypes_by_target_ensemblId` | `search_clinical_trials` + `Pharos_get_target` | Use clinical trials and Pharos for disease associations |
| `OpenTargets_get_target_tractability_by_ensemblId` | `Pharos_get_target` (TDL field) | Pharos provides druggability classification |
| `OpenTargets_get_target_safety_profile_by_ensemblId` | `gnomad_get_gene_constraints` + literature | Use constraint scores and literature |
| `OpenTargets_get_target_interactions_by_ensemblId` | `STRING_get_protein_interactions` | STRING provides comprehensive PPI data |
| `OpenTargets_get_target_gene_ontology_by_ensemblId` | `GO_get_annotations_for_gene` | Direct GO query |
| `OpenTargets_get_publications_by_target_ensemblId` | `PubMed_search_articles` | Direct PubMed search |
| `OpenTargets_get_biological_mouse_models_by_ensemblId` | `gnomad_get_gene_constraints` (pLI) | Use constraint scores as proxy |
| `OpenTargets_get_chemical_probes_by_target_ensemblId` | `BindingDB_get_ligands_by_uniprot` | BindingDB for chemical matter |
| `OpenTargets_get_associated_drugs_by_target_ensemblId` | `search_clinical_trials` + `Pharos_get_target` | Clinical trials + Pharos |
| `OpenTargets_get_target_classes_by_ensemblId` | `Pharos_get_target` (fam field) | Pharos family classification |
| `OpenTargets_get_target_homologues_by_ensemblId` | `Ensembl` cross-references | Use Ensembl for paralogs |
| `BioGRID_get_interactions` | `STRING_get_protein_interactions` + `intact_get_interactions` | Combine STRING and IntAct |
| `DrugBank_search_drugs` | `search_clinical_trials` + `BindingDB` | Clinical trials + BindingDB |

---

## Fallback Chains

When primary tools fail, use these fallback sequences:

### Expression Data

```
GTEx (versioned ID) → GTEx (unversioned ID) → HPA comprehensive → HPA RNA → Document unavailable
```

### Chemical Matter

```
ChEMBL_get_target_activities → BindingDB_get_ligands_by_uniprot → DGIdb_get_gene_info → Document gap
```

### PPI Data

```
STRING → IntAct → BioGRID → OpenTargets interactions → Document gap
```

### Constraint Scores

```
gnomAD_get_gene_constraints → OpenTargets constraint (if available) → Document unavailable
```

### Literature

```
PubMed_search_articles → EuropePMC_search_articles → PubTator3_LiteratureSearch → Document gap
```

### Pathways

```
Reactome_map_uniprot_to_pathways → OpenTargets GO → MyGene pathways → Use GO only
```

---

## GTEx Versioned ID Handling

GTEx OFTEN requires versioned Ensembl IDs (e.g., `ENSG00000146648.18`):

```python
# Get versioned ID from Ensembl
gene_info = ensembl_lookup_gene(gene_id=ensembl_id, species="homo_sapiens")
if gene_info and gene_info.get('version'):
    ensembl_versioned = f"{ensembl_id}.{gene_info['version']}"

# Try versioned first, fall back to unversioned
result = GTEx_get_median_gene_expression(gencode_id=ensembl_versioned, operation="get_median_gene_expression")
if not result or result.get('status') == 'error':
    result = GTEx_get_median_gene_expression(gencode_id=ensembl_id, operation="get_median_gene_expression")
```

---

## SOAP Tools (Require `operation` Parameter)

These tools require the `operation` parameter as the first argument:

| Tool | Required Operation |
|------|-------------------|
| `GPCRdb_get_protein` | `operation="get_protein"` |
| `GPCRdb_get_structures` | `operation="get_structures"` |
| `GPCRdb_get_ligands` | `operation="get_ligands"` |
| `DisGeNET_search_gene` | `operation="search_gene"` |

Example:
```python
result = GPCRdb_get_protein(
    operation="get_protein",  # REQUIRED first
    protein="egfr_human"
)
```

---

## Minimum Data Requirements

| Section | Minimum Data | If Not Met |
|---------|--------------|------------|
| **PPIs** | >= 10 interactors | Document which tools failed + why |
| **Expression** | Top 10 tissues with TPM values | Note "limited data" with specific gaps |
| **Disease** | Top 5 associations with scores | Note if fewer |
| **Constraints** | All 4 scores (pLI, LOEUF, missense Z, pRec) | Note which unavailable |
| **Druggability** | Tractability + drugs + probes assessed | "No drugs/probes" is valid data |
| **Literature** | Total count + key papers | Note if sparse (<50 papers) |

---

## Error Handling Pattern

```python
def safe_tool_call(tool_name, fallback_chain=None, **kwargs):
    """Call tool with fallback chain and error handling."""
    try:
        tool = getattr(tu.tools, tool_name)
        result = tool(**kwargs)
        data = handle_response(result)
        if data:
            return data
    except Exception as e:
        warnings.append(f"{tool_name} failed: {e}")

    # Try fallbacks
    if fallback_chain:
        for fallback_tool, fallback_params in fallback_chain:
            try:
                tool = getattr(tu.tools, fallback_tool)
                result = tool(**fallback_params)
                data = handle_response(result)
                if data:
                    return data
            except Exception:
                continue

    # Document failure
    tool_failures.append({
        'tool': tool_name,
        'params': kwargs,
        'fallbacks_tried': [f[0] for f in fallback_chain] if fallback_chain else []
    })
    return None
```