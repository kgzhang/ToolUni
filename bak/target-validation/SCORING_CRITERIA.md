# Target Validation - Scoring Criteria

Detailed scoring matrices, evidence grading, and priority tier definitions for the Target Validation Score (0-100).

---

## Composite Score (0-100 Points)

| Dimension | Max Points | Sub-dimensions |
|-----------|------------|----------------|
| **Disease Association** | 30 | Genetic (10) + Literature (10) + Pathway (10) |
| **Druggability** | 25 | Structure (10) + Chemical matter (10) + Target class (5) |
| **Safety Profile** | 20 | Expression (5) + Genetic validation (10) + ADRs (5) |
| **Clinical Precedent** | 15 | Based on highest clinical stage |
| **Validation Evidence** | 10 | Functional studies (5) + Disease models (5) |

---

## Disease Association (0-30 points)

### Genetic Evidence (0-10)

| Evidence Type | Points | Source |
|---------------|--------|--------|
| GWAS hits for specific disease | +3 per significant locus (max 6) | GWAS Catalog |
| Rare variant evidence (ClinVar pathogenic) | +2 | ClinVar |
| Somatic mutations in disease | +2 | cBioPortal, COSMIC |
| pLI > 0.9 (essential gene) | +2 | gnomAD |
| LOEUF < 0.35 (constrained) | +1 | gnomAD |

**Maximum**: 10 points

### Literature Evidence (0-10)

| Publication Count | Points |
|-------------------|--------|
| >100 publications on target+disease | 10 |
| 50-100 publications | 7 |
| 10-50 publications | 5 |
| 1-10 publications | 3 |
| 0 publications | 0 |

**Source**: PubMed, EuropePMC

### Pathway Evidence (0-10)

| OpenTargets Association Score | Points |
|------------------------------|--------|
| > 0.8 | 10 |
| 0.5 - 0.8 | 7 |
| 0.2 - 0.5 | 4 |
| < 0.2 | 1 |

---

## Druggability (0-25 points)

### Structural Tractability (0-10)

| Structure Quality | Points | Evidence |
|-------------------|--------|----------|
| High-res co-crystal structure with ligand | 10 | PDB < 2.5Å with bound ligand |
| PDB structure available, pockets detected | 7 | PDB structure + ProteinsPlus pockets |
| AlphaFold only, confident pocket prediction | 5 | pLDDT > 70, predicted pockets |
| AlphaFold low confidence / no structure | 2 | pLDDT < 70 |
| No structural data | 0 | - |

### Chemical Matter (0-10)

| Compound Quality | Points | Evidence |
|------------------|--------|----------|
| Known drug-like compounds (IC50 < 100nM) | 10 | ChEMBL, BindingDB |
| Tool compounds (IC50 < 1µM) | 7 | ChEMBL, BindingDB |
| HTS hits only (IC50 > 1µM) | 4 | PubChem BioAssay |
| No known ligands | 0 | - |

### Target Class Bonus (0-5)

| Target Class | Points | Rationale |
|--------------|--------|-----------|
| Validated druggable family (kinase, GPCR, nuclear receptor) | 5 | Multiple approved drugs in class |
| Enzyme, ion channel | 4 | Established tractability |
| Protein-protein interaction, transporter | 2 | Challenging but precedented |
| Novel/unknown class | 0 | No class precedent |

---

## Safety Profile (0-20 points)

### Tissue Expression Selectivity (0-5)

| Expression Pattern | Points | Assessment |
|--------------------|--------|------------|
| Target restricted to disease tissue | 5 | Favorable therapeutic window |
| Low expression in heart/liver/kidney/brain | 4 | Manageable safety profile |
| Moderate expression in 1-2 critical tissues | 2 | Monitor during development |
| High expression in multiple critical tissues | 0 | Safety concern |

**Critical tissues**: heart, liver, kidney, brain, bone marrow

### Genetic Validation (0-10)

