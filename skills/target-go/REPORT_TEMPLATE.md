# Target-GO 报告模板

**版本**: v2.0
**更新日期**: 2024年
**目的**: 指导生成10页以上的专业靶点评估报告

---

# 报告生成原则

## 核心要求

1. **原始数据准确性**: 所有数据必须直接来自原始JSON文件，禁止编造或估算
2. **解读专业性**: 使用标准药物研发术语，基于证据进行推理
3. **信息丰富度**: 每个章节必须包含足够的原始数据和解读内容
4. **证据分级**: 所有重要声明必须标注T1-T4证据层级
5. **篇幅要求**: 最终报告不少于10页（约15000字以上）

## 证据层级定义

| 层级 | 符号 | 定义 | 示例 |
|------|------|------|------|
| **T1** | ★★★ | 机制明确，人体临床验证 | 已批准药物、临床试验阳性结果 |
| **T2** | ★★ | 功能验证，模式生物支持 | 基因敲除表型、体外功能实验 |
| **T3** | ★ | 统计关联，筛选命中 | GWAS关联、表达差异 |
| **T4** | ○ | 文献提及，计算预测 | 文献报道、生物信息学预测 |

---

# 靶点评估报告: {TARGET_NAME}

**生成日期**: {DATE}
**基因符号**: {GENE_SYMBOL}
**UniProt ID**: {UNIPROT_ID}
**Ensembl ID**: {ENSEMBL_ID}
**ChEMBL ID**: {CHEMBL_ID}

---

## 执行摘要

**字数要求**: 800字以上

### 靶点验证评分

| 维度 | 得分 | 满分 | 占比 | 评估 |
|------|------|------|------|------|
| 疾病关联 | {score} | 30 | {percent}% | {强/中/弱} |
| 可药性 | {score} | 25 | {percent}% | {强/中/弱} |
| 安全性 | {score} | 20 | {percent}% | {强/中/弱} |
| 临床先例 | {score} | 15 | {percent}% | {强/中/弱} |
| 验证证据 | {score} | 10 | {percent}% | {强/中/弱} |
| **总分** | **{total}** | **100** | - | - |

### 优先层级与建议

| 层级 | 建议 | 理由 |
|------|------|------|
| **{TIER}** | {RECOMMENDATION} | {JUSTIFICATION} |

**层级定义**:
- **Tier 1 (80-100分)**: GO - 高度验证靶点，建议直接推进
- **Tier 2 (60-79分)**: CONDITIONAL GO - 良好靶点，需重点验证特定维度
- **Tier 3 (40-59分)**: CAUTION - 中等风险，需大量补充验证
- **Tier 4 (0-39分)**: NO-GO - 高风险，建议考虑替代靶点

### 关键发现（必须包含具体数据支撑）

**1. 核心优势**（3-5项，每项需标注证据层级）:

| 序号 | 优势描述 | 支撑数据 | 证据层级 |
|------|----------|----------|----------|
| 1 | {优势描述} | {具体数值/来源} | T1/T2/T3/T4 |
| 2 | {优势描述} | {具体数值/来源} | T1/T2/T3/T4 |
| 3 | {优势描述} | {具体数值/来源} | T1/T2/T3/T4 |

**2. 主要风险**（3-5项，每项需标注证据层级）:

| 序号 | 风险描述 | 潜在影响 | 证据层级 |
|------|----------|----------|----------|
| 1 | {风险描述} | {高/中/低} | T1/T2/T3/T4 |
| 2 | {风险描述} | {高/中/低} | T1/T2/T3/T4 |
| 3 | {风险描述} | {高/中/低} | T1/T2/T3/T4 |

**3. 数据缺口汇总**:

| 缺口领域 | 缺失数据 | 对评估影响 | 补充建议 |
|----------|----------|------------|----------|
| {领域} | {缺失内容} | {高/中/低} | {补充方案} |

### 靶点概述（200字以上专业描述）

基于收集的原始数据，综合描述：
- 靶点的基本生物学功能
- 在疾病中的作用机制
- 当前开发状态
- 主要研究热点

