---
name: target-evaluation
description: 靶点验证助手 - 从生物学情报到验证决策的一站式评估。整合蛋白信息、疾病关联、可成药性、安全性和临床数据，生成量化评分(0-100)和GO/NO-GO建议。自动发现疾病关联，支持多药物模式评估(10+模式)，输出集成报告和可视化图表。用于靶点验证、优先级排序、竞争分析。
---

# 靶点验证流程 (Target Validation Pipeline)

在投入湿实验前，使用多维度计算证据验证药物靶点假设。生成量化靶点验证评分(0-100)，优先层级分类和GO/NO-GO建议。

**报告语言**: 中文 (Chinese)

## 核心改进

1. **中文报告**: 所有英文数据库内容通过LLM转换为中文
2. **简洁展示**: 少量数据(≤1条)的表格用概述形式表示
3. **代码分离**: 所有代码逻辑在scripts目录，markdown仅包含指导说明
4. **原始数据**: ToolUniverse工具输出直接保存，非必要不做后处理
5. **分章节生成**: 报告按三个部分生成，Executive Summary最后生成
6. **无附录**: 删除Appendices部分，关键信息整合到正文
7. **图表渲染**: 使用matplotlib生成可视化图表，替代ASCII图表

---

## 工作流程 (Workflow)

```
Phase -1: 工具验证 (验证参数)
Phase  0: 靶点消歧 (解析所有标识符)
Phase  1: Open Targets基础数据 (主数据源，首先查询)
Phase  2: UniProt详细信息
Phase  3: 结构与结构域 (PDB, AlphaFold, InterPro)
Phase  4: 功能与通路 (GO, Reactome, KEGG)
Phase  5: 蛋白相互作用 (STRING, IntAct, BioGRID)
Phase  6: 表达谱 (GTEx, HPA)
Phase  7: 遗传变异 (gnomAD, ClinVar, cBioPortal)
Phase  8: 疾病关联评分 (0-30分)
Phase  9: 可成药性评估 (0-25分)
Phase 10: 安全性分析 (0-20分)
Phase 11: 临床先例 (0-15分)
Phase 12: 验证证据 (0-10分)
Phase 13: 综合评分与合成
Phase 14: 生成报告 (三部分 + Executive Summary)
```

---

## 脚本结构 (Script Structure)

所有代码逻辑位于 `scripts/` 目录:

| 脚本文件 | 功能 | 对应章节 |
|---------|------|---------|
| `phase0_disambiguation.py` | 靶点标识符解析 | Phase 0 |
| `phase1_foundation.py` | Open Targets基础数据 | Phase 1 |
| `phases2_7_data_collection.py` | 核心数据收集 | Phases 2-7 |
| `phases8_12_scoring.py` | 评分计算 | Phases 8-12 |
| `visualization.py` | matplotlib可视化 | 图表生成 |
| `report_generator.py` | 报告生成 | 报告输出 |
| `run_validation.py` | 主运行脚本 | 流程编排 |

---

## 数据完整性要求 (Data Completeness Requirements)

**评分前必须验证以下最低要求:**
- ✅ 所有标识符已解析 (UniProt, Ensembl, ChEMBL)
- ✅ Open Targets基础数据已查询 (疾病、可成药性、安全性、药物)
- ✅ 至少5个疾病关联及其评分
- ✅ gnomAD约束评分(全部4项)或记录为不可用
- ✅ GTEx或HPA表达数据
- ✅ 至少10个PPI或说明原因
- ✅ 至少10个通路或说明原因

**如果未满足最低要求:**
1. 尝试备用工具 (见备用链部分)
2. 在数据缺口表中记录
3. 使用可用数据继续，注明限制

---

## Phase -1: 工具参数验证

**在调用不熟悉的工具前验证参数。** 许多API文档是错误的。

### 关键参数修正表

