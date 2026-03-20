# Target Validation - Examples

Worked examples demonstrating the target validation pipeline.

---

## Example 1: EGFR Full Assessment

**Input**: `target="EGFR", disease="non-small cell lung cancer", modality="small molecule"`

### Phase 0: Target Disambiguation

| Identifier Type | Value | Database |
|-----------------|-------|----------|
| Gene Symbol | EGFR | HGNC |
| UniProt Accession | P00533 | UniProtKB |
| Ensembl Gene ID | ENSG00000146648 | Ensembl |
| Entrez Gene ID | 1956 | NCBI Gene |
| ChEMBL Target ID | CHEMBL203 | ChEMBL |
| Target Class | Kinase (Receptor tyrosine) | Pharos |

**GPCR Status**: Not a GPCR
**Target Development Level**: Tclin (FDA-approved drug target)

### Phase 8: Disease Association Scoring

| Sub-score | Points | Evidence |
|-----------|--------|----------|
| Genetic | 10/10 | GWAS: 4 significant loci [T3]; pLI=1.0 (constrained) [T3] |
| Literature | 10/10 | >100 publications on EGFR+NSCLC [T4] |
| Pathway | 10/10 | OpenTargets score=0.98 [T3] |
| **Total** | **30/30** | |

### Phase 9: Druggability Assessment

| Sub-score | Points | Evidence |
|-----------|--------|----------|
| Structural | 10/10 | 150+ PDB structures; best 1.5Å; SM bucket=1 [T1] |
| Chemical | 10/10 | 500+ compounds <100nM in ChEMBL [T2] |
| Target Class | 5/5 | Kinase - validated druggable family [T1] |
| **Total** | **25/25** | |

### Phase 10: Safety Deep Analysis

| Sub-score | Points | Evidence |
|-----------|--------|----------|
| Expression | 2/5 | High expression in liver, moderate in skin [T2] |
| Genetic | 7/10 | Mouse KO viable with skin defects [T2] |
| ADRs | 3/5 | Manageable: rash, diarrhea (on-target) [T1] |
| **Total** | **12/20** | |

**Safety Flags**: Skin toxicity (manageable with supportive care)

### Phase 11: Clinical Precedent

| Score | Points | Evidence |
|-------|--------|----------|
| Clinical | 15/15 | 8 FDA-approved drugs for NSCLC (erlotinib, gefitinib, osimertinib, etc.) [T1] |

### Phase 12: Validation Evidence

| Sub-score | Points | Evidence |
|-----------|--------|----------|
| Functional | 5/5 | CRISPR KO reduces tumor growth [T1] |
| Disease Models | 5/5 | PDX models respond to EGFR inhibitors [T1] |
| **Total** | **10/10** | |

### Composite Score

| Dimension | Score | Max |
|-----------|-------|-----|
| Disease Association | 30 | 30 |
| Druggability | 25 | 25 |
| Safety Profile | 12 | 20 |
| Clinical Precedent | 15 | 15 |
| Validation Evidence | 10 | 10 |
| **Total** | **92** | **100** |

**Tier**: 1 (GO)
**Recommendation**: Highly validated target with multiple approved drugs. New programs should focus on resistance mechanisms or novel combinations.

---

## Example 2: KRAS Assessment

**Input**: `target="KRAS", disease="pancreatic cancer", modality="small molecule"`

### Phase 0: Target Disambiguation

| Identifier Type | Value |
|-----------------|-------|
| Gene Symbol | KRAS |
| UniProt Accession | P01116 |
| Ensembl Gene ID | ENSG00000133703 |
| ChEMBL Target ID | CHEMBL240 |
| Target Class | Small GTPase |

**Target Development Level**: Tclin (after sotorasib approval)

### Phase 8: Disease Association Scoring

| Sub-score | Points | Evidence |
|-----------|--------|----------|
| Genetic | 10/10 | 90% pancreatic cancers have KRAS mutations [T1]; pLI=0.99 [T3] |
| Literature | 10/10 | 1000+ publications [T4] |
| Pathway | 10/10 | OpenTargets score=0.95 [T3] |
| **Total** | **30/30** | |

