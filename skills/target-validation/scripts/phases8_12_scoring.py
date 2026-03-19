#!/usr/bin/env python3
"""
Phase 8-12: Scoring Pipeline
Calculate validation scores across all dimensions.
- Phase 8: Disease Association (0-30 pts)
- Phase 9: Druggability (0-25 pts)
- Phase 10: Safety (0-20 pts)
- Phase 11: Clinical Precedent (0-15 pts)
- Phase 12: Validation Evidence (0-10 pts)

Includes modality-specific tractability assessment.
"""

import json
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path

# Use relative imports
_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from tooluniverse import ToolUniverse

# Import modality tractability module
from modality_tractability import assess_modality_tractability


class ScoringPipeline:
    """Phases 8-12: Calculate validation scores."""

    def __init__(self, tu: ToolUniverse = None):
        self.tu = tu or ToolUniverse()
        self.tu.load_tools()

    def _call_tool(self, tool_name: str, **kwargs) -> Any:
        """Call tool and unwrap data key."""
        try:
            tool = getattr(self.tu.tools, tool_name)
            result = tool(**kwargs)
            if isinstance(result, dict) and 'data' in result:
                return result['data']
            return result
        except:
            return None

    def run(self, ids: Dict, ot_data: Dict, collection_data: Dict, output_dir: str = ".") -> Dict:
        """Run all scoring phases."""
        print(f"\n{'='*60}")
        print("PHASES 8-12: Scoring Pipeline")
        print(f"{'='*60}")

        results = {}

        # Extract data references
        ot = ot_data.get('data', {})
        phase2_7 = collection_data.get('results', {})

        # Phase 8: Disease Association
        results['phase8'] = self._score_disease(ids, ot, phase2_7)

        # Phase 9: Druggability (includes modality assessment)
        results['phase9'] = self._score_druggability(ids, ot, phase2_7)

        # Modality-specific tractability assessment
        results['modality_tractability'] = self._assess_modality_tractability(ids, ot, phase2_7)

        # Phase 10: Safety
        results['phase10'] = self._score_safety(ids, ot, phase2_7)

        # Phase 11: Clinical Precedent
        results['phase11'] = self._score_clinical(ot)

        # Phase 12: Validation Evidence
        results['phase12'] = self._score_validation(ot, phase2_7)

        # Calculate composite
        composite = self._calculate_composite(results)

        output = {
            'phases': ['phase8', 'phase9', 'phase10', 'phase11', 'phase12'],
            'results': results,
            'composite': composite,
            'modality_tractability': results.get('modality_tractability', {})
        }

        # Save
        output_file = f"{output_dir}/phases8-12_scoring.json"
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        print(f"\n  Saved: {output_file}")

        return output

    def _score_disease(self, ids: Dict, ot: Dict, phase2_7: Dict) -> Dict:
        """Phase 8: Disease Association Scoring (0-30 pts)."""
        print(f"\n  {'─'*40}")
        print("  PHASE 8: Disease Association Scoring")
        print(f"  {'─'*40}")

        scores = {'genetic': 0, 'literature': 0, 'pathway': 0, 'total': 0}
        evidence = []

        # Get disease associations from Open Targets
        diseases = []
        if ot.get('diseases'):
            assoc = ot['diseases'].get('associatedDiseases', {})
            for row in assoc.get('rows', []):
                disease = row.get('disease', {})
                ds_scores = row.get('datasourceScores', [])
                max_score = max([s.get('score', 0) for s in ds_scores]) if ds_scores else 0
                diseases.append({
                    'name': disease.get('name'),
                    'id': disease.get('id'),
                    'score': max_score
                })

        if diseases:
            diseases.sort(key=lambda x: x['score'], reverse=True)
            top = diseases[0]

            print(f"      Top disease: {top['name']} (score={top['score']:.2f})")
            evidence.append(f"Top disease: {top['name']} (score={top['score']:.2f}) [T3]")

            # Pathway score (0-10)
            if top['score'] > 0.8:
                scores['pathway'] = 10
            elif top['score'] > 0.5:
                scores['pathway'] = 7
            elif top['score'] > 0.2:
                scores['pathway'] = 4

            # Count significant diseases
            significant = [d for d in diseases if d['score'] > 0.3]
            if len(significant) > 10:
                scores['pathway'] = min(scores['pathway'] + 3, 10)
                evidence.append(f"{len(significant)} disease associations [T3]")

        # Genetic evidence from GWAS
        gwas = phase2_7.get('phase7', {}).get('data', {}).get('gwas', [])
        if gwas:
            significant = [a for a in gwas if a.get('pvalue', 1) < 5e-8]
            if significant:
                scores['genetic'] = min(len(significant) * 2, 10)
                evidence.append(f"GWAS: {len(significant)} significant loci [T3]")
                print(f"      GWAS significant: {len(significant)}")

        # gnomAD constraint
        gnomad = phase2_7.get('phase7', {}).get('data', {}).get('gnomad', {})
        pli = gnomad.get('pLI')
        if pli is not None:
            print(f"      gnomAD pLI: {pli}")
            if pli > 0.9:
                scores['genetic'] = min(scores['genetic'] + 5, 10)
                evidence.append(f"pLI={pli:.3f} (highly constrained) [T3]")
            elif pli > 0.5:
                scores['genetic'] = min(scores['genetic'] + 3, 10)

        scores['total'] = scores['genetic'] + scores['literature'] + scores['pathway']
        scores['total'] = min(scores['total'], 30)

        print(f"      Score: {scores['total']}/30")

        return {
            'phase': 8,
            'status': 'success',
            'scores': scores,
            'evidence': evidence,
            'diseases': diseases[:10]
        }

    def _score_druggability(self, ids: Dict, ot: Dict, phase2_7: Dict) -> Dict:
        """Phase 9: Druggability Scoring (0-25 pts)."""
        print(f"\n  {'─'*40}")
        print("  PHASE 9: Druggability Scoring")
        print(f"  {'─'*40}")

        scores = {'structural': 0, 'chemical': 0, 'target_class': 0, 'total': 0}
        evidence = []

        # Tractability from Open Targets
        tractability = ot.get('tractability', {}).get('tractability', [])
        has_ligand = False
        has_pocket = False

        for t in tractability:
            if t.get('modality') == 'SM':
                if t.get('label') == 'High-Quality Ligand' and t.get('value'):
                    has_ligand = True
                if t.get('label') == 'Structure with Ligand' and t.get('value'):
                    has_ligand = True

        if has_ligand:
            scores['structural'] = 8
            evidence.append("High-quality ligand available [T2]")
            print(f"      ✓ Ligand available")

        # PDB structures
        pdb_count = len(phase2_7.get('phase3', {}).get('data', {}).get('pdb_structures', []))
        if pdb_count > 50:
            scores['structural'] = max(scores['structural'], 10)
            evidence.append(f"{pdb_count} PDB structures [T1]")
        elif pdb_count > 10:
            scores['structural'] = max(scores['structural'], 7)
            evidence.append(f"{pdb_count} PDB structures [T2]")
        elif pdb_count > 0:
            scores['structural'] = max(scores['structural'], 3)
            evidence.append(f"{pdb_count} PDB structures [T3]")

        print(f"      PDB structures: {pdb_count}")

        # Clinical compounds
        drugs = ot.get('drugs', {}).get('knownDrugs', {}).get('rows', [])
        if drugs:
            scores['chemical'] = 7
            compound_names = list(set([d.get('drug', {}).get('name', '') for d in drugs]))[:3]
            evidence.append(f"Clinical compounds: {', '.join(compound_names)} [T2]")
            print(f"      Clinical compounds: {len(drugs)}")

        scores['total'] = min(scores['structural'] + scores['chemical'] + scores['target_class'], 25)
        print(f"      Score: {scores['total']}/25")

        return {
            'phase': 9,
            'status': 'success',
            'scores': scores,
            'evidence': evidence
        }

    def _assess_modality_tractability(self, ids: Dict, ot: Dict, phase2_7: Dict) -> Dict:
        """Assess tractability across all drug modalities."""
        print(f"\n  {'─'*40}")
        print("  MODALITY TRACTABILITY ASSESSMENT")
        print(f"  {'─'*40}")

        # Prepare data for modality assessment
        target_data = {
            'target_class': self._extract_target_class(ot),
            'subcellular_location': self._extract_location(phase2_7),
            'gene_size_kb': 3.0,  # Default estimate
            'is_ppi_target': False
        }

        structure_data = {
            'pdb_count': len(phase2_7.get('phase3', {}).get('data', {}).get('pdb_structures', [])),
            'has_ligand_structure': self._check_ligand_structure(ot),
            'best_resolution': self._get_best_resolution(phase2_7),
            'binding_pockets': [],
            'surface_lysines': 10  # Default estimate
        }

        expression_data = {
            'tissue_specificity_score': self._calculate_tissue_specificity(phase2_7),
            'surface_expression_confirmed': False,
            'primary_tissue': self._get_primary_tissue(phase2_7),
            'tumor_specific_expression': False,
            'normal_tissue_expression': [],
            'internalization_rate': 'unknown'
        }

        genetic_data = {
            'pLI': phase2_7.get('phase7', {}).get('data', {}).get('gnomad', {}).get('pLI'),
            'paralogs': []
        }

        clinical_data = {
            'compound_count': len(ot.get('drugs', {}).get('knownDrugs', {}).get('rows', [])),
            'approved_drugs': sum(1 for d in ot.get('drugs', {}).get('knownDrugs', {}).get('rows', [])
                                  if d.get('drug', {}).get('isApproved', False))
        }

        # Run modality assessment
        try:
            modality_result = assess_modality_tractability(
                target_data, structure_data, expression_data, genetic_data, clinical_data
            )

            # Print summary
            best = modality_result.get('best_modality', 'N/A')
            tractable_count = modality_result.get('tractable_count', 0)
            print(f"      Best modality: {best}")
            print(f"      Tractable modalities: {tractable_count}/9")

            for modality, assessment in modality_result.get('assessments', {}).items():
                score = assessment.get('tractability_score', 0)
                bucket = assessment.get('bucket', 10)
                print(f"      - {assessment.get('modality', modality)}: {score:.0f}/100 (bucket {bucket})")

            return modality_result

        except Exception as e:
            print(f"      ⚠ Modality assessment failed: {e}")
            return {'assessments': {}, 'best_modality': None, 'tractable_count': 0}

    def _extract_target_class(self, ot: Dict) -> str:
        """Extract target class from Open Targets data."""
        classes = ot.get('classes', {}).get('targetClasses', [])
        if classes:
            return classes[0].get('name', 'Unknown')
        return 'Unknown'

    def _extract_location(self, phase2_7: Dict) -> str:
        """Extract subcellular location from UniProt data."""
        location = phase2_7.get('phase2', {}).get('data', {}).get('location')
        if location:
            if isinstance(location, dict):
                locs = location.get('subcellularLocations', [])
                if locs:
                    return locs[0].get('location', 'Unknown')
            return str(location)
        return 'Unknown'

    def _check_ligand_structure(self, ot: Dict) -> bool:
        """Check if ligand-bound structure exists."""
        tractability = ot.get('tractability', {}).get('tractability', [])
        for t in tractability:
            if t.get('modality') == 'SM':
                if 'Ligand' in t.get('label', '') and t.get('value'):
                    return True
        return False

    def _get_best_resolution(self, phase2_7: Dict) -> Optional[float]:
        """Get best PDB resolution."""
        structures = phase2_7.get('phase3', {}).get('data', {}).get('pdb_structures', [])
        best = None
        for s in structures:
            res = s.get('resolution')
            if res:
                try:
                    res_val = float(str(res).replace('Å', '').strip())
                    if best is None or res_val < best:
                        best = res_val
                except:
                    pass
        return best

    def _calculate_tissue_specificity(self, phase2_7: Dict) -> float:
        """Calculate tissue specificity score."""
        gtex = phase2_7.get('phase6', {}).get('data', {}).get('gtex', [])
        if not gtex:
            return 0.5
        # Simple specificity calculation
        tpms = [e.get('median', 0) for e in gtex]
        if not tpms or max(tpms) == 0:
            return 0.5
        # Higher specificity if expression concentrated in few tissues
        high_expr = sum(1 for t in tpms if t > max(tpms) * 0.5)
        return 1 - (high_expr / len(tpms))

    def _get_primary_tissue(self, phase2_7: Dict) -> str:
        """Get primary expressing tissue."""
        gtex = phase2_7.get('phase6', {}).get('data', {}).get('gtex', [])
        if gtex:
            sorted_gtex = sorted(gtex, key=lambda x: x.get('median', 0), reverse=True)
            if sorted_gtex:
                return sorted_gtex[0].get('tissue', {}).get('name', 'Unknown')
        return 'Unknown'

    def _score_safety(self, ids: Dict, ot: Dict, phase2_7: Dict) -> Dict:
        """Phase 10: Safety Scoring (0-20 pts)."""
        print(f"\n  {'─'*40}")
        print("  PHASE 10: Safety Scoring")
        print(f"  {'─'*40}")

        scores = {'expression': 0, 'genetic': 0, 'adverse': 0, 'total': 0}
        evidence = []
        safety_flags = []

        # Critical tissue expression
        critical_expr = phase2_7.get('phase6', {}).get('data', {}).get('critical_tissue_expression', [])
        if not critical_expr:
            scores['expression'] = 5
            evidence.append("Low expression in critical tissues [T2]")
            print(f"      ✓ Low critical tissue expression")
        else:
            tissues = ', '.join([e['tissue'] for e in critical_expr[:3]])
            safety_flags.append(f"High expression in: {tissues}")
            evidence.append(f"Expression in critical tissues: {tissues} [T2]")
            print(f"      ⚠ High expression in: {tissues}")

        # Mouse models
        mouse = ot.get('mouse_models', {}).get('mousePhenotypes', [])
        if mouse:
            lethal = any('lethal' in str(m).lower() for m in mouse)
            if lethal:
                safety_flags.append("Mouse KO lethal")
                evidence.append("Mouse KO: Lethal phenotype [T2]")
                print(f"      ⚠ Mouse KO lethal")
            else:
                scores['genetic'] = 7
                evidence.append(f"Mouse KO: Viable ({len(mouse)} phenotypes) [T2]")
                print(f"      ✓ Mouse KO viable: {len(mouse)} phenotypes")

        # Safety profile (check if liabilities exist)
        if ot.get('safety'):
            liabilities = ot['safety'].get('liabilities', [])
            if not liabilities:
                scores['adverse'] = 5
                evidence.append("No known safety liabilities [T2]")
                print(f"      ✓ No safety liabilities")

        scores['total'] = min(scores['expression'] + scores['genetic'] + scores['adverse'], 20)
        print(f"      Score: {scores['total']}/20")

        return {
            'phase': 10,
            'status': 'success',
            'scores': scores,
            'evidence': evidence,
            'safety_flags': safety_flags
        }

    def _score_clinical(self, ot: Dict) -> Dict:
        """Phase 11: Clinical Precedent Scoring (0-15 pts)."""
        print(f"\n  {'─'*40}")
        print("  PHASE 11: Clinical Precedent Scoring")
        print(f"  {'─'*40}")

        score = 0
        evidence = []
        drugs = []

        drug_data = ot.get('drugs', {}).get('knownDrugs', {}).get('rows', [])
        if drug_data:
            approved = [d for d in drug_data if d.get('drug', {}).get('isApproved', False)]
            phase3 = [d for d in drug_data if d.get('phase') == 3]
            phase2 = [d for d in drug_data if d.get('phase') == 2]
            phase1 = [d for d in drug_data if d.get('phase') == 1]

            if approved:
                score = 15
                evidence.append(f"{len(approved)} FDA-approved drugs [T1]")
                print(f"      ✓ {len(approved)} FDA-approved drugs")
            elif phase3:
                score = 10
                evidence.append("Phase 3 clinical trials [T2]")
                print(f"      Phase 3 trials: {len(phase3)}")
            elif phase2:
                score = 7
                evidence.append("Phase 2 clinical trials [T2]")
                print(f"      Phase 2 trials: {len(phase2)}")
            elif phase1:
                score = 5
                evidence.append("Phase 1 clinical trials [T2]")
                print(f"      Phase 1 trials: {len(phase1)}")

            drugs = list(set([d.get('drug', {}).get('name', '') for d in drug_data]))[:5]
            if drugs and score > 0:
                evidence.append(f"Clinical compounds: {', '.join(drugs[:3])} [T2]")

        if score == 0:
            evidence.append("No clinical development [T4]")
            print(f"      No clinical development")

        print(f"      Score: {score}/15")

        return {
            'phase': 11,
            'status': 'success',
            'score': score,
            'evidence': evidence,
            'drugs': drugs
        }

    def _score_validation(self, ot: Dict, phase2_7: Dict) -> Dict:
        """Phase 12: Validation Evidence Scoring (0-10 pts)."""
        print(f"\n  {'─'*40}")
        print("  PHASE 12: Validation Evidence Scoring")
        print(f"  {'─'*40}")

        scores = {'publications': 0, 'ppi': 0, 'structure': 0, 'total': 0}
        evidence = []

        # Publications
        pubs_count = ot.get('publications', {}).get('publicationsCount', 0)
        if pubs_count > 100:
            scores['publications'] = 4
            evidence.append(f"High publication count: {pubs_count} [T2]")
        elif pubs_count > 50:
            scores['publications'] = 3
            evidence.append(f"Moderate publication count: {pubs_count} [T3]")
        print(f"      Publications: {pubs_count}")

        # PPI network
        ppi_count = phase2_7.get('phase5', {}).get('data', {}).get('total_count', 0)
        if ppi_count > 50:
            scores['ppi'] = 3
            evidence.append(f"Strong PPI network: {ppi_count} interactions [T2]")
        elif ppi_count > 20:
            scores['ppi'] = 2
            evidence.append(f"Moderate PPI network: {ppi_count} interactions [T3]")
        print(f"      PPI interactions: {ppi_count}")

        # Structures
        pdb_count = len(phase2_7.get('phase3', {}).get('data', {}).get('pdb_structures', []))
        if pdb_count > 50:
            scores['structure'] = 3
            evidence.append(f"Extensive structural coverage: {pdb_count} PDB entries [T1]")
        elif pdb_count > 10:
            scores['structure'] = 2
            evidence.append(f"Good structural coverage: {pdb_count} PDB entries [T2]")

        scores['total'] = min(scores['publications'] + scores['ppi'] + scores['structure'], 10)
        print(f"      Score: {scores['total']}/10")

        return {
            'phase': 12,
            'status': 'success',
            'scores': scores,
            'evidence': evidence
        }

    def _calculate_composite(self, results: Dict) -> Dict:
        """Calculate composite score and recommendation."""
        print(f"\n  {'='*40}")
        print("  COMPOSITE SCORING")
        print(f"  {'='*40}")

        total = (
            results['phase8']['scores']['total'] +
            results['phase9']['scores']['total'] +
            results['phase10']['scores']['total'] +
            results['phase11']['score'] +
            results['phase12']['scores']['total']
        )

        if total >= 80:
            tier, recommendation = 1, "GO"
        elif total >= 60:
            tier, recommendation = 2, "CONDITIONAL GO"
        elif total >= 40:
            tier, recommendation = 3, "CAUTION"
        else:
            tier, recommendation = 4, "NO-GO"

        # ASCII visualization
        def bar(score, max_score, width=20):
            filled = int((score / max_score) * width) if max_score > 0 else 0
            return '█' * filled + '░' * (width - filled)

        print(f"\n    VALIDATION SCORE BREAKDOWN")
        print(f"    {'─'*50}")
        print(f"    Disease Association  [{bar(results['phase8']['scores']['total'], 30)}] {results['phase8']['scores']['total']:2d}/30")
        print(f"    Druggability         [{bar(results['phase9']['scores']['total'], 25)}] {results['phase9']['scores']['total']:2d}/25")
        print(f"    Safety Profile       [{bar(results['phase10']['scores']['total'], 20)}] {results['phase10']['scores']['total']:2d}/20")
        print(f"    Clinical Precedent   [{bar(results['phase11']['score'], 15)}] {results['phase11']['score']:2d}/15")
        print(f"    Validation Evidence  [{bar(results['phase12']['scores']['total'], 10)}] {results['phase12']['scores']['total']:2d}/10")
        print(f"    {'─'*50}")
        print(f"    TOTAL: {total}/100 | TIER {tier} | {recommendation}")

        return {
            'total_score': total,
            'tier': tier,
            'recommendation': recommendation,
            'score_breakdown': {
                'disease': results['phase8']['scores']['total'],
                'druggability': results['phase9']['scores']['total'],
                'safety': results['phase10']['scores']['total'],
                'clinical': results['phase11']['score'],
                'validation': results['phase12']['scores']['total']
            }
        }


def main():
    """CLI entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='Phases 8-12: Scoring')
    parser.add_argument('--ids-file', required=True, help='Phase 0 IDs file')
    parser.add_argument('--ot-file', required=True, help='Phase 1 Open Targets file')
    parser.add_argument('--collection-file', required=True, help='Phases 2-7 collection file')
    parser.add_argument('--output-dir', default='.', help='Output directory')
    args = parser.parse_args()

    # Load data
    with open(args.ids_file) as f:
        ids = json.load(f)['ids']
    with open(args.ot_file) as f:
        ot_data = json.load(f)
    with open(args.collection_file) as f:
        collection_data = json.load(f)

    pipeline = ScoringPipeline()
    result = pipeline.run(ids, ot_data, collection_data, args.output_dir)

    return result


if __name__ == '__main__':
    main()