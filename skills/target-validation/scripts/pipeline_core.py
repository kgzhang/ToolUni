#!/usr/bin/env python3
"""
Target Validation Pipeline Core Module

Provides base classes, utilities, and shared functionality for all phases.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json


@dataclass
class PhaseResult:
    """Structured output for each phase."""
    phase: int
    phase_name: str
    status: str  # 'success', 'partial', 'failed', 'skipped'
    start_time: str
    end_time: str
    data: Dict = field(default_factory=dict)
    summary: Dict = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    tool_calls: List[Dict] = field(default_factory=list)
    fallbacks_used: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


class BasePhase:
    """Base class for all pipeline phases."""

    def __init__(self, tooluniverse=None):
        """Initialize with optional ToolUniverse instance."""
        self.tu = tooluniverse
        self.warnings = []
        self.evidence = []
        self.tool_calls = []

    def _handle_response(self, result: Any) -> Any:
        """
        Handle three different response formats from tools.

        ToolUniverse tools return different formats:
        1. Standard wrapper: {'status': 'success', 'data': [...]}
        2. Direct wrapper: {'data': [...]}
        3. Direct list: [...]

        This method normalizes all formats.
        """
        if result is None:
            return None
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            if 'status' in result:
                if result['status'] == 'error':
                    return None
                return result.get('data', result.get('content', result))
            if 'data' in result:
                return result['data']
            return result
        return result

    def _call_tool(self, tool_name: str, fallback_chain: List[Tuple] = None, **kwargs) -> Tuple[Any, str]:
        """
        Call tool with fallback chain and error handling.

        Args:
            tool_name: Name of the primary tool to call
            fallback_chain: List of (tool_name, params_dict) tuples for fallbacks
            **kwargs: Parameters for the primary tool

        Returns:
            Tuple of (result, tool_used)
        """
        try:
            tool = getattr(self.tu.tools, tool_name)
            result = tool(**kwargs)
            data = self._handle_response(result)
            if data:
                self.tool_calls.append({
                    'tool': tool_name,
                    'status': 'success',
                    'params': kwargs
                })
                return data, tool_name
        except Exception as e:
            self.warnings.append(f"{tool_name} failed: {e}")
            self.tool_calls.append({
                'tool': tool_name,
                'status': 'error',
                'error': str(e),
                'params': kwargs
            })

        # Try fallbacks
        if fallback_chain:
            for fallback_tool, fallback_params in fallback_chain:
                try:
                    tool = getattr(self.tu.tools, fallback_tool)
                    result = tool(**fallback_params)
                    data = self._handle_response(result)
                    if data:
                        self.warnings.append(f"Used fallback: {fallback_tool}")
                        self.tool_calls.append({
                            'tool': fallback_tool,
                            'status': 'fallback',
                            'params': fallback_params
                        })
                        return data, fallback_tool
                except Exception:
                    continue

        return None, tool_name


class ValidationScorer:
    """
    Scoring logic for target validation.

    Implements the scoring criteria defined in SCORING_CRITERIA.md.
    """

    @staticmethod
    def score_disease_association(genetic_evidence: Dict, literature_count: int,
                                   pathway_score: float) -> Dict:
        """
        Calculate Disease Association Score (0-30 pts).

        Args:
            genetic_evidence: Dict with gwas_count, pli, clinvar_count
            literature_count: Total publication count
            pathway_score: OpenTargets pathway score (0-1)

        Returns:
            Dict with scores breakdown
        """
        scores = {'genetic': 0, 'literature': 0, 'pathway': 0, 'total': 0}

        # Genetic Evidence (0-10)
        gwas_count = genetic_evidence.get('gwas_count', 0)
        pli = genetic_evidence.get('pli', 0)
        clinvar_count = genetic_evidence.get('clinvar_count', 0)

        scores['genetic'] = min(gwas_count * 3, 6)  # GWAS: +3 each, max 6
        if pli and pli > 0.9:
            scores['genetic'] += 2
        elif pli and pli > 0.5:
            scores['genetic'] += 1
        if clinvar_count > 0:
            scores['genetric'] += min(clinvar_count * 0.5, 2)
        scores['genetic'] = min(scores['genetic'], 10)

        # Literature Evidence (0-10)
        if literature_count > 100:
            scores['literature'] = 10
        elif literature_count > 50:
            scores['literature'] = 7
        elif literature_count > 10:
            scores['literature'] = 5
        else:
            scores['literature'] = 3

        # Pathway Evidence (0-10)
        if pathway_score > 0.8:
            scores['pathway'] = 10
        elif pathway_score > 0.5:
            scores['pathway'] = 7
        elif pathway_score > 0.2:
            scores['pathway'] = 4

        scores['total'] = min(scores['genetic'] + scores['literature'] + scores['pathway'], 30)
        return scores

    @staticmethod
    def score_druggability(pdb_count: int, has_alphafold: bool,
                           compound_count: int, best_affinity_nm: float,
                           target_class: str) -> Dict:
        """
        Calculate Druggability Score (0-25 pts).

        Returns:
            Dict with scores breakdown
        """
        scores = {'structural': 0, 'chemical': 0, 'target_class': 0, 'total': 0}

        # Structural Tractability (0-10)
        if pdb_count > 50:
            scores['structural'] = 10
        elif pdb_count > 10:
            scores['structural'] = 7
        elif pdb_count > 0:
            scores['structural'] = 3
        if has_alphafold:
            scores['structural'] = max(scores['structural'], 3)

        # Chemical Matter (0-10)
        if best_affinity_nm and best_affinity_nm < 100:
            scores['chemical'] = 10
        elif best_affinity_nm and best_affinity_nm < 1000:
            scores['chemical'] = 7
        elif compound_count > 0:
            scores['chemical'] = 3

        # Target Class Bonus (0-5)
        if target_class in ['Tclin', 'GPCR', 'Kinase']:
            scores['target_class'] = 5
        elif target_class == 'Tchem':
            scores['target_class'] = 4
        elif target_class in ['Ion channel', 'Transporter']:
            scores['target_class'] = 3

        scores['total'] = min(scores['structural'] + scores['chemical'] + scores['target_class'], 25)
        return scores

    @staticmethod
    def score_safety(critical_tissue_expression: List[Dict],
                      mouse_ko_viable: bool, pli: float,
                      has_safety_liabilities: bool) -> Dict:
        """
        Calculate Safety Score (0-20 pts).

        Returns:
            Dict with scores breakdown and safety_flags
        """
        scores = {'expression': 0, 'genetic': 0, 'adverse': 0, 'total': 0}
        safety_flags = []

        # Expression Selectivity (0-5)
        high_critical = [t for t in critical_tissue_expression if t.get('tpm', 0) > 10]
        if len(high_critical) == 0:
            scores['expression'] = 5
        elif len(high_critical) <= 2:
            scores['expression'] = 3
        else:
            scores['expression'] = 0
            safety_flags.append(f"High expression in {len(high_critical)} critical tissues")

        # Genetic Validation (0-10)
        if mouse_ko_viable is True:
            scores['genetic'] = 7
        elif mouse_ko_viable is False:
            scores['genetic'] = 0
            safety_flags.append("Mouse KO lethal")
        elif pli and pli > 0.9:
            scores['genetic'] = 5  # Use pLI as proxy
        elif pli and pli > 0.5:
            scores['genetic'] = 3

        # Known ADRs (0-5)
        if not has_safety_liabilities:
            scores['adverse'] = 5
        else:
            scores['adverse'] = 3
            safety_flags.append("Known safety liabilities")

        scores['total'] = min(scores['expression'] + scores['genetic'] + scores['adverse'], 20)
        return {'scores': scores, 'safety_flags': safety_flags}

    @staticmethod
    def score_clinical_precedent(approved_count: int, phase3_count: int,
                                   phase2_count: int, phase1_count: int) -> int:
        """
        Calculate Clinical Precedent Score (0-15 pts).

        Returns:
            Integer score
        """
        if approved_count > 0:
            return 15
        elif phase3_count > 0:
            return 10
        elif phase2_count > 0:
            return 7
        elif phase1_count > 0:
            return 5
        return 0

    @staticmethod
    def score_validation_evidence(publication_count: int, ppi_count: int,
                                    pdb_count: int) -> Dict:
        """
        Calculate Validation Evidence Score (0-10 pts).

        Returns:
            Dict with scores breakdown
        """
        scores = {'publications': 0, 'ppi': 0, 'structure': 0, 'total': 0}

        # Publications (0-4)
        if publication_count > 100:
            scores['publications'] = 4
        elif publication_count > 50:
            scores['publications'] = 3
        elif publication_count > 10:
            scores['publications'] = 2

        # PPI Network (0-3)
        if ppi_count > 50:
            scores['ppi'] = 3
        elif ppi_count > 20:
            scores['ppi'] = 2

        # Structures (0-3)
        if pdb_count > 50:
            scores['structure'] = 3
        elif pdb_count > 10:
            scores['structure'] = 2

        scores['total'] = min(scores['publications'] + scores['ppi'] + scores['structure'], 10)
        return scores

    @staticmethod
    def determine_tier(total_score: int) -> Tuple[int, str]:
        """
        Determine priority tier from total score.

        Returns:
            Tuple of (tier_number, recommendation)
        """
        if total_score >= 80:
            return 1, "GO"
        elif total_score >= 60:
            return 2, "CONDITIONAL GO"
        elif total_score >= 40:
            return 3, "CAUTION"
        else:
            return 4, "NO-GO"


def save_json(data: Dict, filepath: str) -> None:
    """Save data to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def load_json(filepath: str) -> Dict:
    """Load data from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def get_tier_description(tier: int) -> str:
    """Get detailed description for a priority tier."""
    descriptions = {
        1: """**GO** - Highly validated target with strong evidence across all dimensions.

