#!/usr/bin/env python3
"""
Section 7: Genetic Variation
Genetic constraint scores and clinical variants.
Raw data output to intermediate layer.
"""

import json
from typing import Dict, Any
from pathlib import Path


def get_genetic_variation(tu, ids: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """
    Get genetic variation and constraint data.
    Section 7: Genetic Variation

    Parameters:
        tu: ToolUniverse instance
        ids: Resolved target identifiers
        output_dir: Directory for intermediate data

    Returns:
        Dictionary with genetics data
    """
    symbol = ids.get('symbol')
    results = {'data': {}, 'raw_tool_calls': []}

    # gnomAD constraints
    if symbol:
        try:
            tool = getattr(tu.tools, 'gnomad_get_gene_constraints')
            result = tool(gene_symbol=symbol)
            results['raw_tool_calls'].append({
                'tool': 'gnomad_get_gene_constraints',
                'params': {'gene_symbol': symbol},
                'result': result
            })
            results['data']['constraints'] = result
        except Exception as e:
            results['raw_tool_calls'].append({
                'tool': 'gnomad_get_gene_constraints',
                'error': str(e)
            })

    # ClinVar
    if symbol:
        try:
            tool = getattr(tu.tools, 'clinvar_search_variants')
            result = tool(gene=symbol)
            results['raw_tool_calls'].append({
                'tool': 'clinvar_search_variants',
                'params': {'gene': symbol},
                'result': result
            })
            results['data']['clinvar'] = result
        except Exception as e:
            results['raw_tool_calls'].append({
                'tool': 'clinvar_search_variants',
                'error': str(e)
            })

    # CIViC
    if symbol:
        try:
            tool = getattr(tu.tools, 'civic_get_variants_by_gene')
            result = tool(gene_symbol=symbol)
            results['raw_tool_calls'].append({
                'tool': 'civic_get_variants_by_gene',
                'params': {'gene_symbol': symbol},
                'result': result
            })
            results['data']['civic'] = result
        except Exception as e:
            results['raw_tool_calls'].append({
                'tool': 'civic_get_variants_by_gene',
                'error': str(e)
            })

    # cBioPortal
    if symbol:
        try:
            tool = getattr(tu.tools, 'cBioPortal_get_mutations')
            result = tool(gene_symbol=symbol)
            results['raw_tool_calls'].append({
                'tool': 'cBioPortal_get_mutations',
                'params': {'gene_symbol': symbol},
                'result': result
            })
            results['data']['cbioportal'] = result
        except Exception as e:
            results['raw_tool_calls'].append({
                'tool': 'cBioPortal_get_mutations',
                'error': str(e)
            })

    # Save raw data
    output_file = output_dir / 'section7_genetics.json'
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
    genetics = get_genetic_variation(tu, ids, Path('./reports/test'))
    print(f"Constraints: {genetics['data'].get('constraints', {})}")