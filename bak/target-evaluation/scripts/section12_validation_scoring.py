#!/usr/bin/env python3
"""
Section 12: Validation Evidence (0-10 pts)
Evaluates functional studies and disease models.
Raw scores output to intermediate layer.
"""

import json
from typing import Dict, Any
from pathlib import Path


def score_validation_evidence(all_data: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """
    Calculate validation evidence score.
    Section 12: Validation Evidence

    Parameters:
        all_data: All collected data
        output_dir: Directory for intermediate data

    Returns:
        Dictionary with scoring results
    """
    scores = {'functional': 0, 'models': 0, 'total': 0}
    evidence = []

    # Check mouse models for functional validation
    mouse_models = all_data.get('ot_foundation', {}).get('data', {}).get('mouse_models', {})
    if isinstance(mouse_models, dict) and 'data' in mouse_models:
        models = mouse_models['data']
        if models:
            has_phenotype = any(
                m.get('phenotype_label') for m in models if isinstance(m, dict)
            )
            if has_phenotype:
                scores['functional'] = 3
                evidence.append("Mouse model with relevant phenotype [T2]")

    scores['total'] = scores['functional'] + scores['models']

    result = {
        'scores': scores,
        'evidence': evidence
    }

    # Save raw data
    output_file = output_dir / 'section12_validation_scoring.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    return result


if __name__ == "__main__":
    print("Validation evidence scoring module loaded")