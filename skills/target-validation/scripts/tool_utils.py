#!/usr/bin/env python3
"""
Tool Utilities for Target Validation

Utility functions for ToolUniverse tool interaction:
- Response format handling
- Fallback chain execution
- Error handling
- Parameter corrections

Reference: TOOL_REFERENCE.md
"""

from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
import warnings


@dataclass
class ToolCallResult:
    """Result of a tool call with metadata."""
    tool_name: str
    success: bool
    data: Any
    error: Optional[str] = None
    fallback_used: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class ToolResponseHandler:
    """
    Handle different ToolUniverse response formats.

    Tools return THREE different formats:
    1. Standard wrapper: {status: ..., data: ...}
    2. Direct data wrapper: {data: ...}
    3. Direct list or dict
    """

    @staticmethod
    def handle_response(result: Any) -> Optional[Any]:
        """
        Extract data from any ToolUniverse response format.

        Args:
            result: Raw tool response

        Returns:
            Extracted data or None if error
        """
        if result is None:
            return None

        # Format 1: Standard wrapper with status
        if isinstance(result, dict):
            if 'status' in result:
                if result['status'] == 'error':
                    return None
                return result.get('data', result.get('content', result))

            # Format 2: Direct data wrapper
            if 'data' in result:
                return result['data']

            # Format 3: Direct dict (no wrapper)
            return result

        # Format 4: Direct list
        if isinstance(result, list):
            return result

        return result

    @staticmethod
    def get_count(data: Any, key: str = 'count') -> int:
        """Get count from various response formats."""
        if data is None:
            return 0
        if isinstance(data, list):
            return len(data)
        if isinstance(data, dict):
            # Check for count fields
            for count_key in ['count', 'total', 'size']:
                if count_key in data:
                    try:
                        return int(data[count_key])
                    except (ValueError, TypeError):
                        pass
            # Check for nested lists
            for nested_key in ['rows', 'data', 'items', 'results']:
                if nested_key in data and isinstance(data[nested_key], list):
                    return len(data[nested_key])
            return 1
        return 1


class ToolFallbackChain:
    """
    Execute tool calls with fallback chains.

    When primary tool fails, try fallback tools in sequence.
    Document all failures for reporting.
    """

    def __init__(self, tooluniverse):
        self.tu = tooluniverse
        self.call_history: List[ToolCallResult] = []
        self.warnings: List[str] = []

    def call_tool(
        self,
        tool_name: str,
        params: Dict,
        fallback_chain: List[Tuple[str, Dict]] = None,
        required: bool = False
    ) -> ToolCallResult:
        """
        Call a tool with optional fallback chain.

        Args:
            tool_name: Primary tool name
            params: Parameters for primary tool
            fallback_chain: List of (tool_name, params) tuples to try on failure
            required: Whether this data is required (affects warning level)

        Returns:
            ToolCallResult with data and metadata
        """
        # Try primary tool
        result = self._execute_tool(tool_name, params)
        if result.success:
            self.call_history.append(result)
            return result

        # Try fallbacks
        if fallback_chain:
            for fallback_name, fallback_params in fallback_chain:
                result = self._execute_tool(fallback_name, fallback_params)
                if result.success:
                    result.fallback_used = fallback_name
                    self.call_history.append(result)
                    return result

        # All failed
        self.call_history.append(result)

        # Add warning
        if required:
            self.warnings.append(f"REQUIRED: {tool_name} failed and no fallback succeeded")
        else:
            self.warnings.append(f"{tool_name} failed: {result.error}")

        return result

    def _execute_tool(self, tool_name: str, params: Dict) -> ToolCallResult:
        """Execute a single tool call."""
        try:
            tool = getattr(self.tu.tools, tool_name)
            raw_result = tool(**params)
            data = ToolResponseHandler.handle_response(raw_result)

            if data is not None:
                return ToolCallResult(
                    tool_name=tool_name,
                    success=True,
                    data=data
                )
            else:
                return ToolCallResult(
                    tool_name=tool_name,
                    success=False,
                    data=None,
                    error="No data returned"
                )

        except AttributeError:
            return ToolCallResult(
                tool_name=tool_name,
                success=False,
                data=None,
                error=f"Tool not found: {tool_name}"
            )
        except Exception as e:
            return ToolCallResult(
                tool_name=tool_name,
                success=False,
                data=None,
                error=str(e)
            )

    def get_failures(self) -> List[ToolCallResult]:
        """Get all failed tool calls."""
        return [r for r in self.call_history if not r.success]


