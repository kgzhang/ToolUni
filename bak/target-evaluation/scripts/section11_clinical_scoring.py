#!/usr/bin/env python3
"""
Section 11: Clinical Precedent (0-15 pts)
Evaluates clinical development stage and approved drugs.
Raw scores output to intermediate layer.
"""

import json
from typing import Dict, Any
from pathlib import Path


def score_clinical_precedent(all_data: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """
    Calculate clinical precedent score.
    Section 11: Clinical Precedent

    Parameters:
        all_data: All collected data
        output_dir: Directory for intermediate data

    Returns:
        Dictionary with scoring results
    """
    score = 0
    evidence = []
    approved_drugs = []
    clinical_trials = []

    drugs_data = all_data.get('ot_foundation', {}).get('data', {}).get('drugs', {})

    # Handle nested structure: drugs.target.knownDrugs.rows
    drug_rows = []
    if isinstance(drugs_data, dict):
        target = drugs_data.get('target', {})
        if isinstance(target, dict):
            known_drugs = target.get('knownDrugs', {})
            if isinstance(known_drugs, dict):
                drug_rows = known_drugs.get('rows', [])
        # Fallback to direct data
        if not drug_rows and 'data' in drugs_data:
            drug_rows = drugs_data['data']
    elif isinstance(drugs_data, list):
        drug_rows = drugs_data

    for drug_entry in drug_rows:
        if not isinstance(drug_entry, dict):
            continue
        # Get drug info from nested structure
        drug_info = drug_entry.get('drug', drug_entry)
        phase = drug_entry.get('phase', drug_info.get('maximumClinicalTrialPhase', 0))
        drug_name = drug_info.get('name', drug_entry.get('name', 'Unknown'))

        if phase == 4:  # Approved
            approved_drugs.append({
                'name': drug_name,
                'phase': phase,
                'indication': drug_entry.get('disease', {}).get('name', 'Unknown'),
                'trade_names': drug_info.get('tradeNames', [])
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

    result = {
        'score': score,
        'evidence': evidence,
        'approved_drugs': approved_drugs[:5],
        'clinical_trials': clinical_trials[:10]
    }

    # Save raw data
    output_file = output_dir / 'section11_clinical_scoring.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    return result


if __name__ == "__main__":
    print("Clinical precedent scoring module loaded")