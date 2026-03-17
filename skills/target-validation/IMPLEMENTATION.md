# Target Validation - Implementation

Detailed Python implementations for each workflow phase.

---

## Setup and Imports

```python
#!/usr/bin/env python3
"""
Target Validation Pipeline - Python SDK Implementation
Comprehensive target assessment from biological intelligence to validation decisions.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from tooluniverse import ToolUniverse


class TargetValidationPipeline:
    """Target validation pipeline with 14 phases."""

    def __init__(self, tu: Optional[ToolUniverse] = None):
        self.tu = tu or ToolUniverse()
        self.tu.load_tools()
        self.ids = {}  # Resolved identifiers
        self.scores = {}  # Validation scores
        self.data = {}  # Collected data
        self.warnings = []  # Warnings and gaps
```

---

## Phase 0: Target Disambiguation

```python
def resolve_target_ids(self, target: str) -> Dict[str, Any]:
    """
    Resolve target query to ALL needed identifiers.
    Returns dict with all cross-references.
    """
    ids = {
        'query': target,
        'uniprot': None,
        'ensembl': None,
        'ensembl_versioned': None,
        'symbol': None,
        'entrez': None,
        'chembl_target': None,
        'hgnc': None,
        'full_name': None,
        'synonyms': [],
        'target_class': None,
        'is_gpcr': False
    }

    # Step 1: Initial query via MyGene
    try:
        result = self.tu.tools.MyGene_query_genes(query=target, limit=1)
        if result and len(result) > 0:
            gene = result[0] if isinstance(result, list) else result.get('data', [{}])[0]
            ids['symbol'] = gene.get('symbol')
            ids['ensembl'] = gene.get('ensembl', {}).get('gene')
            ids['entrez'] = gene.get('entrezgene')
    except Exception as e:
        self.warnings.append(f"MyGene query failed: {e}")

    # Step 2: UniProt ID mapping
    if not ids['uniprot']:
        try:
            mapping = self.tu.tools.UniProt_id_mapping(
                _from='Gene_Name',
                to='UniProtKB',
                ids=ids['symbol'] or target
            )
            if mapping and 'results' in mapping:
                ids['uniprot'] = mapping['results'][0]['to']['primaryAccession']
        except Exception:
            pass

    # Step 3: Get versioned Ensembl ID (CRITICAL for GTEx)
    if ids['ensembl']:
        try:
            gene_info = self.tu.tools.ensembl_lookup_gene(
                gene_id=ids['ensembl'],
                species="homo_sapiens"
            )
            if gene_info and gene_info.get('version'):
                ids['ensembl_versioned'] = f"{ids['ensembl']}.{gene_info['version']}"
            ids['full_name'] = gene_info.get('description', '').split(' [')[0]
        except Exception as e:
            self.warnings.append(f"Ensembl lookup failed: {e}")

    # Step 4: Get ChEMBL target ID
    if ids['symbol']:
        try:
            chembl = self.tu.tools.ChEMBL_search_targets(query=ids['symbol'])
            if chembl and 'targets' in chembl:
                for t in chembl['targets']:
                    if t.get('target_type') == 'SINGLE_PROTEIN':
                        ids['chembl_target'] = t['target_chembl_id']
                        break
        except Exception:
            pass

    # Step 5: GPCR detection
    if ids['symbol']:
        try:
            entry_name = f"{ids['symbol'].lower()}_human"
            gpcr = self.tu.tools.GPCRdb_get_protein(
                operation="get_protein",
                protein=entry_name
            )
            if gpcr and gpcr.get('status') == 'success':
                ids['is_gpcr'] = True
                ids['target_class'] = 'GPCR'
        except Exception:
            pass

    # Step 6: Get synonyms for collision detection
    if ids['uniprot']:
        try:
            alt_names = self.tu.tools.UniProt_get_alternative_names_by_accession(
                accession=ids['uniprot']
            )
            if alt_names:
                ids['synonyms'].extend(alt_names[:5])
        except Exception:
            pass

    self.ids = ids
    return ids
```

---

## Phase 1: Open Targets Foundation

