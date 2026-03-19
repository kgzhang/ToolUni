#!/usr/bin/env python3
"""
Phase 2-7: Data Collection Pipeline
Combined data collection phases for efficiency.
- Phase 2: Core Identity (UniProt)
- Phase 3: Structure & Domains
- Phase 4: Function & Pathways
- Phase 5: Protein Interactions
- Phase 6: Expression Profile
- Phase 7: Genetic Variation
"""

import json
import sys
from typing import Dict, Optional, Any
from pathlib import Path

# Use relative imports
_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from tooluniverse import ToolUniverse


class DataCollectionPipeline:
    """Phases 2-7: Collect target intelligence data."""

    def __init__(self, tu: Optional[ToolUniverse] = None):
        self.tu = tu or ToolUniverse()
        self.tu.load_tools()

    def _call_tool(self, tool_name: str, **kwargs) -> Optional[Any]:
        """Call tool and unwrap data key."""
        try:
            tool = getattr(self.tu.tools, tool_name)
            result = tool(**kwargs)
            if isinstance(result, dict) and 'data' in result:
                return result['data']
            return result
        except Exception as e:
            return None

    def run(self, ids: Dict, output_dir: str = ".") -> Dict:
        """Run all data collection phases."""
        print(f"\n{'='*60}")
        print("PHASES 2-7: Data Collection Pipeline")
        print(f"{'='*60}")

        results = {}

        # Phase 2: Core Identity
        results['phase2'] = self._run_phase2(ids)

        # Phase 3: Structure & Domains
        results['phase3'] = self._run_phase3(ids, results['phase2'])

        # Phase 4: Function & Pathways
        results['phase4'] = self._run_phase4(ids)

        # Phase 5: Protein Interactions
        results['phase5'] = self._run_phase5(ids)

        # Phase 6: Expression Profile
        results['phase6'] = self._run_phase6(ids)

        # Phase 7: Genetic Variation
        results['phase7'] = self._run_phase7(ids)

        # Save combined results
        output = {
            'phases': ['phase2', 'phase3', 'phase4', 'phase5', 'phase6', 'phase7'],
            'results': results,
            'summary': self._create_summary(results)
        }

        output_file = f"{output_dir}/phases2-7_data_collection.json"
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        print(f"\n  Saved: {output_file}")

        return output

    def _run_phase2(self, ids: Dict) -> Dict:
        """Phase 2: Core Identity - UniProt data."""
        print(f"\n  {'─'*40}")
        print("  PHASE 2: Core Identity (UniProt)")
        print(f"  {'─'*40}")

        data = {'entry': None, 'function': None, 'location': None, 'aliases': []}
        uniprot_id = ids.get('uniprot')

        if not uniprot_id:
            print("      ⚠ No UniProt ID")
            return {'phase': 2, 'status': 'skipped', 'data': data}

        print(f"  Querying UniProt: {uniprot_id}")

        # Complete entry
        data['entry'] = self._call_tool('UniProt_get_entry_by_accession', accession=uniprot_id)

        # Function
        func = self._call_tool('UniProt_get_function_by_accession', accession=uniprot_id)
        data['function'] = func if isinstance(func, list) else [func] if func else []

        # Subcellular location
        data['location'] = self._call_tool('UniProt_get_subcellular_location_by_accession', accession=uniprot_id)

        # Aliases
        alt = self._call_tool('UniProt_get_alternative_names_by_accession', accession=uniprot_id)
        if alt:
            if isinstance(alt, list):
                data['aliases'] = alt
            elif isinstance(alt, dict):
                data['aliases'] = alt.get('alternativeNames', [])

        print(f"      ✓ UniProt entry retrieved")
        if data['function']:
            print(f"      ✓ {len(data['function'])} function annotations")

        return {'phase': 2, 'status': 'success', 'data': data}

    def _run_phase3(self, ids: Dict, phase2: Dict) -> Dict:
        """Phase 3: Structure & Domains."""
        print(f"\n  {'─'*40}")
        print("  PHASE 3: Structure & Domains")
        print(f"  {'─'*40}")

        data = {'pdb_structures': [], 'alphafold': None, 'domains': []}
        uniprot_id = ids.get('uniprot')

        # Extract PDB from UniProt entry
        entry = phase2.get('data', {}).get('entry')
        if entry and isinstance(entry, dict):
            xrefs = entry.get('uniProtKBCrossReferences', [])
            for xref in xrefs:
                if xref.get('database') == 'PDB':
                    props = xref.get('properties', {})
                    # Handle both dict and list formats for properties
                    if isinstance(props, dict):
                        method = props.get('Method')
                        resolution = props.get('Resolution')
                    else:
                        method = None
                        resolution = None
                    data['pdb_structures'].append({
                        'pdb_id': xref.get('id'),
                        'method': method,
                        'resolution': resolution
                    })

        print(f"      PDB structures: {len(data['pdb_structures'])}")

        # AlphaFold
        if uniprot_id:
            data['alphafold'] = self._call_tool('alphafold_get_prediction', qualifier=uniprot_id)
            if data['alphafold']:
                print(f"      ✓ AlphaFold model available")

        # InterPro domains
        if uniprot_id:
            domains = self._call_tool('InterPro_get_protein_domains', protein_id=uniprot_id)
            data['domains'] = domains if isinstance(domains, list) else []
            if data['domains']:
                print(f"      ✓ {len(data['domains'])} InterPro domains")

        return {'phase': 3, 'status': 'success', 'data': data}

    def _run_phase4(self, ids: Dict) -> Dict:
        """Phase 4: Function & Pathways."""
        print(f"\n  {'─'*40}")
        print("  PHASE 4: Function & Pathways")
        print(f"  {'─'*40}")

        data = {'reactome': [], 'wikipathways': [], 'go': []}
        uniprot_id = ids.get('uniprot')
        symbol = ids.get('symbol')

        # Reactome (uses uniprot_id parameter)
        if uniprot_id:
            reactome = self._call_tool('Reactome_map_uniprot_to_pathways', uniprot_id=uniprot_id)
            if reactome:
                data['reactome'] = reactome if isinstance(reactome, list) else [reactome]
            print(f"      Reactome pathways: {len(data['reactome'])}")

        # WikiPathways
        if symbol:
            wp = self._call_tool('WikiPathways_search', query=symbol)
            data['wikipathways'] = wp if isinstance(wp, list) else []
            print(f"      WikiPathways: {len(data['wikipathways'])}")

        # GO annotations
        if symbol:
            go = self._call_tool('GO_get_annotations_for_gene', gene_id=symbol)
            data['go'] = go if isinstance(go, list) else []
            print(f"      GO annotations: {len(data['go'])}")

        return {'phase': 4, 'status': 'success', 'data': data}

    def _run_phase5(self, ids: Dict) -> Dict:
        """Phase 5: Protein Interactions."""
        print(f"\n  {'─'*40}")
        print("  PHASE 5: Protein Interactions")
        print(f"  {'─'*40}")

        data = {'string': [], 'intact': [], 'total_count': 0}
        uniprot_id = ids.get('uniprot')
        symbol = ids.get('symbol')

        # STRING (uses list format for protein_ids)
        if uniprot_id:
            string = self._call_tool('STRING_get_protein_interactions',
                                    protein_ids=[uniprot_id], species=9606)
            data['string'] = string if isinstance(string, list) else []
            print(f"      STRING interactions: {len(data['string'])}")

        # IntAct (uses UniProt accession)
        if uniprot_id:
            intact = self._call_tool('intact_get_interactions', identifier=uniprot_id)
            if intact:
                data['intact'] = intact.get('data', intact.get('rows', [])) if isinstance(intact, dict) else intact
            print(f"      IntAct interactions: {len(data['intact'])}")

        data['total_count'] = len(data['string']) + len(data['intact'])
        print(f"      Total PPIs: {data['total_count']}")

        return {'phase': 5, 'status': 'success', 'data': data}

    def _run_phase6(self, ids: Dict) -> Dict:
        """Phase 6: Expression Profile."""
        print(f"\n  {'─'*40}")
        print("  PHASE 6: Expression Profile")
        print(f"  {'─'*40}")

        data = {'gtex': [], 'hpa': None, 'critical_tissue_expression': []}
        ensembl_id = ids.get('ensembl_versioned') or ids.get('ensembl')

        # GTEx
        if ensembl_id:
            gtex = self._call_tool('GTEx_get_median_gene_expression',
                                  gencode_id=ensembl_id,
                                  operation="get_median_gene_expression")
            if gtex:
                # Extract expression data
                if isinstance(gtex, dict):
                    data['gtex'] = gtex.get('geneExpression', [])
                elif isinstance(gtex, list):
                    data['gtex'] = gtex

            print(f"      GTEx tissues: {len(data['gtex'])}")

        # Check critical tissue expression
        critical_tissues = ['heart', 'liver', 'kidney', 'brain', 'bone marrow']
        for expr in data['gtex']:
            tissue = expr.get('tissue', {}).get('name', '').lower()
            tpm = expr.get('median', 0)
            if any(c in tissue for c in critical_tissues) and tpm > 10:
                data['critical_tissue_expression'].append({
                    'tissue': tissue,
                    'tpm': tpm
                })

        if data['critical_tissue_expression']:
            print(f"      ⚠ High expression in critical tissues: {len(data['critical_tissue_expression'])}")
        else:
            print(f"      ✓ Low expression in critical tissues")

        return {'phase': 6, 'status': 'success', 'data': data}

    def _run_phase7(self, ids: Dict) -> Dict:
        """Phase 7: Genetic Variation."""
        print(f"\n  {'─'*40}")
        print("  PHASE 7: Genetic Variation")
        print(f"  {'─'*40}")

        data = {
            'gnomad': {'pLI': None, 'LOEUF': None, 'missense_z': None, 'pRec': None},
            'clinvar': [],
            'gwas': []
        }
        symbol = ids.get('symbol')

        # gnomAD constraints (uses gene_symbol parameter)
        if symbol:
            gnomad = self._call_tool('gnomad_get_gene_constraints', gene_symbol=symbol)
            if gnomad and isinstance(gnomad, dict):
                data['gnomad'] = {
                    'pLI': gnomad.get('pLI'),
                    'LOEUF': gnomad.get('LOEUF'),
                    'missense_z': gnomad.get('missense_z'),
                    'pRec': gnomad.get('pRec')
                }
            print(f"      gnomAD pLI: {data['gnomad'].get('pLI', 'N/A')}")

        # ClinVar
        if symbol:
            clinvar = self._call_tool('clinvar_search_variants', gene=symbol)
            data['clinvar'] = clinvar if isinstance(clinvar, list) else []
            print(f"      ClinVar variants: {len(data['clinvar'])}")

        # GWAS (uses mapped_gene parameter)
        if symbol:
            gwas = self._call_tool('gwas_get_snps_for_gene', mapped_gene=symbol)
            if gwas and isinstance(gwas, dict):
                data['gwas'] = gwas.get('associations', [])
            elif isinstance(gwas, list):
                data['gwas'] = gwas

            # Count significant
            sig = [a for a in data['gwas'] if a.get('pvalue', 1) < 5e-8]
            print(f"      GWAS significant: {len(sig)}")

        return {'phase': 7, 'status': 'success', 'data': data}

    def _create_summary(self, results: Dict) -> Dict:
        """Create summary of all data collection phases."""
        return {
            'pdb_structures': len(results.get('phase3', {}).get('data', {}).get('pdb_structures', [])),
            'pathway_count': (
                len(results.get('phase4', {}).get('data', {}).get('reactome', [])) +
                len(results.get('phase4', {}).get('data', {}).get('wikipathways', []))
            ),
            'ppi_count': results.get('phase5', {}).get('data', {}).get('total_count', 0),
            'critical_tissue_expression': len(results.get('phase6', {}).get('data', {}).get('critical_tissue_expression', [])),
            'gnomad_pli': results.get('phase7', {}).get('data', {}).get('gnomad', {}).get('pLI')
        }


def main():
    """CLI entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='Phases 2-7: Data Collection')
    parser.add_argument('--ids-file', required=True, help='JSON file with resolved IDs')
    parser.add_argument('--output-dir', default='.', help='Output directory')
    args = parser.parse_args()

    with open(args.ids_file) as f:
        phase0 = json.load(f)
    ids = phase0['ids']

    pipeline = DataCollectionPipeline()
    result = pipeline.run(ids, args.output_dir)

    print(f"\n{'='*60}")
    print(f"SUCCESS: Collected data from 6 phases")
    print(f"{'='*60}")

    return result


if __name__ == '__main__':
    main()