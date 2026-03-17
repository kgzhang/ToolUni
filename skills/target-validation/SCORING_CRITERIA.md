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

| Modality | Bonus/Adjustment | Criteria |
|----------|------------------|----------|
| Small Molecule | +2 | High-res co-crystal structure with small molecule ligand |
| Small Molecule | Focus | Oral tractability buckets 1-7 |
| Antibody | +2 | Confirmed surface accessibility on disease cells |
| Antibody | Focus | Extracellular domain coverage |
| PROTAC | +2 | Known ligand with suitable linker attachment sites |
| PROTAC | Focus | Surface lysines for ubiquitination |

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
| **T1** | ⭐⭐⭐ | Direct mechanistic, human clinical proof | FDA-approved drug, crystal structure with mechanism, patient mutation |
| **T2** | ⭐⭐ | Functional studies, model organism | siRNA phenotype, mouse KO, biochemical assay, CRISPR screen |
| **T3** | ⭐ | Association, screen hits, computational | GWAS hit, DepMap essentiality, expression correlation |
| **T4** | - | Mention, review, text-mined, predicted | Review article, database annotation, AlphaFold prediction |

---

## Score Calculation

```
def calculate_validation_score(scores):
    """Calculate total validation score from component scores."""

    total = (
        scores['disease_genetic'] +      # 0-10
        scores['disease_literature'] +   # 0-10
        scores['disease_pathway'] +      # 0-10
        scores['drug_structural'] +      # 0-10
        scores['drug_chemical'] +        # 0-10
        scores['drug_class'] +           # 0-5
        scores['safety_expression'] +    # 0-5
        scores['safety_genetic'] +       # 0-10
        scores['safety_adverse'] +       # 0-5
        scores['clinical'] +             # 0-15
        scores['validation_functional'] + # 0-5
        scores['validation_models']      # 0-5
    )

    if total >= 80:
        tier, rec = "Tier 1", "GO - Highly validated target"
    elif total >= 60:
        tier, rec = "Tier 2", "CONDITIONAL GO - Needs focused validation"
    elif total >= 40:
        tier, rec = "Tier 3", "CAUTION - Significant validation needed"
    else:
        tier, rec = "Tier 4", "NO-GO - Consider alternatives"

    return total, tier, rec
```

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