**Strengths:**
- Strong disease genetics support
- Multiple clinical programs validate druggability
- Well-characterized mechanism of action
- Extensive structural data available

**Recommended Actions:**
- Proceed with target-specific program development
- Leverage existing clinical data for biomarker development
- Consider combination strategies""",

        2: """**CONDITIONAL GO** - Promising target with some gaps requiring additional validation.

**Strengths:**
- Good disease association evidence
- Demonstrated druggability
- Clinical precedent exists

**Key Gaps:**
- Additional genetic validation may strengthen case
- Safety profile needs further characterization

**Recommended Actions:**
- Conduct additional validation studies
- Develop safety monitoring strategy
- Consider biomarker development""",

        3: """**CAUTION** - Target requires significant additional validation before investment.

**Key Concerns:**
- Limited disease association evidence
- Druggability challenges may exist
- Safety profile requires investigation

**Recommended Actions:**
- Complete additional preclinical validation
- Address safety concerns proactively
- Develop de-risking strategy before major investment""",

        4: """**NO-GO** - Target has fundamental limitations that may preclude therapeutic development.

**Key Limitations:**
- Insufficient evidence for disease relevance
- Major safety or druggability concerns identified
- No clear path forward for clinical development

**Recommended Actions:**
- Re-evaluate target selection
- Consider alternative targets in same pathway
- Monitor for new evidence that could change assessment"""
    }
    return descriptions.get(tier, "Assessment incomplete.")