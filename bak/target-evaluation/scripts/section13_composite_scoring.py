#!/usr/bin/env python3
"""
Section 13: Composite Score
Combines all scores and assigns priority tier.
Raw scores output to intermediate layer.
"""

import json
from typing import Dict, Any
from pathlib import Path


def calculate_composite_score(scoring_results: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """
    Calculate total validation score and assign tier.
    Section 13: Composite Score

    Parameters:
        scoring_results: All section scoring results
        output_dir: Directory for intermediate data

    Returns:
        Dictionary with composite scoring results
    """
    disease_score = scoring_results.get('section8', {}).get('scores', {}).get('total', 0)
    druggability_score = scoring_results.get('section9', {}).get('scores', {}).get('total', 0)
    safety_score = scoring_results.get('section10', {}).get('scores', {}).get('total', 0)
    clinical_score = scoring_results.get('section11', {}).get('score', 0)
    validation_score = scoring_results.get('section12', {}).get('scores', {}).get('total', 5)

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

    result = {
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

    # Save raw data
    output_file = output_dir / 'section13_composite_scoring.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    return result


if __name__ == "__main__":
    print("Composite scoring module loaded")