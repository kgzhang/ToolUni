# Target Validation Report Template

Report template with all sections. Executive Summary is generated last.

---

## Report Structure

```
1. Executive Summary (最后生成)
2. Part A: Target Intelligence (Sections 1-7)
3. Part B: Validation Assessment (Sections 8-13)
4. Part C: Synthesis & Recommendations (Sections 14-17)
```

---

## Part A: Target Intelligence

### Section 1: Target Identifiers

| 标识符类型 (Identifier Type) | 值 (Value) | 数据库 (Database) |
|------------------------------|------------|-------------------|
| 基因符号 (Gene Symbol) | [SYMBOL] | HGNC |
| UniProt登录号 (UniProt Accession) | [P#####] | UniProtKB |
| Ensembl基因ID (Ensembl Gene ID) | [ENSG###] | Ensembl |
| Entrez基因ID (Entrez Gene ID) | [#####] | NCBI Gene |
| ChEMBL靶点ID (ChEMBL Target ID) | [CHEMBL###] | ChEMBL |

**别名 (Aliases)**: [List synonyms]

---

### Section 2: Basic Information

#### 2.1 蛋白描述 (Protein Description)
- **推荐名称 (Recommended Name)**: [Full protein name]
- **基因名称 (Gene Name)**: [Symbol] ([Full gene name])
- **生物体 (Organism)**: [Species]

#### 2.2 蛋白功能 (Protein Function)
[功能描述 - 通过LLM转换为中文]

#### 2.3 亚细胞定位 (Subcellular Localization)
- **主要位置 (Primary Location)**: [e.g., Plasma membrane]
- **拓扑结构 (Topology)**: [e.g., Single-pass type I membrane protein]

---

### Section 3: Structural Biology

#### 3.1 实验结构 (Experimental Structures - PDB)

**少量数据时使用概述格式**:
- PDB ID: [####], 分辨率: [#.#Å], 方法: [X-ray/Cryo-EM]

**多条数据时使用表格**:
| PDB ID | 分辨率 (Resolution) | 方法 (Method) |
|--------|---------------------|---------------|
| [####] | [#.#Å] | [X-ray/Cryo-EM/NMR] |

**PDB条目总数 (Total PDB Entries)**: [###]
**最佳分辨率 (Best Resolution)**: [#.#Å] ([PDB ID])

#### 3.2 AlphaFold预测 (AlphaFold Prediction)
- **可用性**: [是/否]
- **置信度**: [高/中/低 - pLDDT scores]
- **模型链接**: [AlphaFold DB link]

#### 3.3 结构域架构 (Domain Architecture)

| 结构域 (Domain) | 位置 (Position) | ID |
|-----------------|-----------------|-----|
| [Domain name] | [Start-End] | [IPR######] |

#### 3.4 结构可成药性评估 (Structural Druggability Assessment)
- **结合口袋 (Binding Pockets)**: [Identified pockets]
- **别构位点 (Allosteric Sites)**: [Known or predicted]
- **抗体表位 (Antibody Epitopes)**: [Surface accessibility]

---

### Section 4: Function & Pathways

#### 4.1 基因本体注释 (Gene Ontology Annotations)

**分子功能 (Molecular Function)**:
| GO术语 (GO Term) | GO ID | 证据 (Evidence) |
|------------------|-------|-----------------|
| [Term] | [GO:#######] | [IDA/IEA/etc.] |

**生物过程 (Biological Process)**:
| GO术语 (GO Term) | GO ID | 证据 (Evidence) |
|------------------|-------|-----------------|
| [Term] | [GO:#######] | [IDA/IEA/etc.] |

#### 4.2 通路参与 (Pathway Involvement)

| 通路 (Pathway) | 数据库 (Database) | ID |
|----------------|-------------------|-----|
| [Pathway name] | [Reactome/KEGG/WikiPathways] | [ID] |

#### 4.3 功能概述 (Functional Summary)
[描述靶点在细胞信号、疾病机制和生物学重要性中的作用]

---

### Section 5: Protein-Protein Interactions

#### 5.1 相互作用网络概述 (Interaction Network Summary)
- **相互作用蛋白总数 (Total Interactors)**: [###]
- **数据来源 (Source)**: [STRING/IntAct/BioGRID]
- **复合物成员 (Complex Membership)**: [List complexes]

#### 5.2 主要相互作用伙伴 (Top Interacting Partners)

**少量数据时使用概述**:
- [Partner 1]: 分数 [0.###], 类型 [Physical/Functional]
- [Partner 2]: 分数 [0.###], 类型 [Physical/Functional]

**多条数据时使用表格**:
| 相互作用蛋白 (Partner) | 分数 (Score) | 类型 (Type) |
|------------------------|--------------|-------------|
| [Gene] | [0.###] | [Physical/Functional] |

---

### Section 6: Expression Profile

![组织表达热图](visualizations/tissue_expression_heatmap.png)

#### 6.1 组织表达 (Tissue Expression)

| 组织 (Tissue) | TPM | 表达水平 (Level) |
|---------------|-----|------------------|
| [Tissue] | [###] | [高/中/低] |

**组织特异性评分 (Tissue Specificity Score)**: [Score]

#### 6.2 关键组织表达 (Critical Tissue Expression)

关键组织: 心脏、肝脏、肾脏、大脑、骨髓

- **[Tissue]**: [TPM] TPM ([高 ⚠️ /中/低])
- ...

---

### Section 7: Genetic Variation

#### 7.1 遗传约束评分 (Genetic Constraint Scores)

| 指标 (Metric) | 值 (Value) | 解释 (Interpretation) |
|---------------|------------|----------------------|
| pLI | [0.##] | [高度约束/耐受] |
| LOEUF | [0.##] | [解释] |
| Missense Z-score | [#.##] | [解释] |
| pRec | [0.##] | [解释] |

#### 7.2 疾病关联 (Disease Associations)

| 疾病 (Disease) | 关联分数 (Score) | 证据类型 (Evidence Types) |
|----------------|------------------|---------------------------|
| [Disease] | [0.##] | [Genetic/Literature/etc.] |

#### 7.3 致病变异 (Pathogenic Variants - ClinVar)

**SNVs**:
| 变异 (Variant) | 临床意义 (Significance) | 疾病 (Condition) |
|----------------|------------------------|------------------|
| [p.XXX###YYY] | [Pathogenic/Likely pathogenic] | [Condition] |

**致病变异数量 (Total Pathogenic SNVs)**: [###]

---

## Part B: Validation Assessment

![验证评分图表](visualizations/validation_score_chart.png)

### Section 8: Disease Association Scoring (0-30分)

#### 8.1 遗传证据 (Genetic Evidence)
| 证据类型 | 分数 | 来源 |
|----------|------|------|
| GWAS关联 | [X/6] | GWAS Catalog |
| 稀有变异 | [X/2] | ClinVar |
| 体细胞突变 | [X/2] | cBioPortal |
| 约束评分 | [X/3] | gnomAD |

**遗传证据得分**: [X/10]

#### 8.2 文献证据 (Literature Evidence)
| 指标 | 值 | 分数 |
|------|-----|------|
| 靶点+疾病文献数 | [###] | [X/10] |

**文献证据得分**: [X/10]

#### 8.3 通路证据 (Pathway Evidence)
| 疾病 | OpenTargets分数 | 得分 |
|------|-----------------|------|
| [Disease] | [0.##] | [X/10] |

**通路证据得分**: [X/10]

**疾病关联总分**: [X/30]

---

### Section 9: Druggability Assessment (0-25分)

#### 9.1 结构可及性 (Structural Tractability)
| 结构来源 | 质量 | 分数 |
|----------|------|------|
| PDB结构 | [数量, 最佳分辨率] | [X] |
| AlphaFold | [pLDDT置信度] | [X] |
| 结合口袋 | [数量, 质量] | [X] |

**结构可及性得分**: [X/10]

#### 9.2 化学物质 (Chemical Matter)
| 来源 | 化合物数量 | 最佳亲和力 | 分数 |
|------|------------|------------|------|
| ChEMBL | [###] | [IC50/Ki] | [X] |
| BindingDB | [###] | [Ki/Kd] | [X] |

**化学物质得分**: [X/10]

#### 9.3 靶点类别加成 (Target Class Bonus)
| 靶点类别 | 分数 | 理由 |
|----------|------|------|
| [Class] | [X/5] | [Reason] |

**可成药性总分**: [X/25]

---

### Section 10: Safety Analysis (0-20分)

#### 10.1 组织表达选择性 (Tissue Expression Selectivity)
| 关键组织 | 表达水平 | 风险水平 |
|----------|----------|----------|
| 心脏 (Heart) | [高/中/低/无] | [风险] |
| 肝脏 (Liver) | [高/中/低/无] | [风险] |
| 肾脏 (Kidney) | [高/中/低/无] | [风险] |
| 大脑 (Brain) | [高/中/低/无] | [风险] |
| 骨髓 (Bone Marrow) | [高/中/低/无] | [风险] |

**表达选择性得分**: [X/5]

#### 10.2 遗传验证 (Genetic Validation)
| 模型 | 表型 | 存活能力 | 分数 |
|------|------|----------|------|
| 小鼠KO (IMPC) | [Phenotype] | [存活/致死] | [X] |
| 人类遗传学 (pLI) | [Value] | [解释] | [X] |

**遗传验证得分**: [X/10]

#### 10.3 已知不良反应 (Known Adverse Events)
| 不良事件 | 频率 | 药物类别 | 机制 |
|----------|------|----------|------|
| [Event] | [常见/不常见/罕见] | [Class] | [On-target/Off-target] |

**安全性总分**: [X/20]

**安全警示 (Safety Flags)**:
- [Flag 1]
- [Flag 2]

---

### Section 11: Clinical Precedent (0-15分)

#### 11.1 已批准药物 (Approved Drugs)
| 药物名称 (Drug Name) | 商品名 (Brand) | 机制 (Mechanism) | 适应症 (Indication) |
|----------------------|----------------|------------------|---------------------|
| [Drug] | [Brand] | [Inhibitor/Agonist] | [Indication] |

#### 11.2 临床管线 (Clinical Pipeline)
| 药物 (Drug) | 阶段 (Phase) | 适应症 (Indication) | 状态 (Status) |
|-------------|--------------|---------------------|---------------|
| [Drug] | [Phase I/II/III] | [Indication] | [Active/Completed] |

**临床先例得分**: [X/15]

![临床开发现状](visualizations/clinical_timeline.png)

---

### Section 12: Validation Evidence (0-10分)

#### 12.1 功能研究 (Functional Studies)
| 研究类型 | 结果 | 证据层级 | 分数 |
|----------|------|----------|------|
| CRISPR KO | [Phenotype] | T1/T2 | [X] |
| siRNA | [Phenotype] | T2 | [X] |

**功能研究得分**: [X/5]

#### 12.2 疾病模型 (Disease Models)
| 模型类型 | 结果 | 证据层级 | 分数 |
|----------|------|----------|------|
| PDX | [Response] | T1 | [X] |
| GEMM | [Phenotype] | T2 | [X] |

**疾病模型得分**: [X/5]

**验证证据总分**: [X/10]

---

### Section 13: Composite Score

#### 综合评分汇总 (Composite Score Summary)

| 维度 (Dimension) | 得分 (Score) | 满分 (Max) | 百分比 (%) |
|------------------|--------------|------------|------------|
| 疾病关联 (Disease Association) | [XX] | 30 | [XX%] |
| 可成药性 (Druggability) | [XX] | 25 | [XX%] |
| 安全性 (Safety) | [XX] | 20 | [XX%] |
| 临床先例 (Clinical Precedent) | [XX] | 15 | [XX%] |
| 验证证据 (Validation Evidence) | [XX] | 10 | [XX%] |
| **总分 (Total)** | **[XX]** | **100** | **[XX%]** |

#### 优先层级 (Priority Tier)

**层级**: Tier [1-4]
**建议**: [GO/CONDITIONAL GO/CAUTION/NO-GO]

---

## Part C: Synthesis & Recommendations

### Section 14: Validation Roadmap

#### 推荐验证实验 (Recommended Validation Experiments)

| 优先级 (Priority) | 实验 (Experiment) | 理由 (Rationale) | 时间线 (Timeline) |
|-------------------|-------------------|------------------|-------------------|
| 高 (HIGH) | [Experiment] | [Why needed] | [Timeline] |
| 中 (MEDIUM) | [Experiment] | [Why needed] | [Timeline] |
| 低 (LOW) | [Experiment] | [Why needed] | [Timeline] |

#### 数据缺口 (Data Gaps to Address)

| 缺口 (Gap) | 建议行动 (Recommended Action) | 优先级 (Priority) |
|------------|-------------------------------|-------------------|
| [Gap] | [Action] | [Priority] |

---

### Section 15: Tool Compounds

#### 推荐工具化合物 (Recommended Tool Compounds)

| 化合物 (Compound) | 亲和力 (Affinity) | 选择性 (Selectivity) | 来源 (Source) |
|-------------------|-------------------|----------------------|---------------|
| [Compound] | [IC50/Ki] | [Selectivity profile] | [ChEMBL/SGC] |

---

### Section 16: Biomarker Strategy

#### 预测性生物标志物 (Predictive Biomarkers)

| 生物标志物 (Biomarker) | 类型 (Type) | 检测方法 (Assay) | 临床用途 (Clinical Utility) |
|------------------------|-------------|------------------|-----------------------------|
| [Biomarker] | [Genomic/Protein] | [Assay type] | [Utility] |

#### 药效学标志物 (Pharmacodynamic Markers)

| 标志物 (Marker) | 读数 (Readout) | 样本类型 (Sample Type) |
|-----------------|----------------|------------------------|
| [Marker] | [Readout] | [Sample] |

---

### Section 17: Key Risks & Mitigations

#### 风险评估 (Risk Assessment)

| 风险类别 (Risk Category) | 风险 (Risk) | 概率 (Probability) | 影响 (Impact) | 缓解策略 (Mitigation) |
|--------------------------|-------------|--------------------|---------------|-----------------------|
| 安全性 (Safety) | [Risk] | [高/中/低] | [高/中/低] | [Mitigation] |
| 有效性 (Efficacy) | [Risk] | [高/中/低] | [高/中/低] | [Mitigation] |

#### 关键优势 (Key Strengths)

1. [Strength 1]
2. [Strength 2]
3. [Strength 3]

#### 主要挑战 (Key Challenges)

1. [Challenge 1]
2. [Challenge 2]
3. [Challenge 3]

---

## Executive Summary (最后生成)

### 验证评分卡 (Target Validation Scorecard)

| 维度 (Dimension) | 得分 (Score) | 满分 (Max) |
|------------------|--------------|------------|
| 疾病关联 (Disease Association) | [XX] | 30 |
| 可成药性 (Druggability) | [XX] | 25 |
| 安全性 (Safety) | [XX] | 20 |
| 临床先例 (Clinical Precedent) | [XX] | 15 |
| 验证证据 (Validation Evidence) | [XX] | 10 |
| **总分 (Total)** | **[XX]** | **100** |

**优先层级 (Priority Tier)**: Tier [1-4]
**GO/NO-GO建议**: [Recommendation]

### 主要发现 (Key Findings)

1. [Finding 1 with evidence tier]
2. [Finding 2 with evidence tier]
3. [Finding 3 with evidence tier]

### 关键风险 (Critical Risks)

- [Risk 1]
- [Risk 2]

### 建议 (Recommendation)

[基于总分的详细建议]