---

## 1. 靶点标识符

**字数要求**: 300字以上

### 1.1 标识符汇总表

| 标识符类型 | 值 | 来源 | 状态 |
|------------|-----|------|------|
| 基因符号 | {symbol} | HGNC | ✓ 已验证 |
| UniProt ID | {uniprot} | UniProtKB | ✓ 已验证 |
| Ensembl ID | {ensembl} | Ensembl | ✓ 已验证 |
| Ensembl版本化ID | {ensembl_versioned} | Ensembl | ✓ 已验证 |
| Entrez ID | {entrez} | NCBI Gene | ✓ 已验证 |
| ChEMBL靶点ID | {chembl_target} | ChEMBL | ✓ 已验证 |
| 全称 | {full_name} | UniProt | ✓ 已验证 |
| 蛋白存在证据 | {protein_existence} | UniProt | - |
| 审核状态 | {reviewed} | UniProt | - |

### 1.2 别名与同义词

**标准名称**: {primary_name}

**别名列表**:
| 别名 | 类型 | 来源 |
|------|------|------|
| {synonym1} | {type} | {source} |

**潜在命名冲突**: 分析是否存在与其他基因/蛋白的命名冲突风险

### 1.3 标识符解析过程

```
解析日志:
{resolution_log}
```

### 1.4 数据来源原始记录

```json
{phase0_raw_data}
```

---

## 2. 基础信息

**字数要求**: 1000字以上

### 2.1 蛋白概述

| 属性 | 值 | 数据来源 |
|------|-----|----------|
| 蛋白名称 | {name} | UniProt |
| 全称 | {full_name} | UniProt |
| 序列长度 | {length} aa | UniProt |
| 分子量 | {mass} Da | UniProt |
| 生物体 | {organism} | UniProt |
| 分类ID | {taxon_id} | NCBI |
| 蛋白存在证据 | {protein_existence} | UniProt |
| 审核状态 | {reviewed} | UniProt |

**蛋白存在证据分级**:
- 1级: 蛋白水平证据
- 2级: 转录水平证据
- 3级: 同源推断
- 4级: 预测
- 5级: 不确定

### 2.2 功能描述（完整原文）

```
{function_description_raw}
```

**功能解读**（200字以上）:

基于功能描述，分析：
1. 核心生物学功能
2. 关键信号通路参与
3. 与疾病的关联机制
4. 潜在干预靶点

### 2.3 结构域架构

**结构域总数**: {domain_count}

| 序号 | 结构域名称 | Accession | 类型 | 位置 | 功能描述 |
|------|------------|-----------|------|------|----------|
| 1 | {name} | {accession} | {type} | {start}-{end} | {description} |
| 2 | {name} | {accession} | {type} | {start}-{end} | {description} |
| ... | ... | ... | ... | ... | ... |

**关键结构域分析**（200字以上）:

分析主要结构域的功能意义：
- 酶活性位点（如有）
- 配体结合结构域
- 蛋白相互作用界面
- 与可药性的关系

### 2.4 亚细胞定位

| 定位 | 可信度 | 功能意义 |
|------|--------|----------|
| {location1} | {confidence} | {significance} |

**定位分析**（100字以上）:

分析亚细胞定位对药物递送的影响：
- 膜蛋白：抗体可及性
- 胞内蛋白：小分子需求
- 分泌蛋白：特殊考虑

### 2.5 翻译后修饰位点

| PTM类型 | 位置 | 功能影响 | 来源 |
|---------|------|----------|------|
| {ptm_type} | {position} | {effect} | {source} |

### 2.6 结构信息

#### 2.6.1 PDB实验结构

**PDB条目总数**: {pdb_count}

| PDB ID | 分辨率(Å) | 方法 | 配体 | 发布年份 | 链数 |
|--------|----------|------|------|----------|------|
| {pdb_id} | {resolution} | {method} | {ligand} | {year} | {chains} |