| 工具 | 错误参数 | 正确参数 | 说明 |
|------|---------|---------|------|
| `UniProt_id_mapping` | `_from`, `to` | `from_db`, `to_db`, `ids` | 三个参数都必需 |
| `Reactome_map_uniprot_to_pathways` | `id` | `uniprot_id` | 使用 `uniprot_id` |
| `ensembl_get_xrefs` | `gene_id` | `id` | 仅 `id` |
| `GTEx_get_median_gene_expression` | `operation="median"` | `operation="get_median_gene_expression"` | 完整操作名 |
| `OpenTargets_get_publications_by_target_ensemblId` | `ensemblId` | `entityId` | 非ensemblId |
| `OpenTargets_get_associated_drugs_by_target_ensemblId` | 仅`ensemblId` | `ensemblId` + `size` | size必需 |
| `STRING_get_protein_interactions` | 单个ID字符串 | `protein_ids` (列表), `species` | 列表格式 |
| `intact_get_interactions` | 基因符号 | `identifier` (UniProt登录号) | UniProt ID |
| `HPA_get_comprehensive_gene_details_by_ensembl_id` | 仅`ensembl_id` | `ensembl_id` + `include_images` + `include_antibodies` + `include_expression` | 4个参数都必需 |
| `HPA_get_rna_expression_by_source` | `ensembl_id` | `gene_name` + `source_type` + `source_name` | 3个参数都必需 |
| `alphafold_get_prediction` | `uniprot_accession` | `qualifier` | 使用qualifier |
| `ChEMBL_get_target_activities` | `target_chembl_id` | `target_chembl_id__exact` | 双下划线 |
| `MyGene_query_genes` | `q` | `query` | 使用 `query` |
| `gnomad_get_gene_constraints` | `gene_id` | `gene_symbol` | 基因符号 |
| `InterPro_get_protein_domains` | `uniprot_accession` | `protein_id` | 使用 `protein_id` |
| `gwas_get_snps_for_gene` | `gene` | `mapped_gene` | 使用 `mapped_gene` |
| `ensembl_lookup_gene` | `id` | `gene_id` + `species="homo_sapiens"` | 两个参数都必需 |
| SOAP工具 (GPCRdb, DisGeNET) | 缺失 | `operation` | 必需的第一个参数 |

---

## Phase 0: 靶点消歧

**目标**: 在任何分析前解析靶点的所有标识符。

### 需要解析的标识符

- `symbol`: 基因符号
- `uniprot`: UniProt登录号
- `ensembl`: Ensembl基因ID
- `ensembl_versioned`: 版本化的Ensembl ID (GTEx关键)
- `entrez`: Entrez基因ID
- `chembl_target`: ChEMBL靶点ID
- `synonyms`: 别名列表
- `target_class`: 靶点类别
- `is_gpcr`: 是否为GPCR

### 工具执行顺序

| 步骤 | 工具 | 参数 | 输出 |
|------|------|------|------|
| 1 | `MyGene_query_genes` | `query=<target>` | symbol, ensembl, entrez |
| 2 | `UniProt_id_mapping` | `from_db='Gene_Name'`, `to_db='UniProtKB'`, `ids=<symbol>` | uniprot |
| 3 | `ensembl_lookup_gene` | `gene_id=<ensembl>`, `species="homo_sapiens"` | ensembl_versioned, description |
| 4 | `ChEMBL_search_targets` | `query=<symbol>` | chembl_target |
| 5 | `UniProt_get_alternative_names_by_accession` | `accession=<uniprot>` | synonyms |

### 版本化ID备用 (GTEx关键)

GTEx通常需要版本化的ID (如 `ENSG00000146648.18`):

如果存在ensembl ID，通过ensembl_lookup_gene获取版本号，组装成`ENSG###.version`格式。

### GPCR检测

检查是否为GPCR以启用专门处理:
- 使用GPCRdb_get_protein验证
- entry_name格式: `{symbol.lower()}_human`

---

## Phase 1: Open Targets基础数据 (主数据源)

**首先查询Open Targets** - 它为所有后续阶段提供基线数据。

### 基础查询 (全部执行)

| 查询 | 工具 | 参数 | 用途 |
|------|------|------|------|
| 1 | `OpenTargets_get_diseases_phenotypes_by_target_ensemblId` | `ensemblId` | 疾病关联 |
| 2 | `OpenTargets_get_target_tractability_by_ensemblId` | `ensemblId` | 可成药性 |
| 3 | `OpenTargets_get_target_safety_profile_by_ensemblId` | `ensemblId` | 安全性 |
| 4 | `OpenTargets_get_target_interactions_by_ensemblId` | `ensemblId` | PPI网络 |
| 5 | `OpenTargets_get_target_gene_ontology_by_ensemblId` | `ensemblId` | GO注释 |
| 6 | `OpenTargets_get_publications_by_target_ensemblId` | **`entityId`** | 文献 |
| 7 | `OpenTargets_get_biological_mouse_models_by_ensemblId` | `ensemblId` | KO表型 |
| 8 | `OpenTargets_get_chemical_probes_by_target_ensemblId` | `ensemblId` | 化学探针 |
| 9 | `OpenTargets_get_associated_drugs_by_target_ensemblId` | `ensemblId` + **`size`** | 已知药物 |
| 10 | `OpenTargets_get_target_classes_by_ensemblId` | `ensemblId` | 靶点类别 |
| 11 | `OpenTargets_get_target_homologues_by_ensemblId` | `ensemblId` | 同源蛋白 |

