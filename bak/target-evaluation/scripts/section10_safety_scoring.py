#!/usr/bin/env python3
"""
Section 10: Safety Analysis (0-20 pts)
Evaluates expression selectivity, genetic validation, and known ADRs.
Raw scores output to intermediate layer.
"""

import json
from typing import Dict, Any, List
from pathlib import Path


def score_safety(ids: Dict[str, Any], all_data: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """
    Calculate safety score.
    Section 10: Safety Analysis

    Parameters:
        ids: Resolved target identifiers
        all_data: All collected data
        output_dir: Directory for intermediate data

    Returns:
        Dictionary with scoring results
    """
    scores = {'expression': 0, 'genetic': 0, 'adverse': 0, 'total': 0}
    evidence = []
    safety_flags = []

    critical_tissues = ['heart', 'liver', 'kidney', 'brain', 'bone marrow']

    # 1. Expression Selectivity (0-5)
    gtex = all_data.get('section6_expression', {}).get('data', {}).get('gtex', {})

    expression_in_critical = []
    if isinstance(gtex, dict) and 'data' in gtex:
        for tissue_data in gtex['data']:
            tissue = tissue_data.get('tissue', '').lower()
            tpm = tissue_data.get('median', 0)
            if any(c in tissue for c in critical_tissues) and tpm > 10:
                expression_in_critical.append({'tissue': tissue, 'tpm': tpm})

    if not expression_in_critical:
        scores['expression'] = 5
        evidence.append("Low expression in critical tissues [T2]")
    elif len(expression_in_critical) == 1:
        scores['expression'] = 4
        evidence.append(f"Moderate expression in {expression_in_critical[0]['tissue']} [T2]")
    else:
        scores['expression'] = 0
        safety_flags.append(f"High expression in: {', '.join([e['tissue'] for e in expression_in_critical])}")
        evidence.append(f"Expression in critical tissues: {[e['tissue'] for e in expression_in_critical]} [T2]")

    # 2. Genetic Validation (0-10)
    mouse_models = all_data.get('ot_foundation', {}).get('data', {}).get('mouse_models', {})

    if isinstance(mouse_models, dict) and 'data' in mouse_models:
        models = mouse_models['data']
        lethal = any('lethal' in str(m.get('phenotype_label', '')).lower() for m in models if isinstance(m, dict))

        if lethal:
            scores['genetic'] = 0
            safety_flags.append("Mouse KO lethal")
            evidence.append("Mouse KO: Lethal phenotype [T2]")
        elif models:
            scores['genetic'] = 7
            evidence.append("Mouse KO: Viable with phenotype [T2]")
        else:
            # Fall back to pLI
            constraints = all_data.get('section7_genetics', {}).get('data', {}).get('constraints', {})
            if constraints:
                pli = constraints.get('pLI', 0.5)
                if pli < 0.5:
                    scores['genetic'] = 5
                    evidence.append(f"No KO data, low pLI ({pli:.2f}) [T3]")
                else:
                    scores['genetic'] = 2
                    evidence.append(f"No KO data, high pLI ({pli:.2f}) - caution [T3]")

    # 3. Known ADRs (0-5)
    safety_profile = all_data.get('ot_foundation', {}).get('data', {}).get('safety', {})

    if isinstance(safety_profile, dict) and 'data' in safety_profile:
        liabilities = safety_profile.get('data', [])
        severe = [l for l in liabilities if isinstance(l, dict) and l.get('severity') == 'High']

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

    result = {
        'scores': scores,
        'evidence': evidence,
        'safety_flags': safety_flags
    }

    # Save raw data
    output_file = output_dir / 'section10_safety_scoring.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    return result


if __name__ == "__main__":
    print("Safety scoring module loaded")