**结构覆盖度分析**:
- 覆盖区域: {covered_regions}
- 未覆盖区域: {uncovered_regions}
- 结构完整性: {completeness}%

#### 2.6.2 AlphaFold预测结构

**可用性**: {alphafold_status}

| 属性 | 值 |
|------|-----|
| UniProt ID | {uniprot} |
| pLDDT平均置信度 | {plddt_score} |
| 高置信度区域(>90) | {high_confidence_regions} |
| 低置信度区域(<50) | {low_confidence_regions} |
| PDB下载链接 | https://alphafold.ebi.ac.uk/files/AF-{uniprot}-F1-model_v4.pdb |

**结构可药性评估**（150字以上）:

基于结构信息分析：
- 结合口袋特征
- 结构稳定性
- 已知药物结合模式
- 结构指导药物设计建议

### 2.7 原始数据记录

```json
{phase1_protein_info_raw}
```

---

## 3. 通路与功能

**字数要求**: 800字以上

### 3.1 GO注释统计

| 类别 | 注释数量 | 高证据数量 |
|------|----------|------------|
| 分子功能 (MF) | {mf_count} | {mf_high_evidence} |
| 生物学过程 (BP) | {bp_count} | {bp_high_evidence} |
| 细胞组分 (CC) | {cc_count} | {cc_high_evidence} |

### 3.2 分子功能 (MF) - Top 20

| GO ID | 术语名称 | 证据代码 | 来源 |
|-------|----------|----------|------|
| {go_id} | {term} | {evidence} | {reference} |

### 3.3 生物学过程 (BP) - Top 30

| GO ID | 术语名称 | 证据代码 | 来源 |
|-------|----------|----------|------|
| {go_id} | {term} | {evidence} | {reference} |

### 3.4 细胞组分 (CC)

| GO ID | 术语名称 | 证据代码 | 来源 |
|-------|----------|----------|------|
| {go_id} | {term} | {evidence} | {reference} |

### 3.5 Reactome通路

**通路总数**: {pathway_count}

| 通路ID | 通路名称 | 物种 | URL |
|--------|----------|------|-----|
| {stId} | {name} | {species} | {url} |

**通路层次结构分析**:

识别核心通路簇：
1. 信号传导通路
2. 代谢通路
3. 免疫相关通路
4. 细胞周期通路

### 3.6 功能综合解读（300字以上）

基于GO和通路数据，综合分析：
- 核心分子功能
- 关键生物学过程
- 主要信号通路
- 与疾病的关系
- 潜在干预策略

### 3.7 原始数据记录

```json
{phase1_go_pathways_raw}
```

---

## 4. 蛋白相互作用

**字数要求**: 600字以上

### 4.1 相互作用网络概览

| 数据来源 | 相互作用数 | 置信度阈值 | 覆盖度 |
|----------|------------|------------|--------|
| STRING | {string_count} | score > 0.7 | {coverage} |
| BioGRID | {biogrid_count} | - | {coverage} |
| IntAct | {intact_count} | - | {coverage} |
| **总计** | **{total}** | - | - |

### 4.2 STRING相互作用详情 - Top 30

| 伙伴蛋白 | 伙伴名称 | 置信度分数 | 相互作用类型 | 功能相关性 |
|----------|----------|------------|--------------|------------|
| {partner_id} | {partner_name} | {score} | {type} | {relevance} |

### 4.3 相互作用网络特征

**网络拓扑分析**:
- 节点数: {node_count}
- 边数: {edge_count}
- 平均度: {average_degree}
- 聚类系数: {clustering_coefficient}

**中心性分析**:
- 度中心性排名: {degree_ranking}
- 介数中心性排名: {betweenness_ranking}

### 4.4 功能相互作用簇

识别功能相关的相互作用簇：

| 簇编号 | 功能主题 | 成员数 | 关键成员 |
|--------|----------|--------|----------|
| 1 | {theme} | {count} | {members} |

### 4.5 相互作用解读（200字以上）

分析相互作用网络的意义：
- 核心相互作用伙伴
- 信号传导关系
- 功能调控网络
- 对靶点验证的启示

