# Target Validation - Evidence Grading

Evidence grading system and completeness requirements for target validation reports.

---

## Evidence Tiers

| Tier | Symbol | Criteria | Examples |
|------|--------|----------|----------|
| **T1** | [T1] | Direct mechanistic evidence, human clinical proof | CRISPR KO in patients, FDA-approved drug mechanism, crystal structure with mechanism, patient mutation with functional validation |
| **T2** | [T2] | Functional studies, model organism validation | siRNA phenotype, mouse KO, biochemical assay, CRISPR screen hit |
| **T3** | [T3] | Association, screen hits, computational prediction | GWAS hit, DepMap essentiality, expression correlation, eQTL |
| **T4** | [T4] | Mention, review, text-mined, predicted | Review article, database annotation, computational prediction, homology inference |

---

## Tier Assignment Guidelines

### T1 ([T1]) - Clinical/Mechanistic Proof

Assign T1 when evidence directly demonstrates:
- Human clinical validation (FDA-approved drug for target)
- Patient mutations with proven functional impact
- Crystal structure with mechanism-validated binding
- CRISPR KO in human patients showing phenotype
- Biomarker validated in prospective clinical trial

**Citation format**:
```markdown
EGFR mutations cause lung adenocarcinoma [[T1]: PMID:15118125, activating mutations
in patients with functional validation]. *Source: ClinVar, CIViC*
```

### T2 ([T2]) - Functional Validation

Assign T2 when evidence shows:
- siRNA knockdown with phenotype in disease-relevant cells
- Mouse knockout with relevant phenotype
- Biochemical assay validating mechanism
- CRISPR screen hit with validation
- Animal model response to target modulation

**Citation format**:
```markdown
EGFR knockout reduces tumor growth in mouse xenograft models [[T2]: PMID:12345678,
CRISPR KO in A549 xenografts]. *Source: DepMap, Literature*
```

### T3 ([T3]) - Association/Computational

Assign T3 when evidence shows:
- GWAS association with disease
- DepMap essentiality score
- Expression correlation with disease
- eQTL linking target to disease
- Text-mined association from databases

**Citation format**:
```markdown
EGFR amplification associated with glioblastoma [[T3]: TCGA, 40% amplification rate].
*Source: cBioPortal*
```

### T4 - Mention/Predicted

Assign T4 when evidence is:
- Review article mentioning target-disease link
- Database annotation without validation
- Computational prediction (AlphaFold, docking)
- Homology-based inference
- Text-mined relationship

**Citation format**:
```markdown
EGFR implicated in breast cancer progression [[T4]: Review article, PMID:11111111].
*Source: PubMed*
```

---

## Required Evidence Grading Locations

Evidence grades MUST appear in:

1. **Executive Summary** - Key disease claims graded
2. **Section 8 (Disease Associations)** - Every disease link graded with source type
3. **Section 10 (Safety)** - Safety claims graded
4. **Section 12 (Literature)** - Key papers table with evidence tier
5. **Section 14 (Recommendations)** - Actions reference evidence quality

---

## Per-Section Evidence Summary Format

At the end of each major section, add evidence summary:

```markdown
---
**Evidence Quality for this Section**: Strong
- Mechanistic (T1): 12 papers
- Functional (T2): 8 papers
- Association (T3): 15 papers
- Mention (T4): 23 papers
**Data Gaps**: No CRISPR data; mouse KO phenotypes limited
---
```

---

## ClinVar SNV vs CNV Separation

Always separate single nucleotide variants from copy number variants:

```markdown
### 7.3 Clinical Variants (ClinVar)

#### Single Nucleotide Variants (SNVs)
| Variant | Clinical Significance | Condition | Review Status | PMID |
|---------|----------------------|-----------|---------------|------|
| p.L858R | Pathogenic | Lung cancer | 4 stars | 15118125 |

**Total Pathogenic SNVs**: 47

#### Copy Number Variants (CNVs) - Reported Separately
| Type | Region | Clinical Significance | Frequency |
|------|--------|----------------------|-----------|
| Amplification | 7p11.2 | Pathogenic | Common in cancer |

*Note: CNV data separated as it represents different mutation mechanism*
```

---

## DisGeNET Evidence Tier Assignment

Based on DisGeNET score:

| DisGeNET Score | Evidence Tier | Rationale |
|----------------|---------------|-----------|
| >= 0.7 | T2 | Multiple validated sources |
| 0.4 - 0.7 | T3 | Moderate evidence |
| < 0.4 | T4 | Limited evidence |

