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
from typing import Dict, Optional, Any, List
from pathlib import Path

# Use relative imports
_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from tooluniverse import ToolUniverse


class DataCollectionPipeline:
    """Phases 2-7: Collect target intelligence data."""

    # Critical tissues for safety assessment
    CRITICAL_TISSUES = ['heart', 'liver', 'kidney', 'brain', 'bone marrow', 'marrow']

    def __init__(self, tu: Optional[ToolUniverse] = None):
        self.tu = tu or ToolUniverse()
        self.tu.load_tools()
        self.tool_calls = []  # Track all tool calls

    def _call_tool(self, tool_name: str, **kwargs) -> Optional[Any]:
        """Call tool and unwrap data key."""
        call_record = {
            'tool': tool_name,
            'params': kwargs,
            'status': 'failed',
            'error': None
        }
        try:
            tool = getattr(self.tu.tools, tool_name)
            result = tool(**kwargs)
            if isinstance(result, dict) and 'data' in result:
                call_record['status'] = 'success'
                self.tool_calls.append(call_record)
                return result['data']
            call_record['status'] = 'success'
            self.tool_calls.append(call_record)
            return result
        except Exception as e:
            call_record['error'] = str(e)
            self.tool_calls.append(call_record)
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
            'tool_calls': self.tool_calls,
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
            print("      Warning: No UniProt ID available")
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
                data['aliases'] = [str(a) for a in alt if a]  # Ensure strings
            elif isinstance(alt, dict):
                data['aliases'] = [str(a) for a in alt.get('alternativeNames', []) if a]

        print(f"      UniProt entry retrieved")
        if data['function']:
            print(f"      {len(data['function'])} function annotations")

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
                    if isinstance(props, dict):
                        method = props.get('Method', 'Unknown')
                        resolution = props.get('Resolution', 'N/A')
                    else:
                        method = 'Unknown'
                        resolution = 'N/A'
                    data['pdb_structures'].append({
                        'pdb_id': xref.get('id'),
                        'method': str(method) if method else 'Unknown',
                        'resolution': str(resolution) if resolution else 'N/A'
                    })

        print(f"      PDB structures: {len(data['pdb_structures'])}")

        # AlphaFold
        if uniprot_id:
            data['alphafold'] = self._call_tool('alphafold_get_prediction', qualifier=uniprot_id)
            if data['alphafold']:
                print(f"      AlphaFold model available")

        # InterPro domains - properly format
        if uniprot_id:
            domains = self._call_tool('InterPro_get_protein_domains', protein_id=uniprot_id)
            if isinstance(domains, list):
                data['domains'] = [
                    {
                        'name': str(d.get('name', 'Unknown')) if isinstance(d, dict) else str(d),
                        'accession': str(d.get('accession', 'N/A')) if isinstance(d, dict) else 'N/A',
                        'start': d.get('start', '-') if isinstance(d, dict) else '-',
                        'end': d.get('end', '-') if isinstance(d, dict) else '-'
                    }
                    for d in domains
                ]
            print(f"      {len(data['domains'])} InterPro domains")

        return {'phase': 3, 'status': 'success', 'data': data}

    def _run_phase4(self, ids: Dict) -> Dict:
        """Phase 4: Function & Pathways."""
        print(f"\n  {'─'*40}")
        print("  PHASE 4: Function & Pathways")
        print(f"  {'─'*40}")

        data = {'reactome': [], 'wikipathways': [], 'go': {'mf': [], 'bp': [], 'cc': []}}
        uniprot_id = ids.get('uniprot')
        symbol = ids.get('symbol')

        # Reactome (uses uniprot_id parameter)
        if uniprot_id:
            reactome = self._call_tool('Reactome_map_uniprot_to_pathways', uniprot_id=uniprot_id)
            if reactome:
                if isinstance(reactome, list):
                    data['reactome'] = [
                        {
                            'name': str(r.get('name', 'Unknown')) if isinstance(r, dict) else str(r),
                            'stId': str(r.get('stId', 'N/A')) if isinstance(r, dict) else 'N/A'
                        }
                        for r in reactome
                    ]
            print(f"      Reactome pathways: {len(data['reactome'])}")

        # WikiPathways
        if symbol:
            wp = self._call_tool('WikiPathways_search', query=symbol)
            data['wikipathways'] = wp if isinstance(wp, list) else []
            print(f"      WikiPathways: {len(data['wikipathways'])}")

        # GO annotations - properly parse and categorize
        if symbol:
            go = self._call_tool('GO_get_annotations_for_gene', gene_id=symbol)
            if isinstance(go, list):
                for g in go:
                    if not isinstance(g, dict):
                        continue
                    term_name = str(g.get('name', g.get('term', 'Unknown')))
                    go_id = str(g.get('id', g.get('go_id', 'N/A')))
                    ontology = str(g.get('ontology', '')).lower()

                    entry = {'name': term_name, 'id': go_id}

                    if 'molecular_function' in ontology or 'mf' in ontology:
                        data['go']['mf'].append(entry)
                    elif 'biological_process' in ontology or 'bp' in ontology:
                        data['go']['bp'].append(entry)
                    elif 'cellular_component' in ontology or 'cc' in ontology:
                        data['go']['cc'].append(entry)
                    else:
                        # Default to BP if unclassified
                        data['go']['bp'].append(entry)

            total_go = len(data['go']['mf']) + len(data['go']['bp']) + len(data['go']['cc'])
            print(f"      GO annotations: {total_go}")

        return {'phase': 4, 'status': 'success', 'data': data}

    def _run_phase5(self, ids: Dict) -> Dict:
        """Phase 5: Protein Interactions."""
        print(f"\n  {'─'*40}")
        print("  PHASE 5: Protein Interactions")
        print(f"  {'─'*40}")

        data = {'string': [], 'intact': [], 'total_count': 0}
        uniprot_id = ids.get('uniprot')

        # STRING (uses list format for protein_ids)
        if uniprot_id:
            string = self._call_tool('STRING_get_protein_interactions',
                                    protein_ids=[uniprot_id], species=9606)
            if isinstance(string, list):
                data['string'] = [
                    {
                        'partner': str(s.get('preferredName', s.get('stringId', 'Unknown'))),
                        'score': s.get('combinedScore', 0)
                    }
                    for s in string if isinstance(s, dict)
                ]
            print(f"      STRING interactions: {len(data['string'])}")

        # IntAct (uses UniProt accession)
        if uniprot_id:
            intact = self._call_tool('intact_get_interactions', identifier=uniprot_id)
            if intact:
                if isinstance(intact, dict):
                    intact_list = intact.get('data', intact.get('rows', []))
                elif isinstance(intact, list):
                    intact_list = intact
                else:
                    intact_list = []

                data['intact'] = [
                    {
                        'partner': str(i.get('interactorId', i.get('id', 'Unknown'))),
                        'score': i.get('intactScore', 0)
                    }
                    for i in intact_list if isinstance(i, dict)
                ]
            print(f"      IntAct interactions: {len(data['intact'])}")

        data['total_count'] = len(data['string']) + len(data['intact'])
        print(f"      Total PPIs: {data['total_count']}")

        return {'phase': 5, 'status': 'success', 'data': data}

    def _run_phase6(self, ids: Dict) -> Dict:
        """Phase 6: Expression Profile - with improved GTEx handling."""
        print(f"\n  {'─'*40}")
        print("  PHASE 6: Expression Profile")
        print(f"  {'─'*40}")

        data = {'gtex': [], 'hpa': None, 'critical_tissue_expression': [], 'tissue_specificity': 'Unknown'}
        ensembl_id = ids.get('ensembl_versioned') or ids.get('ensembl')
        symbol = ids.get('symbol')

        # GTEx - try multiple approaches
        if ensembl_id:
            # Try with operation parameter
            gtex = self._call_tool('GTEx_get_median_gene_expression',
                                  gencode_id=ensembl_id,
                                  operation="get_median_gene_expression")

            # Handle different response formats
            if gtex:
                if isinstance(gtex, dict):
                    data['gtex'] = gtex.get('geneExpression', gtex.get('data', []))
                elif isinstance(gtex, list):
                    data['gtex'] = gtex

            # If no data, try alternative approach
            if not data['gtex'] and ids.get('ensembl'):
                # Try without versioned ID
                gtex2 = self._call_tool('GTEx_get_median_gene_expression',
                                       gencode_id=ids.get('ensembl'),
                                       operation="get_median_gene_expression")
                if gtex2:
                    if isinstance(gtex2, dict):
                        data['gtex'] = gtex2.get('geneExpression', gtex2.get('data', []))
                    elif isinstance(gtex2, list):
                        data['gtex'] = gtex2

            print(f"      GTEx tissues: {len(data['gtex'])}")

        # HPA as fallback
        if not data['gtex'] and ensembl_id:
            hpa = self._call_tool('HPA_get_rna_expression_by_source',
                                 gene_name=symbol,
                                 source_type='tissue',
                                 source_name='RNA')
            if hpa:
                data['hpa'] = hpa
                print(f"      HPA data available")

        # Process tissue expression data
        all_expressions = []
        for expr in data['gtex']:
            if isinstance(expr, dict):
                tissue_info = expr.get('tissue', {})
                tissue_name = tissue_info.get('name', 'Unknown') if isinstance(tissue_info, dict) else str(tissue_info)
                tpm = expr.get('median', 0)
                all_expressions.append({'tissue': str(tissue_name), 'tpm': float(tpm) if tpm else 0})

        # Sort by TPM
        all_expressions.sort(key=lambda x: x['tpm'], reverse=True)
        data['gtex'] = all_expressions

        # Check critical tissue expression
        for expr in all_expressions:
            tissue_lower = expr['tissue'].lower()
            tpm = expr['tpm']
            if any(c in tissue_lower for c in self.CRITICAL_TISSUES):
                data['critical_tissue_expression'].append({
                    'tissue': expr['tissue'],
                    'tpm': tpm,
                    'level': 'High' if tpm > 50 else 'Medium' if tpm > 10 else 'Low'
                })

        if data['critical_tissue_expression']:
            print(f"      Warning: High expression in critical tissues: {len(data['critical_tissue_expression'])}")
        else:
            print(f"      Low expression in critical tissues")

        # Calculate tissue specificity
        if all_expressions:
            max_tpm = all_expressions[0]['tpm'] if all_expressions else 0
            if max_tpm > 0:
                data['tissue_specificity'] = 'Tissue-enriched' if len([e for e in all_expressions if e['tpm'] > max_tpm * 0.5]) <= 2 else 'Broadly expressed'

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
            pli = data['gnomad'].get('pLI')
            print(f"      gnomAD pLI: {pli if pli is not None else 'N/A'}")

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
            sig = [a for a in data['gwas'] if isinstance(a, dict) and a.get('pvalue', 1) < 5e-8]
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
            'go_count': sum([
                len(results.get('phase4', {}).get('data', {}).get('go', {}).get('mf', [])),
                len(results.get('phase4', {}).get('data', {}).get('go', {}).get('bp', [])),
                len(results.get('phase4', {}).get('data', {}).get('go', {}).get('cc', []))
            ]),
            'ppi_count': results.get('phase5', {}).get('data', {}).get('total_count', 0),
            'gtex_tissues': len(results.get('phase6', {}).get('data', {}).get('gtex', [])),
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