# ============================================================
# PARAMETER CORRECTIONS TABLE
# ============================================================

PARAMETER_CORRECTIONS = {
    # Open Targets tools
    'OpenTargets_get_diseases_phenotypes_by_target_ensembl': {
        'wrong': 'ensembl',
        'correct': 'ensemblId',
        'note': 'Case-sensitive!'
    },
    'OpenTargets_get_target_tractability_by_ensemblID': {
        'wrong': 'ensemblID',
        'correct': 'ensemblId',
        'note': 'Case-sensitive! Note the ID vs Id'
    },
    'OpenTargets_get_target_safety_profile_by_ensemblID': {
        'wrong': 'ensemblID',
        'correct': 'ensemblId',
        'note': 'Case-sensitive!'
    },
    'OpenTargets_get_publications_by_target_ensemblID': {
        'wrong': 'ensemblId',
        'correct': 'entityId',
        'note': 'CRITICAL! Different parameter name entirely'
    },
    'OpenTargets_multi_entity_search_by_query_string': {
        'wrong': 'query',
        'correct': 'queryString',
        'note': 'camelCase parameter name'
    },

    # GTEx
    'GTEx_get_median_gene_expression': {
        'wrong': 'operation="median"',
        'correct': 'operation="get_median_gene_expression"',
        'note': 'Must use full operation name'
    },

    # gnomAD
    'gnomad_get_gene_constraints': {
        'wrong': 'gene_id',
        'correct': 'gene_symbol',
        'note': 'Use gene symbol, not Ensembl ID'
    },

    # STRING
    'STRING_get_protein_interactions': {
        'wrong': 'single ID string',
        'correct': 'protein_ids (list), species=9606',
        'note': 'Must pass list of IDs'
    },

    # Reactome
    'Reactome_map_uniprot_to_pathways': {
        'wrong': 'id',
        'correct': 'uniprot_id',
        'note': 'Parameter name'
    },

    # GWAS
    'gwas_get_snps_for_gene': {
        'wrong': 'gene',
        'correct': 'mapped_gene',
        'note': 'Use mapped_gene parameter'
    },

    # Ensembl
    'ensembl_lookup_gene': {
        'wrong': 'id',
        'correct': 'gene_id, species="homo_sapiens"',
        'note': 'Both parameters required'
    },

    # AlphaFold
    'alphafold_get_prediction': {
        'wrong': 'uniprot_accession',
        'correct': 'qualifier',
        'note': 'Use qualifier parameter'
    },

    # InterPro
    'InterPro_get_protein_domains': {
        'wrong': 'uniprot_accession',
        'correct': 'protein_id',
        'note': 'Parameter name'
    },

    # Clinical trials
    'search_clinical_trials': {
        'wrong': 'query',
        'correct': 'query_term',
        'note': 'Parameter name'
    }
}


def get_correct_params(tool_name: str, params: Dict) -> Tuple[Dict, List[str]]:
    """
    Apply parameter corrections for a tool.

    Args:
        tool_name: Tool to call
        params: Original parameters

    Returns:
        Tuple of (corrected_params, corrections_applied)
    """
    corrected = params.copy()
    corrections = []

    if tool_name in PARAMETER_CORRECTIONS:
        correction = PARAMETER_CORRECTIONS[tool_name]
        wrong_key = correction['wrong'].split('=')[0] if '=' in correction['wrong'] else correction['wrong']

        if wrong_key in corrected:
            # Remove wrong parameter
            del corrected[wrong_key]
            corrections.append(f"{tool_name}: {correction['wrong']} → {correction['correct']}")

    return corrected, corrections


# ============================================================
# STANDARD FALLBACK CHAINS
# ============================================================