### Phase 9: Druggability Assessment

| Sub-score | Points | Evidence |
|-----------|--------|----------|
| Structural | 7/10 | Structures available but shallow pockets; SM bucket=5 [T2] |
| Chemical | 7/10 | Sotorasib (G12C inhibitor) approved [T1]; limited non-G12C compounds [T2] |
| Target Class | 2/5 | Small GTPase - challenging historically [T2] |
| **Total** | **16/25** | |

**Note**: Druggability depends on mutation type. G12C tractable; G12D/G12V more challenging.

### Phase 10: Safety Deep Analysis

| Sub-score | Points | Evidence |
|-----------|--------|----------|
| Expression | 0/5 | Ubiquitous expression including critical tissues [T2] |
| Genetic | 0/10 | Mouse KO embryonic lethal [T1] |
| ADRs | 3/5 | Manageable: GI toxicity, liver enzyme elevation [T1] |
| **Total** | **3/20** | |

**Safety Flags**: Embryonic lethal; ubiquitous expression suggests on-target toxicity risk

### Phase 11: Clinical Precedent

| Score | Points | Evidence |
|-------|--------|----------|
| Clinical | 12/15 | Sotorasib approved for NSCLC (different disease) [T1] |

### Phase 12: Validation Evidence

| Sub-score | Points | Evidence |
|-----------|--------|----------|
| Functional | 5/5 | KRAS KO blocks tumor growth [T1] |
| Disease Models | 5/5 | PDX models with KRAS mutations respond [T1] |
| **Total** | **10/10** | |

### Composite Score

| Dimension | Score | Max |
|-----------|-------|-----|
| Disease Association | 30 | 30 |
| Druggability | 16 | 25 |
| Safety Profile | 3 | 20 |
| Clinical Precedent | 12 | 15 |
| Validation Evidence | 10 | 10 |
| **Total** | **71** | **100** |

**Tier**: 2 (CONDITIONAL GO)
**Recommendation**: Strong genetic validation. Safety concerns due to essentiality. G12C inhibitors validated; G12D/G12V require novel approaches. Consider tumor-selective delivery.

---

## Example 3: Novel Understudied Kinase

**Input**: `target="STK33", disease="auto-discovered", modality="all"`

### Phase 0: Target Disambiguation

| Identifier Type | Value |
|-----------------|-------|
| Gene Symbol | STK33 |
| UniProt Accession | Q9YHK6 |
| Ensembl Gene ID | ENSG00000124207 |
| ChEMBL Target ID | CHEMBL5765 |
| Target Class | Kinase (Serine/threonine) |

**Target Development Level**: Tdark (understudied)

### Auto-Discovered Diseases

| Rank | Disease | Score |
|------|---------|-------|
| 1 | Lung adenocarcinoma | 0.45 |
| 2 | Melanoma | 0.38 |
| 3 | Breast carcinoma | 0.31 |

### Phase 8: Disease Association Scoring

| Sub-score | Points | Evidence |
|-----------|--------|----------|
| Genetic | 2/10 | No significant GWAS; pLI=0.12 (tolerant) [T3] |
| Literature | 3/10 | 10-50 publications [T4] |
| Pathway | 4/10 | OpenTargets score=0.45 [T3] |
| **Total** | **9/30** | |

### Phase 9: Druggability Assessment

| Sub-score | Points | Evidence |
|-----------|--------|----------|
| Structural | 5/10 | AlphaFold only; predicted pockets [T4] |
| Chemical | 0/10 | No known ligands [T4] |
| Target Class | 5/5 | Kinase family [T1] |
| **Total** | **10/25** | |

### Phase 10: Safety Deep Analysis

| Sub-score | Points | Evidence |
|-----------|--------|----------|
| Expression | 5/5 | Testis-specific expression [T2] |
| Genetic | 5/10 | No KO data; low pLI suggests tolerance [T3] |
| ADRs | 5/5 | No known safety signals [T4] |
| **Total** | **15/20** | |