### 4.6 原始数据记录

```json
{phase1_interactions_raw}
```

---

## 5. 表达谱

**字数要求**: 600字以上

### 5.1 GTEx组织表达

**已分析组织数**: {tissue_count}

#### 5.1.1 全部组织表达数据

| 组织 | 中位TPM | 平均TPM | 表达水平 | 百分位排名 |
|------|---------|---------|----------|------------|
| {tissue} | {median_tpm} | {mean_tpm} | {高/中/低} | {percentile} |

#### 5.1.2 高表达组织（TPM > 10）

| 组织 | 中位TPM | 临床意义 |
|------|---------|----------|
| {tissue} | {tpm} | {significance} |

### 5.2 组织特异性分析

| 指标 | 值 | 解释 |
|------|-----|------|
| Tau指数 | {tau} | {1=特异性表达, 0=广泛表达} |
| 组织特异性评分 | {ts_score} | {interpretation} |
| 主要表达组织 | {main_tissue} | - |
| 组织分布类型 | {distribution_type} | {特异性/选择性/广泛} |

### 5.3 关键组织安全性表达

| 关键器官 | 表达水平(TPM) | 风险等级 | 说明 |
|----------|---------------|----------|------|
| 心脏 | {heart_tpm} | {risk} | {note} |
| 肝脏 | {liver_tpm} | {risk} | {note} |
| 肾脏 | {kidney_tpm} | {risk} | {note} |
| 脑 | {brain_tpm} | {risk} | {note} |
| 肺 | {lung_tpm} | {risk} | {note} |

### 5.4 HPA表达数据

| 组织 | 表达水平 | 可靠性 | 抗体 |
|------|----------|--------|------|
| {tissue} | {level} | {reliability} | {antibody} |

### 5.5 表达谱解读（200字以上）

综合分析表达数据：
- 组织表达模式
- 疾病组织表达
- 安全性启示
- 生物标志物潜力

### 5.6 原始数据记录

```json
{phase1_expression_raw}
```

---

## 6. 疾病关联

**字数要求**: 800字以上

### 6.1 OpenTargets疾病关联

**疾病关联总数**: {disease_count}

#### 6.1.1 Top 20疾病关联

| 疾病名称 | EFO ID | 关联分数 | 证据来源 | 层级 |
|----------|--------|----------|----------|------|
| {disease_name} | {efo_id} | {score} | {source} | T1/T2/T3/T4 |

#### 6.1.2 治疗领域分布

| 治疗领域 | 疾病数 | 最强关联分数 |
|----------|--------|--------------|
| {therapeutic_area} | {count} | {max_score} |

### 6.2 遗传约束分析

| 指标 | 值 | 百分位 | 解读 |
|------|-----|--------|------|
| **pLI** | {pli} | {percentile} | {必需性解释} |
| **LOEUF** | {loeuf} | {percentile} | {负选择强度解释} |
| **Missense Z** | {missense_z} | {percentile} | {错义约束解释} |
| **pRec** | {prec} | - | {隐性遗传解释} |
| **oe_lof** | {oe_lof} | - | {LOF观察/期望比} |
| **oe_mis** | {oe_mis} | - | {错义观察/期望比} |

**遗传约束综合解读**（150字以上）:

### 6.3 GWAS证据

**GWAS信号总数**: {gwas_count}

#### 6.3.1 显著GWAS关联 (p < 5e-8)

| rsID | 性状 | P值 | OR/Beta | 染色体 | 位置 | 风险等位基因 |
|------|------|-----|---------|--------|------|--------------|
| {rs_id} | {trait} | {p_value} | {or} | {chr} | {pos} | {allele} |

#### 6.3.2 GWAS信号解读（100字以上）

### 6.4 ClinVar临床变异

#### 6.4.1 变异统计