FALLBACK_CHAINS = {
    'expression': [
        ('GTEx_get_median_gene_expression', {}),
        ('HPA_get_comprehensive_gene_details_by_ensembl_id', {})
    ],
    'ppi': [
        ('STRING_get_protein_interactions', {}),
        ('intact_get_interactions', {}),
        ('BioGRID_get_interactions', {})
    ],
    'chemical_matter': [
        ('ChEMBL_get_target_activities', {}),
        ('BindingDB_get_ligands_by_uniprot', {}),
        ('DGIdb_get_gene_druggability', {})
    ],
    'constraint': [
        ('gnomad_get_gene_constraints', {}),
        ('OpenTargets_get_target_constraint_info_by_ensemblID', {})
    ],
    'literature': [
        ('PubMed_search_articles', {}),
        ('EuropePMC_search_articles', {}),
        ('PubTator3_LiteratureSearch', {})
    ],
    'pathways': [
        ('Reactome_map_uniprot_to_pathways', {}),
        ('GO_get_annotations_for_gene', {}),
        ('WikiPathways_search', {})
    ]
}


def get_fallback_chain(data_type: str) -> List[Tuple[str, Dict]]:
    """Get standard fallback chain for a data type."""
    return FALLBACK_CHAINS.get(data_type, [])


# ============================================================
# GTEx VERSIONED ID HANDLING
# ============================================================

def get_versioned_ensembl_id(
    ensembl_id: str,
    ensembl_version: Optional[int]
) -> str:
    """
    Create versioned Ensembl ID for GTEx queries.

    GTEx often requires versioned IDs like ENSG00000146648.18

    Args:
        ensembl_id: Base Ensembl ID (ENSG...)
        ensembl_version: Version number from Ensembl lookup

    Returns:
        Versioned or unversioned ID
    """
    if ensembl_version:
        return f"{ensembl_id}.{ensembl_version}"
    return ensembl_id


# ============================================================
# SOAP TOOLS OPERATION PARAMETER
# ============================================================

SOAP_TOOLS = {
    'GPCRdb_get_protein': 'get_protein',
    'GPCRdb_get_structures': 'get_structures',
    'GPCRdb_get_ligands': 'get_ligands',
    'DisGeNET_search_gene': 'search_gene'
}


def prepare_soap_tool_call(tool_name: str, params: Dict) -> Dict:
    """
    Add operation parameter for SOAP tools.

    SOAP tools require the operation parameter as first argument.

    Args:
        tool_name: SOAP tool name
        params: Other parameters

    Returns:
        Parameters with operation added
    """
    if tool_name in SOAP_TOOLS:
        params = {'operation': SOAP_TOOLS[tool_name], **params}
    return params


# ============================================================
# MINIMUM DATA REQUIREMENTS
# ============================================================

MINIMUM_REQUIREMENTS = {
    'ppi': {
        'min_count': 10,
        'description': 'Protein-protein interactions'
    },
    'expression': {
        'min_count': 10,
        'description': 'Tissues with TPM values'
    },
    'disease': {
        'min_count': 5,
        'description': 'Disease associations with scores'
    },
    'constraints': {
        'min_count': 4,
        'description': 'gnomAD constraint scores (pLI, LOEUF, missense Z, pRec)'
    }
}


def check_minimum_requirements(data: Dict[str, Any]) -> Dict[str, Tuple[bool, str]]:
    """
    Check if data meets minimum requirements.

    Args:
        data: Collected data by type

    Returns:
        Dictionary of {data_type: (met, description)}
    """
    results = {}

    for data_type, requirement in MINIMUM_REQUIREMENTS.items():
        if data_type in data:
            count = len(data[data_type]) if isinstance(data[data_type], (list, dict)) else 0
            met = count >= requirement['min_count']
            results[data_type] = (
                met,
                f"{requirement['description']}: {count}/{requirement['min_count']}"
            )
        else:
            results[data_type] = (
                False,
                f"{requirement['description']}: Not collected"
            )

    return results


if __name__ == '__main__':
    # Test parameter corrections
    print("Parameter Corrections:")
    print("=" * 50)
    for tool, correction in PARAMETER_CORRECTIONS.items():
        print(f"{tool}:")
        print(f"  WRONG: {correction['wrong']}")
        print(f"  CORRECT: {correction['correct']}")
        print(f"  Note: {correction['note']}")
        print()

    # Test fallback chains
    print("\nFallback Chains:")
    print("=" * 50)
    for data_type, chain in FALLBACK_CHAINS.items():
        tools = [t[0] for t in chain]
        print(f"{data_type}: {' → '.join(tools)}")