| Genetic Evidence | Points | Interpretation |
|------------------|--------|----------------|
| Mouse KO viable, no severe phenotype | 10 | Target inhibition likely safe |
| Mouse KO viable with mild phenotype | 7 | Manageable effects |
| Mouse KO has concerning phenotype | 3 | Safety signal |
| Mouse KO lethal | 0 | Major safety concern |
| No KO data, low pLI (<0.5) | 5 | Moderate confidence |
| No KO data, high pLI (>0.9) | 2 | Caution required |

### Known Adverse Events (0-5)

| Safety Record | Points | Evidence |
|---------------|--------|----------|
| No known safety signals | 5 | Clean profile |
| Mild, manageable ADRs | 3 | Tolerable toxicity |
| Serious ADRs reported | 1 | Significant concern |
| Black box warning or drug withdrawal | 0 | Major liability |

---

## Clinical Precedent (0-15 points)

| Clinical Stage | Points |
|----------------|--------|
| FDA-approved drug for SAME disease | 15 |
| FDA-approved drug for DIFFERENT disease | 12 |
| Phase 3 clinical trial | 10 |
| Phase 2 clinical trial | 7 |
| Phase 1 clinical trial | 5 |
| Preclinical compounds only | 3 |
| No clinical development | 0 |

### Adjustment Factors

| Factor | Adjustment |
|--------|------------|
| Failed clinical program for safety | -3 |
| Drug withdrawal | -5 |
| Multiple approved drugs (validated class) | +2 |

---

## Validation Evidence (0-10 points)

### Functional Studies (0-5)

| Evidence | Points | Quality |
|----------|--------|---------|
| CRISPR KO shows disease-relevant phenotype | 5 | T1 evidence |
| siRNA knockdown shows phenotype | 4 | T2 evidence |
| Biochemical assay validates mechanism | 3 | T2 evidence |
| Overexpression study only | 2 | T3 evidence |
| No functional data | 0 | - |

### Disease Models (0-5)

| Model Type | Points | Quality |
|------------|--------|---------|
| Patient-derived xenograft (PDX) response | 5 | T1 evidence |
| Genetically engineered mouse model | 4 | T2 evidence |
| Cell line model | 3 | T3 evidence |
| In silico model only | 1 | T4 evidence |
| No model data | 0 | - |

---

## Modality-Specific Adjustments

### Small Molecule
| Adjustment | Criteria | Points |
|------------|----------|--------|
| Bonus | High-res co-crystal structure with small molecule ligand | +2 |
| Bonus | Oral bioavailability data from approved drugs | +1 |
| Penalty | Shallow binding pockets (volume < 200 A3) | -2 |
| Focus | Oral tractability buckets 1-7 | N/A |

### Monoclonal Antibody
| Adjustment | Criteria | Points |
|------------|----------|--------|
| Bonus | Confirmed surface expression on disease cells | +2 |
| Bonus | Unique epitope with no cross-reactivity | +1 |
| Penalty | Intracellular localization | -2 |
| Penalty | High homology paralogs (>80% identity) | -1 |
| Focus | Extracellular domain coverage | N/A |

### PROTAC
| Adjustment | Criteria | Points |
|------------|----------|--------|
| Bonus | Known binders with suitable linker attachment sites | +2 |
| Bonus | Multiple E3 ligase options available | +1 |
| Penalty | Membrane protein without intracellular domain | -2 |
| Penalty | Disordered regions near binding site | -1 |
| Focus | Surface lysines for ubiquitination | N/A |

### Gene Therapy
| Adjustment | Criteria | Points |
|------------|----------|--------|
| Bonus | Tissue-specific promoter available | +2 |
| Bonus | AAV delivery data in relevant tissue | +1 |
| Penalty | Ubiquitous expression of essential gene | -2 |
| Penalty | Immune-privileged site required | -1 |
| Focus | Tissue specificity for safety window | N/A |

### RNA Therapeutic (siRNA/ASO/mRNA)
| Adjustment | Criteria | Points |
|------------|----------|--------|
| Bonus | Validated siRNA/ASO with published data | +2 |
| Bonus | Accessible tissue (liver, kidney, CNS) | +1 |
| Penalty | High homology gene family (>80% identity) | -2 |
| Penalty | Nuclear localization (for siRNA) | -1 |
| Focus | Off-target potential assessment | N/A |