**Safety Flags**: None identified; testis-specific expression may offer therapeutic window

### Phase 11: Clinical Precedent

| Score | Points | Evidence |
|-------|--------|----------|
| Clinical | 0/15 | No clinical development [T4] |

### Phase 12: Validation Evidence

| Sub-score | Points | Evidence |
|-----------|--------|----------|
| Functional | 0/5 | No functional data in disease context [T4] |
| Disease Models | 0/5 | No model data [T4] |
| **Total** | **0/10** | |

### Composite Score

| Dimension | Score | Max |
|-----------|-------|-----|
| Disease Association | 9 | 30 |
| Druggability | 10 | 25 |
| Safety Profile | 15 | 20 |
| Clinical Precedent | 0 | 15 |
| Validation Evidence | 0 | 10 |
| **Total** | **34** | **100** |

**Tier**: 4 (NO-GO)
**Recommendation**: Limited validation. Target is understudied (Tdark). Consider:
1. Conduct CRISPR screen in disease-relevant cell lines
2. Develop chemical probe to enable target validation
3. Assess expression in larger patient cohorts
4. Explore synthetic lethality interactions

---

## Example 4: Antibody Target Assessment

**Input**: `target="PDL1", disease="melanoma", modality="antibody"`

### Modality-Specific Assessment

| Sub-score | Points | Evidence |
|-----------|--------|----------|
| Surface Accessibility | 10/10 | Transmembrane protein; extracellular domain well-characterized [T1] |
| Antibody Tractability | 10/10 | AB bucket=1; 3 approved antibodies [T1] |
| Expression Selectivity | 4/5 | Tumor-infiltrating immune cells; limited normal tissue [T2] |

### Composite Score (Antibody Modality)

| Dimension | Score | Max |
|-----------|-------|-----|
| Disease Association | 28 | 30 |
| Druggability (Ab-adjusted) | 22 | 25 |
| Safety Profile | 14 | 20 |
| Clinical Precedent | 15 | 15 |
| Validation Evidence | 8 | 10 |
| **Total** | **87** | **100** |

**Tier**: 1 (GO)
**Recommendation**: Excellent antibody target. Multiple approved antibodies validate tractability. Consider combination approaches.

---

## Example 5: PROTAC Target Assessment

**Input**: `target="BRD4", disease="acute myeloid leukemia", modality="PROTAC"`

### Modality-Specific Assessment

| Sub-score | Points | Evidence |
|-----------|--------|----------|
| Known Binders | 10/10 | Multiple BD1/BD2 binders with nM affinity [T1] |
| Surface Lysines | 8/10 | Multiple lysines near binding sites [T3] |
| Intracellular Location | 5/5 | Nuclear protein - accessible [T2] |

### Composite Score (PROTAC Modality)

| Dimension | Score | Max |
|-----------|-------|-----|
| Disease Association | 24 | 30 |
| Druggability (PROTAC-adjusted) | 21 | 25 |
| Safety Profile | 10 | 20 |
| Clinical Precedent | 7 | 15 |
| Validation Evidence | 8 | 10 |
| **Total** | **70** | **100** |

**Tier**: 2 (CONDITIONAL GO)
**Recommendation**: Good PROTAC target with validated binders. Multiple clinical PROTACs in development. Safety concerns due to essentiality - consider selective degradation approaches.

---

## Example 6: Gene Therapy Target Assessment

**Input**: `target="GAA", disease="Pompe disease", modality="gene_therapy"`

### Phase 0: Target Disambiguation

| Identifier Type | Value |
|-----------------|-------|
| Gene Symbol | GAA |
| UniProt Accession | P10253 |
| Ensembl Gene ID | ENSG00000171298 |
| Target Class | Enzyme (Lysosomal acid alpha-glucosidase) |

### Modality-Specific Assessment

