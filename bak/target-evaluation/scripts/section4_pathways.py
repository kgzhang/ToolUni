#!/usr/bin/env python3
"""
Section 4: Function & Pathways
GO annotations and pathway data.
Raw data output to intermediate layer.
"""

import json
from typing import Dict, Any
from pathlib import Path


def get_function_pathways(tu, ids: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """
    Get function and pathway data.
    Section 4: Function & Pathways

    Parameters:
        tu: ToolUniverse instance
        ids: Resolved target identifiers
        output_dir: Directory for intermediate data

    Returns:
        Dictionary with pathway data
    """
    uniprot_id = ids.get('uniprot')
    symbol = ids.get('symbol')
    results = {'data': {}, 'raw_tool_calls': []}

    # Reactome
    if uniprot_id:
        try:
            tool = getattr(tu.tools, 'Reactome_map_uniprot_to_pathways')
            result = tool(uniprot_id=uniprot_id)
            results['raw_tool_calls'].append({
                'tool': 'Reactome_map_uniprot_to_pathways',
                'params': {'uniprot_id': uniprot_id},
                'result': result
            })
            results['data']['reactome'] = result
        except Exception as e:
            results['raw_tool_calls'].append({
                'tool': 'Reactome_map_uniprot_to_pathways',
                'error': str(e)
            })

    # KEGG
    if symbol:
        try:
            tool = getattr(tu.tools, 'kegg_get_gene_info')
            result = tool(gene_id=symbol)
            results['raw_tool_calls'].append({
                'tool': 'kegg_get_gene_info',
                'params': {'gene_id': symbol},
                'result': result
            })
            results['data']['kegg'] = result
        except Exception as e:
            results['raw_tool_calls'].append({
                'tool': 'kegg_get_gene_info',
                'error': str(e)
            })

    # WikiPathways
    if symbol:
        try:
            tool = getattr(tu.tools, 'WikiPathways_search')
            result = tool(query=symbol)
            results['raw_tool_calls'].append({
                'tool': 'WikiPathways_search',
                'params': {'query': symbol},
                'result': result
            })
            results['data']['wikipathways'] = result
        except Exception as e:
            results['raw_tool_calls'].append({
                'tool': 'WikiPathways_search',
                'error': str(e)
            })

    # GO Annotations
    if symbol:
        try:
            tool = getattr(tu.tools, 'GO_get_annotations_for_gene')
            result = tool(gene_id=symbol)
            results['raw_tool_calls'].append({
                'tool': 'GO_get_annotations_for_gene',
                'params': {'gene_id': symbol},
                'result': result
            })
            results['data']['go'] = result
        except Exception as e:
            results['raw_tool_calls'].append({
                'tool': 'GO_get_annotations_for_gene',
                'error': str(e)
            })

    # Save raw data
    output_file = output_dir / 'section4_pathways.json'
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
    pathways = get_function_pathways(tu, ids, Path('./reports/test'))
    print("Pathway data collected")