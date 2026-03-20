#!/usr/bin/env python3
"""
Section 5: Protein-Protein Interactions
PPI network data from STRING, IntAct, BioGRID.
Raw data output to intermediate layer.
"""

import json
from typing import Dict, Any
from pathlib import Path


def get_protein_interactions(tu, ids: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """
    Get protein-protein interaction data.
    Section 5: Protein Interactions

    Parameters:
        tu: ToolUniverse instance
        ids: Resolved target identifiers
        output_dir: Directory for intermediate data

    Returns:
        Dictionary with PPI data
    """
    uniprot_id = ids.get('uniprot')
    symbol = ids.get('symbol')
    results = {'data': {}, 'source': None, 'raw_tool_calls': []}

    # Primary: STRING
    if uniprot_id:
        try:
            tool = getattr(tu.tools, 'STRING_get_protein_interactions')
            result = tool(protein_ids=[uniprot_id], species=9606)
            results['raw_tool_calls'].append({
                'tool': 'STRING_get_protein_interactions',
                'params': {'protein_ids': [uniprot_id], 'species': 9606},
                'result': result
            })
            if result:
                interactors = result if isinstance(result, list) else result.get('data', [])
                if len(interactors) >= 10:
                    results['data']['interactors'] = interactors
                    results['source'] = 'STRING'
        except Exception as e:
            results['raw_tool_calls'].append({
                'tool': 'STRING_get_protein_interactions',
                'error': str(e)
            })

    # Fallback 1: IntAct
    if not results['data'].get('interactors') and uniprot_id:
        try:
            tool = getattr(tu.tools, 'intact_get_interactions')
            result = tool(identifier=uniprot_id)
            results['raw_tool_calls'].append({
                'tool': 'intact_get_interactions',
                'params': {'identifier': uniprot_id},
                'result': result
            })
            if result:
                interactors = result if isinstance(result, list) else result.get('data', [])
                if len(interactors) >= 10:
                    results['data']['interactors'] = interactors
                    results['source'] = 'IntAct'
        except Exception as e:
            results['raw_tool_calls'].append({
                'tool': 'intact_get_interactions',
                'error': str(e)
            })

    # Fallback 2: BioGRID
    if not results['data'].get('interactors') and symbol:
        try:
            tool = getattr(tu.tools, 'BioGRID_get_interactions')
            result = tool(gene_symbol=symbol)
            results['raw_tool_calls'].append({
                'tool': 'BioGRID_get_interactions',
                'params': {'gene_symbol': symbol},
                'result': result
            })
            if result:
                interactors = result if isinstance(result, list) else result.get('data', [])
                if interactors:
                    results['data']['interactors'] = interactors
                    results['source'] = 'BioGRID'
        except Exception as e:
            results['raw_tool_calls'].append({
                'tool': 'BioGRID_get_interactions',
                'error': str(e)
            })

    # Save raw data
    output_file = output_dir / 'section5_ppi.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    return results


if __name__ == "__main__":
    from tooluniverse import ToolUniverse
    from section1_identifiers import get_target_identifiers

    tu = ToolUniverse()
    tu.load_tools()
    ids = get_target_identifiers(tu, "EGFR", Path('./reports/test'))
    ppi = get_protein_interactions(tu, ids, Path('./reports/test'))
    print(f"PPI source: {ppi['source']}, count: {len(ppi['data'].get('interactors', []))}")