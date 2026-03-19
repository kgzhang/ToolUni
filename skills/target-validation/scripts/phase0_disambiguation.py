#!/usr/bin/env python3
"""
Phase 0: Target Disambiguation
Resolves target query to ALL identifiers before any analysis.
Ensures human biomarker with standard gene name (not synonyms).
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


class TargetDisambiguation:
    """Phase 0: Target Disambiguation - resolves all identifiers."""

    def __init__(self, tu: Optional[ToolUniverse] = None):
        self.tu = tu or ToolUniverse()
        self.tu.load_tools()

    def _call_tool(self, tool_name: str, **kwargs) -> Optional[Any]:
        """Call a tool and handle response formats."""
        try:
            tool = getattr(self.tu.tools, tool_name)
            result = tool(**kwargs)
            # Unwrap 'data' key if present
            if isinstance(result, dict) and 'data' in result:
                return result['data']
            return result
        except Exception as e:
            return None

    def run(self, target_query: str, output_dir: str = ".") -> Dict:
        """
        Run target disambiguation phase.

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
            'warnings': []
        }

        # Step 1: Try UniProt search
        print(f"\n  [1] Searching UniProt for human gene '{target_query}'...")
        uniprot_search = self._call_tool('UniProt_search_entries',
                                         query=f"gene:{target_query} AND organism_id:9606")

        if uniprot_search and isinstance(uniprot_search, list):
            for entry in uniprot_search:
                gene_names = entry.get('genes', [])
                primary_gene = None
                for g in gene_names:
                    if g.get('geneName', {}).get('value', '').upper() == target_query.upper():
                        primary_gene = g.get('geneName', {}).get('value')
                        break
                    synonyms = g.get('synonyms', [])
                    for s in synonyms:
                        if s.get('value', '').upper() == target_query.upper():
                            primary_gene = g.get('geneName', {}).get('value')
                            break

                if primary_gene or entry.get('primaryAccession'):
                    ids['uniprot'] = entry.get('primaryAccession')
                    ids['symbol'] = primary_gene or entry.get('genes', [{}])[0].get('geneName', {}).get('value')
                    ids['symbol_source'] = 'uniprot'
                    ids['name'] = entry.get('proteinDescription', {}).get('recommendedName', {}).get('fullName', {}).get('value', '')
                    ids['is_human'] = True
                    print(f"      Symbol: {ids['symbol']}")
                    print(f"      UniProt: {ids['uniprot']}")
                    print(f"      Name: {ids['name']}")
                    break

        # Step 2: MyGene fallback
        if not ids['symbol']:
            print(f"\n  [2] Querying MyGene for exact symbol match...")
            mygene_result = self._call_tool('MyGene_query_genes', query=target_query)

            if mygene_result and isinstance(mygene_result, dict):
                hits = mygene_result.get('hits', [])
                if hits:
                    human_gene = None
                    for hit in hits:
                        if hit.get('taxid') == 9606:
                            symbol = hit.get('symbol', '').upper()
                            if symbol == target_query.upper():
                                human_gene = hit
                                break

                    if not human_gene:
                        for hit in hits:
                            if hit.get('taxid') == 9606:
                                human_gene = hit
                                break

                    if human_gene:
                        ids['symbol'] = human_gene.get('symbol')
                        ids['symbol_source'] = 'mygene'
                        ids['entrez'] = human_gene.get('entrezgene')
                        ids['name'] = human_gene.get('name')
                        ids['is_human'] = True

                        ensembl_data = human_gene.get('ensembl', [])
                        if isinstance(ensembl_data, list) and ensembl_data:
                            ids['ensembl'] = ensembl_data[0].get('gene') if isinstance(ensembl_data[0], dict) else ensembl_data[0]

                        print(f"      Symbol: {ids['symbol']}")
                        print(f"      Name: {ids['name']}")
                        print(f"      Ensembl: {ids['ensembl']}")

        # Step 3: OpenTargets fallback
        if not ids['symbol']:
            print(f"\n  [3] Searching OpenTargets...")
            ot_result = self._call_tool('OpenTargets_multi_entity_search_by_query_string',
                                        queryString=target_query)
            if ot_result:
                if isinstance(ot_result, dict):
                    search = ot_result.get('search', {})
                    hits = search.get('hits', [])
                elif isinstance(ot_result, list):
                    hits = ot_result
                else:
                    hits = []

                for item in hits[:10]:
                    if isinstance(item, dict):
                        if item.get('entity') == 'target':
                            ids['symbol'] = item.get('name')
                            ids['ensembl'] = item.get('id')
                            ids['name'] = item.get('description')
                            ids['symbol_source'] = 'opentargets'
                            ids['is_human'] = True
                            print(f"      Symbol: {ids['symbol']}")
                            print(f"      Ensembl: {ids['ensembl']}")
                            print(f"      Name: {ids['name'][:60]}...")
                            break

        if not ids['symbol']:
            ids['warnings'].append(f"Could not resolve gene symbol for query: {target_query}")
            print(f"      ERROR: Could not resolve gene symbol!")
            return self._save_and_return(ids, output_dir)

        # Step 4: Get UniProt accession
        if ids['symbol'] and not ids['uniprot']:
            print(f"\n  [4] Mapping to UniProt...")
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
                            print(f"      UniProt: {ids['uniprot']} ({protein_id})")
                            break

        # Step 5: Ensembl lookup
        if ids['ensembl']:
            print(f"\n  [5] Getting Ensembl versioned ID...")
            ensembl_result = self._call_tool('ensembl_lookup_gene',
                                             gene_id=ids['ensembl'],
                                             species="homo_sapiens")
            if ensembl_result and isinstance(ensembl_result, dict):
                version = ensembl_result.get('version')
                if version:
                    ids['ensembl_versioned'] = f"{ids['ensembl']}.{version}"
                    print(f"      Versioned: {ids['ensembl_versioned']}")
                ids['description'] = ensembl_result.get('description', '')

        # Step 6: ChEMBL search
        if ids['symbol']:
            print(f"\n  [6] Searching ChEMBL...")
            chembl_result = self._call_tool('ChEMBL_search_targets', query=ids['symbol'])
            if chembl_result:
                if isinstance(chembl_result, list) and chembl_result:
                    for t in chembl_result:
                        if t.get('target_type') == 'SINGLE_PROTEIN':
                            ids['chembl_target'] = t.get('target_chembl_id')
                            print(f"      ChEMBL: {ids['chembl_target']}")
                            break
                    if not ids['chembl_target'] and chembl_result:
                        ids['chembl_target'] = chembl_result[0].get('target_chembl_id')
                        print(f"      ChEMBL: {ids['chembl_target']}")

        # Step 7: Get synonyms
        if ids['uniprot']:
            print(f"\n  [7] Getting synonyms...")
            alt_names = self._call_tool('UniProt_get_alternative_names_by_accession',
                                        accession=ids['uniprot'])
            if alt_names:
                if isinstance(alt_names, list):
                    ids['aliases'] = alt_names[:10]
                elif isinstance(alt_names, dict):
                    ids['aliases'] = alt_names.get('alternativeNames', [])[:10]
            if ids['aliases']:
                print(f"      Aliases: {', '.join(ids['aliases'][:5])}")

        # Determine confidence
        required_ids = ['symbol', 'uniprot', 'ensembl', 'entrez']
        resolved_count = sum(1 for k in required_ids if ids.get(k))
        if resolved_count >= 4:
            ids['confidence'] = 'high'
        elif resolved_count >= 3:
            ids['confidence'] = 'medium'
        else:
            ids['confidence'] = 'low'

        # Print summary
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