### 自动疾病发现

如果未提供疾病参数，从Open Targets提取前3个关联疾病:

1. 按关联评分排序
2. 过滤掉宽泛的测量/属性术语
3. 返回前3个相关疾病

---

## Phases 2-7: 核心数据收集

### Phase 2: UniProt详细信息

查询UniProt获取蛋白详细信息:
- `UniProt_get_entry_by_accession`: 完整条目(包含PDB交叉引用)
- `UniProt_get_function_by_accession`: 功能描述
- `UniProt_get_subcellular_location_by_accession`: 亚细胞定位
- `UniProt_get_recommended_name_by_accession`: 推荐名称

### Phase 3: 结构与结构域

**3步结构搜索链**:

1. **UniProt PDB交叉引用** (最可靠) - 从UniProt条目提取PDB引用
2. **AlphaFold** (始终可用) - 使用`alphafold_get_prediction`和`alphafold_get_summary`
3. **结构域** - 使用`InterPro_get_protein_domains` (参数: `protein_id`)

**GPCR特殊处理**: 如果是GPCR，额外查询GPCRdb_get_structures

### Phase 4: 功能与通路

| 工具 | 参数 | 说明 |
|------|------|------|
| `Reactome_map_uniprot_to_pathways` | `uniprot_id` (非`id`) | Reactome通路 |
| `kegg_get_gene_info` | `gene_id` | KEGG通路 |
| `WikiPathways_search` | `query` | WikiPathways |
| `GO_get_annotations_for_gene` | `gene_id` | GO注释 |

**最低要求**: 10个通路或说明原因。

### Phase 5: 蛋白相互作用

**PPI查询备用链**:

```
STRING (protein_ids列表格式) → IntAct (UniProt登录号) → BioGRID (基因符号) → OpenTargets interactions
```

**最低要求**: 20个相互作用蛋白或说明原因。

### Phase 6: 表达谱

**GTEx版本化ID备用**:

```
GTEx (版本化ID) → GTEx (非版本化ID) → HPA comprehensive → HPA RNA
```

**关键参数**:
- GTEx: `gencode_id` + `operation="get_median_gene_expression"`
- HPA comprehensive: `ensembl_id` + `include_images=False` + `include_antibodies=False` + `include_expression=True`
- HPA RNA: `gene_name` + `source_type='tissue'` + `source_name='all'`

**关键组织检查**: heart, liver, kidney, brain, bone marrow

**最低要求**: 前10个组织的TPM值。

### Phase 7: 遗传变异

**约束评分 (gnomAD)**:

使用`gnomad_get_gene_constraints`获取全部4项评分: pLI, LOEUF, missense Z, pRec

**临床变异**:
- `clinvar_search_variants`: 临床变异
- `civic_get_variants_by_gene`: CIViC变异
- `cBioPortal_get_mutations`: 癌症突变

---

## Phases 8-12: 评分系统

### 评分维度

| 维度 | 满分 | 子维度 |
|------|------|--------|
| **疾病关联** | 30 | 遗传(10) + 文献(10) + 通路(10) |
| **可成药性** | 25 | 结构(10) + 化学物质(10) + 靶点类别(5) |
| **安全性** | 20 | 表达(5) + 遗传验证(10) + ADR(5) |
| **临床先例** | 15 | 基于最高临床阶段 |
| **验证证据** | 10 | 功能研究(5) + 疾病模型(5) |

### 优先层级

| 分数 | 层级 | 建议 | 行动 |
|------|------|------|------|
| **80-100** | Tier 1 | GO | 高度验证 - 放心推进 |
| **60-79** | Tier 2 | CONDITIONAL GO | 良好靶点 - 需重点验证 |
| **40-59** | Tier 3 | CAUTION | 中等风险 - 需大量验证 |
| **0-39** | Tier 4 | NO-GO | 高风险 - 考虑替代 |

### 证据分级系统