| 临床意义 | 数量 | 百分比 |
|----------|------|--------|
| 致病性 (Pathogenic) | {pathogenic_count} | {percent}% |
| 可能致病 (Likely pathogenic) | {likely_pathogenic_count} | {percent}% |
| 良性 (Benign) | {benign_count} | {percent}% |
| 可能良性 (Likely benign) | {likely_benign_count} | {percent}% |
| 意义不明 (VUS) | {vus_count} | {percent}% |

#### 6.4.2 致病/可能致病变异详情

| 变异 | 临床意义 | 相关疾病 | 审核状态 | 条目ID |
|------|----------|----------|----------|--------|
| {variant} | {significance} | {disease} | {review_status} | {id} |

### 6.5 疾病关联综合解读（300字以上）

基于所有遗传学证据：
- 主要关联疾病
- 遗传证据强度
- 机制启示
- 验证建议

### 6.6 原始数据记录

```json
{phase2_disease_raw}
```

---

## 7. 可药性评估

**字数要求**: 1000字以上

### 7.1 OpenTargets可药性评估

| 药物模式 | 可药性状态 | Bucket | 详细评估 |
|----------|------------|--------|----------|
| 小分子 | {sm_status} | {sm_bucket} | {sm_assessment} |
| 抗体 | {ab_status} | {ab_bucket} | {ab_assessment} |
| PROTAC | {pr_status} | {pr_bucket} | {pr_assessment} |

**Bucket定义**:
- Bucket 1-3: 高可药性，有已知药物/活性化合物
- Bucket 4-5: 中等可药性，有结构/同源信息
- Bucket 6-7: 低可药性，需新模式

### 7.2 靶点开发水平 (Pharos TDL)

| 属性 | 值 |
|------|-----|
| TDL分类 | {tdl} |
| 靶点家族 | {family} |
| 新颖性评分 | {novelty} |
| 发表文献数 | {publication_count} |
| 描述 | {description} |

**TDL分类定义**:
- **Tclin**: 已批准药物靶点，最高置信度
- **Tchem**: 有小分子活性数据，良好可药性
- **Tbio**: 生物学研究充分，可能需要新模式
- **Tdark**: 研究不足，高新颖性潜力

### 7.3 DGIdb可药性类别

| 类别 | 来源 |
|------|------|
| {category} | {source} |

### 7.4 已批准药物

**已批准药物数量**: {approved_drug_count}

| 药物名称 | ChEMBL ID | 批准年份 | 适应症 | 作用机制 | 靶点作用 |
|----------|-----------|----------|--------|----------|----------|
| {drug_name} | {chembl_id} | {year} | {indication} | {moa} | {action} |

### 7.5 临床在研药物

**临床药物总数**: {clinical_drug_count}

| 药物名称 | 临床阶段 | 适应症 | 机制 | 开发企业 |
|----------|----------|--------|------|----------|
| {drug_name} | Phase {phase} | {indication} | {moa} | {company} |

### 7.6 ChEMBL生物活性数据

**活性记录总数**: {activity_count}

#### 7.6.1 高活性化合物 (pChEMBL >= 7)

| 化合物ID | SMILES | 活性类型 | 活性值 | pChEMBL | 检测类型 |
|----------|--------|----------|--------|---------|----------|
| {molecule_id} | {smiles} | {type} | {value} | {pchembl} | {assay} |

#### 7.6.2 活性分布统计

| pChEMBL范围 | 化合物数 | 占比 |
|--------------|----------|------|
| >= 9 | {count} | {percent}% |
| 7-9 | {count} | {percent}% |
| 5-7 | {count} | {percent}% |
| < 5 | {count} | {percent}% |

### 7.7 化学探针

**探针数量**: {probe_count}

| 探针名称 | 来源 | 验证状态 | 推荐用途 |
|----------|------|----------|----------|
| {probe_name} | {source} | {validation} | {use_case} |

### 7.8 DepMap基因依赖性

| 指标 | 值 |
|------|-----|
| 必需细胞系数 | {essential_count} |
| 普遍必需细胞系数 | {common_essential_count} |
| 非必需细胞系数 | {non_essential_count} |

### 7.9 可药性综合评估（300字以上）

综合分析：
- 最优药物模式
- 竞争格局
- 差异化机会
- 开发策略建议

