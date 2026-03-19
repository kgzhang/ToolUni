# Target Validation Report Template

This template defines the comprehensive report format for target validation reports, combining target intelligence and validation assessment into a unified structure.

---

## Report Structure Overview

```
Part A: Executive Summary
  1. Executive Summary
     - Validation Scorecard
     - Key Findings
     - Critical Risks
     - Recommendation

Part B: Target Intelligence
  2. Target Identifiers
  3. Basic Information
  4. Structural Biology
  5. Function & Pathways
  6. Protein-Protein Interactions
  7. Expression Profile
  8. Genetic Variation & Disease

Part C: Validation Assessment
  9. Disease Association Scoring (0-30 pts)
  10. Druggability Assessment (0-25 pts)
  11. Safety Deep Analysis (0-20 pts)
  12. Clinical Precedent (0-15 pts)
  13. Validation Evidence (0-10 pts)
  14. Validation Scorecard

Part D: Synthesis & Recommendations
  15. Validation Roadmap
  16. Tool Compounds for Testing
  17. Biomarker Strategy
  18. Key Risks & Mitigations

Appendices
  A. Data Sources & Methodology
  B. Completeness Checklist
  C. Data Gaps & Limitations
  D. Structured Data Export
```

---

## Complete Report Template

```markdown
# Target Validation Report: [FULL PROTEIN NAME]

**Generated**: [Date] | **Query**: [Original query] | **Completeness**: [X/14 phases]

---

## 1. Executive Summary

[2-3 sentence overview covering: what the target is, primary function, druggability status, and key clinical relevance]

**Bottom Line**: [One sentence: Is this a good drug target? Why/why not?]

### Target Validation Scorecard

| Dimension | Score | Max | Percentage | Evidence |
|-----------|-------|-----|------------|----------|
| Disease Association | [XX] | 30 | [XX%] | ★★★/★★/★ |
| Druggability | [XX] | 25 | [XX%] | ★★★/★★/★ |
| Safety Profile | [XX] | 20 | [XX%] | ★★★/★★/★ |
| Clinical Precedent | [XX] | 15 | [XX%] | ★★★/★★/★ |
| Validation Evidence | [XX] | 10 | [XX%] | ★★★/★★/★ |
| **TOTAL** | **[XX]** | **100** | **[XX%]** | |

**Priority Tier**: [1-4]
**GO/NO-GO Recommendation**: **[Recommendation]**

### Visualization

![Validation Score](figures/validation_score.png)

### Key Findings

1. [Finding 1 with evidence tier T1-T4]
2. [Finding 2 with evidence tier]
3. [Finding 3 with evidence tier]
4. [Finding 4 with evidence tier]
5. [Finding 5 with evidence tier]

### Critical Risks

- **[Risk Category]**: [Risk description with evidence tier] [T2]
- **[Risk Category]**: [Risk description with evidence tier] [T3]

### Key Strengths

1. [Strength 1]
2. [Strength 2]
3. [Strength 3]

---

## Part B: Target Intelligence

---

## 2. Target Identifiers

| Identifier Type | Value | Database |
|-----------------|-------|----------|
| Gene Symbol | [SYMBOL] | [HGNC/UniProt/MyGene] |
| UniProt Accession | [P#####] | UniProtKB |
| Ensembl Gene ID | [ENSG###] | Ensembl |
| Ensembl (versioned) | [ENSG###.#] | Ensembl |
| Entrez Gene ID | [#####] | NCBI Gene |
| ChEMBL Target ID | [CHEMBL###] | ChEMBL |
| HGNC ID | [HGNC:####] | HGNC |

**Confidence Level**: [HIGH/MEDIUM/LOW]

**Aliases**: [List all known aliases/synonyms]

---
**Sources:**
- UniProt: `UniProt_search_entries` (gene:[SYMBOL] AND organism_id:9606)
- Ensembl: `ensembl_lookup_gene` ([ensembl_id])
- ChEMBL: `ChEMBL_search_targets` ([symbol])
---

## 3. Basic Information

### 3.1 Protein Description
- **Recommended Name**: [Full protein name]
- **Alternative Names**: [List]
- **Gene Name**: [Symbol] ([Full gene name])
- **Organism**: Homo sapiens (Taxonomy ID: 9606)
- **Protein Length**: [###] amino acids
- **Molecular Weight**: [###] kDa
- **Isoforms**: [Number] known isoforms

### 3.2 Protein Function
[Detailed description of protein function - at least 3-4 sentences covering:
- Primary molecular function
- Biological process involvement
- Cellular role
- Signaling pathway context]

### 3.3 Subcellular Localization
- **Primary Location**: [e.g., Plasma membrane]
- **Additional Locations**: [List]
- **Topology**: [e.g., Single-pass type I membrane protein]

---
**Sources:**
- UniProt: `UniProt_get_entry_by_accession` ([accession])
- UniProt: `UniProt_get_function_by_accession` ([accession])
- UniProt: `UniProt_get_subcellular_location_by_accession` ([accession])
---

## 4. Structural Biology

### 4.1 Experimental Structures (PDB)

| PDB ID | Resolution | Method | Ligand | Description |
|--------|------------|--------|--------|-------------|
| [####] | [#.#Å] | [X-ray/Cryo-EM/NMR] | [Ligand or Apo] | [Brief description] |

**Total PDB Entries**: [###]
**Best Resolution**: [#.#Å] ([PDB ID])
**Structure Coverage**: [Complete/Partial - which domains?]

### 4.2 AlphaFold Prediction

![AlphaFold Model](https://alphafold.ebi.ac.uk/entry/[UNIPROT_ID])

- **Available**: [Yes/No]
- **Confidence**: [High/Medium/Low - pLDDT scores]
- **Model URL**: [AlphaFold DB link]

### 4.3 Domain Architecture

| Domain | Position | InterPro ID | Description |
|--------|----------|-------------|-------------|
| [Domain name] | [Start-End] | [IPR######] | [Function] |

### 4.4 Key Structural Features
- **Active Sites**: [List with positions]
- **Binding Sites**: [List - substrate, cofactor, drug binding]
- **PTM Sites**: [Phosphorylation, glycosylation, etc. with positions]
- **Disulfide Bonds**: [List]

### 4.5 Structural Druggability Assessment

| Feature | Assessment | Evidence |
|---------|------------|----------|
| Binding Pockets | [Number/Quality] | [Source] [T2] |
| Allosteric Sites | [Known/Predicted/None] | [Source] [T3] |
| Antibody Epitopes | [Accessible/Limited] | [Surface accessibility] [T3] |

**Structural Druggability Interpretation**:
[Paragraph interpreting structural data for drug design - include implications for modality selection]

---
**Sources:**
- PDB: Cross-references from UniProt entry
- AlphaFold: `alphafold_get_prediction` ([accession])
- InterPro: `InterPro_get_protein_domains` ([accession])
---

## 5. Function & Pathways

### 5.1 Gene Ontology Annotations

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

### 5.2 Pathway Involvement

| Pathway | Database | Pathway ID | Relevance |
|---------|----------|------------|-----------|
| [Pathway name] | [Reactome/KEGG/WikiPathways] | [ID] | [Disease relevance] |

### 5.3 Functional Summary
[Paragraph describing the target's role in cellular signaling, disease mechanisms, and biological importance]

---
**Sources:**
- GO: `GO_get_annotations_for_gene` ([gene_id])
- Reactome: `Reactome_map_uniprot_to_pathways` ([uniprot_id])
- WikiPathways: `WikiPathways_search` ([symbol])
---

## 6. Protein-Protein Interactions

### 6.1 Interaction Network Summary
- **Total Interactors (STRING, score >0.7)**: [###]
- **Experimentally Validated (IntAct)**: [###]
- **Complex Membership**: [List complexes]

### 6.2 Top Interacting Partners

| Partner | Score | Interaction Type | Evidence | Biological Context |
|---------|-------|------------------|----------|-------------------|
| [Gene] | [0.###] | [Physical/Functional] | [Experimental/Predicted] | [Context] |

### 6.3 Protein Complexes

| Complex Name | Members | Function |
|--------------|---------|----------|
| [Complex] | [List] | [Function] |

### 6.4 Interaction Network Implications
[Paragraph on network topology, hub status, and implications for drugging]

---
**Sources:**
- STRING: `STRING_get_protein_interactions` ([[uniprot_id]], species=9606)
- IntAct: `intact_get_interactions` ([uniprot_id])
---

## 7. Expression Profile

### 7.1 Tissue Expression (GTEx/HPA)

![Tissue Expression](figures/tissue_expression.png)

| Tissue | Expression Level (TPM) | Specificity |
|--------|------------------------|-------------|
| [Tissue] | [###] | [High/Medium/Low] |

**Tissue Specificity Score**: [Score] ([Broadly expressed/Tissue-specific/Tissue-enriched])

### 7.2 Critical Tissue Expression

| Critical Tissue | Expression Level | Risk Level |
|-----------------|------------------|------------|
| Heart | [High/Med/Low/None] | [Risk] |
| Liver | [High/Med/Low/None] | [Risk] |
| Kidney | [High/Med/Low/None] | [Risk] |
| Brain | [High/Med/Low/None] | [Risk] |
| Bone Marrow | [High/Med/Low/None] | [Risk] |

### 7.3 Cell Type Expression
[Single-cell data if available - top cell types]

### 7.4 Disease-Relevant Expression

| Cancer/Disease | Expression Change | Prognostic Value |
|----------------|-------------------|------------------|
| [Disease] | [Up/Down/Unchanged] | [Favorable/Unfavorable/None] |

### 7.5 Expression-Based Druggability
- **Tumor vs Normal**: [Differential expression ratio]
- **Therapeutic Window**: [Assessment based on expression pattern]

---
**Sources:**
- GTEx: `GTEx_get_median_gene_expression` ([gencode_id])
- HPA: `HPA_get_comprehensive_gene_details_by_ensembl_id` ([ensembl_id])
---

## 8. Genetic Variation & Disease

### 8.1 Genetic Constraint Scores

| Metric | Value | Interpretation |
|--------|-------|----------------|
| pLI | [0.##] | [Highly constrained (pLI > 0.9 means LOF intolerant)/Moderately constrained/Tolerant] |
| LOEUF | [0.##] | [Interpretation] |
| Missense Z-score | [#.##] | [Interpretation] |
| pRec | [0.##] | [Interpretation] |

### 8.2 Disease Associations (Open Targets)

![Disease Associations](figures/disease_associations.png)

| Disease | Association Score | Evidence Types | Evidence Tier | EFO ID |
|---------|-------------------|----------------|---------------|--------|
| [Disease] | [0.##] | [Genetic/Literature/etc.] | [T1-T4] | [EFO_#######] |

### 8.3 Pathogenic Variants (ClinVar)

#### Single Nucleotide Variants (SNVs)
| Variant | Clinical Significance | Condition | Review Status |
|---------|----------------------|-----------|---------------|
| [p.XXX###YYY] | [Pathogenic/Likely pathogenic] | [Condition] | [Stars] |

**Total ClinVar Entries**: [###]
**Pathogenic/Likely Pathogenic**: [###]

#### Copy Number Variants (CNVs)
| Type | Region | Clinical Significance | Frequency |
|------|--------|----------------------|-----------|
| [Amplification/Deletion] | [Region] | [Significance] | [Frequency] |

### 8.4 Cancer Mutations (COSMIC/cBioPortal)

| Mutation | Frequency | Cancer Types | Functional Impact |
|----------|-----------|--------------|-------------------|
| [Mutation] | [#%] | [Cancers] | [Activating/Inactivating/Unknown] |

### 8.5 GWAS Associations

| Trait | SNPs | P-value | OR/Beta |
|-------|------|---------|---------|
| [Trait] | [rs###] | [##e-##] | [OR] |

### 8.6 Genetic Evidence Summary
[Paragraph summarizing genetic validation of the target - include constraint implications and disease relevance]

---
**Sources:**
- gnomAD: `gnomad_get_gene_constraints` ([gene_symbol])
- ClinVar: `clinvar_search_variants` ([gene])
- OpenTargets: `OpenTargets_get_diseases_phenotypes_by_target_ensembl` ([ensembl_id])
- GWAS: `gwas_get_snps_for_gene` ([mapped_gene])
---

## Part C: Validation Assessment

---

## 9. Disease Association Scoring (0-30 pts)

### 9.1 Genetic Evidence (0-10)

| Evidence Type | Points | Source |
|---------------|--------|--------|
| GWAS associations | [X/6] | GWAS Catalog |
| Rare variants (ClinVar) | [X/2] | ClinVar |
| Somatic mutations | [X/2] | cBioPortal/COSMIC |
| Constraint scores (gnomAD) | [X/3] | gnomAD |

**Genetic Evidence Score**: [X]/10

### 9.2 Literature Evidence (0-10)

| Metric | Value | Points |
|--------|-------|--------|
| Total target+disease publications | [###] | [X/10] |
| Recent 5-year trend | [Increasing/Stable/Declining] | - |
| Key publications count | [###] | - |

**Literature Evidence Score**: [X]/10

### 9.3 Pathway Evidence (0-10)

| Disease | OpenTargets Score | Points |
|---------|-------------------|--------|
| [Disease] | [0.##] | [X/10] |

**Pathway Evidence Score**: [X]/10

**Total Disease Association Score**: [X]/30

---

## 10. Druggability Assessment (0-25 pts)

### 10.1 Structural Tractability (0-10)

| Structure Source | Quality | Points |
|------------------|---------|--------|
| PDB structures | [Count, best resolution] | [X] |
| AlphaFold | [pLDDT confidence] | [X] |
| Binding pockets | [Number, quality] | [X] |

**Structural Tractability Score**: [X]/10

### 10.2 Chemical Matter (0-10)

| Source | Compound Count | Best Affinity | Points |
|--------|----------------|---------------|--------|
| ChEMBL | [###] | [IC50/Ki] | [X] |
| BindingDB | [###] | [Ki/Kd] | [X] |
| PubChem BioAssay | [###] | [IC50] | [X] |

**Chemical Matter Score**: [X]/10

### 10.3 Target Class Bonus (0-5)

| Target Class | Points | Rationale |
|--------------|--------|-----------|
| [Class] | [X/5] | [Reason] |

### 10.4 Modality-Specific Tractability

| Modality | Tractability | Bucket | Evidence |
|----------|--------------|--------|----------|
| Small Molecule | [✅/⚠️/❌] | [1-10] | [Evidence] |
| Antibody | [✅/⚠️/❌] | [1-10] | [Evidence] |
| PROTAC | [✅/⚠️/❌] | [1-10] | [Evidence] |

### 10.5 Chemical Probes

| Probe | Selectivity | Use | Source |
|-------|-------------|-----|--------|
| [Probe] | [Selective/Broad] | [Recommended use] | [SGC/etc.] |

**Total Druggability Score**: [X]/25

---
**Sources:**
- OpenTargets: `OpenTargets_get_target_tractability_by_ensemblID` ([ensembl_id])
- ChEMBL: `ChEMBL_get_target_activities` ([target_chembl_id])
- BindingDB: `BindingDB_get_ligands_by_uniprot` ([uniprot])
---

## 11. Safety Deep Analysis (0-20 pts)

![Safety Dashboard](figures/safety_dashboard.png)

### 11.1 Tissue Expression Selectivity (0-5)

| Critical Tissue | Expression Level | Risk Level |
|-----------------|------------------|------------|
| Heart | [High/Med/Low/None] | [Risk] |
| Liver | [High/Med/Low/None] | [Risk] |
| Kidney | [High/Med/Low/None] | [Risk] |
| Brain | [High/Med/Low/None] | [Risk] |
| Bone Marrow | [High/Med/Low/None] | [Risk] |

**Expression Selectivity Score**: [X]/5

### 11.2 Genetic Validation (0-10)

| Model | Phenotype | Viability | Points |
|-------|-----------|-----------|--------|
| Mouse KO (IMPC) | [Phenotype] | [Viable/Lethal] | [X] |
| Human genetics (pLI) | [Value] | [Interpretation] | [X] |

**Genetic Validation Score**: [X]/10

### 11.3 Known Adverse Events (0-5)

| Adverse Event | Frequency | Drug Class | Mechanism |
|---------------|-----------|------------|-----------|
| [Event] | [Common/Uncommon/Rare] | [Class] | [On-target/Off-target] |

**ADR Score**: [X]/5

### 11.4 Safety Liabilities Summary

| Safety Concern | Evidence | Severity | Organ System |
|----------------|----------|----------|--------------|
| [Concern] | [Animal/Human/Both] | [High/Medium/Low] | [System] |

### 11.5 Paralog & Off-Target Risks

| Paralog | Sequence Identity | Cross-reactivity Risk |
|---------|-------------------|----------------------|
| [Gene] | [##%] | [Risk assessment] |

**Total Safety Score**: [X]/20

---
**Sources:**
- OpenTargets: `OpenTargets_get_target_safety_profile_by_ensemblID` ([ensembl_id])
- OpenTargets: `OpenTargets_get_biological_mouse_models_by_ensemblID` ([ensembl_id])
- GTEx: `GTEx_get_median_gene_expression` ([gencode_id])
---

## 12. Clinical Precedent (0-15 pts)

![Clinical Timeline](figures/clinical_timeline.png)

### 12.1 Approved Drugs

| Drug Name | Brand Name | Mechanism | Indication | Approval Year |
|-----------|------------|-----------|------------|---------------|
| [Drug] | [Brand] | [Inhibitor/Agonist/etc.] | [Indication] | [Year] |

### 12.2 Clinical Pipeline

| Drug | Phase | Indication | Trial Count | Status |
|------|-------|------------|-------------|--------|
| [Drug] | [Phase I/II/III] | [Indication] | [###] | [Active/Completed] |

**Total Clinical Trials**: [###]
**Active Trials**: [###]

### 12.3 Failed Programs & Lessons

| Drug | Phase Failed | Reason | Lesson |
|------|--------------|--------|--------|
| [Drug] | [Phase] | [Reason] | [Lesson] |

### 12.4 Clinical Precedent Score

| Stage | Points |
|-------|--------|
| [Highest stage] | [X/15] |

**Total Clinical Precedent Score**: [X]/15

---
**Sources:**
- OpenTargets: `OpenTargets_get_associated_drugs_by_target_ensemblID` ([ensembl_id])
- ClinicalTrials.gov: `search_clinical_trials` ([query_term])
---

## 13. Validation Evidence (0-10 pts)

### 13.1 Functional Studies (0-5)

| Study Type | Result | Evidence Tier | Points |
|------------|--------|---------------|--------|
| CRISPR KO | [Phenotype] | T1/T2 | [X] |
| siRNA | [Phenotype] | T2 | [X] |
| Biochemical | [Result] | T2 | [X] |

**Functional Studies Score**: [X]/5

### 13.2 Disease Models (0-5)

| Model Type | Result | Evidence Tier | Points |
|------------|--------|---------------|--------|
| PDX | [Response] | T1 | [X] |
| GEMM | [Phenotype] | T2 | [X] |
| Cell line | [Result] | T3 | [X] |

**Disease Models Score**: [X]/5

### 13.3 Target Essentiality (DepMap)

| Cell Line | Dependency Score | Essentiality |
|-----------|------------------|--------------|
| [Cell line] | [Score] | [Essential/Non-essential] |

**Total Validation Evidence Score**: [X]/10

---

## 14. Validation Scorecard

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

[Tier description paragraph]

### Modality-Specific Assessment

| Modality | Adjusted Score | Tier | Notes |
|----------|---------------|------|-------|
| Small Molecule | [XX] | [Tier] | [Notes] |
| Antibody | [XX] | [Tier] | [Notes] |
| PROTAC | [XX] | [Tier] | [Notes] |

---

## Part D: Synthesis & Recommendations

---

## 15. Validation Roadmap

### Recommended Validation Experiments

| Priority | Experiment | Rationale | Expected Timeline |
|----------|------------|-----------|-------------------|
| 🔴 HIGH | [Experiment] | [Why needed] | [Timeline] |
| 🔴 HIGH | [Experiment] | [Why needed] | [Timeline] |
| 🟡 MEDIUM | [Experiment] | [Why needed] | [Timeline] |
| 🟡 MEDIUM | [Experiment] | [Why needed] | [Timeline] |
| 🟢 LOW | [Experiment] | [Why needed] | [Timeline] |

### Data Gaps to Address

| Gap | Recommended Action | Priority |
|-----|-------------------|----------|
| [Gap] | [Action] | [Priority] |

### Testable Hypotheses

1. **Hypothesis 1**: [Statement]
   - Perturbation: [Approach]
   - Expected Readout: [Measurement]
   - Success Criteria: [Threshold]

2. **Hypothesis 2**: [Statement]
   - Perturbation: [Approach]
   - Expected Readout: [Measurement]
   - Success Criteria: [Threshold]

3. **Hypothesis 3**: [Statement]
   - Perturbation: [Approach]
   - Expected Readout: [Measurement]
   - Success Criteria: [Threshold]

---

## 16. Tool Compounds for Testing

### Recommended Tool Compounds

| Compound | Affinity | Selectivity | Source | Recommended Use |
|----------|----------|-------------|--------|-----------------|
| [Compound] | [IC50/Ki] | [Selectivity profile] | [ChEMBL/SGC] | [Use case] |

### Chemical Probes

| Probe | Selectivity | Use | Source |
|-------|-------------|-----|--------|
| [Probe] | [Selective/Broad] | [Recommended use] | [SGC/etc.] |

### Drug Resistance Considerations

[Known resistance mechanisms, mutations, or strategies to overcome resistance]

---

## 17. Biomarker Strategy

### Predictive Biomarkers

| Biomarker | Type | Assay | Clinical Utility |
|-----------|------|-------|------------------|
| [Biomarker] | [Genomic/Protein/etc.] | [Assay type] | [Utility] |

### Pharmacodynamic Markers

| Marker | Readout | Sample Type | Timepoint |
|--------|---------|-------------|-----------|
| [Marker] | [Readout] | [Sample] | [Timepoint] |

### Patient Stratification

[Strategy for selecting patients most likely to respond]

---

## 18. Key Risks & Mitigations

### Risk Assessment

| Risk Category | Risk | Probability | Impact | Mitigation Strategy |
|---------------|------|-------------|--------|---------------------|
| Safety | [Risk] | [High/Med/Low] | [High/Med/Low] | [Mitigation] |
| Efficacy | [Risk] | [High/Med/Low] | [High/Med/Low] | [Mitigation] |
| Competition | [Risk] | [High/Med/Low] | [High/Med/Low] | [Mitigation] |
| Technical | [Risk] | [High/Med/Low] | [High/Med/Low] | [Mitigation] |

### Key Strengths

1. [Strength 1]
2. [Strength 2]
3. [Strength 3]

### Key Challenges

1. [Challenge 1]
2. [Challenge 2]
3. [Challenge 3]

### Competitive Landscape

- **Market Status**: [First-in-Class/Best-in-Class/Follower]
- **Patent Landscape**: [Crowded/Moderate/Open]
- **Differentiation Opportunities**: [List]

---

## Appendices

---

## Appendix A: Data Sources & Methodology

### Databases Queried

| Database | Section(s) | Queries | Status |
|----------|------------|---------|--------|
| UniProtKB | 2, 3, 4 | [accession] | ✅ Success |
| RCSB PDB | 4 | [PDB IDs] | ✅ Success |
| AlphaFold DB | 4 | [accession] | ✅ Success |
| InterPro | 4 | [accession] | ✅ Success |
| Gene Ontology | 5 | [gene_id] | ✅ Success |
| Reactome | 5 | [accession] | ✅ Success |
| STRING | 6 | [protein_ids] | ✅ Success |
| IntAct | 6 | [accession] | ✅ Success |
| GTEx | 7 | [gencode_id] | ✅ Success |
| Human Protein Atlas | 7 | [ensembl_id] | ✅ Success |
| gnomAD | 8 | [gene_symbol] | ✅ Success |
| ClinVar | 8 | [gene] | ✅ Success |
| Open Targets | 8, 9, 10, 11 | [ensembl_id] | ✅ Success |
| ChEMBL | 10 | [target_chembl_id] | ✅ Success |
| GWAS Catalog | 8 | [mapped_gene] | ✅ Success |

### Tools Used by Phase

| Phase | Tools Used |
|-------|------------|
| 0. Disambiguation | `MyGene_query_genes`, `UniProt_id_mapping`, `ensembl_lookup_gene`, `ChEMBL_search_targets` |
| 1. OT Foundation | `OpenTargets_get_diseases_phenotypes_by_target_ensembl`, etc. (11 endpoints) |
| 2-7. Collection | UniProt, PDB, STRING, GTEx, gnomAD, Reactome tools |
| 8-12. Scoring | Scoring calculation from collected data |

### Data Freshness

- **Report Generated**: [YYYY-MM-DD HH:MM UTC]
- **UniProt Release**: [Release number if available]
- **GTEx Version**: v8
- **gnomAD Version**: v4.0

---

## Appendix B: Completeness Checklist

### Phase Coverage
- [ ] Phase 0: Target disambiguation (all IDs resolved)
- [ ] Phase 1: Open Targets foundation (11 endpoints)
- [ ] Phase 2: Core identity (UniProt)
- [ ] Phase 3: Structure & domains (PDB, AlphaFold, InterPro)
- [ ] Phase 4: Function & pathways (GO, Reactome)
- [ ] Phase 5: PPIs (STRING, IntAct)
- [ ] Phase 6: Expression (GTEx, HPA)
- [ ] Phase 7: Genetics (gnomAD, ClinVar, GWAS)
- [ ] Phases 8-12: Scoring complete

### Data Minimums
- [ ] All identifiers resolved (UniProt, Ensembl, Entrez, ChEMBL)
- [ ] PDB structures listed (if available)
- [ ] All 4 constraint scores reported
- [ ] Top 10 disease associations listed
- [ ] All approved drugs listed
- [ ] Safety concerns documented
- [ ] Validation scorecard complete
- [ ] PPIs: >= 20 interactors OR documented explanation
- [ ] Expression: Top 10 tissues with TPM values OR "unavailable"
- [ ] Pathways: >= 10 pathways OR explanation

### Quality Checks
- [ ] Evidence grading applied (T1-T4)
- [ ] All claims have source citations
- [ ] Negative results documented
- [ ] Failed tools with fallbacks documented
- [ ] Interpretation paragraphs included

---

## Appendix C: Data Gaps & Limitations

| Section | Expected Data | Actual | Reason | Alternative |
|---------|---------------|--------|--------|-------------|
| [Section] | [Expected] | [Actual] | [Reason] | [Alternative] |

### Tool Failures

| Tool | Error | Fallback Used |
|------|-------|---------------|
| [Tool] | [Error] | [Fallback] |

---

## Appendix D: Structured Data Export

```json
{
  "metadata": {
    "target": "[SYMBOL]",
    "uniprot_id": "[P#####]",
    "ensembl_id": "[ENSG###]",
    "report_date": "[YYYY-MM-DD]"
  },
  "validation_score": {
    "total": [XX],
    "tier": [1-4],
    "recommendation": "[GO/CONDITIONAL GO/CAUTION/NO-GO]",
    "components": {
      "disease_association": {"score": [XX], "max": 30},
      "druggability": {"score": [XX], "max": 25},
      "safety": {"score": [XX], "max": 20},
      "clinical_precedent": {"score": [XX], "max": 15},
      "validation_evidence": {"score": [XX], "max": 10}
    }
  },
  "identifiers": {
    "symbol": "[SYMBOL]",
    "uniprot": "[P#####]",
    "ensembl": "[ENSG###]",
    "entrez": [#####],
    "chembl": "[CHEMBL###]"
  },
  "diseases": [...],
  "drugs": [...],
  "safety_flags": [...],
  "recommended_actions": [...]
}
```

---

*Report generated by ToolUniverse Target Validation Pipeline*
*Date: [YYYY-MM-DD]*
```

---

## Visualization Placement

Reports must include these visualizations at specified locations:

| Figure | Location | Description |
|--------|----------|-------------|
| `validation_score.png` | Section 1 (Executive Summary) | Score breakdown with tier gauge |
| `tissue_expression.png` | Section 7.1 | Expression heatmap with critical tissues |
| `disease_associations.png` | Section 8.2 | Disease bar chart with evidence tiers |
| `safety_dashboard.png` | Section 11 | Multi-panel safety indicators |
| `clinical_timeline.png` | Section 12 | Drug development timeline |

---

## Evidence Grading Format

Every claim must include evidence tier:

| Tier | Symbol | Criteria |
|------|--------|----------|
| T1 | ★★★ | Clinical proof, FDA-approved drug, mechanistic study |
| T2 | ★★ | Functional study (knockdown, overexpression, clinical trial) |
| T3 | ★ | Association (GWAS, screen hit, correlation) |
| T4 | ☆ | Mention (review, text-mined, prediction) |

**Format**: `[Claim] [T1]` or `[Claim] ★★★`

---

## Interpretation Requirements

Each major data section must include:

1. **What the data means**: Significance and implications
2. **How it affects validation**: Impact on scoring, risks, opportunities
3. **Recommended actions**: Next steps justified by data

### Example Interpretation Format

```markdown
### 10.5 Safety Summary

**Interpretation**: The ubiquitous expression pattern across critical tissues
(heart, liver, kidney, brain) presents a significant safety challenge. The
mouse knockout phenotype of embryonic lethality confirms target essentiality,
which may limit therapeutic window. However, the manageable adverse event
profile of approved drugs demonstrates that modulation is feasible with
appropriate patient management strategies.

**Impact on Validation**: -8 points for safety profile. The essentiality
concern reduces the safety score to the lower tier. However, clinical
precedent demonstrates manageable toxicity.

**Recommendation**: Implement patient stratification based on predictive
biomarkers; develop targeted delivery approaches to improve therapeutic
index; establish clear safety monitoring protocols.
```

---

## Section-Specific Guidance

### Executive Summary
**Purpose**: Give reader the key takeaways in 30 seconds

Include:
1. What the target IS (protein class, function)
2. Clinical relevance (disease associations)
3. Druggability status (has drugs? tractable?)
4. One-line recommendation with score

### Section 4: Structural Biology
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

### Section 15: Validation Roadmap
**Purpose**: Provide actionable next steps

Requirements:
- Use priority levels (🔴 HIGH/🟡 MEDIUM/🟢 LOW)
- Each recommendation must be actionable
- Include timeline estimates
- Address identified data gaps
- Provide testable hypotheses (>=3)