| 层级 | 符号 | 标准 | 示例 |
|------|------|------|------|
| **T1** | [T1] | 直接机制/临床证据 | FDA批准药物、晶体结构、患者突变 |
| **T2** | [T2] | 功能研究/模式生物 | siRNA表型、小鼠KO、生化实验 |
| **T3** | [T3] | 关联/筛选/计算 | GWAS命中、DepMap必要性、表达相关 |
| **T4** | [T4] | 提及/综述/预测 | 综述文章、数据库注释、AlphaFold预测 |

---

## 备用链 (Fallback Chains)

当主工具失败时，按顺序尝试备用:

### 表达数据

```
GTEx (版本化ID) → GTEx (非版本化ID) → HPA comprehensive → HPA RNA → 记录不可用
```

### 化学物质

```
ChEMBL_get_target_activities → BindingDB_get_ligands_by_uniprot → DGIdb_get_gene_info → 记录缺口
```

### PPI数据

```
STRING → IntAct → BioGRID → OpenTargets interactions → 记录缺口
```

### 约束评分

```
gnomAD_get_gene_constraints → OpenTargets constraint → 记录不可用
```

### 文献

```
PubMed_search_articles → EuropePMC_search_articles → PubTator3_LiteratureSearch → 记录缺口
```

### 通路

```
Reactome_map_uniprot_to_pathways → OpenTargets GO → MyGene pathways → 仅使用GO
```

---

## 报告生成

报告分三部分生成，**Executive Summary最后生成**。

### 报告结构

1. **Executive Summary** (最后生成)
   - 评分卡
   - 层级与建议
   - 主要发现
   - 关键风险

2. **Part A: 靶点情报 (Target Intelligence)** (第1部分)
   - 1. 靶点标识符
   - 2. 基本信息
   - 3. 结构生物学
   - 4. 功能与通路
   - 5. 蛋白相互作用
   - 6. 表达谱
   - 7. 遗传变异

3. **Part B: 验证评估 (Validation Assessment)** (第2部分)
   - 8. 疾病关联评分
   - 9. 可成药性评估
   - 10. 安全性分析
   - 11. 临床先例
   - 12. 验证证据
   - 13. 综合评分

4. **Part C: 综合与建议 (Synthesis & Recommendations)** (第3部分)
   - 14. 验证路线图
   - 15. 工具化合物
   - 16. 生物标志物策略
   - 17. 主要风险与缓解措施

### 可视化要求

使用matplotlib生成以下可视化:

1. **验证评分条形图** - 显示各维度得分
2. **组织表达热图** - 显示各组织TPM值，标注关键组织
3. **疾病关联图表** - 显示前10个疾病关联评分
4. **临床时间线** - 显示已批准药物和临床试验

### 数据展示规则

- **表格**: 数据≥2行时使用表格格式
- **概述**: 数据≤1行时使用列表/概述格式
- **缺失数据**: 明确标注"暂无数据"

---

## 完整性验证

报告完成前验证所有项目:

### 数据最低要求检查

- [ ] PPIs: ≥20个相互作用蛋白或说明原因
- [ ] 表达: 前10个组织的TPM值或明确"不可用"
- [ ] 疾病: 前10个关联及其评分或"无关联"
- [ ] 约束: 全部4项评分或"不可用"
- [ ] 可成药性: 所有模式评估;探针和药物列出或"无"
- [ ] 文献: 总数+5年趋势+3-5篇关键论文

### 负面结果记录

- [ ] 空工具结果明确记录(不空白)
- [ ] 失败工具及备用链记录
- [ ] "无数据"部分注明影响

### 证据质量

- [ ] Executive Summary疾病声明有T1-T4分级
- [ ] 疾病关联表有T1-T4分级
- [ ] 关键论文表有证据层级
- [ ] 每节末尾有证据摘要

### 来源归属

- [ ] 每个数据点有来源工具/数据库引用
- [ ] 每节末尾有来源摘要

---

## 参考文件

- [SCORING_CRITERIA.md](SCORING_CRITERIA.md) - 详细评分矩阵
- [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md) - 报告模板
- [TOOL_REFERENCE.md](TOOL_REFERENCE.md) - 完整工具参考
- [EVIDENCE_GRADING.md](EVIDENCE_GRADING.md) - T1-T4层级定义
- [EXAMPLES.md](EXAMPLES.md) - 示例 (EGFR, KRAS等)
- [scripts/](scripts/) - Python实现脚本