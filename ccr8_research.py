"""
CCR8 Target Research Report Generator
"""
from tooluniverse.tools import (
    UniProt_get_entry_by_accession,
    MyGene_get_gene_annotation,
    GPCRdb_get_protein,
    Ensembl_lookup_gene,
    OpenTargets_get_diseases_phenotypes_by_target_ensemblId,
    OpenTargets_get_target_tractability_by_ensemblId,
    OpenTargets_get_target_safety_profile_by_ensemblId,
    OpenTargets_get_target_interactions_by_ensemblId,
    OpenTargets_get_target_gene_ontology_by_ensemblId,
    OpenTargets_get_publications_by_target_ensemblId,
    OpenTargets_get_biological_mouse_models_by_ensemblId,
    OpenTargets_get_chemical_probes_by_target_ensemblId,
    OpenTargets_get_associated_drugs_by_target_ensemblId,
    UniProt_get_function_by_accession,
    UniProt_get_alternative_names_by_accession,
    UniProt_get_subcellular_location_by_accession,
    UniProt_get_ptm_processing_by_accession,
    InterPro_get_protein_domains,
    Reactome_map_uniprot_to_pathways,
    GO_get_annotations_for_gene,
    STRING_get_protein_interactions,
    IntAct_get_interactions,
    GTEx_get_median_gene_expression,
    HPA_get_rna_expression_by_source,
    HPA_get_comprehensive_gene_details_by_ensembl_id,
    HPA_get_subcellular_location,
    HPA_get_cancer_prognostics_by_gene,
    gnomad_get_gene_constraints,
    ClinVar_search_variants,
    DisGeNET_search_gene,
    DGIdb_get_druggability,
    DGIdb_get_drug_gene_interactions,
    ChEMBL_search_targets,
    Pharos_get_target,
    BindingDB_get_ligands_by_uniprot,
    PubChem_search_assays_by_target_gene,
    DepMap_get_gene_dependencies,
    GPCRdb_get_structures,
    GPCRdb_get_ligands,
    PubMed_search_articles,
    alphafold_get_prediction,
    get_protein_metadata_by_pdb_id,
    WikiPathways_search,
)

import json
import os

# Output directory
OUTPUT_DIR = "/Users/biomap/Code/2026/work/ToolUniverse"
REPORT_FILE = os.path.join(OUTPUT_DIR, "CCR8_target_report.md")

# Helper function to safely get results
def safe_call(func, **kwargs):
    """Safely call a function and return result or None"""
    try:
        result = func(**kwargs)
        return result
    except Exception as e:
        print(f"Error calling {func.__name__}: {e}")
        return None

def save_report(content):
    """Save report content to file"""
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

# Resolve all identifiers for CCR8
print("=" * 60)
print("CCR8 TARGET RESEARCH REPORT")
print("=" * 60)

# Phase 0: Identifier Resolution
print("\n--- PHASE 0: IDENTIFIER RESOLUTION ---")

# 1. Get UniProt entry
print("\n1. UniProt Lookup...")
uniprot_result = safe_call(UniProt_get_entry_by_accession, accession="CCR8")
print(f"UniProt Result: {json.dumps(uniprot_result, indent=2, default=str) if uniprot_result else 'None'}")

# Extract key identifiers
uniprot_id = None
ensembl_id = None
gene_symbol = "CCR8"
entrez_id = None

if uniprot_result and 'entry' in uniprot_result:
    entry = uniprot_result['entry']
    uniprot_id = entry.get('accession', 'P57706')
    print(f"\n  UniProt Accession: {uniprot_id}")

    # Get cross-references for Ensembl
    xrefs = entry.get('uniProtKBCrossReferences', [])
    for xref in xrefs:
        if xref.get('database') == 'Ensembl':
            ensembl_id = xref.get('id')
            print(f"  Ensembl ID: {ensembl_id}")
            break
        if xref.get('database') == 'GeneID':
            entrez_id = xref.get('id')
            print(f"  Entrez Gene ID: {entrez_id}")

# 2. Get MyGene annotation for additional identifiers
print("\n2. MyGene Annotation Lookup...")
mygene_result = safe_call(MyGene_get_gene_annotation, gene_symbol="CCR8")
if mygene_result:
    print(f"MyGene Result: {json.dumps(mygene_result, indent=2, default=str)[:500]}...")
    if 'ensembl' in str(mygene_result).lower() and not ensembl_id:
        # Try to extract ensembl ID
        if isinstance(mygene_result, dict) and 'ensembl' in mygene_result:
            ensembl_id = mygene_result['ensembl'].get('gene', ensembl_id)

# 3. Check if GPCR
print("\n3. GPCRdb Lookup (checking if GPCR)...")
gpcr_result = safe_call(GPCRdb_get_protein, entry_name="CCR8")
is_gpcr = gpcr_result is not None and 'error' not in str(gpcr_result).lower()
print(f"Is GPCR: {is_gpcr}")
if is_gpcr:
    print(f"GPCRdb Result: {json.dumps(gpcr_result, indent=2, default=str)[:500] if gpcr_result else 'None'}...")

# Set default IDs if not found
if not uniprot_id:
    uniprot_id = "P57706"  # Known CCR8 UniProt ID
if not ensembl_id:
    ensembl_id = "ENSG00000170522"  # Known CCR8 Ensembl ID

print(f"\n--- RESOLVED IDENTIFIERS ---")
print(f"Gene Symbol: {gene_symbol}")
print(f"UniProt Accession: {uniprot_id}")
print(f"Ensembl Gene ID: {ensembl_id}")
print(f"Is GPCR: {is_gpcr}")