| Sub-score | Points | Evidence |
|-----------|--------|----------|
| Tissue Promoter | 10/10 | Liver-specific promoter available for systemic delivery [T1] |
| AAV Tropism | 8/10 | AAV9 crosses BBB; AAV8 targets liver effectively [T1] |
| Immunogenicity | 6/10 | Pre-existing antibodies to GAA reported in some patients [T2] |

### Composite Score (Gene Therapy Modality)

| Dimension | Score | Max |
|-----------|-------|-----|
| Disease Association | 30 | 30 |
| Druggability (GT-adjusted) | 18 | 25 |
| Safety Profile | 18 | 20 |
| Clinical Precedent | 12 | 15 |
| Validation Evidence | 9 | 10 |
| **Total** | **87** | **100** |

**Tier**: 1 (GO)
**Recommendation**: Excellent gene therapy target. ERT (enzyme replacement therapy) validates target; gene therapy offers improved tissue distribution and reduced immunogenicity.

---

## Example 7: RNA Therapeutic Target Assessment

**Input**: `target="PCSK9", disease="hypercholesterolemia", modality="rna_therapeutic"`

### Modality-Specific Assessment

| Sub-score | Points | Evidence |
|-----------|--------|----------|
| Sequence Accessibility | 8/10 | siRNA designs published; accessible target site identified [T1] |
| Off-target Potential | 7/10 | Low homology family; some cross-reactivity possible [T2] |
| Tissue Accessibility | 10/10 | Liver-expressed; GalNAc conjugation validated [T1] |

### Composite Score (RNA Therapeutic Modality)

| Dimension | Score | Max |
|-----------|-------|-----|
| Disease Association | 28 | 30 |
| Druggability (RNA-adjusted) | 20 | 25 |
| Safety Profile | 16 | 20 |
| Clinical Precedent | 15 | 15 |
| Validation Evidence | 8 | 10 |
| **Total** | **87** | **100** |

**Tier**: 1 (GO)
**Recommendation**: Validated RNA therapeutic target (inclisiran approved). Strong genetic validation from LOF mutations. Liver accessibility enables GalNAc conjugation.

---

## Example 8: Cell Therapy Target Assessment

**Input**: `target="CD19", disease="B-cell lymphoma", modality="cell_therapy"`

### Modality-Specific Assessment

| Sub-score | Points | Evidence |
|-----------|--------|----------|
| Tumor Specificity | 10/10 | Expressed on B-cells and B-cell malignancies; not on vital organs [T1] |
| Exhaustion Resistance | 7/10 | CD19 CAR-T shows durable responses; some relapse reported [T2] |
| Heterogeneity | 6/10 | CD19 loss variants identified in 10-20% of relapses [T2] |

### Composite Score (Cell Therapy Modality)

| Dimension | Score | Max |
|-----------|-------|-----|
| Disease Association | 28 | 30 |
| Druggability (CT-adjusted) | 22 | 25 |
| Safety Profile | 15 | 20 |
| Clinical Precedent | 15 | 15 |
| Validation Evidence | 9 | 10 |
| **Total** | **89** | **100** |

**Tier**: 1 (GO)
**Recommendation**: Benchmark CAR-T target with 6 FDA-approved products. Consider bispecific or dual-target approaches to address CD19-negative relapse.

---

## Example 9: ADC Target Assessment

**Input**: `target="HER2", disease="breast cancer", modality="adc"`

### Modality-Specific Assessment

| Sub-score | Points | Evidence |
|-----------|--------|----------|
| Internalization Rate | 10/10 | Rapid internalization documented; enhanced by trastuzumab binding [T1] |
| Tumor Selectivity | 8/10 | HER2+ tumors show high expression; low normal tissue [T1] |
| Shed Antigen | 4/10 | Circulating HER2 extracellular domain detected [T2] |

### Composite Score (ADC Modality)

| Dimension | Score | Max |
|-----------|-------|-----|
| Disease Association | 28 | 30 |
| Druggability (ADC-adjusted) | 23 | 25 |
| Safety Profile | 14 | 20 |
| Clinical Precedent | 15 | 15 |
| Validation Evidence | 9 | 10 |
| **Total** | **89** | **100** |

