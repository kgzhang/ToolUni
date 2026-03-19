#!/usr/bin/env python3
"""
Target Validation Pipeline Orchestrator

Coordinates all phases with modular architecture, visualization generation,
and comprehensive report production.

Usage:
    python run_validation.py TARGET [--disease DISEASE] [--modality MODALITY]
"""

import json
import os
import sys
import argparse
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path

# Use relative imports - add parent directory to path for imports
_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from tooluniverse import ToolUniverse

# Import phase modules using relative imports
from phase0_disambiguation import TargetDisambiguation
from phase1_opentargets import OpenTargetsFoundation
from phases2_7_data_collection import DataCollectionPipeline
from phases8_12_scoring import ScoringPipeline

# Import utility modules
from visualization import ValidationVisualizer
from report_generator import ReportGenerator
from pipeline_core import save_json, get_tier_description


class TargetValidationOrchestrator:
    """
    Orchestrates the target validation pipeline with modular architecture.

    Flow:
    1. Phase 0: Disambiguation (must succeed)
    2. Phase 1: Open Targets Foundation
    3. Phases 2-7: Data Collection
    4. Phases 8-12: Scoring
    5. Visualization Generation
    6. Report Generation
    """

    def __init__(self, tu: Optional[ToolUniverse] = None, language: str = 'zh'):
        self.tu = tu or ToolUniverse()
        self.tu.load_tools()
        self.target = None
        self.context = {'disease': None, 'modality': None}
        self.language = language

    def run(self, target: str, disease: str = None, modality: str = None) -> Dict:
        """
        Run complete validation pipeline.

        Args:
            target: Gene symbol, alias, or name to validate
            disease: Disease context for targeted analysis
            modality: Drug modality (SM, AB, PROTAC)

        Returns:
            Complete validation results dictionary
        """
        self.target = target
        self.context = {'disease': disease, 'modality': modality}

        # Create timestamped output directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path('reports') / f'run_{target}_{timestamp}'
        output_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = str(output_dir)

        # Create figures subdirectory
        Path(f"{self.output_dir}/figures").mkdir(parents=True, exist_ok=True)

        self._print_header(target, disease, modality)

        results = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'context': self.context,
            'phases': {}
        }

        # Execute phases
        phase0_result = self._run_phase0(target)
        results['phases']['phase0'] = phase0_result

        if phase0_result['status'] != 'success':
            print(f"\n  ERROR: Phase 0 failed - cannot continue")
            return results

        ids = phase0_result['ids']

        # Phase 1: Open Targets
        phase1_result = self._run_phase1(ids)
        results['phases']['phase1'] = phase1_result

        # Phases 2-7: Data Collection
        phases2_7_result = self._run_phases2_7(ids)
        results['phases']['phases2-7'] = phases2_7_result

        # Phases 8-12: Scoring
        phases8_12_result = self._run_phases8_12(ids, phase1_result, phases2_7_result)
        results['phases']['phases8-12'] = phases8_12_result

        # Generate visualizations
        figure_files = self._generate_visualizations(results)

        # Generate report
        report_file = self._generate_report(results, figure_files)

        # Compile final results
        final_output = self._compile_results(
            ids, results, phases8_12_result, report_file, figure_files
        )

        # Save and print summary
        self._save_results(final_output)
        self._print_summary(phases8_12_result, report_file)

        return final_output

    def _print_header(self, target: str, disease: str, modality: str):
        """Print pipeline header."""
        print(f"\n{'='*70}")
        print(f"  TARGET VALIDATION PIPELINE")
        print(f"  Target: {target}")
        if disease:
            print(f"  Disease Context: {disease}")
        if modality:
            print(f"  Modality: {modality}")
        print(f"  Output: {self.output_dir}")
        print(f"{'='*70}")

    def _run_phase0(self, target: str) -> Dict:
        """Run Phase 0: Target Disambiguation."""
        print(f"\n{'─'*70}")
        print("  PHASE 0: Target Disambiguation (MUST RUN FIRST)")
        print(f"{'─'*70}")

        phase = TargetDisambiguation(self.tu)
        return phase.run(target, self.output_dir)

    def _run_phase1(self, ids: Dict) -> Dict:
        """Run Phase 1: Open Targets Foundation."""
        print(f"\n{'─'*70}")
        print("  PHASE 1: Open Targets Foundation")
        print(f"{'─'*70}")

        phase = OpenTargetsFoundation(self.tu)
        return phase.run(ids, self.output_dir)

    def _run_phases2_7(self, ids: Dict) -> Dict:
        """Run Phases 2-7: Data Collection."""
        print(f"\n{'─'*70}")
        print("  PHASES 2-7: Data Collection Pipeline")
        print(f"{'─'*70}")

        pipeline = DataCollectionPipeline(self.tu)
        return pipeline.run(ids, self.output_dir)

    def _run_phases8_12(self, ids: Dict, phase1: Dict, phases2_7: Dict) -> Dict:
        """Run Phases 8-12: Scoring."""
        print(f"\n{'─'*70}")
        print("  PHASES 8-12: Scoring Pipeline")
        print(f"{'─'*70}")

        pipeline = ScoringPipeline(self.tu)
        return pipeline.run(ids, phase1, phases2_7, self.output_dir)

    def _generate_visualizations(self, results: Dict) -> List[str]:
        """Generate all matplotlib visualizations."""
        print(f"\n{'─'*70}")
        print("  GENERATING VISUALIZATIONS")
        print(f"{'─'*70}")

        viz = ValidationVisualizer(f"{self.output_dir}/figures", language=self.language)
        files = []

        composite = results['phases']['phases8-12'].get('composite', {})
        ids = results['phases']['phase0']['ids']
        phase1_data = results['phases']['phase1'].get('data', {})
        phases2_7 = results['phases']['phases2-7']
        phases8_12 = results['phases']['phases8-12']

        # 1. Validation Score Radar
        if composite:
            files.append(viz.plot_validation_score(composite))
            print(f"      validation_score.png")

        # 2. Disease Associations Bar Chart
        diseases = self._extract_diseases(phase1_data)
        if diseases:
            files.append(viz.plot_disease_associations(diseases))
            print(f"      disease_associations.png")

        # 3. Tissue Expression Bar Chart
        gtex_data = phases2_7.get('results', {}).get('phase6', {}).get('data', {}).get('gtex', [])
        if gtex_data:
            tissues = [{'tissue': e.get('tissue', {}).get('name', 'Unknown'),
                       'tpm': e.get('median', 0)} for e in gtex_data]
            files.append(viz.plot_tissue_expression({
                'tissues': tissues,
                'critical_tissues': ['heart', 'liver', 'kidney', 'brain', 'bone marrow']
            }))
            print(f"      tissue_expression.png")

        # 4. Clinical Precedent Pie Chart
        drugs_data = phase1_data.get('drugs', {}).get('knownDrugs', {}).get('rows', [])
        if drugs_data:
            drugs = [{'name': d.get('drug', {}).get('name', 'Unknown'),
                     'phase': d.get('phase', 0),
                     'is_approved': d.get('drug', {}).get('isApproved', False)}
                    for d in drugs_data[:10]]
            files.append(viz.plot_clinical_timeline(drugs))
            print(f"      clinical_timeline.png")

        # 5. Safety Dashboard Radar
        safety_data = self._build_safety_data(phases2_7, phase1_data, phases8_12)
        files.append(viz.plot_safety_dashboard(safety_data))
        print(f"      safety_dashboard.png")

        return files

    def _extract_diseases(self, phase1_data: Dict) -> List[Dict]:
        """Extract disease list from Open Targets data."""
        diseases = []
        rows = phase1_data.get('diseases', {}).get('associatedDiseases', {}).get('rows', [])
        for row in rows[:10]:
            disease = row.get('disease', {})
            scores = row.get('datasourceScores', [])
            max_score = max([s.get('score', 0) for s in scores]) if scores else 0
            diseases.append({
                'name': disease.get('name', 'Unknown'),
                'id': disease.get('id', ''),
                'score': max_score
            })
        return diseases

    def _build_safety_data(self, phases2_7: Dict, phase1_data: Dict, phases8_12: Dict) -> Dict:
        """Build safety data for visualization."""
        safety_data = {
            'expression': {},
            'mouse_ko': 'unknown',
            'gnomad_pli': phases2_7.get('summary', {}).get('gnomad_pli', 0),
            'flags': phases8_12.get('results', {}).get('phase10', {}).get('safety_flags', []),
            'score': phases8_12.get('results', {}).get('phase10', {}).get('scores', {}).get('total', 0)
        }

        # Critical tissue expression
        critical_tissues = phases2_7.get('results', {}).get('phase6', {}).get('data', {}).get('critical_tissue_expression', [])
        for ct in critical_tissues:
            safety_data['expression'][ct['tissue']] = ct['tpm']

        # Mouse models
        mouse_models = phase1_data.get('mouse_models', {}).get('mousePhenotypes', [])
        if mouse_models:
            lethal = any('lethal' in str(m).lower() for m in mouse_models)
            safety_data['mouse_ko'] = 'lethal' if lethal else 'viable'

        return safety_data

    def _generate_report(self, results: Dict, figure_files: List[str]) -> str:
        """Generate comprehensive markdown report."""
        print(f"\n{'─'*70}")
        print("  GENERATING REPORT")
        print(f"{'─'*70}")

        generator = ReportGenerator(self.output_dir, language=self.language)
        report_file = generator.generate(results, figure_files)

        print(f"      {report_file}")
        return report_file

    def _compile_results(self, ids: Dict, results: Dict, phases8_12: Dict,
                         report_file: str, figure_files: List[str]) -> Dict:
        """Compile final results dictionary."""
        composite = phases8_12.get('composite', {})

        return {
            'metadata': {
                'target': ids.get('symbol', self.target),
                'query': self.target,
                'timestamp': datetime.now().isoformat(),
                'disease_context': self.context.get('disease'),
                'modality': self.context.get('modality'),
            },
            'ids': ids,
            'phases': results['phases'],
            'composite': composite,
            'report_file': report_file,
            'figure_files': figure_files,
        }

    def _save_results(self, final_output: Dict):
        """Save final results to JSON."""
        symbol = final_output['ids'].get('symbol', self.target)
        output_file = f"{self.output_dir}/{symbol}_validation_results.json"
        save_json(final_output, output_file)
        self.final_file = output_file

    def _print_summary(self, phases8_12: Dict, report_file: str):
        """Print final summary."""
        composite = phases8_12.get('composite', {})

        print(f"\n{'='*70}")
        print(f"  VALIDATION COMPLETE")
        print(f"{'='*70}")
        print(f"  Score: {composite.get('total_score', 0)}/100")
        print(f"  Tier: {composite.get('tier', 4)}")
        print(f"  Recommendation: {composite.get('recommendation', 'N/A')}")
        print(f"{'='*70}")
        print(f"\n  Output Files:")
        print(f"    - {self.final_file}")
        print(f"    - {report_file}")
        print(f"    - {self.output_dir}/figures/")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Target Validation Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_validation.py STING
    python run_validation.py EGFR
    python run_validation.py KRAS --disease "non-small cell lung cancer"
    python run_validation.py CCR8 --modality "small molecule"
        """
    )
    parser.add_argument('target', help='Gene symbol, alias, or name to validate')
    parser.add_argument('--disease', '-d', default=None, help='Disease context')
    parser.add_argument('--modality', '-m', default=None, help='Drug modality')
    parser.add_argument('--language', '-l', default='zh', choices=['zh', 'en'], help='Report language (default: zh)')
    args = parser.parse_args()

    orchestrator = TargetValidationOrchestrator(language=args.language)
    result = orchestrator.run(
        args.target,
        disease=args.disease,
        modality=args.modality
    )

    return result


if __name__ == '__main__':
    main()