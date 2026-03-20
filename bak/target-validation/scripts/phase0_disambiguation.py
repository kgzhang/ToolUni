#!/usr/bin/env python3
"""
Phase 0: Target Disambiguation
Resolves target query to ALL identifiers before any analysis.
Uses OpenTargets as primary source, then supplements from other databases.
Ensures human biomarker with standard gene name (not synonyms).
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


class TargetDisambiguation:
    """Phase 0: Target Disambiguation - resolves all identifiers using OpenTargets as primary source."""

    def __init__(self, tu: Optional[ToolUniverse] = None):
        self.tu = tu or ToolUniverse()
        self.tu.load_tools()
        self.tool_calls = []  # Track all tool calls for reporting

    def _call_tool(self, tool_name: str, **kwargs) -> Optional[Any]:
        """Call a tool and handle response formats."""
        call_record = {
            'tool': tool_name,
            'params': kwargs,
            'status': 'failed',
            'error': None
        }
        try:
            tool = getattr(self.tu.tools, tool_name)
            result = tool(**kwargs)
            # Unwrap 'data' key if present
            if isinstance(result, dict) and 'data' in result:
                call_record['status'] = 'success'
                call_record['result_type'] = 'wrapped'
                self.tool_calls.append(call_record)
                return result['data']
            call_record['status'] = 'success'
            call_record['result_type'] = 'direct'
            self.tool_calls.append(call_record)
            return result
        except Exception as e:
            call_record['error'] = str(e)
            self.tool_calls.append(call_record)
            return None

    def run(self, target_query: str, output_dir: str = ".") -> Dict:
        """
        Run target disambiguation phase.

        NEW ORDER (Issue #1 fix):
        1. OpenTargets search - get target name and basic identifiers
        2. MyGene query - supplement with gene info
        3. UniProt ID mapping - get UniProt accession
        4. Ensembl lookup - get versioned ID
        5. ChEMBL search - get ChEMBL target ID
        6. Get synonyms from UniProt

        Args:
            target_query: Gene symbol, alias, or name to resolve
            output_dir: Directory to save intermediate files

        Returns:
            Dictionary with resolved identifiers and metadata
        """
        print(f"\n{'='*60}")
        print("PHASE 0: Target Disambiguation")
        print(f"{'='*60}")
        print(f"  Query: {target_query}")
        print(f"  Strategy: OpenTargets -> MyGene -> UniProt -> Ensembl -> ChEMBL")

        ids = {
            'query': target_query,
            'symbol': None,
            'symbol_source': None,
            'uniprot': None,
            'ensembl': None,
            'ensembl_versioned': None,
            'entrez': None,
            'chembl_target': None,
            'hgnc_id': None,
            'name': None,
            'description': None,
            'aliases': [],
            'is_human': False,
            'confidence': 'low',
            'warnings': [],
            'raw_data': {}  # Store raw data for reporting
        }

        # ========================================
        # STEP 1: OpenTargets Search (PRIMARY)
        # ========================================
        print(f"\n  [1] Searching OpenTargets (PRIMARY SOURCE)...")
        ot_result = self._call_tool('OpenTargets_multi_entity_search_by_query_string',
                                    queryString=target_query)

        if ot_result:
            # Handle different response formats
            hits = []
            if isinstance(ot_result, dict):
                search = ot_result.get('search', {})
                hits = search.get('hits', [])
            elif isinstance(ot_result, list):
                hits = ot_result

            # Find target entity
            for item in hits[:20]:
                if isinstance(item, dict) and item.get('entity') == 'target':
                    ids['symbol'] = item.get('name')
                    ids['ensembl'] = item.get('id')
                    ids['name'] = item.get('description', '')
                    ids['symbol_source'] = 'opentargets'
                    ids['is_human'] = True

                    # Store raw data
                    ids['raw_data']['opentargets_search'] = {
                        'symbol': ids['symbol'],
                        'ensembl': ids['ensembl'],
                        'name': ids['name'],
                        'description': item.get('description', ''),
                        'id': item.get('id')
                    }

                    print(f"      Symbol: {ids['symbol']}")
                    print(f"      Ensembl: {ids['ensembl']}")
                    if ids['name']:
                        print(f"      Name: {ids['name'][:60]}...")
                    break

        # ========================================
        # STEP 2: MyGene Query (SUPPLEMENT)
        # ========================================
        if not ids['symbol']:
            print(f"\n  [2] Querying MyGene for gene symbol...")
        else:
            print(f"\n  [2] Supplementing with MyGene data...")

        mygene_result = self._call_tool('MyGene_query_genes', query=target_query)

        if mygene_result:
            hits = []
            if isinstance(mygene_result, dict):
                hits = mygene_result.get('hits', [])
            elif isinstance(mygene_result, list):
                hits = mygene_result

            human_gene = None
            for hit in hits:
                if hit.get('taxid') == 9606:
                    symbol = hit.get('symbol', '').upper()
                    # If we don't have symbol yet, or exact match found
                    if not ids['symbol'] or symbol == target_query.upper():
                        human_gene = hit
                        break

            # If no exact match but we need a symbol, take first human gene
            if not human_gene and hits:
                for hit in hits:
                    if hit.get('taxid') == 9606:
                        human_gene = hit
                        break

            if human_gene:
                if not ids['symbol']:
                    ids['symbol'] = human_gene.get('symbol')
                    ids['symbol_source'] = 'mygene'
                    ids['name'] = human_gene.get('name')
                    ids['is_human'] = True

                ids['entrez'] = human_gene.get('entrezgene')

                # Get Ensembl from MyGene if not from OpenTargets
                if not ids['ensembl']:
                    ensembl_data = human_gene.get('ensembl', [])
                    if isinstance(ensembl_data, list) and ensembl_data:
                        ids['ensembl'] = ensembl_data[0].get('gene') if isinstance(ensembl_data[0], dict) else ensembl_data[0]

                # Store raw data
                ids['raw_data']['mygene'] = {
                    'symbol': human_gene.get('symbol'),
                    'name': human_gene.get('name'),
                    'entrez': human_gene.get('entrezgene'),
                    'ensembl': ids['ensembl'],
                    'summary': human_gene.get('summary', '')
                }

                print(f"      Symbol: {ids['symbol']}")
                print(f"      Entrez: {ids['entrez']}")
                print(f"      Name: {ids['name'][:60] if ids.get('name') else 'N/A'}...")

        # Check if we have a symbol at this point
        if not ids['symbol']:
            ids['warnings'].append(f"Could not resolve gene symbol for query: {target_query}")
            print(f"      ERROR: Could not resolve gene symbol!")
            return self._save_and_return(ids, output_dir)

        # ========================================
        # STEP 3: UniProt ID Mapping
        # ========================================
        print(f"\n  [3] Mapping to UniProt accession...")
        uniprot_result = self._call_tool('UniProt_id_mapping',
                                         from_db='Gene_Name',
                                         to_db='UniProtKB',
                                         ids=ids['symbol'])

        if uniprot_result and isinstance(uniprot_result, dict):
            results = uniprot_result.get('results', [])
            for r in results:
                to = r.get('to', {})
                if isinstance(to, dict):
                    protein_id = to.get('id', '')
                    organism_id = to.get('organism_id', 0)
                    if organism_id == 9606 or '_HUMAN' in protein_id:
                        ids['uniprot'] = to.get('accession')

                        # Store raw data
                        ids['raw_data']['uniprot_mapping'] = {
                            'accession': ids['uniprot'],
                            'protein_id': protein_id,
                            'organism_id': organism_id
                        }

                        print(f"      UniProt: {ids['uniprot']} ({protein_id})")
                        break

        # ========================================
        # STEP 4: Ensembl Lookup (get versioned ID)
        # ========================================
        if ids['ensembl']:
            print(f"\n  [4] Getting Ensembl versioned ID...")
            ensembl_result = self._call_tool('ensembl_lookup_gene',
                                             gene_id=ids['ensembl'],
                                             species="homo_sapiens")
            if ensembl_result and isinstance(ensembl_result, dict):
                version = ensembl_result.get('version')
                if version:
                    ids['ensembl_versioned'] = f"{ids['ensembl']}.{version}"
                    print(f"      Versioned: {ids['ensembl_versioned']}")
                ids['description'] = ensembl_result.get('description', '')

                # Store raw data
                ids['raw_data']['ensembl'] = {
                    'id': ids['ensembl'],
                    'version': version,
                    'versioned_id': ids['ensembl_versioned'],
                    'description': ids['description'],
                    'biotype': ensembl_result.get('biotype'),
                    'strand': ensembl_result.get('strand')
                }

        # ========================================
        # STEP 5: ChEMBL Target Search
        # ========================================
        if ids['symbol']:
            print(f"\n  [5] Searching ChEMBL...")
            chembl_result = self._call_tool('ChEMBL_search_targets', query=ids['symbol'])
            if chembl_result:
                targets = []
                if isinstance(chembl_result, dict):
                    targets = chembl_result.get('targets', [])
                elif isinstance(chembl_result, list):
                    targets = chembl_result

                for t in targets:
                    if isinstance(t, dict) and t.get('target_type') == 'SINGLE_PROTEIN':
                        ids['chembl_target'] = t.get('target_chembl_id')

                        # Store raw data
                        ids['raw_data']['chembl'] = {
                            'target_chembl_id': ids['chembl_target'],
                            'target_type': t.get('target_type'),
                            'pref_name': t.get('pref_name')
                        }

                        print(f"      ChEMBL: {ids['chembl_target']}")
                        break

                # Fallback to first target if no SINGLE_PROTEIN
                if not ids['chembl_target'] and targets:
                    ids['chembl_target'] = targets[0].get('target_chembl_id')
                    print(f"      ChEMBL: {ids['chembl_target']} (fallback)")

        # ========================================
        # STEP 6: Get Synonyms/Aliases
        # ========================================
        if ids['uniprot']:
            print(f"\n  [6] Getting synonyms from UniProt...")
            alt_names = self._call_tool('UniProt_get_alternative_names_by_accession',
                                        accession=ids['uniprot'])
            if alt_names:
                if isinstance(alt_names, list):
                    ids['aliases'] = alt_names[:10]
                elif isinstance(alt_names, dict):
                    ids['aliases'] = alt_names.get('alternativeNames', [])[:10]
                if ids['aliases']:
                    print(f"      Aliases: {', '.join(str(a) for a in ids['aliases'][:5])}")

                    # Store raw data
                    ids['raw_data']['aliases'] = ids['aliases']

        # ========================================
        # Determine Confidence Level
        # ========================================
        required_ids = ['symbol', 'uniprot', 'ensembl', 'entrez']
        resolved_count = sum(1 for k in required_ids if ids.get(k))
        if resolved_count >= 4:
            ids['confidence'] = 'high'
        elif resolved_count >= 3:
            ids['confidence'] = 'medium'
        else:
            ids['confidence'] = 'low'

        # ========================================
        # Print Summary
        # ========================================
        print(f"\n  {'─'*40}")
        print(f"  DISAMBIGUATION SUMMARY")
        print(f"  {'─'*40}")
        print(f"  Standard Symbol: {ids['symbol']} (source: {ids['symbol_source']})")
        print(f"  UniProt: {ids['uniprot']}")
        print(f"  Ensembl: {ids['ensembl']}")
        print(f"  Entrez: {ids['entrez']}")
        print(f"  ChEMBL: {ids['chembl_target']}")
        print(f"  Confidence: {ids['confidence'].upper()}")
        if ids['warnings']:
            print(f"  Warnings: {len(ids['warnings'])}")

        return self._save_and_return(ids, output_dir)

    def _save_and_return(self, ids: Dict, output_dir: str) -> Dict:
        """Save intermediate file and return results."""
        result = {
            'phase': 0,
            'phase_name': 'Target Disambiguation',
            'status': 'success' if ids['symbol'] else 'failed',
            'ids': ids,
            'tool_calls': self.tool_calls,
            'summary': {
                'standard_symbol': ids['symbol'],
                'uniprot': ids['uniprot'],
                'ensembl': ids['ensembl'],
                'confidence': ids['confidence'],
                'is_human': ids['is_human'],
                'warnings_count': len(ids['warnings'])
            }
        }

        output_file = f"{output_dir}/phase0_disambiguation.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n  Saved: {output_file}")

        return result


def main():
    """CLI entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='Phase 0: Target Disambiguation')
    parser.add_argument('target', help='Gene symbol, alias, or name to resolve')
    parser.add_argument('--output-dir', default='.', help='Output directory for intermediate files')
    args = parser.parse_args()

    phase = TargetDisambiguation()
    result = phase.run(args.target, args.output_dir)

    print(f"\n{'='*60}")
    if result['ids']['symbol']:
        print(f"SUCCESS: Resolved to {result['ids']['symbol']}")
    else:
        print(f"FAILED: Could not resolve target")
    print(f"{'='*60}")

    return result


if __name__ == '__main__':
    main()