### 7.10 原始数据记录

```json
{phase3_druggability_raw}
```

---

## 8. 安全性评估

**字数要求**: 600字以上

### 8.1 安全性风险汇总

| 风险等级 | 评估依据 |
|----------|----------|
| **{risk_level}** | {risk_basis} |

### 8.2 OpenTargets安全性档案

**已识别风险数**: {liability_count}

| 风险类型 | 描述 | 严重程度 | 来源 |
|----------|------|----------|------|
| {liability_type} | {description} | {severity} | {source} |

### 8.3 小鼠模型表型

**模型数量**: {model_count}

| 模型类型 | 表型 | 严重程度 | 来源 |
|----------|------|----------|------|
| {model_type} | {phenotype} | {severity} | {source} |

**关键表型解读**:
- 致死表型: {lethal_phenotypes}
- 可存活表型: {viable_phenotypes}
- 对安全性的启示

### 8.4 关键组织表达安全性

| 组织 | 表达水平 | 安全风险 | 风险等级 | 监测建议 |
|------|----------|----------|----------|----------|
| 心脏 | {level} | {risk} | {grade} | {monitoring} |
| 肝脏 | {level} | {risk} | {grade} | {monitoring} |
| 肾脏 | {level} | {risk} | {grade} | {monitoring} |
| 脑 | {level} | {risk} | {grade} | {monitoring} |
| 肺 | {level} | {risk} | {grade} | {monitoring} |

### 8.5 基因必需性分析

| 指标 | 值 | 安全性意义 |
|------|-----|------------|
| pLI | {pli} | {safety_implication} |
| DepMap必需性 | {depmap_essential} | {safety_implication} |

### 8.6 同源物与选择性风险

| 同源物 | 相似度 | 选择性风险 | 缓解策略 |
|--------|--------|------------|----------|
| {homolog} | {similarity}% | {risk} | {strategy} |

### 8.7 安全性综合评估（200字以上）

综合所有安全性数据：
- 主要安全风险
- 风险可控性
- 监测建议
- 临床开发注意事项

### 8.8 原始数据记录

```json
{phase4_safety_raw}
```

---

## 9. 文献与研究

**字数要求**: 500字以上

### 9.1 发表统计

| 指标 | 数值 |
|------|------|
| 总发表量 | {total_count} |
| 近5年发表 | {last_5_years} |
| 近10年发表 | {last_10_years} |
| 年均发表 | {annual_average} |
| PubMed检索 | {pubmed_count} |

### 9.2 发表趋势分析

| 年份 | 发表量 | 趋势 |
|------|--------|------|
| {year} | {count} | {trend} |

**趋势解读**: {trend_analysis}

### 9.3 关键文献 - Top 20

| PMID | 标题 | 年份 | 期刊 | 证据层级 |
|------|------|------|------|----------|
| {pmid} | {title} | {year} | {journal} | T1/T2/T3/T4 |

### 9.4 高影响因子文献

筛选标准：Nature, Science, Cell, Nature Medicine, NEJM等

| 标题 | 期刊 | 年份 | 主要发现 |
|------|------|------|----------|
| {title} | {journal} | {year} | {finding} |

### 9.5 临床指南关联

| 指南名称 | 来源 | 年份 | 相关性 |
|----------|------|------|--------|
| {guideline} | {source} | {year} | {relevance} |

### 9.6 研究热点分析（100字以上）

基于文献分析：
- 主要研究方向
- 研究热点演变
- 未来研究趋势

### 9.7 原始数据记录

```json
{phase5_literature_raw}
```

---

## 10. 临床开发

**字数要求**: 300字以上

### 10.1 临床试验汇总

| 阶段 | 试验数 | 状态 |
|------|--------|------|
| Phase I | {phase1_count} | {status} |
| Phase II | {phase2_count} | {status} |
| Phase III | {phase3_count} | {status} |
| Phase IV | {phase4_count} | {status} |

### 10.2 临床试验详情