```python
def get_open_targets_foundation(self) -> Dict[str, Any]:
    """
    Open Targets foundation data - fills gaps for all subsequent phases.
    ALWAYS run this first after disambiguation.
    """
    ensembl_id = self.ids.get('ensembl')
    if not ensembl_id:
        return {'status': 'skipped', 'reason': 'No Ensembl ID'}

    results = {}

    # Disease associations (for auto-discovery)
    try:
        diseases = self.tu.tools.OpenTargets_get_diseases_phenotypes_by_target_ensemblId(
            ensemblId=ensembl_id
        )
        results['diseases'] = diseases if diseases else {'note': 'No disease associations'}
    except Exception as e:
        results['diseases'] = {'error': str(e)}

    # Tractability
    try:
        tractability = self.tu.tools.OpenTargets_get_target_tractability_by_ensemblId(
            ensemblId=ensembl_id
        )
        results['tractability'] = tractability if tractability else {'note': 'No tractability data'}
    except Exception as e:
        results['tractability'] = {'error': str(e)}

    # Safety profile
    try:
        safety = self.tu.tools.OpenTargets_get_target_safety_profile_by_ensemblId(
            ensemblId=ensembl_id
        )
        results['safety'] = safety if safety else {'note': 'No safety liabilities'}
    except Exception as e:
        results['safety'] = {'error': str(e)}

    # Interactions
    try:
        interactions = self.tu.tools.OpenTargets_get_target_interactions_by_ensemblId(
            ensemblId=ensembl_id
        )
        results['interactions'] = interactions if interactions else {'note': 'No interactions'}
    except Exception as e:
        results['interactions'] = {'error': str(e)}

    # GO terms
    try:
        go_terms = self.tu.tools.OpenTargets_get_target_gene_ontology_by_ensemblId(
            ensemblId=ensembl_id
        )
        results['go_terms'] = go_terms if go_terms else {'note': 'No GO annotations'}
    except Exception as e:
        results['go_terms'] = {'error': str(e)}

    # Publications
    try:
        publications = self.tu.tools.OpenTargets_get_publications_by_target_ensemblId(
            entityId=ensembl_id
        )
        results['publications'] = publications if publications else {'note': 'No publications'}
    except Exception as e:
        results['publications'] = {'error': str(e)}

    # Mouse models
    try:
        mouse_models = self.tu.tools.OpenTargets_get_biological_mouse_models_by_ensemblId(
            ensemblId=ensembl_id
        )
        results['mouse_models'] = mouse_models if mouse_models else {'note': 'No mouse model data'}
    except Exception as e:
        results['mouse_models'] = {'error': str(e)}

    # Chemical probes
    try:
        probes = self.tu.tools.OpenTargets_get_chemical_probes_by_target_ensemblId(
            ensemblId=ensembl_id
        )
        results['chemical_probes'] = probes if probes else {'note': 'No chemical probes'}
    except Exception as e:
        results['chemical_probes'] = {'error': str(e)}

    # Associated drugs
    try:
        drugs = self.tu.tools.OpenTargets_get_associated_drugs_by_target_ensemblId(
            ensemblId=ensembl_id,
            size=50
        )
        results['drugs'] = drugs if drugs else {'note': 'No drugs found'}
    except Exception as e:
        results['drugs'] = {'error': str(e)}

    self.data['ot_foundation'] = results
    return results
```

---

## Auto Disease Discovery

```python
def auto_discover_diseases(self, top_n: int = 3) -> List[Dict[str, Any]]:
    """
    Auto-discover top associated diseases from Open Targets.
    Used when disease parameter not provided.
    """
    diseases_data = self.data.get('ot_foundation', {}).get('diseases', {})

    if isinstance(diseases_data, dict) and 'data' in diseases_data:
        diseases = diseases_data['data']
    elif isinstance(diseases_data, list):
        diseases = diseases_data
    else:
        return []

    # Sort by association score
    sorted_diseases = sorted(
        diseases,
        key=lambda x: x.get('associationScore', 0) if isinstance(x, dict) else 0,
        reverse=True
    )

    # Filter to therapeutic areas (exclude broad phenotypes)
    relevant_diseases = []
    for d in sorted_diseases[:top_n * 2]:
        if isinstance(d, dict):
            efo_id = d.get('id', '')
            # Skip broad terms
            if not any(x in efo_id.lower() for x in ['measurement', 'procedure', 'attribute']):
                relevant_diseases.append({
                    'name': d.get('name', 'Unknown'),
                    'efo_id': efo_id,
                    'score': d.get('associationScore', 0)
                })
        if len(relevant_diseases) >= top_n:
            break

    return relevant_diseases[:top_n]
```

---

## Phase 8: Disease Association Scoring

