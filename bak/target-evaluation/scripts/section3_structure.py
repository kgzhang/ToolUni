#!/usr/bin/env python3
"""
Section 3: Structural Biology
PDB structures, AlphaFold predictions, and domain architecture.
Raw data output to intermediate layer.
"""

import json
from typing import Dict, Any
from pathlib import Path


def get_structural_biology(tu, ids: Dict[str, Any], section2_data: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """
    Get structural biology data.
    Section 3: Structural Biology

    Parameters:
        tu: ToolUniverse instance
        ids: Resolved target identifiers
        section2_data: Section 2 data (for PDB cross-references)
        output_dir: Directory for intermediate data

    Returns:
        Dictionary with structure data
    """
    uniprot_id = ids.get('uniprot')
    results = {'data': {}, 'raw_tool_calls': []}

    # Extract PDB cross-references from UniProt entry
    entry = section2_data.get('data', {}).get('entry', {})
    if entry and isinstance(entry, dict) and 'uniProtKBCrossReferences' in entry:
        pdb_refs = []
        for xref in entry['uniProtKBCrossReferences']:
            if xref.get('database') == 'PDB':
                # Handle properties as either dict or list
                props = xref.get('properties', {})
                if isinstance(props, list):
                    # Convert list of key-value pairs to dict
                    props_dict = {}
                    for item in props:
                        if isinstance(item, dict) and 'key' in item and 'value' in item:
                            props_dict[item['key']] = item['value']
                    props = props_dict
                pdb_refs.append({
                    'pdb_id': xref.get('id'),
                    'method': props.get('Method', 'Unknown') if isinstance(props, dict) else 'Unknown',
                    'resolution': props.get('Resolution', 'N/A') if isinstance(props, dict) else 'N/A'
                })
        results['data']['pdb_structures'] = pdb_refs

    # AlphaFold prediction
    if uniprot_id:
        try:
            tool = getattr(tu.tools, 'alphafold_get_prediction')
            result = tool(qualifier=uniprot_id)
            results['raw_tool_calls'].append({
                'tool': 'alphafold_get_prediction',
                'params': {'qualifier': uniprot_id},
                'result': result
            })
            results['data']['alphafold'] = result
        except Exception as e:
            results['raw_tool_calls'].append({
                'tool': 'alphafold_get_prediction',
                'error': str(e)
            })

        try:
            tool = getattr(tu.tools, 'alphafold_get_summary')
            result = tool(qualifier=uniprot_id)
            results['raw_tool_calls'].append({
                'tool': 'alphafold_get_summary',
                'params': {'qualifier': uniprot_id},
                'result': result
            })
            results['data']['alphafold_summary'] = result
        except Exception as e:
            results['raw_tool_calls'].append({
                'tool': 'alphafold_get_summary',
                'error': str(e)
            })

    # Domain architecture
    if uniprot_id:
        try:
            tool = getattr(tu.tools, 'InterPro_get_protein_domains')
            result = tool(protein_id=uniprot_id)
            results['raw_tool_calls'].append({
                'tool': 'InterPro_get_protein_domains',
                'params': {'protein_id': uniprot_id},
                'result': result
            })
            results['data']['domains'] = result
        except Exception as e:
            results['raw_tool_calls'].append({
                'tool': 'InterPro_get_protein_domains',
                'error': str(e)
            })

    # GPCR structures
    if ids.get('is_gpcr') and ids.get('symbol'):
        entry_name = f"{ids['symbol'].lower()}_human"
        try:
            tool = getattr(tu.tools, 'GPCRdb_get_structures')
            result = tool(operation="get_structures", protein=entry_name)
            results['raw_tool_calls'].append({
                'tool': 'GPCRdb_get_structures',
                'params': {'operation': 'get_structures', 'protein': entry_name},
                'result': result
            })
            results['data']['gpcr_structures'] = result
        except Exception as e:
            results['raw_tool_calls'].append({
                'tool': 'GPCRdb_get_structures',
                'error': str(e)
            })

    # Save raw data
    output_file = output_dir / 'section3_structure.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    return results


if __name__ == "__main__":
    from tooluniverse import ToolUniverse
    from section1_identifiers import get_target_identifiers
    from section2_basic_info import get_basic_information

    tu = ToolUniverse()
    tu.load_tools()
    ids = get_target_identifiers(tu, "EGFR", Path('./reports/test'))
    basic = get_basic_information(tu, ids, Path('./reports/test'))
    structure = get_structural_biology(tu, ids, basic, Path('./reports/test'))
    print(f"PDB structures: {len(structure['data'].get('pdb_structures', []))}")