---

## Open Targets Evidence Types

Map Open Targets evidence types to tiers:

| Evidence Type | Tier | Rationale |
|---------------|------|-----------|
| Genetic_association | T2-T3 | Depends on study type |
| Somatic_mutation | T2 | Cancer driver evidence |
| Known_drug | T1 | Clinical validation |
| RNA_expression | T3 | Association |
| Animal_model | T2 | Functional validation |
| Affected_pathway | T3 | Computational |

---

## Minimum Data Requirements

| Section | Minimum Data | If Not Met |
|---------|--------------|------------|
| **5. PPIs** | >= 20 interactors | Document which tools failed + why |
| **6. Expression** | Top 10 tissues with TPM + HPA RNA summary | Note "limited data" with specific gaps |
| **7. Disease** | Top 10 OT diseases + gnomAD constraints + ClinVar summary | Separate SNV/CNV; note if constraint unavailable |
| **9. Druggability** | OT tractability + probes + drugs + DGIdb + GtoPdb fallback | "No drugs/probes" is valid data |
| **11. Literature** | Total count + 5-year trend + 3-5 key papers with evidence tiers | Note if sparse (<50 papers) |

---

## Completeness Audit Checklist

Before finalizing the report, verify ALL items:

### Data Minimums Check
- [ ] PPIs: >= 20 interactors OR explanation why fewer
- [ ] Expression: Top 10 tissues with values OR explicit "unavailable"
- [ ] Diseases: Top 10 associations with scores OR "no associations"
- [ ] Constraints: All 4 scores (pLI, LOEUF, missense Z, pRec) OR "unavailable"
- [ ] Druggability: All modalities assessed; probes + drugs listed OR "none"

### Negative Results Documented
- [ ] Empty tool results noted explicitly (not left blank)
- [ ] Failed tools with fallbacks documented
- [ ] "No data" sections have implications noted

### Evidence Quality
- [ ] T1-T4 grades in Executive Summary disease claims
- [ ] T1-T4 grades in Disease Associations table
- [ ] Key papers table has evidence tiers
- [ ] Per-section evidence summaries included

### Source Attribution
- [ ] Every data point has source tool/database cited
- [ ] Section-end source summaries present

---

## Data Gap Table Template

When minimums not met, document in report:

```markdown
## Appendix C: Data Gaps & Limitations

| Section | Expected Data | Actual | Reason | Alternative Source |
|---------|---------------|--------|--------|-------------------|
| 5. PPIs | >= 20 interactors | 8 | Novel target, limited studies | Literature review needed |
| 6. Expression | GTEx TPM | None | Versioned ID not recognized | See HPA data |
| 9. Probes | Chemical probes | None | No validated probes exist | Consider tool compound dev |

**Recommendations for Data Gaps**:
1. For PPIs: Query BioGRID with broader parameters; check yeast-2-hybrid studies
2. For Expression: Query GEO directly for tissue-specific datasets
```

---

## Scoring Impact of Evidence Tiers

Evidence tier affects scoring confidence:

| Score Component | High Confidence (T1/T2) | Medium (T3) | Low (T4) |
|-----------------|------------------------|-------------|----------|
| Disease Association | Full points | 70% points | 40% points |
| Druggability | Full points | 70% points | 50% points |
| Safety | Full points | 80% points | 60% points |
| Clinical Precedent | Full points | Full points | N/A |
| Validation Evidence | Full points | 70% points | 30% points |

---

## Example Evidence Summary

```markdown
### 7.2 Disease Associations (Open Targets)

| Disease | Association Score | Evidence Types | EFO ID | Evidence Tier |
|---------|-------------------|----------------|--------|---------------|
| Non-small cell lung cancer | 0.95 | Known_drug, Somatic_mutation | EFO_0003060 | [T1] |
| Glioblastoma | 0.82 | Somatic_mutation, Genetic_association | EFO_0000519 | [T2] |
| Colorectal carcinoma | 0.71 | RNA_expression, Genetic_association | EFO_0000518 | [T3] |

---
**Evidence Quality for this Section**: Strong
- Mechanistic (T1): 2 diseases (NSCLC with approved drugs)
- Functional (T2): 3 diseases (somatic mutation validated)
- Association (T3): 5 diseases (expression/GWAS)
- Mention (T4): 12 diseases (text-mined)
**Data Gaps**: No rare variant evidence; GWAS limited to cancer types
---
```