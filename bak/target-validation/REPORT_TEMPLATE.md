# Target Validation Report Template

Full report template with all sections, completeness checklist, and section-specific guidance.

---

## Report Template

```markdown
# Target Validation Report: [FULL PROTEIN NAME]

**Generated**: [Date] | **Query**: [Original query] | **Completeness**: [X/14 phases]

---

## Executive Summary

### Target Validation Scorecard

| Dimension | Score | Max |
|-----------|-------|-----|
| Disease Association | [XX] | 30 |
| Druggability | [XX] | 25 |
| Safety Profile | [XX] | 20 |
| Clinical Precedent | [XX] | 15 |
| Validation Evidence | [XX] | 10 |
| **Total** | **[XX]** | **100** |

**Priority Tier**: [Tier 1-4]
**GO/NO-GO Recommendation**: [Recommendation]

### Key Findings

1. [Finding 1 with evidence tier]
2. [Finding 2 with evidence tier]
3. [Finding 3 with evidence tier]

### Critical Risks

- [Risk 1]
- [Risk 2]

---

## Part A: Target Intelligence

---

## 1. Target Identifiers

| Identifier Type | Value | Database |
|-----------------|-------|----------|
| Gene Symbol | [SYMBOL] | HGNC |
| UniProt Accession | [P#####] | UniProtKB |
| Ensembl Gene ID | [ENSG###] | Ensembl |
| Entrez Gene ID | [#####] | NCBI Gene |
| ChEMBL Target ID | [CHEMBL###] | ChEMBL |
| HGNC ID | [HGNC:####] | HGNC |

**Aliases**: [List all known aliases/synonyms]

---

## 2. Basic Information

### 2.1 Protein Description
- **Recommended Name**: [Full protein name]
- **Alternative Names**: [List]
- **Gene Name**: [Symbol] ([Full gene name])
- **Organism**: [Species] (Taxonomy ID: [####])
- **Protein Length**: [###] amino acids
- **Molecular Weight**: [###] kDa
- **Isoforms**: [Number] known isoforms

### 2.2 Protein Function
[Detailed description of protein function - at least 3-4 sentences]

### 2.3 Subcellular Localization
- **Primary Location**: [e.g., Plasma membrane]
- **Additional Locations**: [List]
- **Topology**: [e.g., Single-pass type I membrane protein]

---

## 3. Structural Biology

### 3.1 Experimental Structures (PDB)

| PDB ID | Resolution | Method | Ligand | Description |
|--------|------------|--------|--------|-------------|
| [####] | [#.#Å] | [X-ray/Cryo-EM/NMR] | [Ligand or Apo] | [Brief description] |

**Total PDB Entries**: [###]
**Best Resolution**: [#.#Å] ([PDB ID])
**Structure Coverage**: [Complete/Partial - which domains?]

### 3.2 AlphaFold Prediction
- **Available**: [Yes/No]
- **Confidence**: [High/Medium/Low - pLDDT scores]
- **Model URL**: [AlphaFold DB link]

### 3.3 Domain Architecture

| Domain | Position | InterPro ID | Description |
|--------|----------|-------------|-------------|
| [Domain name] | [Start-End] | [IPR######] | [Function] |

### 3.4 Key Structural Features
- **Active Sites**: [List with positions]
- **Binding Sites**: [List - substrate, cofactor, drug binding]
- **PTM Sites**: [Phosphorylation, glycosylation, etc.]

### 3.5 Structural Druggability Assessment
- **Binding Pockets**: [Identified pockets suitable for small molecules]
- **Allosteric Sites**: [Known or predicted]
- **Antibody Epitopes**: [Surface accessibility for biologics]

---

## 4. Function & Pathways

### 4.1 Gene Ontology Annotations

**Molecular Function (MF)**:
| GO Term | GO ID | Evidence |
|---------|-------|----------|
| [Term] | [GO:#######] | [IDA/IEA/etc.] |

**Biological Process (BP)**:
| GO Term | GO ID | Evidence |
|---------|-------|----------|
| [Term] | [GO:#######] | [IDA/IEA/etc.] |

**Cellular Component (CC)**:
| GO Term | GO ID | Evidence |
|---------|-------|----------|
| [Term] | [GO:#######] | [IDA/IEA/etc.] |

### 4.2 Pathway Involvement

| Pathway | Database | Pathway ID |
|---------|----------|------------|
| [Pathway name] | [Reactome/KEGG/WikiPathways] | [ID] |

### 4.3 Functional Summary
[Paragraph describing the target's role in cellular signaling, disease mechanisms, and biological importance]

---

## 5. Protein-Protein Interactions

### 5.1 Interaction Network Summary
- **Total Interactors (STRING, score >0.7)**: [###]
- **Experimentally Validated (IntAct)**: [###]
- **Complex Membership**: [List complexes]

### 5.2 Top Interacting Partners

| Partner | Score | Interaction Type | Evidence | Biological Context |
|---------|-------|------------------|----------|-------------------|
| [Gene] | [0.###] | [Physical/Functional] | [Experimental/Predicted] | [Context] |

### 5.3 Protein Complexes

| Complex Name | Members | Function |
|--------------|---------|----------|
| [Complex] | [List] | [Function] |

---

## 6. Expression Profile

### 6.1 Tissue Expression (GTEx/HPA)

| Tissue | Expression Level (TPM) | Specificity |
|--------|------------------------|-------------|
| [Tissue] | [###] | [High/Medium/Low] |

**Tissue Specificity Score**: [Score] ([Broadly expressed/Tissue-specific/Tissue-enriched])

### 6.2 Cell Type Expression
[Single-cell data if available]

### 6.3 Disease-Relevant Expression

| Cancer/Disease | Expression Change | Prognostic Value |
|----------------|-------------------|------------------|
| [Disease] | [Up/Down/Unchanged] | [Favorable/Unfavorable/None] |

---

## 7. Genetic Variation & Disease

### 7.1 Genetic Constraint Scores

| Metric | Value | Interpretation |
|--------|-------|----------------|
| pLI | [0.##] | [Highly constrained/Tolerant] |
| LOEUF | [0.##] | [Interpretation] |
| Missense Z-score | [#.##] | [Interpretation] |
| pRec | [0.##] | [Interpretation] |

### 7.2 Disease Associations (Open Targets)

| Disease | Association Score | Evidence Types | EFO ID |
|---------|-------------------|----------------|--------|
| [Disease] | [0.##] | [Genetic/Literature/etc.] | [EFO_#######] |

### 7.3 Pathogenic Variants (ClinVar)

#### Single Nucleotide Variants (SNVs)
| Variant | Clinical Significance | Condition | Review Status |
|---------|----------------------|-----------|---------------|
| [p.XXX###YYY] | [Pathogenic/Likely pathogenic] | [Condition] | [Stars] |

**Total Pathogenic SNVs**: [###]

#### Copy Number Variants (CNVs)
| Type | Region | Clinical Significance | Frequency |
|------|--------|----------------------|-----------|
| [Amplification/Deletion] | [Region] | [Significance] | [Frequency] |

### 7.4 Cancer Mutations (COSMIC/cBioPortal)

| Mutation | Frequency | Cancer Types | Functional Impact |
|----------|-----------|--------------|-------------------|
| [Mutation] | [#%] | [Cancers] | [Activating/Inactivating/Unknown] |

---

## Part B: Validation Assessment

---

## 8. Disease Association Scoring (0-30 pts)

### 8.1 Genetic Evidence (0-10)

| Evidence Type | Points | Source |
|---------------|--------|--------|
| GWAS associations | [X/6] | GWAS Catalog |
| Rare variants | [X/2] | ClinVar |
| Somatic mutations | [X/2] | cBioPortal |
| Constraint scores | [X/3] | gnomAD |

**Genetic Evidence Score**: [X/10]

### 8.2 Literature Evidence (0-10)

| Metric | Value | Points |
|--------|-------|--------|
| Total target+disease publications | [###] | [X/10] |
| Recent 5-year trend | [Increasing/Stable/Declining] | - |

**Literature Evidence Score**: [X/10]

### 8.3 Pathway Evidence (0-10)

| Disease | OpenTargets Score | Points |
|---------|-------------------|--------|
| [Disease] | [0.##] | [X/10] |

**Pathway Evidence Score**: [X/10]

**Total Disease Association Score**: [X/30]

---

## 9. Druggability Assessment (0-25 pts)

### 9.1 Structural Tractability (0-10)

| Structure Source | Quality | Points |
|------------------|---------|--------|
| PDB structures | [Count, best resolution] | [X] |
| AlphaFold | [pLDDT confidence] | [X] |
| Binding pockets | [Number, quality] | [X] |

**Structural Tractability Score**: [X]/10

### 9.2 Chemical Matter (0-10)

| Source | Compound Count | Best Affinity | Points |
|--------|----------------|---------------|--------|
| ChEMBL | [###] | [IC50/Ki] | [X] |
| BindingDB | [###] | [Ki/Kd] | [X] |
| PubChem BioAssay | [###] | [IC50] | [X] |

**Chemical Matter Score**: [X]/10

### 9.3 Target Class Bonus (0-5)

| Target Class | Points | Rationale |
|--------------|--------|-----------|
| [Class] | [X/5] | [Reason] |

### 9.4 Modality-Specific Tractability

| Modality | Tractability | Bucket | Evidence |
|----------|--------------|--------|----------|
| Small Molecule | [Yes/No] | [1-10] | [Evidence] |
| Antibody | [Yes/No] | [1-10] | [Evidence] |
| PROTAC | [Yes/No] | [1-10] | [Evidence] |

**Total Druggability Score**: [X]/25

---

## 10. Safety Deep Analysis (0-20 pts)

### 10.1 Tissue Expression Selectivity (0-5)

| Critical Tissue | Expression Level | Risk Level |
|-----------------|------------------|------------|
| Heart | [High/Med/Low/None] | [Risk] |
| Liver | [High/Med/Low/None] | [Risk] |
| Kidney | [High/Med/Low/None] | [Risk] |
| Brain | [High/Med/Low/None] | [Risk] |
| Bone Marrow | [High/Med/Low/None] | [Risk] |

**Expression Selectivity Score**: [X]/5

### 10.2 Genetic Validation (0-10)

| Model | Phenotype | Viability | Points |
|-------|-----------|-----------|--------|
| Mouse KO (IMPC) | [Phenotype] | [Viable/Lethal] | [X] |
| Human genetics (pLI) | [Value] | [Interpretation] | [X] |

**Genetic Validation Score**: [X]/10

### 10.3 Known Adverse Events (0-5)

| Adverse Event | Frequency | Drug Class | Mechanism |
|---------------|-----------|------------|-----------|
| [Event] | [Common/Uncommon/Rare] | [Class] | [On-target/Off-target] |

**ADR Score**: [X]/5

### 10.4 Safety Liabilities Summary

| Safety Concern | Evidence | Severity | Organ System |
|----------------|----------|----------|--------------|
| [Concern] | [Animal/Human/Both] | [High/Medium/Low] | [System] |

**Total Safety Score**: [X]/20

---

## 11. Clinical Precedent (0-15 pts)

### 11.1 Approved Drugs

| Drug Name | Brand Name | Mechanism | Indication | Approval Year |
|-----------|------------|-----------|------------|---------------|
| [Drug] | [Brand] | [Inhibitor/Agonist/etc.] | [Indication] | [Year] |

### 11.2 Clinical Pipeline

| Drug | Phase | Indication | Trial Count | Status |
|------|-------|------------|-------------|--------|
| [Drug] | [Phase I/II/III] | [Indication] | [###] | [Active/Completed] |

**Total Clinical Trials**: [###]

### 11.3 Clinical Precedent Score

| Stage | Points |
|-------|--------|
| [Highest stage] | [X/15] |

**Total Clinical Precedent Score**: [X]/15

---

## 12. Validation Evidence (0-10 pts)

### 12.1 Functional Studies (0-5)

| Study Type | Result | Evidence Tier | Points |
|------------|--------|---------------|--------|
| CRISPR KO | [Phenotype] | T1/T2 | [X] |
| siRNA | [Phenotype] | T2 | [X] |
| Biochemical | [Result] | T2 | [X] |

**Functional Studies Score**: [X]/5

### 12.2 Disease Models (0-5)

| Model Type | Result | Evidence Tier | Points |
|------------|--------|---------------|--------|
| PDX | [Response] | T1 | [X] |
| GEMM | [Phenotype] | T2 | [X] |
| Cell line | [Result] | T3 | [X] |

**Disease Models Score**: [X]/5

**Total Validation Evidence Score**: [X]/10

---

## 13. Validation Scorecard

### Composite Score Summary

| Dimension | Score | Max | Percentage |
|-----------|-------|-----|------------|
| Disease Association | [XX] | 30 | [XX%] |
| Druggability | [XX] | 25 | [XX%] |
| Safety Profile | [XX] | 20 | [XX%] |
| Clinical Precedent | [XX] | 15 | [XX%] |
| Validation Evidence | [XX] | 10 | [XX%] |
| **Total** | **[XX]** | **100** | **[XX%]** |

### Priority Tier Assignment

**Tier**: [1-4]
**Recommendation**: [GO/CONDITIONAL GO/CAUTION/NO-GO]

### Modality-Specific Assessment

| Modality | Adjusted Score | Tier | Notes |
|----------|---------------|------|-------|
| Small Molecule | [XX] | [Tier] | [Notes] |
| Antibody | [XX] | [Tier] | [Notes] |
| PROTAC | [XX] | [Tier] | [Notes] |

---

## Part C: Synthesis & Recommendations

---

## 14. Validation Roadmap

### Recommended Validation Experiments

| Priority | Experiment | Rationale | Expected Timeline |
|----------|------------|-----------|-------------------|
| HIGH | [Experiment] | [Why needed] | [Timeline] |
| MEDIUM | [Experiment] | [Why needed] | [Timeline] |
| LOW | [Experiment] | [Why needed] | [Timeline] |

### Data Gaps to Address

| Gap | Recommended Action | Priority |
|-----|-------------------|----------|
| [Gap] | [Action] | [Priority] |

---

## 15. Tool Compounds for Testing

### Recommended Tool Compounds

| Compound | Affinity | Selectivity | Source | Recommended Use |
|----------|----------|-------------|--------|-----------------|
| [Compound] | [IC50/Ki] | [Selectivity profile] | [Database] | [Use case] |

### Chemical Probes

| Probe | Selectivity | Use | Source |
|-------|-------------|-----|--------|
| [Probe] | [Selective/Broad] | [Recommended use] | [Source] |

---

## 16. Biomarker Strategy

### Predictive Biomarkers

| Biomarker | Type | Assay | Clinical Utility |
|-----------|------|-------|------------------|
| [Biomarker] | [Genomic/Protein/etc.] | [Assay type] | [Utility] |

### Pharmacodynamic Markers

| Marker | Readout | Sample Type | Timepoint |
|--------|---------|-------------|-----------|
| [Marker] | [Readout] | [Sample] | [Timepoint] |

---

## 17. Key Risks & Mitigations

### Risk Assessment

| Risk Category | Risk | Probability | Impact | Mitigation Strategy |
|---------------|------|-------------|--------|---------------------|
| Safety | [Risk] | [High/Med/Low] | [High/Med/Low] | [Mitigation] |
| Efficacy | [Risk] | [High/Med/Low] | [High/Med/Low] | [Mitigation] |
| Competition | [Risk] | [High/Med/Low] | [High/Med/Low] | [Mitigation] |

### Key Strengths

1. [Strength 1]
2. [Strength 2]
3. [Strength 3]

### Key Challenges

1. [Challenge 1]
2. [Challenge 2]
3. [Challenge 3]

---

## Section-Specific Guidance

### Executive Summary
**Purpose**: Give reader the key takeaways in 30 seconds

Include:
1. What the target IS (protein class, function)
2. Clinical relevance (disease associations)
3. Druggability status (has drugs? tractable?)
4. One-line recommendation with score

### Section 3: Structural Biology
**Purpose**: Enable structure-based drug design decisions

Must include:
- Total PDB count and best resolution
- Coverage (which domains have structures?)
- AlphaFold availability and confidence
- Complete domain list with positions
- Key binding sites for drug design

### Section 10: Safety Deep Analysis
**Purpose**: Identify safety risks early

Must include:
- Expression in ALL critical tissues (heart, liver, kidney, brain, bone marrow)
- Mouse KO phenotype (if available)
- Known ADRs from approved drugs
- Paralog risks for selectivity

### Section 14: Validation Roadmap
**Purpose**: Provide actionable next steps

Requirements:
- Use priority levels (HIGH/MEDIUM/LOW)
- Each recommendation must be actionable
- Include timeline estimates
- Address identified data gaps

---

## Visualization Requirements

Reports must include ASCII visualizations for key data. These visualizations improve readability and allow quick comprehension of complex data.

### 1. Validation Score Visualization

Display the composite score as a visual bar chart:

```
    Validation Score Breakdown
    ========================================
    Disease Association  [████████████████████] 28/30 (93%)
    Druggability         [███████████████████ ] 24/25 (96%)
    Safety Profile       [████████████        ] 12/20 (60%)
    Clinical Precedent   [████████████████████] 15/15 (100%)
    Validation Evidence  [█████████████████   ]  9/10 (90%)
    ========================================
    TOTAL: 88/100 | TIER 1 | RECOMMENDATION: GO
