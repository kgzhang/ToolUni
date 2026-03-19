#!/usr/bin/env python3
"""
Detailed Scoring Utilities for Target Validation

Implements the scoring matrices defined in SCORING_CRITERIA.md:
- Disease Association (0-30 pts)
- Druggability (0-25 pts)
- Safety Profile (0-20 pts)
- Clinical Precedent (0-15 pts)
- Validation Evidence (0-10 pts)

Includes modality-specific adjustments for all supported modalities.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class DimensionScore:
    """Score for a single dimension."""
    name: str
    score: float
    max_score: float
    components: Dict[str, float]
    evidence: List[str]
    tier: int  # T1-T4


class DetailedScorer:
    """
    Detailed scoring following SCORING_CRITERIA.md matrices.

    Provides granular scoring with evidence grading and component breakdown.
    """

    # ============================================================
    # DISEASE ASSOCIATION SCORING (0-30 pts)
    # ============================================================

    @staticmethod
    def score_genetic_evidence(
        gwas_hits: List[Dict],
        clinvar_pathogenic: int,
        somatic_mutations: int,
        pli: Optional[float],
        loeuf: Optional[float]
    ) -> Tuple[float, Dict[str, float], List[str]]:
        """
        Score genetic evidence component (0-10 pts).

        Criteria from SCORING_CRITERIA.md:
        - GWAS hits: +3 per significant locus (max 6)
        - Rare variant (ClinVar pathogenic): +2
        - Somatic mutations in disease: +2
        - pLI > 0.9 (essential gene): +2
        - LOEUF < 0.35 (constrained): +1
        """
        components = {}
        evidence = []
        total = 0.0

        # GWAS scoring
        significant_gwas = [g for g in gwas_hits if g.get('pvalue', 1) < 5e-8]
        gwas_score = min(len(significant_gwas) * 3, 6)
        components['gwas'] = gwas_score
        total += gwas_score
        if significant_gwas:
            evidence.append(f"GWAS: {len(significant_gwas)} significant loci (+{gwas_score}) [T3]")

        # ClinVar pathogenic
        if clinvar_pathogenic > 0:
            components['clinvar'] = 2
            total += 2
            evidence.append(f"ClinVar: {clinvar_pathogenic} pathogenic variants (+2) [T2]")

        # Somatic mutations
        if somatic_mutations > 0:
            components['somatic'] = 2
            total += 2
            evidence.append(f"Somatic: {somatic_mutations} cancer mutations (+2) [T2]")

        # gnomAD constraint
        if pli is not None:
            if pli > 0.9:
                components['pli'] = 2
                total += 2
                evidence.append(f"pLI={pli:.2f} - highly constrained (+2) [T3]")
            elif pli > 0.5:
                components['pli'] = 1
                total += 1
                evidence.append(f"pLI={pli:.2f} - moderately constrained (+1) [T3]")

        if loeuf is not None and loeuf < 0.35:
            components['loeuf'] = 1
            total += 1
            evidence.append(f"LOEUF={loeuf:.2f} - constrained (+1) [T3]")

        return min(total, 10), components, evidence

    @staticmethod
    def score_literature_evidence(
        publication_count: int,
        target_disease_pubs: int
    ) -> Tuple[float, List[str]]:
        """
        Score literature evidence component (0-10 pts).

        Criteria:
        - >100 publications on target+disease: 10
        - 50-100 publications: 7
        - 10-50 publications: 5
        - 1-10 publications: 3
        - 0 publications: 0
        """
        evidence = []

        if target_disease_pubs > 100:
            score = 10
            evidence.append(f"Literature: {target_disease_pubs} target+disease papers (+10) [T2]")
        elif target_disease_pubs >= 50:
            score = 7
            evidence.append(f"Literature: {target_disease_pubs} papers (+7) [T2]")
        elif target_disease_pubs >= 10:
            score = 5
            evidence.append(f"Literature: {target_disease_pubs} papers (+5) [T3]")
        elif target_disease_pubs >= 1:
            score = 3
            evidence.append(f"Literature: {target_disease_pubs} papers (+3) [T4]")
        else:
            score = 0
            evidence.append("Literature: No target+disease publications (+0)")

        return score, evidence

    @staticmethod
    def score_pathway_evidence(
        opentargets_score: float,
        pathway_count: int
    ) -> Tuple[float, List[str]]:
        """
        Score pathway evidence component (0-10 pts).

        Criteria:
        - OpenTargets score > 0.8: 10
        - OpenTargets score 0.5-0.8: 7
        - OpenTargets score 0.2-0.5: 4
        - OpenTargets score < 0.2: 1
        """
        evidence = []

        if opentargets_score > 0.8:
            score = 10
            evidence.append(f"OT association: {opentargets_score:.2f} (+10) [T2]")
        elif opentargets_score >= 0.5:
            score = 7
            evidence.append(f"OT association: {opentargets_score:.2f} (+7) [T3]")
        elif opentargets_score >= 0.2:
            score = 4
            evidence.append(f"OT association: {opentargets_score:.2f} (+4) [T3]")
        else:
            score = 1
            evidence.append(f"OT association: {opentargets_score:.2f} (+1) [T4]")

        # Bonus for multiple pathways
        if pathway_count > 10:
            score = min(score + 2, 10)
            evidence.append(f"Pathways: {pathway_count} pathways (+2 bonus) [T3]")

        return score, evidence

    def score_disease_association(
        self,
        gwas_hits: List[Dict],
        clinvar_pathogenic: int,
        somatic_mutations: int,
        pli: Optional[float],
        loeuf: Optional[float],
        publication_count: int,
        target_disease_pubs: int,
        opentargets_score: float,
        pathway_count: int
    ) -> DimensionScore:
        """Calculate complete disease association score (0-30 pts)."""

        # Genetic evidence (0-10)
        genetic_score, genetic_components, genetic_evidence = self.score_genetic_evidence(
            gwas_hits, clinvar_pathogenic, somatic_mutations, pli, loeuf
        )

        # Literature evidence (0-10)
        literature_score, literature_evidence = self.score_literature_evidence(
            publication_count, target_disease_pubs
        )

        # Pathway evidence (0-10)
        pathway_score, pathway_evidence = self.score_pathway_evidence(
            opentargets_score, pathway_count
        )

        total = genetic_score + literature_score + pathway_score
        total = min(total, 30)

        return DimensionScore(
            name="Disease Association",
            score=total,
            max_score=30,
            components={
                'genetic': genetic_score,
                'literature': literature_score,
                'pathway': pathway_score
            },
            evidence=genetic_evidence + literature_evidence + pathway_evidence,
            tier=self._get_evidence_tier(total, 30)
        )

    # ============================================================
    # DRUGGABILITY SCORING (0-25 pts)
    # ============================================================

    @staticmethod
    def score_structural_tractability(
        pdb_count: int,
        has_ligand_structure: bool,
        best_resolution: Optional[float],
        has_alphafold: bool,
        alphafold_plddt: Optional[float],
        pocket_count: int,
        pocket_volume: Optional[float]
    ) -> Tuple[float, Dict[str, float], List[str]]:
        """
        Score structural tractability (0-10 pts).

        Criteria:
        - High-res co-crystal with ligand: 10
        - PDB structure, pockets detected: 7
        - AlphaFold confident, predicted pockets: 5
        - AlphaFold low confidence: 2
        - No structural data: 0
        """
        components = {}
        evidence = []
        total = 0.0

        # Check for high-res co-crystal first
        if has_ligand_structure and best_resolution and best_resolution < 2.5:
            total = 10
            components['co_crystal'] = 10
            evidence.append(f"Co-crystal with ligand at {best_resolution}Å (+10) [T1]")
            return total, components, evidence

        # PDB structures
        if pdb_count > 0:
            if pdb_count > 10 and best_resolution and best_resolution < 3.0:
                total = 7
                components['pdb'] = 7
                evidence.append(f"{pdb_count} PDB structures, best {best_resolution}Å (+7) [T1]")
            elif pdb_count > 0:
                total = 5
                components['pdb'] = 5
                evidence.append(f"{pdb_count} PDB structures (+5) [T2]")

            # Pocket bonus
            if pocket_count > 0 and pocket_volume and pocket_volume > 200:
                total += 2
                components['pocket'] = 2
                evidence.append(f"Binding pocket {pocket_volume:.0f}Å³ (+2) [T2]")
                total = min(total, 10)

        # AlphaFold fallback
        elif has_alphafold and alphafold_plddt:
            if alphafold_plddt > 70:
                total = 5
                components['alphafold'] = 5
                evidence.append(f"AlphaFold confident (pLDDT={alphafold_plddt:.0f}) (+5) [T3]")
            else:
                total = 2
                components['alphafold'] = 2
                evidence.append(f"AlphaFold low confidence (pLDDT={alphafold_plddt:.0f}) (+2) [T4]")

        return total, components, evidence

    @staticmethod
    def score_chemical_matter(
        compound_count: int,
        best_affinity_nm: Optional[float],
        has_drug_like: bool
    ) -> Tuple[float, List[str]]:
        """
        Score chemical matter (0-10 pts).

        Criteria:
        - Drug-like compounds (IC50 < 100nM): 10
        - Tool compounds (IC50 < 1µM): 7
        - HTS hits only (IC50 > 1µM): 4
        - No known ligands: 0
        """
        evidence = []

        if has_drug_like or (best_affinity_nm and best_affinity_nm < 100):
            score = 10
            evidence.append(f"Drug-like compounds ({compound_count}, best {best_affinity_nm}nM) (+10) [T1]")
        elif compound_count > 0 and (not best_affinity_nm or best_affinity_nm < 1000):
            score = 7
            evidence.append(f"Tool compounds ({compound_count}) (+7) [T2]")
        elif compound_count > 0:
            score = 4
            evidence.append(f"HTS hits ({compound_count}) (+4) [T3]")
        else:
            score = 0
            evidence.append("No known ligands (+0)")

        return score, evidence

    @staticmethod
    def score_target_class(target_class: str) -> Tuple[float, List[str]]:
        """
        Score target class bonus (0-5 pts).

        Criteria:
        - Validated family (kinase, GPCR, NR): 5
        - Enzyme, ion channel: 4
        - PPI, transporter: 2
        - Novel/unknown: 0
        """
        evidence = []

        validated_families = ['Kinase', 'GPCR', 'Nuclear Receptor', 'G-Protein Coupled Receptor']
        established_families = ['Enzyme', 'Ion Channel', 'Protease']
        challenging_families = ['PPI', 'Transporter', 'Transcription Factor']

        if target_class in validated_families:
            score = 5
            evidence.append(f"Validated drug class: {target_class} (+5) [T1]")
        elif target_class in established_families:
            score = 4
            evidence.append(f"Established class: {target_class} (+4) [T2]")
        elif target_class in challenging_families:
            score = 2
            evidence.append(f"Challenging class: {target_class} (+2) [T3]")
        else:
            score = 0
            evidence.append(f"Class: {target_class} (+0)")

        return score, evidence

    def score_druggability(
        self,
        pdb_count: int,
        has_ligand_structure: bool,
        best_resolution: Optional[float],
        has_alphafold: bool,
        alphafold_plddt: Optional[float],
        pocket_count: int,
        pocket_volume: Optional[float],
        compound_count: int,
        best_affinity_nm: Optional[float],
        has_drug_like: bool,
        target_class: str
    ) -> DimensionScore:
        """Calculate complete druggability score (0-25 pts)."""

        # Structural tractability (0-10)
        struct_score, struct_components, struct_evidence = self.score_structural_tractability(
            pdb_count, has_ligand_structure, best_resolution,
            has_alphafold, alphafold_plddt, pocket_count, pocket_volume
        )

        # Chemical matter (0-10)
        chem_score, chem_evidence = self.score_chemical_matter(
            compound_count, best_affinity_nm, has_drug_like
        )

        # Target class bonus (0-5)
        class_score, class_evidence = self.score_target_class(target_class)

        total = struct_score + chem_score + class_score
        total = min(total, 25)

        return DimensionScore(
            name="Druggability",
            score=total,
            max_score=25,
            components={
                'structural': struct_score,
                'chemical': chem_score,
                'target_class': class_score
            },
            evidence=struct_evidence + chem_evidence + class_evidence,
            tier=self._get_evidence_tier(total, 25)
        )

    # ============================================================
    # SAFETY SCORING (0-20 pts)
    # ============================================================

    @staticmethod
    def score_expression_selectivity(
        critical_tissue_expression: Dict[str, float],
        tissue_specificity: float
    ) -> Tuple[float, List[str]]:
        """
        Score tissue expression selectivity (0-5 pts).

        Criteria:
        - Target restricted to disease tissue: 5
        - Low expression in heart/liver/kidney/brain: 4
        - Moderate in 1-2 critical tissues: 2
        - High in multiple critical tissues: 0
        """
        evidence = []
        critical_tissues = ['heart', 'liver', 'kidney', 'brain', 'bone marrow']

        # Check critical tissue expression
        high_expr_critical = [
            tissue for tissue, tpm in critical_tissue_expression.items()
            if tpm > 10 and tissue.lower() in critical_tissues
        ]

        if not high_expr_critical and tissue_specificity > 0.7:
            score = 5
            evidence.append("Disease-restricted expression (+5) [T2]")
        elif not high_expr_critical:
            score = 4
            evidence.append("Low critical tissue expression (+4) [T2]")
        elif len(high_expr_critical) <= 2:
            score = 2
            evidence.append(f"Moderate in: {', '.join(high_expr_critical)} (+2) [T2]")
        else:
            score = 0
            evidence.append(f"High in critical tissues: {', '.join(high_expr_critical)} (+0) [T2]")

        return score, evidence

    @staticmethod
    def score_genetic_validation(
        mouse_ko_viable: Optional[bool],
        mouse_ko_phenotype: Optional[str],
        pli: Optional[float]
    ) -> Tuple[float, List[str]]:
        """
        Score genetic validation (0-10 pts).

        Criteria:
        - Mouse KO viable, no severe phenotype: 10
        - Mouse KO viable, mild phenotype: 7
        - Mouse KO concerning phenotype: 3
        - Mouse KO lethal: 0
        - No KO data, low pLI (<0.5): 5
        - No KO data, high pLI (>0.9): 2
        """
        evidence = []

        if mouse_ko_viable is not None:
            if mouse_ko_viable and (not mouse_ko_phenotype or 'severe' not in mouse_ko_phenotype.lower()):
                if mouse_ko_phenotype and 'mild' in mouse_ko_phenotype.lower():
                    score = 7
                    evidence.append(f"Mouse KO viable, mild phenotype (+7) [T2]")
                else:
                    score = 10
                    evidence.append("Mouse KO viable, no severe phenotype (+10) [T1]")
            elif mouse_ko_viable:
                score = 3
                evidence.append(f"Mouse KO concerning phenotype (+3) [T2]")
            else:
                score = 0
                evidence.append("Mouse KO lethal (+0) [T1]")
        elif pli is not None:
            if pli < 0.5:
                score = 5
                evidence.append(f"No KO data, pLI={pli:.2f} (not essential) (+5) [T3]")
            elif pli > 0.9:
                score = 2
                evidence.append(f"No KO data, pLI={pli:.2f} (essential) (+2) [T3]")
            else:
                score = 4
                evidence.append(f"No KO data, pLI={pli:.2f} (+4) [T3]")
        else:
            score = 5
            evidence.append("No genetic validation data (+5)")

        return score, evidence

    @staticmethod
    def score_adverse_events(
        known_adrs: List[str],
        has_black_box: bool,
        withdrawn: bool
    ) -> Tuple[float, List[str]]:
        """
        Score known adverse events (0-5 pts).

        Criteria:
        - No known safety signals: 5
        - Mild, manageable ADRs: 3
        - Serious ADRs: 1
        - Black box warning or withdrawal: 0
        """
        evidence = []

        if withdrawn:
            score = 0
            evidence.append("Drug withdrawn (+0) [T1]")
        elif has_black_box:
            score = 0
            evidence.append("Black box warning (+0) [T1]")
        elif not known_adrs:
            score = 5
            evidence.append("No known safety signals (+5) [T2]")
        elif any('serious' in adr.lower() or 'severe' in adr.lower() for adr in known_adrs):
            score = 1
            evidence.append(f"Serious ADRs: {len(known_adrs)} (+1) [T1]")
        else:
            score = 3
            evidence.append(f"Mild ADRs: {len(known_adrs)} (+3) [T2]")

        return score, evidence

    def score_safety(
        self,
        critical_tissue_expression: Dict[str, float],
        tissue_specificity: float,
        mouse_ko_viable: Optional[bool],
        mouse_ko_phenotype: Optional[str],
        pli: Optional[float],
        known_adrs: List[str],
        has_black_box: bool,
        withdrawn: bool
    ) -> DimensionScore:
        """Calculate complete safety score (0-20 pts)."""

        # Expression selectivity (0-5)
        expr_score, expr_evidence = self.score_expression_selectivity(
            critical_tissue_expression, tissue_specificity
        )

        # Genetic validation (0-10)
        gen_score, gen_evidence = self.score_genetic_validation(
            mouse_ko_viable, mouse_ko_phenotype, pli
        )

        # Adverse events (0-5)
        adr_score, adr_evidence = self.score_adverse_events(
            known_adrs, has_black_box, withdrawn
        )

        total = expr_score + gen_score + adr_score
        total = min(total, 20)

        return DimensionScore(
            name="Safety Profile",
            score=total,
            max_score=20,
            components={
                'expression': expr_score,
                'genetic': gen_score,
                'adverse': adr_score
            },
            evidence=expr_evidence + gen_evidence + adr_evidence,
            tier=self._get_evidence_tier(total, 20)
        )

    # ============================================================
    # CLINICAL PRECEDENT SCORING (0-15 pts)
    # ============================================================

    @staticmethod
    def score_clinical_precedent(
        approved_same_disease: int,
        approved_different_disease: int,
        phase3_count: int,
        phase2_count: int,
        phase1_count: int,
        preclinical_only: bool,
        failed_for_safety: bool,
        withdrawn: bool
    ) -> DimensionScore:
        """
        Score clinical precedent (0-15 pts).

        Criteria:
        - FDA-approved for SAME disease: 15
        - FDA-approved for DIFFERENT disease: 12
        - Phase 3: 10
        - Phase 2: 7
        - Phase 1: 5
        - Preclinical only: 3
        - No clinical: 0

        Adjustments:
        - Failed for safety: -3
        - Drug withdrawal: -5
        - Multiple approved (+2)
        """
        evidence = []
        adjustments = []

        if approved_same_disease > 0:
            base_score = 15
            evidence.append(f"{approved_same_disease} FDA-approved for same disease (+15) [T1]")
        elif approved_different_disease > 0:
            base_score = 12
            evidence.append(f"{approved_different_disease} FDA-approved for other disease (+12) [T1]")
        elif phase3_count > 0:
            base_score = 10
            evidence.append(f"{phase3_count} Phase 3 trials (+10) [T2]")
        elif phase2_count > 0:
            base_score = 7
            evidence.append(f"{phase2_count} Phase 2 trials (+7) [T2]")
        elif phase1_count > 0:
            base_score = 5
            evidence.append(f"{phase1_count} Phase 1 trials (+5) [T2]")
        elif preclinical_only:
            base_score = 3
            evidence.append("Preclinical compounds only (+3) [T3]")
        else:
            base_score = 0
            evidence.append("No clinical development (+0)")

        # Adjustments
        score = base_score
        if failed_for_safety:
            score -= 3
            adjustments.append("Failed for safety (-3)")
        if withdrawn:
            score -= 5
            adjustments.append("Drug withdrawal (-5)")
        if approved_same_disease > 1 or approved_different_disease > 1:
            score += 2
            adjustments.append("Multiple approved (+2)")

        score = max(0, min(15, score))

        return DimensionScore(
            name="Clinical Precedent",
            score=score,
            max_score=15,
            components={
                'base': base_score,
                'adjustments': sum(adjustments) if adjustments else 0
            },
            evidence=evidence + adjustments,
            tier=DetailedScorer._get_evidence_tier(score, 15)
        )

    # ============================================================
    # VALIDATION EVIDENCE SCORING (0-10 pts)
    # ============================================================

    @staticmethod
    def score_functional_studies(
        has_crispr_ko: bool,
        crispr_phenotype: Optional[str],
        has_sirna: bool,
        has_biochemical: bool,
        has_overexpression: bool
    ) -> Tuple[float, List[str]]:
        """
        Score functional studies (0-5 pts).

        Criteria:
        - CRISPR KO disease-relevant phenotype: 5
        - siRNA phenotype: 4
        - Biochemical validation: 3
        - Overexpression only: 2
        - No data: 0
        """
        evidence = []

        if has_crispr_ko and crispr_phenotype:
            score = 5
            evidence.append(f"CRISPR KO: {crispr_phenotype} (+5) [T1]")
        elif has_sirna:
            score = 4
            evidence.append("siRNA knockdown phenotype (+4) [T2]")
        elif has_biochemical:
            score = 3
            evidence.append("Biochemical assay validation (+3) [T2]")
        elif has_overexpression:
            score = 2
            evidence.append("Overexpression study (+2) [T3]")
        else:
            score = 0
            evidence.append("No functional data (+0)")

        return score, evidence

    @staticmethod
    def score_disease_models(
        has_pdx: bool,
        has_gemm: bool,
        has_cell_line: bool,
        has_in_silico: bool
    ) -> Tuple[float, List[str]]:
        """
        Score disease models (0-5 pts).

        Criteria:
        - PDX response: 5
        - GEMM: 4
        - Cell line: 3
        - In silico only: 1
        - No model: 0
        """
        evidence = []

        if has_pdx:
            score = 5
            evidence.append("PDX model response (+5) [T1]")
        elif has_gemm:
            score = 4
            evidence.append("GEMM phenotype (+4) [T2]")
        elif has_cell_line:
            score = 3
            evidence.append("Cell line model (+3) [T3]")
        elif has_in_silico:
            score = 1
            evidence.append("In silico model only (+1) [T4]")
        else:
            score = 0
            evidence.append("No disease model (+0)")

        return score, evidence

    def score_validation_evidence(
        self,
        has_crispr_ko: bool,
        crispr_phenotype: Optional[str],
        has_sirna: bool,
        has_biochemical: bool,
        has_overexpression: bool,
        has_pdx: bool,
        has_gemm: bool,
        has_cell_line: bool,
        has_in_silico: bool
    ) -> DimensionScore:
        """Calculate complete validation evidence score (0-10 pts)."""

        # Functional studies (0-5)
        func_score, func_evidence = self.score_functional_studies(
            has_crispr_ko, crispr_phenotype, has_sirna, has_biochemical, has_overexpression
        )

        # Disease models (0-5)
        model_score, model_evidence = self.score_disease_models(
            has_pdx, has_gemm, has_cell_line, has_in_silico
        )

        total = func_score + model_score
        total = min(total, 10)

        return DimensionScore(
            name="Validation Evidence",
            score=total,
            max_score=10,
            components={
                'functional': func_score,
                'models': model_score
            },
            evidence=func_evidence + model_evidence,
            tier=self._get_evidence_tier(total, 10)
        )

    # ============================================================
    # UTILITY METHODS
    # ============================================================

    @staticmethod
    def _get_evidence_tier(score: float, max_score: float) -> int:
        """Get evidence tier (T1-T4) based on score percentage."""
        pct = (score / max_score * 100) if max_score > 0 else 0
        if pct >= 70:
            return 1  # T1
        elif pct >= 50:
            return 2  # T2
        elif pct >= 30:
            return 3  # T3
        else:
            return 4  # T4

    def calculate_composite_score(
        self,
        disease_score: DimensionScore,
        druggability_score: DimensionScore,
        safety_score: DimensionScore,
        clinical_score: DimensionScore,
        validation_score: DimensionScore
    ) -> Tuple[float, int, str, Dict]:
        """
        Calculate composite validation score.

        Returns:
            Tuple of (total_score, tier, recommendation, score_breakdown)
        """
        total = (
            disease_score.score +
            druggability_score.score +
            safety_score.score +
            clinical_score.score +
            validation_score.score
        )

        # Determine tier and recommendation
        if total >= 80:
            tier, recommendation = 1, "GO"
        elif total >= 60:
            tier, recommendation = 2, "CONDITIONAL GO"
        elif total >= 40:
            tier, recommendation = 3, "CAUTION"
        else:
            tier, recommendation = 4, "NO-GO"

        score_breakdown = {
            'disease': disease_score.score,
            'druggability': druggability_score.score,
            'safety': safety_score.score,
            'clinical': clinical_score.score,
            'validation': validation_score.score
        }

        return total, tier, recommendation, score_breakdown


# Convenience function for full scoring
def calculate_full_validation_score(
    # Disease association inputs
    gwas_hits: List[Dict] = None,
    clinvar_pathogenic: int = 0,
    somatic_mutations: int = 0,
    pli: float = None,
    loeuf: float = None,
    publication_count: int = 0,
    target_disease_pubs: int = 0,
    opentargets_score: float = 0,
    pathway_count: int = 0,
    # Druggability inputs
    pdb_count: int = 0,
    has_ligand_structure: bool = False,
    best_resolution: float = None,
    has_alphafold: bool = False,
    alphafold_plddt: float = None,
    pocket_count: int = 0,
    pocket_volume: float = None,
    compound_count: int = 0,
    best_affinity_nm: float = None,
    has_drug_like: bool = False,
    target_class: str = "",
    # Safety inputs
    critical_tissue_expression: Dict[str, float] = None,
    tissue_specificity: float = 0,
    mouse_ko_viable: bool = None,
    mouse_ko_phenotype: str = None,
    known_adrs: List[str] = None,
    has_black_box: bool = False,
    withdrawn: bool = False,
    # Clinical inputs
    approved_same_disease: int = 0,
    approved_different_disease: int = 0,
    phase3_count: int = 0,
    phase2_count: int = 0,
    phase1_count: int = 0,
    preclinical_only: bool = False,
    failed_for_safety: bool = False,
    # Validation inputs
    has_crispr_ko: bool = False,
    crispr_phenotype: str = None,
    has_sirna: bool = False,
    has_biochemical: bool = False,
    has_overexpression: bool = False,
    has_pdx: bool = False,
    has_gemm: bool = False,
    has_cell_line: bool = False,
    has_in_silico: bool = False
) -> Dict:
    """
    Calculate full validation score from all inputs.

    Returns dictionary with dimension scores and composite.
    """
    scorer = DetailedScorer()

    # Default empty values
    gwas_hits = gwas_hits or []
    critical_tissue_expression = critical_tissue_expression or {}
    known_adrs = known_adrs or []

    # Score each dimension
    disease = scorer.score_disease_association(
        gwas_hits, clinvar_pathogenic, somatic_mutations, pli, loeuf,
        publication_count, target_disease_pubs, opentargets_score, pathway_count
    )

    druggability = scorer.score_druggability(
        pdb_count, has_ligand_structure, best_resolution, has_alphafold,
        alphafold_plddt, pocket_count, pocket_volume, compound_count,
        best_affinity_nm, has_drug_like, target_class
    )

    safety = scorer.score_safety(
        critical_tissue_expression, tissue_specificity,
        mouse_ko_viable, mouse_ko_phenotype, pli,
        known_adrs, has_black_box, withdrawn
    )

    clinical = scorer.score_clinical_precedent(
        approved_same_disease, approved_different_disease,
        phase3_count, phase2_count, phase1_count,
        preclinical_only, failed_for_safety, withdrawn
    )

    validation = scorer.score_validation_evidence(
        has_crispr_ko, crispr_phenotype, has_sirna, has_biochemical, has_overexpression,
        has_pdx, has_gemm, has_cell_line, has_in_silico
    )

    # Calculate composite
    total, tier, recommendation, breakdown = scorer.calculate_composite_score(
        disease, druggability, safety, clinical, validation
    )

    return {
        'total_score': total,
        'tier': tier,
        'recommendation': recommendation,
        'score_breakdown': breakdown,
        'dimensions': {
            'disease_association': {
                'score': disease.score,
                'max': disease.max_score,
                'components': disease.components,
                'evidence': disease.evidence,
                'tier': disease.tier
            },
            'druggability': {
                'score': druggability.score,
                'max': druggability.max_score,
                'components': druggability.components,
                'evidence': druggability.evidence,
                'tier': druggability.tier
            },
            'safety': {
                'score': safety.score,
                'max': safety.max_score,
                'components': safety.components,
                'evidence': safety.evidence,
                'tier': safety.tier
            },
            'clinical_precedent': {
                'score': clinical.score,
                'max': clinical.max_score,
                'components': clinical.components,
                'evidence': clinical.evidence,
                'tier': clinical.tier
            },
            'validation_evidence': {
                'score': validation.score,
                'max': validation.max_score,
                'components': validation.components,
                'evidence': validation.evidence,
                'tier': validation.tier
            }
        }
    }


if __name__ == '__main__':
    # Test the scorer
    result = calculate_full_validation_score(
        gwas_hits=[{'pvalue': 1e-10}, {'pvalue': 5e-9}],
        clinvar_pathogenic=3,
        pli=0.95,
        publication_count=500,
        target_disease_pubs=150,
        opentargets_score=0.85,
        pdb_count=20,
        has_ligand_structure=True,
        best_resolution=2.1,
        compound_count=30,
        best_affinity_nm=50,
        target_class='Kinase',
        mouse_ko_viable=True,
        approved_same_disease=2
    )

    print(f"Total Score: {result['total_score']}/100")
    print(f"Tier: {result['tier']}")
    print(f"Recommendation: {result['recommendation']}")
    print("\nDimension Scores:")
    for name, data in result['dimensions'].items():
        print(f"  {name}: {data['score']}/{data['max']}")