**Tier**: 1 (GO)
**Recommendation**: Validated ADC target (T-DM1, T-DXd approved). High internalization rate supports payload delivery. Consider next-gen payloads for resistance.

---

## Example Reports with Visualizations

### EGFR Full Report - Executive Summary Visualization

```
    VALIDATION SCORE BREAKDOWN
    ========================================
    Disease Association  [████████████████████] 28/30 (93%)
    Druggability         [████████████████████] 25/25 (100%)
    Safety Profile       [████████████        ] 12/20 (60%)
    Clinical Precedent   [████████████████████] 15/15 (100%)
    Validation Evidence  [████████████████████] 10/10 (100%)
    ========================================
    TOTAL: 90/100 | TIER 1 | RECOMMENDATION: GO


    TISSUE EXPRESSION HEATMAP
    ========================================
    Lung          [████████████████████] 120 | DISEASE-RELEVANT
    Liver         [████████████████    ]  96 | *CRITICAL*
    Kidney        [███████████         ]  68 | *CRITICAL*
    Heart         [████████            ]  48 | *CRITICAL*
    Brain         [████                ]  24 | *CRITICAL*
    Bone Marrow   [██                  ]  12 | *CRITICAL*
    Skin          [████████████        ]  72 | ADR-RELATED
    ========================================


    CLINICAL DEVELOPMENT TIMELINE
    ========================================
    2003 |--[Gefitinib]----| FDA Approved (NSCLC)
    2004 |--[Erlotinib]----| FDA Approved (NSCLC)
    2013 |--[Afatinib]-----| FDA Approved (NSCLC)
    2015 |--[Osimertinib]--| FDA Approved (NSCLC)
    2020 |--[Amivantamab]--| FDA Approved (NSCLC)
    2021 |--[Mobocertinib]-| FDA Approved (NSCLC)
    ========================================
    Total: 6 FDA-approved drugs | First approval: 2003


    MODALITY COMPARISON
    ========================================
    Small Molecule    [████████████████████] 92/100 | BEST MATCH
    Antibody          [███████████████████ ] 88/100 |
    ADC               [██████████████████  ] 85/100 |
    PROTAC            [█████████████████   ] 80/100 |
    Bispecific        [██████████████████  ] 86/100 |
    Gene Therapy      [████████████        ] 60/100 |
    RNA Therapeutic   [██████████████      ] 70/100 |
    ========================================
    Recommended: Small Molecule (existing approvals) or Bispecific (differentiation)
```

### STK33 Understudied Kinase - Visualization

```
    VALIDATION SCORE BREAKDOWN
    ========================================
    Disease Association  [██████              ]  9/30 (30%)
    Druggability         [████████            ] 10/25 (40%)
    Safety Profile       [███████████████     ] 15/20 (75%)
    Clinical Precedent   [                    ]  0/15 (0%)
    Validation Evidence  [                    ]  0/10 (0%)
    ========================================
    TOTAL: 34/100 | TIER 4 | RECOMMENDATION: NO-GO


    DATA GAPS IDENTIFIED
    ========================================
    Section              | Expected  | Actual    | Gap
    ---------------------|-----------|-----------|------------------
    Disease Association  | >0.7      | 0.45      | Weak evidence
    Chemical Matter      | Compounds | None      | No known ligands
    Functional Studies   | Validated | None      | Unstudied
    Clinical Pipeline    | Active    | None      | Tdark target
    ========================================


    RECOMMENDED VALIDATION EXPERIMENTS
    ========================================
    Priority | Experiment                          | Timeline
    ---------|-------------------------------------|----------
    HIGH     | CRISPR screen in cancer cell lines  | 2-3 months
    HIGH     | Kinase activity assay development   | 1-2 months
    MEDIUM   | Chemical probe development          | 6-12 months
    LOW      | Mouse KO phenotype analysis         | 3-6 months
    ========================================
```