```python
def score_disease_association(self, disease: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculate disease association score (0-30 pts).
    If no disease provided, use auto-discovered top disease.
    """
    scores = {
        'genetic': 0,
        'literature': 0,
        'pathway': 0,
        'total': 0
    }
    evidence = []

    # Get disease for scoring
    if not disease:
        top_diseases = self.auto_discover_diseases(top_n=1)
        if top_diseases:
            disease = top_diseases[0]['name']

    # Genetic Evidence (0-10)
    symbol = self.ids.get('symbol')

    # GWAS associations
    if symbol:
        try:
            gwas = self.tu.tools.gwas_get_snps_for_gene(gene=symbol)
            if gwas and 'associations' in gwas:
                significant = [a for a in gwas['associations']
                             if a.get('pvalue', 1) < 5e-8]
                scores['genetic'] += min(len(significant) * 3, 6)
                if significant:
                    evidence.append(f"GWAS: {len(significant)} significant loci [T3]")
        except Exception:
            pass

    # gnomAD constraints
    if symbol:
        try:
            constraints = self.tu.tools.gnomad_get_gene_constraints(gene_symbol=symbol)
            if constraints:
                pli = constraints.get('pLI', 0)
                if pli > 0.9:
                    scores['genetic'] += 2
                    evidence.append(f"pLI={pli:.2f} (highly constrained) [T3]")
        except Exception:
            pass

    # Literature Evidence (0-10)
    if symbol and disease:
        try:
            pub_result = self.tu.tools.PubMed_search_articles(
                query=f"{symbol} AND {disease}",
                limit=200
            )
            if isinstance(pub_result, list):
                count = len(pub_result)
            elif isinstance(pub_result, dict):
                count = pub_result.get('total', 0)
            else:
                count = 0

            if count > 100:
                scores['literature'] = 10
            elif count > 50:
                scores['literature'] = 7
            elif count > 10:
                scores['literature'] = 5
            elif count > 0:
                scores['literature'] = 3

            evidence.append(f"Literature: {count} publications [T4]")
        except Exception:
            pass

    # Pathway Evidence (0-10)
    ensembl_id = self.ids.get('ensembl')
    if ensembl_id and disease:
        try:
            ot_diseases = self.data.get('ot_foundation', {}).get('diseases', {})
            if isinstance(ot_diseases, dict) and 'data' in ot_diseases:
                for d in ot_diseases['data']:
                    if disease.lower() in d.get('name', '').lower():
                        score = d.get('associationScore', 0)
                        if score > 0.8:
                            scores['pathway'] = 10
                        elif score > 0.5:
                            scores['pathway'] = 7
                        elif score > 0.2:
                            scores['pathway'] = 4
                        else:
                            scores['pathway'] = 1
                        evidence.append(f"OpenTargets score={score:.2f} [T3]")
                        break
        except Exception:
            pass

    scores['total'] = scores['genetic'] + scores['literature'] + scores['pathway']
    self.scores['disease_association'] = scores

    return {
        'disease': disease,
        'scores': scores,
        'evidence': evidence
    }
```

---

## Phase 9: Druggability Assessment

