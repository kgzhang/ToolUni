#!/usr/bin/env python3
"""
Open Targets Foundation Data
Primary data source for target validation.
Raw data output to intermediate layer.
"""

import json
from typing import Dict, Any, List
from pathlib import Path


def get_open_targets_foundation(tu, ids: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """
    Get Open Targets foundation data.
    Foundation data for all subsequent phases.

    Parameters:
        tu: ToolUniverse instance
        ids: Resolved target identifiers
        output_dir: Directory for intermediate data

    Returns:
        Dictionary with Open Targets data
    """
    ensembl_id = ids.get('ensembl')
    if not ensembl_id:
        return {'status': 'skipped', 'reason': 'No Ensembl ID'}

    results = {'data': {}, 'raw_tool_calls': []}

    # Standard queries - using correct tool names with ensemblID (capital ID)
    queries = [
        ('OpenTargets_get_diseases_phenotypes_by_target_ensembl', {'ensemblId': ensembl_id}, 'diseases'),
        ('OpenTargets_get_target_tractability_by_ensemblID', {'ensemblId': ensembl_id}, 'tractability'),
        ('OpenTargets_get_target_safety_profile_by_ensemblID', {'ensemblId': ensembl_id}, 'safety'),
        ('OpenTargets_get_target_interactions_by_ensemblID', {'ensemblId': ensembl_id}, 'interactions'),
        ('OpenTargets_get_target_gene_ontology_by_ensemblID', {'ensemblId': ensembl_id}, 'go_terms'),
        ('OpenTargets_get_biological_mouse_models_by_ensemblID', {'ensemblId': ensembl_id}, 'mouse_models'),
        ('OpenTargets_get_chemical_probes_by_target_ensemblID', {'ensemblId': ensembl_id}, 'chemical_probes'),
        ('OpenTargets_get_target_classes_by_ensemblID', {'ensemblId': ensembl_id}, 'target_classes'),
        ('OpenTargets_get_target_homologues_by_ensemblID', {'ensemblId': ensembl_id}, 'homologues'),
    ]

    # Special queries
    special_queries = [
        ('OpenTargets_get_publications_by_target_ensemblID', {'ensemblId': ensembl_id}, 'publications'),
        ('OpenTargets_get_associated_drugs_by_target_ensemblID', {'ensemblId': ensembl_id, 'size': 100}, 'drugs'),
    ]

    all_queries = queries + special_queries

    for tool_name, params, key in all_queries:
        try:
            tool = getattr(tu.tools, tool_name)
            result = tool(**params)
            results['raw_tool_calls'].append({
                'tool': tool_name,
                'params': params,
                'result': result
            })

            # Extract data
            if result is None:
                results['data'][key] = None
            elif isinstance(result, dict):
                if 'status' in result and result['status'] == 'error':
                    results['data'][key] = None
                elif 'data' in result:
                    results['data'][key] = result['data']
                else:
                    results['data'][key] = result
            elif isinstance(result, list):
                results['data'][key] = result
            else:
                results['data'][key] = result

        except Exception as e:
            results['raw_tool_calls'].append({
                'tool': tool_name,
                'params': params,
                'error': str(e)
            })
            results['data'][key] = None

    # Auto-discover diseases
    diseases = results['data'].get('diseases', {})
    if diseases:
        # Handle nested structure: diseases.target.associatedDiseases.rows
        disease_list = []
        if isinstance(diseases, dict):
            # Try direct target structure first
            target = diseases.get('target', {})
            if isinstance(target, dict):
                associated = target.get('associatedDiseases', {})
                if isinstance(associated, dict):
                    disease_list = associated.get('rows', [])
            # Try data wrapper structure
            if not disease_list:
                data_wrapper = diseases.get('data', {})
                if isinstance(data_wrapper, dict):
                    target = data_wrapper.get('target', {})
                    if isinstance(target, dict):
                        associated = target.get('associatedDiseases', {})
                        if isinstance(associated, dict):
                            disease_list = associated.get('rows', [])
            # Fallback to direct list
            if not disease_list and isinstance(diseases, list):
                disease_list = diseases
        elif isinstance(diseases, list):
            disease_list = diseases

        # Calculate overall association score from datasourceScores
        def get_overall_score(d):
            if not isinstance(d, dict):
                return 0
            # Try direct associationScore first
            if d.get('associationScore'):
                return d.get('associationScore', 0)
            # Calculate from datasourceScores
            ds_scores = d.get('datasourceScores', [])
            if ds_scores:
                # Take max of available scores
                return max((s.get('score', 0) for s in ds_scores if isinstance(s, dict)), default=0)
            return 0

        sorted_diseases = sorted(
            [d for d in disease_list if isinstance(d, dict)],
            key=get_overall_score,
            reverse=True
        )

        relevant = []
        for d in sorted_diseases[:20]:
            disease_info = d.get('disease', d)
            efo_id = disease_info.get('id', '') if isinstance(disease_info, dict) else ''
            name = disease_info.get('name', '') if isinstance(disease_info, dict) else ''
            if not any(x in efo_id.lower() for x in ['measurement', 'procedure', 'attribute']):
                relevant.append({
                    'name': name,
                    'efo_id': efo_id,
                    'score': get_overall_score(d)
                })

        results['data']['auto_discovered_diseases'] = relevant[:3]

    # Save raw data
    output_file = output_dir / 'open_targets_foundation.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    return results


def auto_discover_diseases(ot_data: Dict[str, Any], top_n: int = 3) -> List[Dict[str, Any]]:
    """Extract top diseases from Open Targets data."""
    diseases = ot_data.get('data', {}).get('diseases', [])

    if isinstance(diseases, dict) and 'data' in diseases:
        disease_list = diseases['data']
    elif isinstance(diseases, list):
        disease_list = diseases
    else:
        return []

    sorted_diseases = sorted(
        [d for d in disease_list if isinstance(d, dict)],
        key=lambda x: x.get('associationScore', 0),
        reverse=True
    )

    relevant = []
    for d in sorted_diseases[:top_n * 3]:
        efo_id = d.get('id', '')
        if not any(x in efo_id.lower() for x in ['measurement', 'procedure', 'attribute']):
            relevant.append({
                'name': d.get('name'),
                'efo_id': efo_id,
                'score': d.get('associationScore', 0)
            })
        if len(relevant) >= top_n:
            break

    return relevant[:top_n]


if __name__ == "__main__":
    from tooluniverse import ToolUniverse
    from section1_identifiers import get_target_identifiers

    tu = ToolUniverse()
    tu.load_tools()
    ids = get_target_identifiers(tu, "EGFR", Path('./reports/test'))
    ot = get_open_targets_foundation(tu, ids, Path('./reports/test'))
    print(f"Diseases found: {len(ot['data'].get('auto_discovered_diseases', []))}")