```

### 2. Tissue Expression Heatmap

Show expression levels across tissues with critical tissue highlighting:

```
    Tissue Expression Profile (TPM)
    ========================================
    Lung          [████████████████████] 120 | Disease-relevant
    Liver         [████████████████    ]  96 | CRITICAL TISSUE
    Kidney        [███████████         ]  68 | CRITICAL TISSUE
    Heart         [████████            ]  48 | CRITICAL TISSUE
    Brain         [████                ]  24 | CRITICAL TISSUE
    Bone Marrow   [██                  ]  12 | CRITICAL TISSUE
    Skin          [████████████        ]  72
    Intestine     [██████              ]  36
    ========================================
    Expression Threshold: Low <20 | Medium 20-50 | High >50 TPM
    Critical Tissues: Heart, Liver, Kidney, Brain, Bone Marrow
```

### 3. Disease Association Bar Chart

Visualize top disease associations:

```
    Top Disease Associations (Score)
    ========================================
    NSCLC           [████████████████████] 0.95 | [T1] Strong evidence
    Glioblastoma    [████████████████    ] 0.82 | [T2] Good evidence
    Colorectal      [█████████████████   ] 0.71 | [T3] Moderate evidence
    Head & Neck     [█████████████       ] 0.55 | [T3] Moderate evidence
    Ovarian         [██████████          ] 0.42 | [T4] Limited evidence
    ========================================
    Score Threshold: Strong >0.7 | Moderate 0.4-0.7 | Weak <0.4
```

### 4. Clinical Development Timeline

Show clinical precedent over time:

```
    Clinical Development Timeline
    ========================================
    2003 |--[Drug1]--| FDA Approved (NSCLC)
    2004 |--[Drug2]--| FDA Approved (NSCLC)
    2013 |--[Drug3]--| FDA Approved (NSCLC)
    2015 |--[Drug4]--| FDA Approved (NSCLC)
    2020 |--[Drug5]--| FDA Approved (NSCLC)
    ========================================
    Total: 5 FDA-approved drugs | First approval: 2003
```

---

## Interpretation Requirements

Every data section must include interpretation that connects findings to validation decisions. DO NOT simply list data without context.

### Required Interpretation Elements

**1. What the data means**:
- Explain significance of findings
- Compare to benchmark targets
- Identify implications for drug development

**2. How it affects validation**:
- Impact on scoring
- Risk considerations
- Opportunities identified

**3. Recommended actions**:
- Next steps justified by data
- Gaps to address
- Experiments to prioritize
```