### Cell Therapy (CAR-T/CAR-NK)
| Adjustment | Criteria | Points |
|------------|----------|--------|
| Bonus | Tumor-specific antigen (no normal tissue expression) | +2 |
| Bonus | Resistance to exhaustion demonstrated | +1 |
| Penalty | Expression on vital normal tissues | -2 |
| Penalty | Heterogeneous expression in tumor | -1 |
| Focus | Surface marker specificity | N/A |

### Peptide Therapeutic
| Adjustment | Criteria | Points |
|------------|----------|--------|
| Bonus | Structurally constrained (cyclized, stapled) | +2 |
| Bonus | Cell-penetrating potential | +1 |
| Penalty | Protease-sensitive cleavage sites | -2 |
| Penalty | Rapid renal clearance expected | -1 |
| Focus | Stability and permeability | N/A |

### Bispecific Antibody
| Adjustment | Criteria | Points |
|------------|----------|--------|
| Bonus | Synergistic mechanism demonstrated | +2 |
| Bonus | Optimal spatial arrangement possible | +1 |
| Penalty | Competing epitopes on same target | -2 |
| Penalty | Steric hindrance between arms | -1 |
| Focus | Dual target engagement geometry | N/A |

### Antibody-Drug Conjugate (ADC)
| Adjustment | Criteria | Points |
|------------|----------|--------|
| Bonus | Rapid internalization rate (>50% in 1hr) | +2 |
| Bonus | Tumor-selective expression (low normal tissue) | +1 |
| Penalty | Slow surface turnover | -2 |
| Penalty | Shed soluble antigen | -1 |
| Focus | Internalization and trafficking | N/A |

---

## Priority Tiers

| Score | Tier | Recommendation | Action |
|-------|------|----------------|--------|
| **80-100** | Tier 1 | GO | Highly validated - proceed with confidence |
| **60-79** | Tier 2 | CONDITIONAL GO | Good target - needs focused validation |
| **40-59** | Tier 3 | CAUTION | Moderate risk - significant validation needed |
| **0-39** | Tier 4 | NO-GO | High risk - consider alternatives |

---

## Evidence Grading System

| Tier | Symbol | Criteria | Examples |
|------|--------|----------|----------|
| **T1** | [T1] | Direct mechanistic, human clinical proof | FDA-approved drug, crystal structure with mechanism, patient mutation |
| **T2** | [T2] | Functional studies, model organism | siRNA phenotype, mouse KO, biochemical assay, CRISPR screen |
| **T3** | [T3] | Association, screen hits, computational | GWAS hit, DepMap essentiality, expression correlation |
| **T4** | [T4] | Mention, review, text-mined, predicted | Review article, database annotation, AlphaFold prediction |

---

## Score Calculation

**Implementation**: See [scripts/scoring_utils.py](scripts/scoring_utils.py) for the detailed scoring implementation.

**Algorithm**:

1. Sum component scores from all 5 dimensions
2. Apply modality-specific adjustments (see [scripts/modality_tractability.py](scripts/modality_tractability.py))
3. Determine tier based on total:
   - **≥80**: Tier 1 (GO)
   - **≥60**: Tier 2 (CONDITIONAL GO)
   - **≥40**: Tier 3 (CAUTION)
   - **<40**: Tier 4 (NO-GO)

---

## Example Scores

### EGFR for NSCLC (Well-validated target)
- Disease Association: 28/30 (strong genetic + pathway + literature)
- Druggability: 24/25 (kinase, many structures, abundant compounds)
- Safety: 14/20 (widely expressed but manageable toxicity)
- Clinical Precedent: 15/15 (multiple approved drugs)
- Validation Evidence: 9/10 (extensive functional data)
- **Total: 90/100 = Tier 1**

### Novel Understudied Kinase
- Disease Association: 8/30 (limited GWAS, few publications)
- Druggability: 15/25 (kinase family bonus, AlphaFold structure)
- Safety: 12/20 (limited data, unknown KO phenotype)
- Clinical Precedent: 0/15 (no clinical development)
- Validation Evidence: 2/10 (minimal functional data)
- **Total: 37/100 = Tier 4**