```python
def score_druggability(self, modality: str = 'all') -> Dict[str, Any]:
    """
    Calculate druggability score (0-25 pts).
    Modality: 'small molecule', 'antibody', 'PROTAC', 'all'
    """
    scores = {
        'structural': 0,
        'chemical': 0,
        'target_class': 0,
        'total': 0
    }
    evidence = []

    ensembl_id = self.ids.get('ensembl')
    uniprot_id = self.ids.get('uniprot')
    symbol = self.ids.get('symbol')

    # Structural Tractability (0-10)
    tractability = self.data.get('ot_foundation', {}).get('tractability', {})

    if modality in ['small molecule', 'all']:
        sm_bucket = tractability.get('smallMolecule', {}).get('bucket', 0)
        if sm_bucket and sm_bucket <= 3:
            scores['structural'] = 10
        elif sm_bucket and sm_bucket <= 5:
            scores['structural'] = 7
        elif sm_bucket and sm_bucket <= 7:
            scores['structural'] = 5
        elif sm_bucket:
            scores['structural'] = 2
        evidence.append(f"SM tractability bucket: {sm_bucket} [T3]")

    # Chemical Matter (0-10)
    chembl_id = self.ids.get('chembl_target')

    if chembl_id:
        try:
            activities = self.tu.tools.ChEMBL_get_target_activities(
                target_chembl_id__exact=chembl_id
            )
            if activities:
                compounds = activities.get('compounds', [])
                potent = [c for c in compounds
                         if c.get('standard_value', 10000) < 100]

                if potent:
                    scores['chemical'] = 10
                    evidence.append(f"{len(potent)} compounds with IC50 < 100nM [T2]")
                elif compounds:
                    scores['chemical'] = 7
                    evidence.append(f"{len(compounds)} compounds in ChEMBL [T3]")
        except Exception:
            pass

    if uniprot_id and scores['chemical'] < 10:
        try:
            ligands = self.tu.tools.BindingDB_get_ligands_by_uniprot(
                uniprot=uniprot_id,
                affinity_cutoff=1000
            )
            if ligands and len(ligands) > 0:
                scores['chemical'] = max(scores['chemical'], 7)
                evidence.append(f"BindingDB: {len(ligands)} ligands [T2]")
        except Exception:
            pass

    # Target Class Bonus (0-5)
    # Check Pharos TDL
    if symbol:
        try:
            pharos = self.tu.tools.Pharos_get_target(gene=symbol)
            if pharos and 'tdl' in pharos:
                tdl = pharos['tdl']
                if tdl == 'Tclin':
                    scores['target_class'] = 5
                    evidence.append("Pharos TDL: Tclin (clinical target) [T1]")
                elif tdl == 'Tchem':
                    scores['target_class'] = 4
                    evidence.append("Pharos TDL: Tchem (chemical probe) [T2]")
                elif tdl == 'Tbio':
                    scores['target_class'] = 2
                    evidence.append("Pharos TDL: Tbio (biology known) [T3]")
        except Exception:
            pass

    # GPCR/Kinase bonus
    if self.ids.get('is_gpcr'):
        scores['target_class'] = max(scores['target_class'], 5)
        evidence.append("GPCR target class - validated druggable [T1]")

    # Check target class from OT
    try:
        classes = self.tu.tools.OpenTargets_get_target_classes_by_ensemblId(
            ensemblId=ensembl_id
        )
        if classes:
            for c in classes.get('data', []):
                if 'kinase' in c.get('label', '').lower():
                    scores['target_class'] = max(scores['target_class'], 5)
                    evidence.append("Kinase target class [T1]")
                    break
    except Exception:
        pass

    scores['total'] = scores['structural'] + scores['chemical'] + scores['target_class']
    self.scores['druggability'] = scores

    return {
        'modality': modality,
        'scores': scores,
        'evidence': evidence
    }
```

---

## Phase 10: Safety Deep Analysis

