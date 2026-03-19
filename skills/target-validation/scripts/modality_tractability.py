#!/usr/bin/env python3
"""
Modality-Specific Tractability Assessment Module

Comprehensive assessment of target tractability across multiple drug modalities:
- Small Molecule
- Monoclonal Antibody
- PROTAC
- Gene Therapy (AAV)
- RNA Therapeutic (siRNA/ASO/mRNA)
- Cell Therapy (CAR-T/CAR-NK)
- Peptide Therapeutic
- Bispecific Antibody
- Antibody-Drug Conjugate (ADC)

Each modality has specific criteria, scoring adjustments, and data requirements.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


class ModalityType(Enum):
    """Supported drug modalities."""
    SMALL_MOLECULE = "small_molecule"
    ANTIBODY = "antibody"
    PROTAC = "protac"
    GENE_THERAPY = "gene_therapy"
    RNA_THERAPEUTIC = "rna_therapeutic"
    CELL_THERAPY = "cell_therapy"
    PEPTIDE = "peptide"
    BISPECIFIC = "bispecific"
    ADC = "adc"


@dataclass
class ModalityAssessment:
    """Assessment result for a single modality."""
    modality: str
    tractability_score: float  # 0-100
    bucket: int  # 1-10 tractability bucket
    is_tractable: bool
    bonuses: List[str] = field(default_factory=list)
    penalties: List[str] = field(default_factory=list)
    requirements_met: List[str] = field(default_factory=list)
    requirements_failed: List[str] = field(default_factory=list)
    recommendation: str = ""
    evidence: List[str] = field(default_factory=list)


class ModalityTractabilityAssessor:
    """
    Comprehensive modality-specific tractability assessment.

    Evaluates target across 9 major drug modalities with specific criteria
    for each including bonuses, penalties, and tractability buckets.
    """

    # Modality-specific thresholds
    TRACTABILITY_THRESHOLDS = {
        'highly_tractable': 70,
        'tractable': 50,
        'challenging': 30,
        'difficult': 0
    }

    # Bucket definitions (1-10 scale)
    BUCKET_THRESHOLDS = {
        1: 90, 2: 80, 3: 70, 4: 60, 5: 50,
        6: 40, 7: 30, 8: 20, 9: 10, 10: 0
    }

    def __init__(self):
        self.assessments: Dict[str, ModalityAssessment] = {}

    def assess_all_modalities(
        self,
        target_data: Dict,
        structure_data: Dict,
        expression_data: Dict,
        genetic_data: Dict,
        clinical_data: Dict
    ) -> Dict[str, ModalityAssessment]:
        """
        Assess tractability across all modalities.

        Args:
            target_data: Target class, family, subcellular location
            structure_data: PDB structures, AlphaFold, domains, pockets
            expression_data: Tissue expression, surface expression
            genetic_data: Constraint scores, paralogs
            clinical_data: Existing drugs, compounds

        Returns:
            Dictionary of modality assessments
        """
        self.assessments = {}

        # Assess each modality
        self.assessments['small_molecule'] = self._assess_small_molecule(
            target_data, structure_data, clinical_data
        )
        self.assessments['antibody'] = self._assess_antibody(
            target_data, expression_data, genetic_data
        )
        self.assessments['protac'] = self._assess_protac(
            target_data, structure_data, clinical_data
        )
        self.assessments['gene_therapy'] = self._assess_gene_therapy(
            target_data, expression_data, genetic_data
        )
        self.assessments['rna_therapeutic'] = self._assess_rna_therapeutic(
            target_data, genetic_data, expression_data
        )
        self.assessments['cell_therapy'] = self._assess_cell_therapy(
            target_data, expression_data
        )
        self.assessments['peptide'] = self._assess_peptide(
            target_data, structure_data
        )
        self.assessments['bispecific'] = self._assess_bispecific(
            target_data, expression_data, genetic_data
        )
        self.assessments['adc'] = self._assess_adc(
            target_data, expression_data
        )

        return self.assessments

    def _assess_small_molecule(
        self,
        target_data: Dict,
        structure_data: Dict,
        clinical_data: Dict
    ) -> ModalityAssessment:
        """
        Assess small molecule tractability.

        Criteria:
        - Binding pocket presence and quality
        - High-resolution co-crystal structures
        - Known small molecule binders
        - Oral bioavailability potential
        """
        score = 50.0  # Base score
        bonuses = []
        penalties = []
        requirements_met = []
        requirements_failed = []
        evidence = []

        # Structure assessment
        pdb_count = structure_data.get('pdb_count', 0)
        has_ligand_structure = structure_data.get('has_ligand_structure', False)
        best_resolution = structure_data.get('best_resolution')

        if pdb_count > 10:
            score += 10
            bonuses.append("Multiple PDB structures available")
            requirements_met.append("Structure coverage")
            evidence.append(f"{pdb_count} PDB structures [T1]")

        if has_ligand_structure:
            score += 15
            bonuses.append("High-quality ligand-bound structure")
            requirements_met.append("Ligand-bound structure")
            evidence.append("Co-crystal structure with ligand [T1]")

        if best_resolution and best_resolution < 2.5:
            score += 5
            bonuses.append(f"High resolution structure ({best_resolution}Å)")

        # Pocket assessment
        pockets = structure_data.get('binding_pockets', [])
        if pockets:
            pocket_volume = max([p.get('volume', 0) for p in pockets]) if pockets else 0
            if pocket_volume > 300:
                score += 10
                bonuses.append(f"Large binding pocket ({pocket_volume}Å³)")
                requirements_met.append("Drug-like pocket")
            elif pocket_volume > 200:
                score += 5
                bonuses.append(f"Moderate pocket ({pocket_volume}Å³)")
            elif pocket_volume < 200 and pocket_volume > 0:
                score -= 5
                penalties.append(f"Shallow binding pocket ({pocket_volume}Å³)")
                requirements_failed.append("Pocket depth")

        # Chemical matter
        known_compounds = clinical_data.get('compound_count', 0)
        if known_compounds > 10:
            score += 15
            bonuses.append(f"Extensive chemical matter ({known_compounds} compounds)")
            requirements_met.append("Chemical starting points")
            evidence.append(f"{known_compounds} known compounds [T1]")
        elif known_compounds > 0:
            score += 5
            bonuses.append(f"Some chemical matter ({known_compounds} compounds)")

        # Approved drugs bonus
        approved_drugs = clinical_data.get('approved_drugs', 0)
        if approved_drugs > 0:
            score += 10
            bonuses.append(f"Small molecule drugs approved ({approved_drugs})")
            evidence.append(f"{approved_drugs} FDA-approved SM drugs [T1]")

        # Target class bonus
        target_class = target_data.get('target_class', '')
        if target_class in ['Kinase', 'GPCR', 'Nuclear Receptor', 'Enzyme']:
            score += 10
            bonuses.append(f"Validated drug class ({target_class})")
            requirements_met.append("Drug class precedent")
            evidence.append(f"{target_class} - validated SM target class [T1]")
        elif target_class in ['Ion Channel', 'Transporter']:
            score += 5
            bonuses.append(f"Established target class ({target_class})")
            evidence.append(f"{target_class} - established SM target [T2]")

        # Calculate final score and bucket
        score = max(0, min(100, score))
        bucket = self._calculate_bucket(score)

        return ModalityAssessment(
            modality="Small Molecule",
            tractability_score=score,
            bucket=bucket,
            is_tractable=score >= 50,
            bonuses=bonuses,
            penalties=penalties,
            requirements_met=requirements_met,
            requirements_failed=requirements_failed,
            recommendation=self._get_recommendation(score, "small_molecule"),
            evidence=evidence
        )

    def _assess_antibody(
        self,
        target_data: Dict,
        expression_data: Dict,
        genetic_data: Dict
    ) -> ModalityAssessment:
        """
        Assess monoclonal antibody tractability.

        Criteria:
        - Extracellular/surface localization
        - Surface expression confirmed
        - Unique epitopes without cross-reactivity
        - No high-homology paralogs
        """
        score = 40.0  # Base score (lower than SM)
        bonuses = []
        penalties = []
        requirements_met = []
        requirements_failed = []
        evidence = []

        # Localization check
        location = target_data.get('subcellular_location', '').lower()
        is_membrane = any(term in location for term in ['membrane', 'surface', 'extracellular'])
        is_secreted = 'secreted' in location

        if is_membrane or is_secreted:
            score += 25
            bonuses.append(f"Extracellular localization ({location})")
            requirements_met.append("Extracellular access")
            evidence.append(f"Location: {location} - accessible to antibodies [T1]")
        else:
            score -= 20
            penalties.append("Intracellular localization")
            requirements_failed.append("Surface expression")
            evidence.append("Intracellular - not accessible to antibodies [T2]")

        # Surface expression confirmation
        surface_expr = expression_data.get('surface_expression_confirmed', False)
        if surface_expr:
            score += 15
            bonuses.append("Surface expression confirmed")
            requirements_met.append("Surface expression")
            evidence.append("Surface expression confirmed by IHC/flow cytometry [T1]")

        # Domain accessibility
        extracellular_domains = target_data.get('extracellular_domains', 0)
        if extracellular_domains > 0:
            score += 10
            bonuses.append(f"Extracellular domains available ({extracellular_domains})")
            requirements_met.append("Epitope availability")

        # Paralog risk
        paralogs = genetic_data.get('paralogs', [])
        high_homology_paralogs = [p for p in paralogs if p.get('identity', 0) > 80]
        if high_homology_paralogs:
            score -= 15
            penalties.append(f"High-homology paralogs ({len(high_homology_paralogs)})")
            requirements_failed.append("Selectivity")
            evidence.append(f"Cross-reactivity risk: {len(high_homology_paralogs)} paralogs >80% identity [T2]")
        elif paralogs:
            score += 5
            bonuses.append("No high-homology paralogs")

        # Approved antibody drugs
        approved_mabs = expression_data.get('approved_antibodies', 0)
        if approved_mabs > 0:
            score += 20
            bonuses.append(f"Antibody drugs approved ({approved_mabs})")
            evidence.append(f"{approved_mabs} FDA-approved antibody drugs [T1]")

        score = max(0, min(100, score))
        bucket = self._calculate_bucket(score)

        return ModalityAssessment(
            modality="Monoclonal Antibody",
            tractability_score=score,
            bucket=bucket,
            is_tractable=score >= 50,
            bonuses=bonuses,
            penalties=penalties,
            requirements_met=requirements_met,
            requirements_failed=requirements_failed,
            recommendation=self._get_recommendation(score, "antibody"),
            evidence=evidence
        )

    def _assess_protac(
        self,
        target_data: Dict,
        structure_data: Dict,
        clinical_data: Dict
    ) -> ModalityAssessment:
        """
        Assess PROTAC tractability.

        Criteria:
        - Known binders for linker attachment
        - Surface lysines for ubiquitination
        - Multiple E3 ligase options
        - Non-membrane target preferred
        """
        score = 35.0  # Base score
        bonuses = []
        penalties = []
        requirements_met = []
        requirements_failed = []
        evidence = []

        # Known binders
        known_binders = clinical_data.get('compound_count', 0)
        if known_binders > 5:
            score += 20
            bonuses.append(f"Multiple binders available for linker attachment")
            requirements_met.append("Binder availability")
            evidence.append(f"{known_binders} binders available for PROTAC development [T2]")
        elif known_binders > 0:
            score += 10
            bonuses.append("Binders available")

        # Lysine surface accessibility
        surface_lysines = structure_data.get('surface_lysines', 0)
        if surface_lysines > 10:
            score += 15
            bonuses.append(f"Multiple surface lysines ({surface_lysines})")
            requirements_met.append("Ubiquitination sites")
            evidence.append(f"{surface_lysines} surface lysines for ubiquitination [T3]")
        elif surface_lysines > 0:
            score += 5

        # E3 ligase options
        e3_options = ['CRBN', 'VHL', 'MDM2', 'IAP']  # Common E3 ligases
        available_e3 = len(e3_options)  # Assume all available
        if available_e3 >= 3:
            score += 10
            bonuses.append(f"Multiple E3 ligase options ({available_e3})")
            requirements_met.append("E3 ligase availability")
            evidence.append(f"{available_e3} E3 ligases available for recruitment [T2]")

        # Target location
        location = target_data.get('subcellular_location', '').lower()
        if 'membrane' in location:
            score -= 10
            penalties.append("Membrane protein may limit PROTAC access")
            requirements_failed.append("Cytoplasmic access")

        # Domain structure
        domains = structure_data.get('domains', [])
        disordered_regions = [d for d in domains if 'disordered' in d.get('name', '').lower()]
        if disordered_regions:
            score -= 5
            penalties.append("Disordered regions near binding site")
            requirements_failed.append("Defined binding site")

        score = max(0, min(100, score))
        bucket = self._calculate_bucket(score)

        return ModalityAssessment(
            modality="PROTAC",
            tractability_score=score,
            bucket=bucket,
            is_tractable=score >= 50,
            bonuses=bonuses,
            penalties=penalties,
            requirements_met=requirements_met,
            requirements_failed=requirements_failed,
            recommendation=self._get_recommendation(score, "protac"),
            evidence=evidence
        )

    def _assess_gene_therapy(
        self,
        target_data: Dict,
        expression_data: Dict,
        genetic_data: Dict
    ) -> ModalityAssessment:
        """
        Assess gene therapy (AAV) tractability.

        Criteria:
        - Tissue-specific expression
        - AAV delivery feasibility
        - Gene size constraints
        - Essentiality considerations
        """
        score = 30.0  # Base score
        bonuses = []
        penalties = []
        requirements_met = []
        requirements_failed = []
        evidence = []

        # Tissue specificity
        tissue_specificity = expression_data.get('tissue_specificity_score', 0)
        if tissue_specificity > 0.7:
            score += 25
            bonuses.append("High tissue specificity")
            requirements_met.append("Tissue-specific promoter available")
            evidence.append(f"Tissue specificity: {tissue_specificity:.1%} [T2]")
        elif tissue_specificity > 0.3:
            score += 10
            bonuses.append("Moderate tissue specificity")

        # Gene size (AAV limit ~4.7kb)
        gene_size = target_data.get('gene_size_kb', 0)
        if gene_size > 0 and gene_size < 4.5:
            score += 15
            bonuses.append(f"Gene size fits AAV ({gene_size}kb)")
            requirements_met.append("AAV packaging compatible")
            evidence.append(f"Gene size {gene_size}kb - AAV compatible [T2]")
        elif gene_size > 4.7:
            score -= 20
            penalties.append(f"Gene exceeds AAV capacity ({gene_size}kb)")
            requirements_failed.append("AAV packaging")

        # Expression level
        expression_level = expression_data.get('expression_level', 'moderate')
        if expression_level == 'high':
            score += 10
            bonuses.append("High expression achievable")
        elif expression_level == 'low':
            score -= 5
            penalties.append("Low expression may limit efficacy")

        # Essentiality
        pli = genetic_data.get('pLI', 0)
        if pli > 0.9:
            score -= 15
            penalties.append("Essential gene - overexpression risk")
            requirements_failed.append("Safety window")
            evidence.append(f"pLI={pli:.2f} - essential gene [T2]")

        # Target tissue delivery
        target_tissue = expression_data.get('primary_tissue', '')
        aav_accessible_tissues = ['liver', 'eye', 'muscle', 'CNS', 'heart']
        if any(t in target_tissue.lower() for t in aav_accessible_tissues):
            score += 10
            bonuses.append(f"Target tissue ({target_tissue}) accessible to AAV")
            requirements_met.append("AAV delivery route")
            evidence.append(f"Target tissue: {target_tissue} - AAV accessible [T2]")

        score = max(0, min(100, score))
        bucket = self._calculate_bucket(score)

        return ModalityAssessment(
            modality="Gene Therapy (AAV)",
            tractability_score=score,
            bucket=bucket,
            is_tractable=score >= 50,
            bonuses=bonuses,
            penalties=penalties,
            requirements_met=requirements_met,
            requirements_failed=requirements_failed,
            recommendation=self._get_recommendation(score, "gene_therapy"),
            evidence=evidence
        )

    def _assess_rna_therapeutic(
        self,
        target_data: Dict,
        genetic_data: Dict,
        expression_data: Dict
    ) -> ModalityAssessment:
        """
        Assess RNA therapeutic (siRNA/ASO/mRNA) tractability.

        Criteria:
        - Accessible tissue (liver, kidney, CNS)
        - Low homology gene family
        - Cytoplasmic localization for siRNA
        - Expression level
        """
        score = 35.0  # Base score
        bonuses = []
        penalties = []
        requirements_met = []
        requirements_failed = []
        evidence = []

        # Tissue accessibility
        target_tissue = expression_data.get('primary_tissue', '')
        accessible_tissues = ['liver', 'kidney', 'CNS', 'eye', 'lung', 'muscle']
        if any(t in target_tissue.lower() for t in accessible_tissues):
            score += 20
            bonuses.append(f"Accessible tissue ({target_tissue})")
            requirements_met.append("RNA delivery feasible")
            evidence.append(f"Target tissue: {target_tissue} - RNA accessible [T2]")
        else:
            score -= 10
            penalties.append("Limited RNA delivery options")
            requirements_failed.append("Delivery route")

        # Gene family homology
        paralogs = genetic_data.get('paralogs', [])
        high_homology = [p for p in paralogs if p.get('identity', 0) > 80]
        if high_homology:
            score -= 20
            penalties.append(f"High homology gene family ({len(high_homology)})")
            requirements_failed.append("Selectivity")
            evidence.append(f"Off-target risk: {len(high_homology)} paralogs >80% identity [T2]")
        else:
            score += 10
            bonuses.append("Unique sequence enables specific targeting")

        # Localization for siRNA
        location = target_data.get('subcellular_location', '').lower()
        if 'nuclear' in location:
            score -= 10
            penalties.append("Nuclear localization limits siRNA efficacy")
            requirements_failed.append("Cytoplasmic access")
        elif 'cytoplasm' in location:
            score += 5
            bonuses.append("Cytoplasmic localization")

        # Expression level
        expr_level = expression_data.get('expression_level', 'moderate')
        if expr_level == 'high':
            score += 5
            bonuses.append("High expression - good target abundance")
            evidence.append("High expression level [T2]")

        # Validated siRNA/ASO
        validated_rna = genetic_data.get('validated_siRNA', False)
        if validated_rna:
            score += 15
            bonuses.append("Validated siRNA/ASO available")
            requirements_met.append("Prior RNA therapeutic validation")
            evidence.append("Published siRNA/ASO data available [T1]")

        score = max(0, min(100, score))
        bucket = self._calculate_bucket(score)

        return ModalityAssessment(
            modality="RNA Therapeutic",
            tractability_score=score,
            bucket=bucket,
            is_tractable=score >= 50,
            bonuses=bonuses,
            penalties=penalties,
            requirements_met=requirements_met,
            requirements_failed=requirements_failed,
            recommendation=self._get_recommendation(score, "rna_therapeutic"),
            evidence=evidence
        )

    def _assess_cell_therapy(
        self,
        target_data: Dict,
        expression_data: Dict
    ) -> ModalityAssessment:
        """
        Assess cell therapy (CAR-T/CAR-NK) tractability.

        Criteria:
        - Tumor-specific antigen (no normal tissue expression)
        - Surface expression
        - Resistance to exhaustion
        - Homogeneous tumor expression
        """
        score = 25.0  # Base score (most stringent requirements)
        bonuses = []
        penalties = []
        requirements_met = []
        requirements_failed = []
        evidence = []

        # Tumor vs normal expression
        tumor_specific = expression_data.get('tumor_specific_expression', False)
        normal_tissue_expr = expression_data.get('normal_tissue_expression', [])

        if tumor_specific:
            score += 30
            bonuses.append("Tumor-specific antigen")
            requirements_met.append("No normal tissue expression")
            evidence.append("Tumor-specific expression - ideal CAR target [T1]")
        elif not normal_tissue_expr or len(normal_tissue_expr) == 0:
            score += 20
            bonuses.append("Limited normal tissue expression")
            requirements_met.append("Favorable safety window")
        else:
            critical_normal = [t for t in normal_tissue_expr
                             if t.get('tissue') in ['heart', 'brain', 'liver', 'kidney']]
            if critical_normal:
                score -= 25
                penalties.append(f"Expression in vital tissues: {[t['tissue'] for t in critical_normal]}")
                requirements_failed.append("On-target off-tumor toxicity")
                evidence.append(f"Expression in {len(critical_normal)} vital normal tissues [T2]")

        # Surface expression
        surface_expr = expression_data.get('surface_expression_confirmed', False)
        if surface_expr:
            score += 15
            bonuses.append("Surface expression confirmed")
            requirements_met.append("Surface antigen")
            evidence.append("Surface expression confirmed [T1]")
        else:
            score -= 20
            penalties.append("Surface expression not confirmed")
            requirements_failed.append("Surface antigen")

        # Tumor heterogeneity
        tumor_heterogeneity = expression_data.get('tumor_heterogeneity', 'unknown')
        if tumor_heterogeneity == 'homogeneous':
            score += 10
            bonuses.append("Homogeneous tumor expression")
            requirements_met.append("Uniform target expression")
        elif tumor_heterogeneity == 'heterogeneous':
            score -= 15
            penalties.append("Heterogeneous tumor expression")
            requirements_failed.append("Uniform expression")
            evidence.append("Heterogeneous expression may limit efficacy [T2]")

        # Internalization rate
        internalization = expression_data.get('internalization_rate', 'unknown')
        if internalization == 'high':
            score += 5
            bonuses.append("Rapid internalization (>50%/hr)")

        score = max(0, min(100, score))
        bucket = self._calculate_bucket(score)

        return ModalityAssessment(
            modality="Cell Therapy (CAR-T/NK)",
            tractability_score=score,
            bucket=bucket,
            is_tractable=score >= 50,
            bonuses=bonuses,
            penalties=penalties,
            requirements_met=requirements_met,
            requirements_failed=requirements_failed,
            recommendation=self._get_recommendation(score, "cell_therapy"),
            evidence=evidence
        )

    def _assess_peptide(
        self,
        target_data: Dict,
        structure_data: Dict
    ) -> ModalityAssessment:
        """
        Assess peptide therapeutic tractability.

        Criteria:
        - Structurally constrained (cyclized, stapled)
        - Cell-penetrating potential
        - Protease resistance
        - Stability considerations
        """
        score = 40.0  # Base score
        bonuses = []
        penalties = []
        requirements_met = []
        requirements_failed = []
        evidence = []

        # Known peptide binders
        peptide_binders = structure_data.get('peptide_binders', 0)
        if peptide_binders > 0:
            score += 15
            bonuses.append(f"Known peptide binders ({peptide_binders})")
            requirements_met.append("Peptide starting points")
            evidence.append(f"{peptide_binders} peptide binders identified [T2]")

        # Binding pocket
        pockets = structure_data.get('binding_pockets', [])
        if pockets:
            pocket_type = pockets[0].get('type', 'unknown') if pockets else 'unknown'
            if pocket_type in ['groove', 'extended']:
                score += 10
                bonuses.append(f"Extended binding site suitable for peptides")
                requirements_met.append("Peptide-compatible site")

        # PPI interface
        is_ppi_target = target_data.get('is_ppi_target', False)
        if is_ppi_target:
            score += 10
            bonuses.append("PPI target - peptides often effective")
            requirements_met.append("PPI interface")
            evidence.append("PPI target - peptides can disrupt interface [T2]")

        # Structural constraints
        constrained = structure_data.get('constrained_peptide_possible', False)
        if constrained:
            score += 10
            bonuses.append("Constrained peptide design possible")
            requirements_met.append("Structural stability")

        # Protease sites
        protease_sites = structure_data.get('protease_cleavage_sites', 0)
        if protease_sites > 3:
            score -= 15
            penalties.append(f"Multiple protease cleavage sites ({protease_sites})")
            requirements_failed.append("Protease stability")
        elif protease_sites > 0:
            score -= 5
            penalties.append(f"Some protease sites ({protease_sites})")

        # Cell penetration
        cell_penetrating = target_data.get('cell_penetrating_possible', False)
        if cell_penetrating:
            score += 10
            bonuses.append("Cell-penetrating peptide possible")
            requirements_met.append("Intracellular delivery")

        score = max(0, min(100, score))
        bucket = self._calculate_bucket(score)

        return ModalityAssessment(
            modality="Peptide Therapeutic",
            tractability_score=score,
            bucket=bucket,
            is_tractable=score >= 50,
            bonuses=bonuses,
            penalties=penalties,
            requirements_met=requirements_met,
            requirements_failed=requirements_failed,
            recommendation=self._get_recommendation(score, "peptide"),
            evidence=evidence
        )

    def _assess_bispecific(
        self,
        target_data: Dict,
        expression_data: Dict,
        genetic_data: Dict
    ) -> ModalityAssessment:
        """
        Assess bispecific antibody tractability.

        Criteria:
        - Two targets with synergistic mechanism
        - Optimal spatial arrangement possible
        - No competing epitopes
        - No steric hindrance
        """
        score = 35.0  # Base score
        bonuses = []
        penalties = []
        requirements_met = []
        requirements_failed = []
        evidence = []

        # First target accessibility
        location = target_data.get('subcellular_location', '').lower()
        if 'membrane' in location or 'surface' in location:
            score += 15
            bonuses.append("Surface target accessible")
            requirements_met.append("Target 1 surface expression")
            evidence.append("Target is surface-exposed [T1]")
        else:
            score -= 15
            penalties.append("Target not surface accessible")
            requirements_failed.append("Surface expression")

        # Partner target considerations (for bispecific)
        partner_target = target_data.get('bispecific_partner', {})
        if partner_target:
            score += 10
            bonuses.append(f"Potential partner target: {partner_target.get('name', 'identified')}")
            requirements_met.append("Bispecific partner")
            evidence.append("Partner target identified for bispecific [T3]")

        # Synergistic mechanism
        synergistic = target_data.get('synergistic_mechanism', False)
        if synergistic:
            score += 15
            bonuses.append("Synergistic mechanism demonstrated")
            requirements_met.append("Mechanistic synergy")
            evidence.append("Dual targeting provides synergistic effect [T2]")

        # Format compatibility
        format_options = target_data.get('bispecific_formats', [])
        if len(format_options) >= 3:
            score += 10
            bonuses.append(f"Multiple format options ({len(format_options)})")
            requirements_met.append("Format flexibility")

        # Steric considerations
        domain_spacing = target_data.get('domain_spacing', 'unknown')
        if domain_spacing == 'compatible':
            score += 5
            bonuses.append("Domain spacing compatible")
        elif domain_spacing == 'challenging':
            score -= 10
            penalties.append("Domain spacing may cause steric hindrance")
            requirements_failed.append("Steric compatibility")

        score = max(0, min(100, score))
        bucket = self._calculate_bucket(score)

        return ModalityAssessment(
            modality="Bispecific Antibody",
            tractability_score=score,
            bucket=bucket,
            is_tractable=score >= 50,
            bonuses=bonuses,
            penalties=penalties,
            requirements_met=requirements_met,
            requirements_failed=requirements_failed,
            recommendation=self._get_recommendation(score, "bispecific"),
            evidence=evidence
        )

    def _assess_adc(
        self,
        target_data: Dict,
        expression_data: Dict
    ) -> ModalityAssessment:
        """
        Assess antibody-drug conjugate (ADC) tractability.

        Criteria:
        - Rapid internalization
        - Tumor-selective expression
        - Surface turnover rate
        - No shed soluble antigen
        """
        score = 35.0  # Base score
        bonuses = []
        penalties = []
        requirements_met = []
        requirements_failed = []
        evidence = []

        # Internalization rate
        internalization = expression_data.get('internalization_rate', 'unknown')
        if internalization == 'high':
            score += 20
            bonuses.append("Rapid internalization (>50%/hr)")
            requirements_met.append("Fast internalization")
            evidence.append("High internalization rate [T1]")
        elif internalization == 'moderate':
            score += 10
            bonuses.append("Moderate internalization")
        elif internalization == 'low':
            score -= 15
            penalties.append("Slow internalization")
            requirements_failed.append("Internalization rate")
            evidence.append("Slow surface turnover [T2]")

        # Tumor selectivity
        tumor_selective = expression_data.get('tumor_selective', False)
        if tumor_selective:
            score += 20
            bonuses.append("Tumor-selective expression")
            requirements_met.append("Tumor specificity")
            evidence.append("Tumor-selective expression [T1]")
        else:
            score -= 10
            penalties.append("Expression in normal tissues")
            requirements_failed.append("Tumor selectivity")

        # Soluble antigen
        has_soluble = expression_data.get('soluble_antigen', False)
        if has_soluble:
            score -= 15
            penalties.append("Shed soluble antigen present")
            requirements_failed.append("No soluble isoform")
            evidence.append("Soluble antigen may compete for ADC [T2]")
        else:
            score += 5
            bonuses.append("No soluble antigen isoform")
            requirements_met.append("Membrane-only expression")

        # Surface expression level
        surface_level = expression_data.get('surface_expression_level', 'moderate')
        if surface_level == 'high':
            score += 10
            bonuses.append("High surface expression")
            requirements_met.append("High antigen density")
            evidence.append("High surface expression [T2]")

        # ADC precedent
        approved_adcs = expression_data.get('approved_adcs', 0)
        if approved_adcs > 0:
            score += 15
            bonuses.append(f"Approved ADC exists ({approved_adcs})")
            evidence.append(f"{approved_adcs} FDA-approved ADCs [T1]")

        score = max(0, min(100, score))
        bucket = self._calculate_bucket(score)

        return ModalityAssessment(
            modality="Antibody-Drug Conjugate",
            tractability_score=score,
            bucket=bucket,
            is_tractable=score >= 50,
            bonuses=bonuses,
            penalties=penalties,
            requirements_met=requirements_met,
            requirements_failed=requirements_failed,
            recommendation=self._get_recommendation(score, "adc"),
            evidence=evidence
        )

    def _calculate_bucket(self, score: float) -> int:
        """Calculate tractability bucket (1-10) from score."""
        if score >= 90:
            return 1
        elif score >= 80:
            return 2
        elif score >= 70:
            return 3
        elif score >= 60:
            return 4
        elif score >= 50:
            return 5
        elif score >= 40:
            return 6
        elif score >= 30:
            return 7
        elif score >= 20:
            return 8
        elif score >= 10:
            return 9
        else:
            return 10

    def _get_recommendation(self, score: float, modality: str) -> str:
        """Get recommendation based on score and modality."""
        if score >= 70:
            return f"Highly tractable - prioritize {modality} development"
        elif score >= 50:
            return f"Tractable - {modality} development feasible with optimization"
        elif score >= 30:
            return f"Challenging - {modality} requires significant R&D investment"
        else:
            return f"Difficult - {modality} not recommended without major innovation"

    def get_best_modality(self) -> Tuple[str, ModalityAssessment]:
        """Get the highest-scoring modality."""
        if not self.assessments:
            return None, None
        best = max(self.assessments.items(), key=lambda x: x[1].tractability_score)
        return best[0], best[1]

    def get_tractable_modalities(self, threshold: float = 50.0) -> List[Tuple[str, ModalityAssessment]]:
        """Get all modalities above tractability threshold."""
        return [(k, v) for k, v in self.assessments.items()
                if v.tractability_score >= threshold]

    def to_dict(self) -> Dict:
        """Convert assessments to dictionary for JSON export."""
        return {
            'assessments': {
                modality: {
                    'modality': assessment.modality,
                    'tractability_score': assessment.tractability_score,
                    'bucket': assessment.bucket,
                    'is_tractable': assessment.is_tractable,
                    'bonuses': assessment.bonuses,
                    'penalties': assessment.penalties,
                    'requirements_met': assessment.requirements_met,
                    'requirements_failed': assessment.requirements_failed,
                    'recommendation': assessment.recommendation,
                    'evidence': assessment.evidence
                }
                for modality, assessment in self.assessments.items()
            },
            'best_modality': self.get_best_modality()[0] if self.assessments else None,
            'tractable_count': len(self.get_tractable_modalities())
        }


# Convenience functions for integration
def assess_modality_tractability(
    target_data: Dict,
    structure_data: Dict,
    expression_data: Dict,
    genetic_data: Dict,
    clinical_data: Dict
) -> Dict:
    """
    Convenience function to assess all modalities and return dictionary.

    Args:
        target_data: Target class, family, location
        structure_data: PDB, AlphaFold, pockets, domains
        expression_data: Tissue, surface, tumor expression
        genetic_data: Constraints, paralogs
        clinical_data: Compounds, drugs

    Returns:
        Dictionary with all modality assessments
    """
    assessor = ModalityTractabilityAssessor()
    assessor.assess_all_modalities(
        target_data, structure_data, expression_data, genetic_data, clinical_data
    )
    return assessor.to_dict()


def main():
    """Test modality assessment with sample data."""
    # Sample data for testing
    target_data = {
        'target_class': 'Kinase',
        'subcellular_location': 'Cytoplasm',
        'gene_size_kb': 3.2
    }

    structure_data = {
        'pdb_count': 15,
        'has_ligand_structure': True,
        'best_resolution': 2.1,
        'binding_pockets': [{'volume': 350}],
        'surface_lysines': 25
    }

    expression_data = {
        'tissue_specificity_score': 0.8,
        'surface_expression_confirmed': False,
        'primary_tissue': 'Liver'
    }

    genetic_data = {
        'pLI': 0.95,
        'paralogs': []
    }

    clinical_data = {
        'compound_count': 50,
        'approved_drugs': 2
    }

    result = assess_modality_tractability(
        target_data, structure_data, expression_data, genetic_data, clinical_data
    )

    print("Modality Tractability Assessment Results:")
    print("=" * 50)
    for modality, data in result['assessments'].items():
        print(f"\n{data['modality']}:")
        print(f"  Score: {data['tractability_score']:.1f}/100")
        print(f"  Bucket: {data['bucket']}")
        print(f"  Tractable: {'Yes' if data['is_tractable'] else 'No'}")
        if data['bonuses']:
            print(f"  Bonuses: {', '.join(data['bonuses'][:2])}")
        if data['penalties']:
            print(f"  Penalties: {', '.join(data['penalties'][:2])}")

    print(f"\nBest modality: {result['best_modality']}")
    print(f"Tractable modalities: {result['tractable_count']}")


if __name__ == '__main__':
    main()