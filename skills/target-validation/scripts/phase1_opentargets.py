#!/usr/bin/env python3
"""
Phase 1: Open Targets Foundation
PRIMARY data source - query FIRST before other phases.
Provides baseline data for all subsequent phases.
"""

import json
import sys
from typing import Dict, Optional, Any, List
from pathlib import Path

# Use relative imports
_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from tooluniverse import ToolUniverse


class OpenTargetsFoundation:
    """Phase 1: Query Open Targets for baseline data."""

    # Open Targets queries to execute
    QUERIES = [
        ('diseases', 'OpenTargets_get_diseases_phenotypes_by_target_ensembl', {'ensemblId': 'ensembl'}),
        ('tractability', 'OpenTargets_get_target_tractability_by_ensemblID', {'ensemblId': 'ensembl'}),
        ('safety', 'OpenTargets_get_target_safety_profile_by_ensemblID', {'ensemblId': 'ensembl'}),
        ('interactions', 'OpenTargets_get_target_interactions_by_ensemblID', {'ensemblId': 'ensembl'}),
        ('go_terms', 'OpenTargets_get_target_gene_ontology_by_ensemblID', {'ensemblId': 'ensembl'}),
        ('mouse_models', 'OpenTargets_get_biological_mouse_models_by_ensemblID', {'ensemblId': 'ensembl'}),
        ('probes', 'OpenTargets_get_chemical_probes_by_target_ensemblID', {'ensemblId': 'ensembl'}),
        ('drugs', 'OpenTargets_get_associated_drugs_by_target_ensemblID', {'ensemblId': 'ensembl', 'size': 100}),
        ('classes', 'OpenTargets_get_target_classes_by_ensemblID', {'ensemblId': 'ensembl'}),
        ('homologues', 'OpenTargets_get_target_homologues_by_ensemblID', {'ensemblId': 'ensembl'}),
        ('publications', 'OpenTargets_get_publications_by_target_ensemblID', {'entityId': 'ensembl'}),
    ]

    def __init__(self, tu: Optional[ToolUniverse] = None):
        self.tu = tu or ToolUniverse()
        self.tu.load_tools()

    def _call_tool(self, tool_name: str, **kwargs) -> Optional[Any]:
        """Call a tool and unwrap data key."""
        try:
            tool = getattr(self.tu.tools, tool_name)
            result = tool(**kwargs)
            if isinstance(result, dict) and 'data' in result:
                return result['data']
            return result
        except Exception as e:
            print(f"      [ERROR] {tool_name}: {e}")
            return None

    def run(self, ids: Dict, output_dir: str = ".") -> Dict:
        """
        Run Open Targets foundation queries.

        Args:
            ids: Resolved identifiers from Phase 0
            output_dir: Directory to save intermediate files

        Returns:
            Dictionary with all Open Targets data
        """
        print(f"\n{'='*60}")
        print("PHASE 1: Open Targets Foundation")
        print(f"{'='*60}")

        ensembl_id = ids.get('ensembl')
        if not ensembl_id:
            print("  ERROR: No Ensembl ID available")
            return {'phase': 1, 'status': 'failed', 'error': 'No Ensembl ID'}

        print(f"  Ensembl ID: {ensembl_id}")

        data = {}
        warnings = []

        # Execute all queries
        for key, tool_name, params_template in self.QUERIES:
            print(f"\n  Querying {key}...")

            # Build parameters
            params = {}
            for k, v in params_template.items():
                if v == 'ensembl':
                    params[k] = ensembl_id
                else:
                    params[k] = v

            result = self._call_tool(tool_name, **params)
            data[key] = self._extract_target_data(result, key)

            if data[key]:
                count = self._get_count(data[key], key)
                print(f"      ✓ {count} records")
            else:
                warnings.append(f"No data for {key}")
                print(f"      ⚠ No data")

        # Parse and summarize
        summary = self._create_summary(data)

        result = {
            'phase': 1,
            'phase_name': 'Open Targets Foundation',
            'status': 'success',
            'data': data,
            'summary': summary,
            'warnings': warnings
        }

        # Save intermediate file
        output_file = f"{output_dir}/phase1_opentargets.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n  Saved: {output_file}")

        return result

    def _extract_target_data(self, result: Any, key: str) -> Any:
        """Extract target-specific data from response."""
        if not result:
            return None
        if isinstance(result, dict):
            # Most Open Targets responses have target as top-level key
            if 'target' in result:
                return result['target']
            return result
        return result

    def _get_count(self, data: Any, key: str) -> str:
        """Get count description for data."""
        if data is None:
            return "0"
        if isinstance(data, list):
            return str(len(data))
        if isinstance(data, dict):
            # Check for count fields
            for count_key in ['count', 'total']:
                if count_key in data:
                    return str(data[count_key])
            # Check for nested lists
            for nested_key in ['rows', 'data', 'items']:
                if nested_key in data and isinstance(data[nested_key], list):
                    return str(len(data[nested_key]))
            return "1"
        return "1"

    def _create_summary(self, data: Dict) -> Dict:
        """Create summary of Open Targets data."""

        # Extract top diseases
        diseases = []
        if data.get('diseases'):
            disease_data = data['diseases'].get('associatedDiseases', {})
            rows = disease_data.get('rows', [])
            for row in rows[:10]:
                disease = row.get('disease', {})
                scores = row.get('datasourceScores', [])
                max_score = max([s.get('score', 0) for s in scores]) if scores else 0
                diseases.append({
                    'name': disease.get('name'),
                    'id': disease.get('id'),
                    'score': max_score
                })

        # Extract tractability
        tractability_sm = {'has_ligand': False, 'has_pocket': False, 'bucket': None}
        if data.get('tractability'):
            for t in data['tractability'].get('tractability', []):
                if t.get('modality') == 'SM':
                    if t.get('label') == 'High-Quality Ligand' and t.get('value'):
                        tractability_sm['has_ligand'] = True
                    if t.get('label') == 'High-Quality Pocket' and t.get('value'):
                        tractability_sm['has_pocket'] = True

        # Extract drugs
        drugs = {'approved': 0, 'clinical': 0, 'names': []}
        if data.get('drugs'):
            drug_data = data['drugs'].get('knownDrugs', {})
            rows = drug_data.get('rows', [])
            for d in rows:
                phase = d.get('phase', 0)
                if phase == 4:
                    drugs['approved'] += 1
                elif phase in [1, 2, 3]:
                    drugs['clinical'] += 1
                if d.get('drug', {}).get('name'):
                    drugs['names'].append(d['drug']['name'])
            drugs['names'] = list(set(drugs['names']))[:5]

        # Extract mouse models
        mouse_count = 0
        if data.get('mouse_models'):
            mouse_count = len(data['mouse_models'].get('mousePhenotypes', []))

        # Extract publications count
        pubs_count = 0
        if data.get('publications'):
            pubs_count = data['publications'].get('publicationsCount', 0)

        return {
            'disease_count': len(diseases),
            'top_diseases': diseases[:5],
            'tractability_sm': tractability_sm,
            'drugs': drugs,
            'mouse_model_count': mouse_count,
            'publications_count': pubs_count
        }


def main():
    """CLI entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='Phase 1: Open Targets Foundation')
    parser.add_argument('--ids-file', required=True, help='JSON file with resolved IDs from Phase 0')
    parser.add_argument('--output-dir', default='.', help='Output directory')
    args = parser.parse_args()

    # Load IDs from Phase 0
    with open(args.ids_file) as f:
        phase0_result = json.load(f)
    ids = phase0_result['ids']

    phase = OpenTargetsFoundation()
    result = phase.run(ids, args.output_dir)

    print(f"\n{'='*60}")
    print(f"SUCCESS: Queried {len(result['data'])} Open Targets endpoints")
    print(f"{'='*60}")

    return result


if __name__ == '__main__':
    main()