```python
def score_safety(self) -> Dict[str, Any]:
    """
    Calculate safety score (0-20 pts).
    Includes expression selectivity, genetic validation, and ADRs.
    """
    scores = {
        'expression': 0,
        'genetic': 0,
        'adverse': 0,
        'total': 0
    }
    evidence = []
    safety_flags = []

    ensembl_id = self.ids.get('ensembl')
    symbol = self.ids.get('symbol')

    # Expression Selectivity (0-5)
    critical_tissues = ['heart', 'liver', 'kidney', 'brain', 'bone marrow']
    expression_in_critical = []

    # GTEx expression
    gencode_id = self.ids.get('ensembl_versioned') or self.ids.get('ensembl')
    if gencode_id:
        try:
            gtex = self.tu.tools.GTEx_get_median_gene_expression(
                gencode_id=gencode_id,
                operation="median"
            )
            if gtex and 'data' in gtex:
                for tissue_data in gtex['data']:
                    tissue = tissue_data.get('tissue', '').lower()
                    tpm = tissue_data.get('median', 0)
                    if any(c in tissue for c in critical_tissues) and tpm > 10:
                        expression_in_critical.append(tissue)

            if not expression_in_critical:
                scores['expression'] = 5
                evidence.append("Low expression in critical tissues [T2]")
            elif len(expression_in_critical) == 1:
                scores['expression'] = 4
                evidence.append(f"Moderate expression in {expression_in_critical[0]} [T2]")
            else:
                scores['expression'] = 0
                safety_flags.append(f"High expression in: {', '.join(expression_in_critical)}")
                evidence.append(f"Expression in critical tissues: {expression_in_critical} [T2]")
        except Exception as e:
            self.warnings.append(f"GTEx query failed: {e}")

    # Genetic Validation (0-10)
    mouse_models = self.data.get('ot_foundation', {}).get('mouse_models', {})

    if isinstance(mouse_models, dict) and 'data' in mouse_models:
        models = mouse_models['data']
        lethal = any(m.get('phenotype_label', '').lower().contains('lethal')
                    for m in models if isinstance(m, dict))

        if lethal:
            scores['genetic'] = 0
            safety_flags.append("Mouse KO lethal")
            evidence.append("Mouse KO: Lethal phenotype [T2]")
        elif models:
            scores['genetic'] = 7
            evidence.append("Mouse KO: Viable with phenotype [T2]")
        else:
            # Fall back to pLI
            constraints = self.scores.get('gnomad_constraints', {})
            pli = constraints.get('pLI', 0.5)
            if pli < 0.5:
                scores['genetic'] = 5
                evidence.append(f"No KO data, low pLI ({pli:.2f}) [T3]")
            else:
                scores['genetic'] = 2
                evidence.append(f"No KO data, high pLI ({pli:.2f}) - caution [T3]")

    # Known Adverse Events (0-5)
    safety_profile = self.data.get('ot_foundation', {}).get('safety', {})

    if isinstance(safety_profile, dict) and 'data' in safety_profile:
        liabilities = safety_profile.get('data', [])
        severe = [l for l in liabilities if l.get('severity') == 'High']

        if not liabilities:
            scores['adverse'] = 5
            evidence.append("No known safety liabilities [T2]")
        elif severe:
            scores['adverse'] = 1
            safety_flags.append(f"Severe safety concerns: {len(severe)}")
            evidence.append(f"Severe safety liabilities: {len(severe)} [T2]")
        else:
            scores['adverse'] = 3
            evidence.append(f"Mild/moderate safety concerns: {len(liabilities)} [T2]")

    scores['total'] = scores['expression'] + scores['genetic'] + scores['adverse']
    self.scores['safety'] = scores
    self.safety_flags = safety_flags

    return {
        'scores': scores,
        'evidence': evidence,
        'safety_flags': safety_flags
    }
```

---

## Phase 11: Clinical Precedent

```python
def score_clinical_precedent(self) -> Dict[str, Any]:
    """
    Calculate clinical precedent score (0-15 pts).
    Based on highest clinical stage achieved.
    """
    score = 0
    evidence = []
    approved_drugs = []
    clinical_trials = []

    symbol = self.ids.get('symbol')

    # Get drugs from OT foundation
    drugs_data = self.data.get('ot_foundation', {}).get('drugs', {})

    if isinstance(drugs_data, dict) and 'data' in drugs_data:
        for drug in drugs_data['data']:
            phase = drug.get('phase', 0)
            drug_name = drug.get('name', 'Unknown')

            if phase == 4:  # Approved
                approved_drugs.append({
                    'name': drug_name,
                    'phase': phase,
                    'indication': drug.get('indication', 'Unknown')
                })

            elif phase in [1, 2, 3]:
                clinical_trials.append({
                    'name': drug_name,
                    'phase': phase
                })

    # Score based on highest stage
    if approved_drugs:
        score = 15
        evidence.append(f"{len(approved_drugs)} FDA-approved drugs [T1]")
    elif any(t['phase'] == 3 for t in clinical_trials):
        score = 10
        evidence.append("Phase 3 clinical trials [T2]")
    elif any(t['phase'] == 2 for t in clinical_trials):
        score = 7
        evidence.append("Phase 2 clinical trials [T2]")
    elif any(t['phase'] == 1 for t in clinical_trials):
        score = 5
        evidence.append("Phase 1 clinical trials [T2]")
    elif clinical_trials:
        score = 3
        evidence.append("Preclinical compounds [T3]")
    else:
        score = 0
        evidence.append("No clinical development [T4]")

    self.scores['clinical_precedent'] = {'score': score, 'max': 15}
    self.data['approved_drugs'] = approved_drugs
    self.data['clinical_trials'] = clinical_trials

    return {
        'score': score,
        'evidence': evidence,
        'approved_drugs': approved_drugs[:5],
        'clinical_trials': clinical_trials[:10]
    }
```

---

## Phase 13: Composite Scoring

