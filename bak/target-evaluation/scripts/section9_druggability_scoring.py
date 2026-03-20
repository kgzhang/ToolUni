#!/usr/bin/env python3
"""
Section 9: Druggability Assessment (0-25 pts)
Evaluates structural tractability, chemical matter, and target class.
Raw scores output to intermediate layer.
"""

import json
from typing import Dict, Any
from pathlib import Path


def score_druggability(tu, ids: Dict[str, Any], all_data: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """
    Calculate druggability score.
    Section 9: Druggability Assessment

    Parameters:
        tu: ToolUniverse instance
        ids: Resolved target identifiers
        all_data: All collected data
        output_dir: Directory for intermediate data

    Returns:
        Dictionary with scoring results
    """
    scores = {'structural': 0, 'chemical': 0, 'target_class': 0, 'total': 0}
    evidence = []
    raw_calls = []

    # 1. Structural Tractability (0-10)
    tractability = all_data.get('ot_foundation', {}).get('data', {}).get('tractability', {})
    if tractability:
        # Handle nested structure: tractability.target.tractability
        tract_data = tractability
        if isinstance(tractability, dict):
            target = tractability.get('target', {})
            if isinstance(target, dict):
                tract_data = target.get('tractability', [])
            elif isinstance(tractability, dict) and 'smallMolecule' in tractability:
                tract_data = tractability

        # Check for approved drug (highest score)
        if isinstance(tract_data, list):
            for item in tract_data:
                if isinstance(item, dict):
                    if item.get('label') == 'Approved Drug' and item.get('modality') == 'SM' and item.get('value'):
                        scores['structural'] = 10
                        evidence.append("SM: Approved drug exists [T1]")
                        break
                    elif item.get('label') == 'High-Quality Pocket' and item.get('value'):
                        if scores['structural'] < 8:
                            scores['structural'] = 8
                            evidence.append("SM: High-quality pocket [T3]")
        elif isinstance(tract_data, dict):
            sm_bucket = tract_data.get('smallMolecule', {}).get('bucket', 0)
            if sm_bucket and sm_bucket <= 3:
                scores['structural'] = 10
            elif sm_bucket and sm_bucket <= 5:
                scores['structural'] = 7
            elif sm_bucket and sm_bucket <= 7:
                scores['structural'] = 5
            elif sm_bucket:
                scores['structural'] = 2
            if sm_bucket:
                evidence.append(f"SM tractability bucket: {sm_bucket} [T3]")

    # 2. Chemical Matter (0-10)
    chembl_id = ids.get('chembl_target')
    if chembl_id:
        try:
            tool = getattr(tu.tools, 'ChEMBL_get_target_activities')
            result = tool(target_chembl_id__exact=chembl_id)
            raw_calls.append({
                'tool': 'ChEMBL_get_target_activities',
                'params': {'target_chembl_id__exact': chembl_id},
                'result': result
            })

            if result:
                if isinstance(result, dict):
                    compounds = result.get('compounds', result.get('data', []))
                else:
                    compounds = result if isinstance(result, list) else []

                potent = [c for c in compounds if isinstance(c, dict) and c.get('standard_value', 10000) < 100]

                if potent:
                    scores['chemical'] = 10
                    evidence.append(f"{len(potent)} compounds with IC50 < 100nM [T2]")
                elif compounds:
                    scores['chemical'] = 7
                    evidence.append(f"{len(compounds)} compounds in ChEMBL [T3]")
        except Exception as e:
            raw_calls.append({'tool': 'ChEMBL_get_target_activities', 'error': str(e)})

    # Fallback: BindingDB
    if scores['chemical'] < 10 and ids.get('uniprot'):
        try:
            tool = getattr(tu.tools, 'BindingDB_get_ligands_by_uniprot')
            result = tool(uniprot=ids['uniprot'], affinity_cutoff=1000)
            raw_calls.append({
                'tool': 'BindingDB_get_ligands_by_uniprot',
                'params': {'uniprot': ids['uniprot'], 'affinity_cutoff': 1000},
                'result': result
            })
            if result:
                ligands = result if isinstance(result, list) else result.get('data', [])
                if ligands:
                    scores['chemical'] = max(scores['chemical'], 7)
                    evidence.append(f"BindingDB: {len(ligands)} ligands [T2]")
        except Exception as e:
            raw_calls.append({'tool': 'BindingDB_get_ligands_by_uniprot', 'error': str(e)})

    # 3. Target Class Bonus (0-5)
    tdl = ids.get('target_development_level')
    if tdl == 'Tclin':
        scores['target_class'] = 5
        evidence.append("Pharos TDL: Tclin (clinical target) [T1]")
    elif tdl == 'Tchem':
        scores['target_class'] = 4
        evidence.append("Pharos TDL: Tchem (chemical probe) [T2]")
    elif tdl == 'Tbio':
        scores['target_class'] = 2
        evidence.append("Pharos TDL: Tbio (biology known) [T3]")

    # GPCR bonus
    if ids.get('is_gpcr'):
        scores['target_class'] = max(scores['target_class'], 5)
        evidence.append("GPCR target class - validated druggable [T1]")

    scores['total'] = scores['structural'] + scores['chemical'] + scores['target_class']

    result = {
        'scores': scores,
        'evidence': evidence,
        'raw_tool_calls': raw_calls
    }

    # Save raw data
    output_file = output_dir / 'section9_druggability_scoring.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    return result


if __name__ == "__main__":
    from tooluniverse import ToolUniverse
    from section1_identifiers import get_target_identifiers
    from open_targets_foundation import get_open_targets_foundation

    tu = ToolUniverse()
    tu.load_tools()
    ids = get_target_identifiers(tu, "EGFR", Path('./reports/test'))
    ot = get_open_targets_foundation(tu, ids, Path('./reports/test'))
    all_data = {'ot_foundation': ot}
    score = score_druggability(tu, ids, all_data, Path('./reports/test'))
    print(f"Druggability score: {score['scores']['total']}/25")