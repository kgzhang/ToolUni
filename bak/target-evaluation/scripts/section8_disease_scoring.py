#!/usr/bin/env python3
"""
Section 8: Disease Association Scoring (0-30 pts)
Calculates disease association score from genetic, literature, and pathway evidence.
Raw scores output to intermediate layer.
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path


def score_disease_association(tu, ids: Dict[str, Any], all_data: Dict[str, Any],
                              disease: Optional[str], output_dir: Path) -> Dict[str, Any]:
    """
    Calculate disease association score.
    Section 8: Disease Association Scoring

    Parameters:
        tu: ToolUniverse instance
        ids: Resolved target identifiers
        all_data: All collected data
        disease: Disease context (optional, auto-discovered if None)
        output_dir: Directory for intermediate data

    Returns:
        Dictionary with scoring results
    """
    scores = {'genetic': 0, 'literature': 0, 'pathway': 0, 'total': 0}
    evidence = []
    raw_calls = []

    symbol = ids.get('symbol')

    # Auto-discover disease
    if not disease:
        ot_diseases = all_data.get('ot_foundation', {}).get('data', {}).get('auto_discovered_diseases', [])
        if ot_diseases:
            disease = ot_diseases[0].get('name')

    # 1. Genetic Evidence (0-10)
    # GWAS
    if symbol:
        try:
            tool = getattr(tu.tools, 'gwas_get_snps_for_gene')
            result = tool(mapped_gene=symbol)
            raw_calls.append({
                'tool': 'gwas_get_snps_for_gene',
                'params': {'mapped_gene': symbol},
                'result': result
            })
            if result:
                associations = result.get('associations', []) if isinstance(result, dict) else result
                if isinstance(associations, list):
                    significant = [a for a in associations if isinstance(a, dict) and a.get('pvalue', 1) < 5e-8]
                    scores['genetic'] += min(len(significant) * 3, 6)
                    if significant:
                        evidence.append(f"GWAS: {len(significant)} significant loci [T3]")
        except Exception as e:
            raw_calls.append({'tool': 'gwas_get_snps_for_gene', 'error': str(e)})

    # Constraint scores
    constraints = all_data.get('section7_genetics', {}).get('data', {}).get('constraints', {})
    if constraints:
        pli = constraints.get('pLI', 0)
        if pli and pli > 0.9:
            scores['genetic'] += 2
            evidence.append(f"pLI={pli:.2f} (highly constrained) [T3]")

    # 2. Literature Evidence (0-10)
    if symbol and disease:
        try:
            tool = getattr(tu.tools, 'PubMed_search_articles')
            result = tool(query=f"{symbol} AND {disease}", limit=200)
            raw_calls.append({
                'tool': 'PubMed_search_articles',
                'params': {'query': f"{symbol} AND {disease}", 'limit': 200},
                'result': result
            })

            count = 0
            if isinstance(result, list):
                count = len(result)
            elif isinstance(result, dict):
                count = result.get('total', len(result.get('data', [])))

            if count > 100:
                scores['literature'] = 10
            elif count > 50:
                scores['literature'] = 7
            elif count > 10:
                scores['literature'] = 5
            elif count > 0:
                scores['literature'] = 3

            evidence.append(f"Literature: {count} publications [T4]")
        except Exception as e:
            raw_calls.append({'tool': 'PubMed_search_articles', 'error': str(e)})

    # 3. Pathway Evidence (0-10)
    diseases_data = all_data.get('ot_foundation', {}).get('data', {}).get('diseases', {})
    if isinstance(diseases_data, list):
        disease_list = diseases_data
    elif isinstance(diseases_data, dict) and 'data' in diseases_data:
        disease_list = diseases_data['data']
    else:
        disease_list = []

    for d in disease_list:
        if isinstance(d, dict) and disease:
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

    scores['total'] = scores['genetic'] + scores['literature'] + scores['pathway']

    result = {
        'disease': disease,
        'scores': scores,
        'evidence': evidence,
        'raw_tool_calls': raw_calls
    }

    # Save raw data
    output_file = output_dir / 'section8_disease_scoring.json'
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
    score = score_disease_association(tu, ids, all_data, None, Path('./reports/test'))
    print(f"Disease score: {score['scores']['total']}/30")