| NCT ID | 标题 | 阶段 | 状态 | 适应症 | 开始日期 |
|--------|------|------|------|--------|----------|
| {nct_id} | {title} | {phase} | {status} | {indication} | {start_date} |

### 10.3 临床开发解读（100字以上）

---

## 11. 综合评分卡

### 11.1 评分明细

| 维度 | 子维度 | 得分 | 满分 | 计算依据 | 数据来源 |
|------|--------|------|------|----------|----------|
| 疾病关联 | 遗传证据 | {score} | 10 | {basis} | gnomAD/GWAS/ClinVar |
| 疾病关联 | 文献证据 | {score} | 10 | {basis} | PubMed |
| 疾病关联 | 通路证据 | {score} | 10 | {basis} | Reactome/GO |
| 可药性 | 结构可及性 | {score} | 10 | {basis} | PDB/AlphaFold |
| 可药性 | 化合物资源 | {score} | 10 | {basis} | ChEMBL |
| 可药性 | 靶点类别 | {score} | 5 | {basis} | Pharos TDL |
| 安全性 | 组织选择性 | {score} | 5 | {basis} | GTEx |
| 安全性 | 遗传验证 | {score} | 10 | {basis} | Mouse models/pLI |
| 安全性 | 不良事件 | {score} | 5 | {basis} | Safety profile |
| 临床先例 | 临床阶段 | {score} | 15 | {basis} | Drugs/Clinical trials |
| 验证证据 | 功能研究 | {score} | 5 | {basis} | DepMap |
| 验证证据 | 疾病模型 | {score} | 5 | {basis} | Pathways/PPIs |

### 11.2 维度得分雷达图描述

```
疾病关联: ████████████████████░░░░░░░░░░ {score}/30
可药性:   ████████████████░░░░░░░░░░░░░░ {score}/25
安全性:   ████████████████░░░░░░░░░░░░░░ {score}/20
临床先例: ███████████░░░░░░░░░░░░░░░░░░░ {score}/15
验证证据: ████████░░░░░░░░░░░░░░░░░░░░░░ {score}/10
```

### 11.3 评分方法说明

详细说明每个维度的评分标准和方法...

---

## 12. 建议与下一步

**字数要求**: 500字以上

### 12.1 推荐验证实验

| 优先级 | 实验类型 | 目的 | 预期结果 | 预估周期 |
|--------|----------|------|----------|----------|
| 🔴 高 | {experiment} | {purpose} | {expected_result} | {timeline} |
| 🟡 中 | {experiment} | {purpose} | {expected_result} | {timeline} |
| 🟢 低 | {experiment} | {purpose} | {expected_result} | {timeline} |

### 12.2 推荐工具化合物

| 化合物 | 用途 | 活性 | 可用性 | 获取方式 |
|--------|------|------|--------|----------|
| {compound} | {use} | {activity} | {availability} | {source} |

### 12.3 生物标志物策略

**预测性生物标志物**:
- 患者筛选标志物: {predictive_marker}
- 疗效监测标志物: {monitoring_marker}

**药效学生物标志物**:
- 机制相关标志物: {pd_marker}

### 12.4 风险缓解策略

| 风险 | 严重程度 | 缓解策略 | 可行性 |
|------|----------|----------|--------|
| {risk} | {severity} | {mitigation} | {feasibility} |

### 12.5 开发路径建议（200字以上）

基于所有分析，给出：
- 短期行动建议（1-3月）
- 中期行动建议（3-12月）
- Go/No-Go决策点
- 关键里程碑

---

## 13. 数据来源与方法

**字数要求**: 400字以上

### 13.1 工具与数据库完整列表

