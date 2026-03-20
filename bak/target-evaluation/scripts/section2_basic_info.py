#!/usr/bin/env python3
"""
Section 2: Basic Information
UniProt protein details including function and location.
Raw data output to intermediate layer.
"""

import json
from typing import Dict, Any
from pathlib import Path


def get_basic_information(tu, ids: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """
    Get basic protein information from UniProt.
    Section 2: Basic Information

    Parameters:
        tu: ToolUniverse instance
        ids: Resolved target identifiers
        output_dir: Directory for intermediate data

    Returns:
        Dictionary with UniProt data
    """
    uniprot_id = ids.get('uniprot')
    if not uniprot_id:
        return {'status': 'skipped', 'reason': 'No UniProt ID'}

    results = {'data': {}, 'raw_tool_calls': []}

    # UniProt entry
    try:
        tool = getattr(tu.tools, 'UniProt_get_entry_by_accession')
        result = tool(accession=uniprot_id)
        results['raw_tool_calls'].append({
            'tool': 'UniProt_get_entry_by_accession',
            'params': {'accession': uniprot_id},
            'result': result
        })
        results['data']['entry'] = result
    except Exception as e:
        results['raw_tool_calls'].append({
            'tool': 'UniProt_get_entry_by_accession',
            'error': str(e)
        })

    # Function
    try:
        tool = getattr(tu.tools, 'UniProt_get_function_by_accession')
        result = tool(accession=uniprot_id)
        results['raw_tool_calls'].append({
            'tool': 'UniProt_get_function_by_accession',
            'params': {'accession': uniprot_id},
            'result': result
        })
        results['data']['functions'] = result
    except Exception as e:
        results['raw_tool_calls'].append({
            'tool': 'UniProt_get_function_by_accession',
            'error': str(e)
        })

    # Subcellular location
    try:
        tool = getattr(tu.tools, 'UniProt_get_subcellular_location_by_accession')
        result = tool(accession=uniprot_id)
        results['raw_tool_calls'].append({
            'tool': 'UniProt_get_subcellular_location_by_accession',
            'params': {'accession': uniprot_id},
            'result': result
        })
        results['data']['location'] = result
    except Exception as e:
        results['raw_tool_calls'].append({
            'tool': 'UniProt_get_subcellular_location_by_accession',
            'error': str(e)
        })

    # Recommended name
    try:
        tool = getattr(tu.tools, 'UniProt_get_recommended_name_by_accession')
        result = tool(accession=uniprot_id)
        results['raw_tool_calls'].append({
            'tool': 'UniProt_get_recommended_name_by_accession',
            'params': {'accession': uniprot_id},
            'result': result
        })
        results['data']['recommended_name'] = result
    except Exception as e:
        results['raw_tool_calls'].append({
            'tool': 'UniProt_get_recommended_name_by_accession',
            'error': str(e)
        })

    # Save raw data
    output_file = output_dir / 'section2_basic_info.json'
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
    data = get_basic_information(tu, ids, Path('./reports/test'))
    print("Basic info collected")