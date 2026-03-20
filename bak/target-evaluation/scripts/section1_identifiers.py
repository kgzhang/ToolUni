#!/usr/bin/env python3
"""
Section 1: Target Identifiers
Target ID resolution from various databases.
Raw data output to intermediate layer.
"""

import json
from typing import Dict, Any
from pathlib import Path


def get_target_identifiers(tu, target: str, output_dir: Path) -> Dict[str, Any]:
    """
    Resolve target query to all identifiers.
    Section 1: Target Identifiers

    Parameters:
        tu: ToolUniverse instance
        target: Target gene symbol or name
        output_dir: Directory for intermediate data

    Returns:
        Dictionary with resolved identifiers
    """
    ids = {
        'query': target,
        'symbol': None,
        'uniprot': None,
        'ensembl': None,
        'ensembl_versioned': None,
        'entrez': None,
        'chembl_target': None,
        'hgnc': None,
        'full_name': None,
        'synonyms': [],
        'target_class': None,
        'target_development_level': None,
        'is_gpcr': False
    }

    raw_calls = []

    # Step 1: MyGene query
    try:
        tool = getattr(tu.tools, 'MyGene_query_genes')
        result = tool(query=target, limit=1)
        raw_calls.append({'tool': 'MyGene_query_genes', 'params': {'query': target, 'limit': 1}, 'result': result})

        if result:
            # MyGene returns {"hits": [...], "total": N, ...} structure
            if isinstance(result, dict) and 'hits' in result and result['hits']:
                gene = result['hits'][0]
            elif isinstance(result, list):
                gene = result[0]
            elif isinstance(result, dict) and 'data' in result:
                gene = result['data'][0] if isinstance(result['data'], list) else result['data']
            else:
                gene = result
            ids['symbol'] = gene.get('symbol')
            ensembl_data = gene.get('ensembl', {})
            ids['ensembl'] = ensembl_data.get('gene') if isinstance(ensembl_data, dict) else ensembl_data
            ids['entrez'] = gene.get('entrezgene')
            ids['full_name'] = gene.get('name', '')
    except Exception as e:
        raw_calls.append({'tool': 'MyGene_query_genes', 'error': str(e)})

    # Step 2: UniProt mapping
    if ids['symbol']:
        try:
            tool = getattr(tu.tools, 'UniProt_id_mapping')
            result = tool(from_db='Gene_Name', to_db='UniProtKB', ids=ids['symbol'])
            raw_calls.append({'tool': 'UniProt_id_mapping', 'params': {'from_db': 'Gene_Name', 'to_db': 'UniProtKB', 'ids': ids['symbol']}, 'result': result})
            if result and isinstance(result, dict):
                # Handle data wrapper
                results = result.get('results', []) or result.get('data', {}).get('results', [])
                for r in results:
                    to = r.get('to', {})
                    if isinstance(to, dict):
                        protein_id = to.get('id', '')
                        organism_id = to.get('organism_id', 0)
                        # Check for human protein (organism_id 9606 or _HUMAN suffix)
                        if organism_id == 9606 or '_HUMAN' in protein_id:
                            ids['uniprot'] = to.get('accession')
                            break
        except Exception as e:
            raw_calls.append({'tool': 'UniProt_id_mapping', 'error': str(e)})

    # Step 3: Ensembl versioned ID
    if ids['ensembl']:
        try:
            tool = getattr(tu.tools, 'ensembl_lookup_gene')
            result = tool(gene_id=ids['ensembl'], species="homo_sapiens")
            raw_calls.append({'tool': 'ensembl_lookup_gene', 'params': {'gene_id': ids['ensembl'], 'species': 'homo_sapiens'}, 'result': result})
            if result:
                data = result.get('data', result) if isinstance(result, dict) else result
                if data.get('version'):
                    ids['ensembl_versioned'] = f"{ids['ensembl']}.{data['version']}"
                if not ids['full_name']:
                    ids['full_name'] = data.get('description', '').split(' [')[0]
        except Exception as e:
            raw_calls.append({'tool': 'ensembl_lookup_gene', 'error': str(e)})

    # Step 4: ChEMBL target
    if ids['symbol']:
        try:
            tool = getattr(tu.tools, 'ChEMBL_search_targets')
            result = tool(query=ids['symbol'])
            raw_calls.append({'tool': 'ChEMBL_search_targets', 'params': {'query': ids['symbol']}, 'result': result})

            # Handle nested data structure
            if result and isinstance(result, dict):
                targets = result.get('targets', result.get('data', {}).get('targets', []))
            elif isinstance(result, list):
                targets = result
            else:
                targets = []

            for t in targets:
                if isinstance(t, dict) and t.get('target_type') == 'SINGLE_PROTEIN':
                    ids['chembl_target'] = t.get('target_chembl_id')
                    break

            # Fallback: search with full_name if no SINGLE_PROTEIN found
            if not ids['chembl_target'] and ids.get('full_name'):
                result2 = tool(query=ids['full_name'])
                raw_calls.append({'tool': 'ChEMBL_search_targets', 'params': {'query': ids['full_name']}, 'result': result2})
                if result2 and isinstance(result2, dict):
                    targets2 = result2.get('targets', result2.get('data', {}).get('targets', []))
                    for t in targets2:
                        if isinstance(t, dict) and t.get('target_type') == 'SINGLE_PROTEIN':
                            ids['chembl_target'] = t.get('target_chembl_id')
                            break
        except Exception as e:
            raw_calls.append({'tool': 'ChEMBL_search_targets', 'error': str(e)})

    # Step 5: Synonyms
    if ids['uniprot']:
        try:
            tool = getattr(tu.tools, 'UniProt_get_alternative_names_by_accession')
            result = tool(accession=ids['uniprot'])
            raw_calls.append({'tool': 'UniProt_get_alternative_names_by_accession', 'params': {'accession': ids['uniprot']}, 'result': result})
            if result:
                ids['synonyms'] = result[:5] if isinstance(result, list) else [str(result)]
        except Exception as e:
            raw_calls.append({'tool': 'UniProt_get_alternative_names_by_accession', 'error': str(e)})

    # Step 6: Pharos classification
    if ids['symbol']:
        try:
            tool = getattr(tu.tools, 'Pharos_get_target')
            result = tool(gene=ids['symbol'])
            raw_calls.append({'tool': 'Pharos_get_target', 'params': {'gene': ids['symbol']}, 'result': result})
            if result and isinstance(result, dict):
                ids['target_development_level'] = result.get('tdl')
                if result.get('fam') and not ids['target_class']:
                    ids['target_class'] = result['fam']
        except Exception as e:
            raw_calls.append({'tool': 'Pharos_get_target', 'error': str(e)})

    # Step 7: GPCR detection (only set if explicit success)
    if ids['symbol']:
        try:
            entry_name = f"{ids['symbol'].lower()}_human"
            tool = getattr(tu.tools, 'GPCRdb_get_protein')
            result = tool(operation="get_protein", protein=entry_name)
            raw_calls.append({'tool': 'GPCRdb_get_protein', 'params': {'operation': 'get_protein', 'protein': entry_name}, 'result': result})
            # Only mark as GPCR if we get a valid response with entry_name or name field
            if result and isinstance(result, dict):
                # Check if this is a valid GPCR response (has entry_name or name field)
                if result.get('entry_name') or result.get('name') or result.get('receptor_family'):
                    ids['is_gpcr'] = True
                    ids['target_class'] = 'GPCR'
        except Exception:
            pass

    # Save raw data
    output_file = output_dir / 'section1_identifiers.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({'identifiers': ids, 'raw_tool_calls': raw_calls}, f, ensure_ascii=False, indent=2, default=str)

    return ids


if __name__ == "__main__":
    from tooluniverse import ToolUniverse
    tu = ToolUniverse()
    tu.load_tools()
    ids = get_target_identifiers(tu, "EGFR", Path('./reports/test'))
    print(json.dumps(ids, indent=2, default=str))