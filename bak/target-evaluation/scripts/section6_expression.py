#!/usr/bin/env python3
"""
Section 6: Expression Profile
Tissue expression data from GTEx and HPA.
Raw data output to intermediate layer.
"""

import json
from typing import Dict, Any
from pathlib import Path


def get_expression_profile(tu, ids: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """
    Get tissue expression data.
    Section 6: Expression Profile

    Parameters:
        tu: ToolUniverse instance
        ids: Resolved target identifiers
        output_dir: Directory for intermediate data

    Returns:
        Dictionary with expression data
    """
    results = {'data': {}, 'source': None, 'raw_tool_calls': []}

    gencode_id = ids.get('ensembl_versioned') or ids.get('ensembl')
    symbol = ids.get('symbol')

    # Primary: GTEx
    if gencode_id:
        try:
            tool = getattr(tu.tools, 'GTEx_get_median_gene_expression')
            result = tool(gencode_id=gencode_id, operation="get_median_gene_expression")
            results['raw_tool_calls'].append({
                'tool': 'GTEx_get_median_gene_expression',
                'params': {'gencode_id': gencode_id, 'operation': 'get_median_gene_expression'},
                'result': result
            })
            if result and not (isinstance(result, dict) and result.get('status') == 'error'):
                results['data']['gtex'] = result
                results['source'] = 'GTEx'
        except Exception as e:
            results['raw_tool_calls'].append({
                'tool': 'GTEx_get_median_gene_expression',
                'error': str(e)
            })

    # Fallback: HPA
    if not results['data'].get('gtex') and ids.get('ensembl'):
        try:
            tool = getattr(tu.tools, 'HPA_get_comprehensive_gene_details_by_ensembl_id')
            result = tool(
                ensembl_id=ids['ensembl'],
                include_images=False,
                include_antibodies=False,
                include_expression=True
            )
            results['raw_tool_calls'].append({
                'tool': 'HPA_get_comprehensive_gene_details_by_ensembl_id',
                'params': {'ensembl_id': ids['ensembl'], 'include_images': False, 'include_antibodies': False, 'include_expression': True},
                'result': result
            })
            if result:
                results['data']['hpa'] = result
                results['source'] = 'HPA'
        except Exception as e:
            results['raw_tool_calls'].append({
                'tool': 'HPA_get_comprehensive_gene_details_by_ensembl_id',
                'error': str(e)
            })

    # HPA RNA expression
    if symbol:
        try:
            tool = getattr(tu.tools, 'HPA_get_rna_expression_by_source')
            result = tool(gene_name=symbol, source_type='tissue', source_name='all')
            results['raw_tool_calls'].append({
                'tool': 'HPA_get_rna_expression_by_source',
                'params': {'gene_name': symbol, 'source_type': 'tissue', 'source_name': 'all'},
                'result': result
            })
            if result:
                results['data']['hpa_rna'] = result
        except Exception as e:
            results['raw_tool_calls'].append({
                'tool': 'HPA_get_rna_expression_by_source',
                'error': str(e)
            })

    # Save raw data
    output_file = output_dir / 'section6_expression.json'
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
    expr = get_expression_profile(tu, ids, Path('./reports/test'))
    print(f"Expression source: {expr['source']}")