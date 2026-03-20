#!/usr/bin/env python3
"""
Target Validation Pipeline Runner
Orchestrates all sections and generates the complete report.
Each section is independent and outputs to intermediate layer.
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from tooluniverse import ToolUniverse

# Part A: Target Intelligence
from section1_identifiers import get_target_identifiers
from section2_basic_info import get_basic_information
from section3_structure import get_structural_biology
from section4_pathways import get_function_pathways
from section5_ppi import get_protein_interactions
from section6_expression import get_expression_profile
from section7_genetics import get_genetic_variation

# Open Targets Foundation
from open_targets_foundation import get_open_targets_foundation

# Part B: Validation Assessment
from section8_disease_scoring import score_disease_association
from section9_druggability_scoring import score_druggability
from section10_safety_scoring import score_safety
from section11_clinical_scoring import score_clinical_precedent
from section12_validation_scoring import score_validation_evidence
from section13_composite_scoring import calculate_composite_score

# Visualization
from visualization import generate_all_visualizations

# Report Generation
from report_generator import ReportGenerator


def run_validation_pipeline(
    target: str,
    disease: Optional[str] = None,
    output_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Run the complete target validation pipeline.
    Each section is independent and saves raw data to intermediate layer.

    Parameters:
        target: Target gene symbol or name
        disease: Optional disease context
        output_dir: Directory to save all outputs

    Returns:
        Dictionary containing all results
    """
    # Initialize
    tu = ToolUniverse()
    tu.load_tools()

    if output_dir is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path(f'./reports/run_{target}_{timestamp}')

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Starting target validation for: {target}")
    print(f"Output directory: {output_dir}")

    # ===== Part A: Target Intelligence =====
    print("\n" + "="*50)
    print("Part A: Target Intelligence")
    print("="*50)

    # Section 1: Target Identifiers
    print("\n--- Section 1: Target Identifiers ---")
    ids = get_target_identifiers(tu, target, output_dir)
    if not ids.get('symbol') and not ids.get('uniprot'):
        return {'error': f"Could not resolve target: {target}"}
    print(f"Resolved: {ids.get('symbol')} ({ids.get('uniprot')})")

    # Section 2: Basic Information
    print("\n--- Section 2: Basic Information ---")
    section2_data = get_basic_information(tu, ids, output_dir)

    # Section 3: Structural Biology
    print("\n--- Section 3: Structural Biology ---")
    section3_data = get_structural_biology(tu, ids, section2_data, output_dir)
    print(f"PDB structures: {len(section3_data.get('data', {}).get('pdb_structures', []))}")

    # Section 4: Function & Pathways
    print("\n--- Section 4: Function & Pathways ---")
    section4_data = get_function_pathways(tu, ids, output_dir)

    # Section 5: Protein Interactions
    print("\n--- Section 5: Protein Interactions ---")
    section5_data = get_protein_interactions(tu, ids, output_dir)
    print(f"PPI source: {section5_data.get('source')}, count: {len(section5_data.get('data', {}).get('interactors', []))}")

    # Section 6: Expression Profile
    print("\n--- Section 6: Expression Profile ---")
    section6_data = get_expression_profile(tu, ids, output_dir)
    print(f"Expression source: {section6_data.get('source')}")

    # Section 7: Genetic Variation
    print("\n--- Section 7: Genetic Variation ---")
    section7_data = get_genetic_variation(tu, ids, output_dir)

    # ===== Open Targets Foundation =====
    print("\n" + "="*50)
    print("Open Targets Foundation Data")
    print("="*50)
    ot_data = get_open_targets_foundation(tu, ids, output_dir)

    # Auto-discover disease
    if not disease:
        auto_diseases = ot_data.get('data', {}).get('auto_discovered_diseases', [])
        if auto_diseases:
            disease = auto_diseases[0].get('name')
            print(f"Auto-discovered disease: {disease}")

    # Compile all data
    all_data = {
        'section2_basic_info': section2_data,
        'section3_structure': section3_data,
        'section4_pathways': section4_data,
        'section5_ppi': section5_data,
        'section6_expression': section6_data,
        'section7_genetics': section7_data,
        'ot_foundation': ot_data
    }

    # ===== Part B: Validation Assessment =====
    print("\n" + "="*50)
    print("Part B: Validation Assessment")
    print("="*50)

    # Section 8: Disease Association Scoring
    print("\n--- Section 8: Disease Association Scoring ---")
    section8_result = score_disease_association(tu, ids, all_data, disease, output_dir)
    print(f"Disease score: {section8_result['scores']['total']}/30")

    # Section 9: Druggability Assessment
    print("\n--- Section 9: Druggability Assessment ---")
    section9_result = score_druggability(tu, ids, all_data, output_dir)
    print(f"Druggability score: {section9_result['scores']['total']}/25")

    # Section 10: Safety Analysis
    print("\n--- Section 10: Safety Analysis ---")
    section10_result = score_safety(ids, all_data, output_dir)
    print(f"Safety score: {section10_result['scores']['total']}/20")

    # Section 11: Clinical Precedent
    print("\n--- Section 11: Clinical Precedent ---")
    section11_result = score_clinical_precedent(all_data, output_dir)
    print(f"Clinical precedent score: {section11_result['score']}/15")

    # Section 12: Validation Evidence
    print("\n--- Section 12: Validation Evidence ---")
    section12_result = score_validation_evidence(all_data, output_dir)
    print(f"Validation evidence score: {section12_result['scores']['total']}/10")

    # Section 13: Composite Score
    print("\n--- Section 13: Composite Score ---")
    scoring_results = {
        'section8': section8_result,
        'section9': section9_result,
        'section10': section10_result,
        'section11': section11_result,
        'section12': section12_result
    }
    section13_result = calculate_composite_score(scoring_results, output_dir)
    print(f"Total score: {section13_result['total']}/100")
    print(f"Tier: {section13_result['tier']}")

    # Update scoring results with composite
    scoring_results['section13'] = section13_result

    # ===== Visualizations =====
    print("\n" + "="*50)
    print("Generating Visualizations")
    print("="*50)
    viz_paths = generate_all_visualizations(scoring_results, all_data, output_dir)
    print(f"Generated {len(viz_paths)} visualizations")

    # ===== Part C: Report Generation =====
    print("\n" + "="*50)
    print("Part C: Report Generation")
    print("="*50)

    generator = ReportGenerator(output_dir)

    # Generate Part A report
    print("  Generating Part A report...")
    generator.generate_part_a(ids, all_data, viz_paths)

    # Generate Part B report
    print("  Generating Part B report...")
    generator.generate_part_b(scoring_results, viz_paths)

    # Generate Part C report
    print("  Generating Part C report...")
    generator.generate_part_c(ids, scoring_results, all_data)

    # Generate Executive Summary (last)
    print("  Generating Executive Summary (last)...")
    generator.generate_executive_summary(ids, scoring_results, viz_paths)

    # Generate combined report
    print("  Generating combined report...")
    combined_path = generator.generate_combined_report(ids, all_data, scoring_results, viz_paths)

    # Save summary
    summary = {
        'metadata': {
            'target': ids.get('symbol'),
            'uniprot_id': ids.get('uniprot'),
            'ensembl_id': ids.get('ensembl'),
            'disease': disease,
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'identifiers': ids,
        'validation_score': section13_result,
        'safety_flags': section10_result.get('safety_flags', []),
        'report_path': str(combined_path)
    }

    summary_path = output_dir / 'validation_summary.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

    # Print final summary
    print("\n" + "="*50)
    print("VALIDATION COMPLETE")
    print("="*50)
    print(f"Target: {ids.get('symbol')} ({ids.get('uniprot')})")
    print(f"Total Score: {section13_result['total']}/100")
    print(f"Tier: {section13_result['tier']}")
    print(f"Recommendation: {section13_result['recommendation']}")
    print(f"\nReport saved to: {combined_path}")
    print("="*50)

    return {
        'ids': ids,
        'all_data': all_data,
        'scoring_results': scoring_results,
        'report_path': combined_path
    }


def main():
    parser = argparse.ArgumentParser(description='Target Validation Pipeline')
    parser.add_argument('target', help='Target gene symbol or name')
    parser.add_argument('--disease', '-d', help='Disease context')
    parser.add_argument('--output', '-o', help='Output directory')

    args = parser.parse_args()
    output_dir = Path(args.output) if args.output else None

    return run_validation_pipeline(
        target=args.target,
        disease=args.disease,
        output_dir=output_dir
    )


if __name__ == "__main__":
    main()