| 数据库 | 用途 | 查询状态 | 数据量 | 查询日期 |
|--------|------|----------|--------|----------|
| UniProt | 蛋白信息 | ✓ 成功 | {count}条 | {date} |
| Ensembl | 基因信息 | ✓ 成功 | {count}条 | {date} |
| OpenTargets | 疾病关联/可药性 | ✓ 成功 | {count}条 | {date} |
| ChEMBL | 化合物活性 | ✓ 成功 | {count}条 | {date} |
| gnomAD | 遗传约束 | ✓ 成功 | {count}条 | {date} |
| GTEx | 基因表达 | ✓ 成功 | {count}条 | {date} |
| STRING | 蛋白相互作用 | ✓ 成功 | {count}条 | {date} |
| Reactome | 通路信息 | ✓ 成功 | {count}条 | {date} |
| InterPro | 结构域 | ✓ 成功 | {count}条 | {date} |
| Pharos | TDL分类 | ✓ 成功 | {count}条 | {date} |
| ClinVar | 临床变异 | ✓ 成功 | {count}条 | {date} |
| GWAS Catalog | GWAS数据 | ✓ 成功 | {count}条 | {date} |
| PubMed | 文献数据 | ✓ 成功 | {count}条 | {date} |
| AlphaFold | 结构预测 | ✓ 成功 | {count}条 | {date} |
| HPA | 蛋白表达 | ✓ 成功 | {count}条 | {date} |
| DepMap | 基因依赖性 | ✓ 成功 | {count}条 | {date} |

### 13.2 数据收集日志

```
{collection_log}
```

### 13.3 评分方法

**评分公式说明**:
- 疾病关联 (30分) = 遗传证据(10) + 文献证据(10) + 通路证据(10)
- 可药性 (25分) = 结构可及性(10) + 化合物资源(10) + 靶点类别(5)
- 安全性 (20分) = 组织选择性(5) + 遗传验证(10) + 不良事件(5)
- 临床先例 (15分) = 临床阶段评分
- 验证证据 (10分) = 功能研究(5) + 疾病模型(5)

### 13.4 数据质量评估

| 数据类型 | 覆盖度 | 完整性 | 置信度 | 备注 |
|----------|--------|--------|--------|------|
| 结构数据 | {coverage}% | {completeness}% | {confidence} | {note} |
| 表达数据 | {coverage}% | {completeness}% | {confidence} | {note} |
| 疾病关联 | {coverage}% | {completeness}% | {confidence} | {note} |
| 可药性数据 | {coverage}% | {completeness}% | {confidence} | {note} |
| 安全性数据 | {coverage}% | {completeness}% | {confidence} | {note} |

---

## 14. 数据缺口与局限性

### 14.1 数据缺口汇总表

| 章节 | 预期数据 | 实际数据 | 缺失原因 | 替代来源 | 影响 |
|------|----------|----------|----------|----------|------|
| {section} | {expected} | {actual} | {reason} | {alternative} | {impact} |

### 14.2 方法局限性

1. **数据时效性**: 数据收集于{date}，可能不反映最新研究进展
2. **API可用性**: 部分API可能返回空数据或错误
3. **数据质量**: 依赖公开数据库的数据质量
4. **解读局限**: 自动解读可能遗漏特定领域的专业知识

### 14.3 建议补充数据

| 数据类型 | 获取途径 | 优先级 | 预估成本 |
|----------|----------|--------|----------|
| {data_type} | {source} | {priority} | {cost} |

---

## 完整性检查清单

### 必须完成项

- [ ] 所有标识符已解析并验证
- [ ] PPI数据 >= 20条或已说明原因
- [ ] 表达数据覆盖主要组织(>= 30个)
- [ ] 疾病关联包含Top 10
- [ ] 遗传约束全部4个核心分数已获取
- [ ] 可药性评估所有模式
- [ ] 安全性评估关键组织
- [ ] 文献分析包含趋势
- [ ] 评分计算完成
- [ ] 负结果已记录
- [ ] 证据分级已标注
- [ ] 所有章节达到字数要求

### 质量检查项

- [ ] 所有数据来自原始JSON文件
- [ ] 无编造或估算数据
- [ ] 专业术语使用正确
- [ ] 表格格式完整
- [ ] 引用来源明确

---

**报告生成完成**

*本报告由 Target-GO 靶点评估系统生成*
*报告版本: v2.0*
*总字数要求: 15000字以上（约10页）*