```python
def calculate_composite_score(self) -> Dict[str, Any]:
    """
    Calculate total validation score (0-100) and assign tier.
    """
    disease_score = self.scores.get('disease_association', {}).get('total', 0)
    druggability_score = self.scores.get('druggability', {}).get('total', 0)
    safety_score = self.scores.get('safety', {}).get('total', 0)
    clinical_score = self.scores.get('clinical_precedent', {}).get('score', 0)

    # Validation evidence score (simplified - would need more data)
    validation_score = self.scores.get('validation_evidence', 5)  # Default

    total = (disease_score + druggability_score + safety_score +
             clinical_score + validation_score)

    # Assign tier
    if total >= 80:
        tier, recommendation = 1, "GO - Highly validated target"
    elif total >= 60:
        tier, recommendation = 2, "CONDITIONAL GO - Needs focused validation"
    elif total >= 40:
        tier, recommendation = 3, "CAUTION - Significant validation needed"
    else:
        tier, recommendation = 4, "NO-GO - Consider alternatives"

    return {
        'total': total,
        'tier': tier,
        'recommendation': recommendation,
        'components': {
            'disease_association': {'score': disease_score, 'max': 30},
            'druggability': {'score': druggability_score, 'max': 25},
            'safety': {'score': safety_score, 'max': 20},
            'clinical_precedent': {'score': clinical_score, 'max': 15},
            'validation_evidence': {'score': validation_score, 'max': 10}
        }
    }
```

---

## Main Pipeline Function

```python
def run_validation_pipeline(
    target: str,
    disease: Optional[str] = None,
    modality: str = 'all',
    output_format: str = 'markdown'
) -> Dict[str, Any]:
    """
    Run the complete target validation pipeline.

    Parameters:
        target: Gene symbol, protein name, or UniProt ID
        disease: Disease context (optional, auto-discovered if not provided)
        modality: 'small molecule', 'antibody', 'PROTAC', or 'all'
        output_format: 'markdown', 'json', or 'both'

    Returns:
        Dictionary with validation results
    """
    pipeline = TargetValidationPipeline()

    # Phase 0: Disambiguation
    print(f"Phase 0: Resolving target '{target}'...")
    ids = pipeline.resolve_target_ids(target)

    if not ids.get('symbol') and not ids.get('uniprot'):
        return {'error': f"Could not resolve target: {target}"}

    print(f"  Resolved: {ids.get('symbol')} ({ids.get('uniprot')})")

    # Phase 1: Open Targets Foundation
    print("Phase 1: Fetching Open Targets foundation data...")
    ot_data = pipeline.get_open_targets_foundation()

    # Auto-discover diseases if not provided
    if not disease:
        top_diseases = pipeline.auto_discover_diseases(top_n=3)
        if top_diseases:
            disease = top_diseases[0]['name']
            print(f"  Auto-discovered disease: {disease}")

    # Phase 8: Disease Association Scoring
    print("Phase 8: Scoring disease association...")
    disease_result = pipeline.score_disease_association(disease)

    # Phase 9: Druggability Assessment
    print("Phase 9: Assessing druggability...")
    druggability_result = pipeline.score_druggability(modality)

    # Phase 10: Safety Deep Analysis
    print("Phase 10: Analyzing safety profile...")
    safety_result = pipeline.score_safety()

    # Phase 11: Clinical Precedent
    print("Phase 11: Assessing clinical precedent...")
    clinical_result = pipeline.score_clinical_precedent()

    # Phase 13: Composite Scoring
    print("Phase 13: Calculating composite score...")
    composite = pipeline.calculate_composite_score()

    # Compile results
    results = {
        'metadata': {
            'target': ids.get('symbol'),
            'uniprot_id': ids.get('uniprot'),
            'ensembl_id': ids.get('ensembl'),
            'disease': disease,
            'modality': modality,
            'report_date': datetime.now().strftime('%Y-%m-%d')
        },
        'identifiers': ids,
        'validation_score': composite,
        'disease_association': disease_result,
        'druggability': druggability_result,
        'safety': safety_result,
        'clinical_precedent': clinical_result,
        'safety_flags': pipeline.safety_flags,
        'warnings': pipeline.warnings
    }

    # Generate report
    if output_format in ['markdown', 'both']:
        report_path = generate_report(results)
        results['report_path'] = report_path

    if output_format in ['json', 'both']:
        json_path = export_json(results)
        results['json_path'] = json_path

    return results


if __name__ == "__main__":
    # Example usage
    result = run_validation_pipeline(
        target="EGFR",
        modality="small molecule",
        output_format="markdown"
    )
    print(f"\nValidation Score: {result['validation_score']['total']}/100")
    print(f"Tier: {result['validation_score']['tier']}")
    print(f"Recommendation: {result['validation_score']['recommendation']}")
```