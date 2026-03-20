# Target-GO 工具参考

验证过的工具参数、已知修正、后备链和模式特定指导。

---

## 已知参数修正

| 工具 | 错误参数 | 正确参数 | 备注 |
|------|----------|----------|------|
| `ensembl_lookup_gene` | `id` | `gene_id` + `species="homo_sapiens"` | species 必需 |
| `Reactome_map_uniprot_to_pathways` | `id` | `uniprot_id` | 参数名称修正 |
| `ensembl_get_xrefs` | `gene_id` | `id` | 参数名称修正 |
| `GTEx_get_median_gene_expression` | `operation="median"` | `operation="get_median_gene_expression"` | operation 值必须是固定字符串 |
| `OpenTargets_get_diseases_phenotypes_by_target_ensembl` | - | `ensemblId` | 工具名以 `ensembl` 结尾 |
| `OpenTargets_*_by_ensemblID` | `ensemblID` | `ensemblId` | 大部分用驼峰式 |
| `OpenTargets_get_publications_*` | `ensemblId` | `entityId` | 参数名不同 |
| `OpenTargets_get_associated_drugs_*` | 仅 `ensemblId` | `ensemblId` + `size` | size 必需 |
| `OpenTargets_get_target_id_description_by_name` | `name` | `targetName` | 参数名修正 |
| `MyGene_query_genes` | `q` | `query` | 参数名修正 |
| `STRING_get_protein_interactions` | 单个ID字符串 | `protein_ids` (数组), `species=9606` | 数组格式 |
| `intact_get_interactions` | 基因符号 | `identifier` (UniProt accession) | 使用UniProt ID |
| `ChEMBL_get_target_activities` | `target_chembl_id` | `target_chembl_id__exact` | 双下划线 |
| `UniProt_get_function_by_accession` | 返回字典 | 返回**字符串列表** | 返回格式 |
| `PubMed_search_articles` | 返回 `{articles: [...]}` | 返回**字典列表** | 返回格式 |
| `HPA_get_rna_expression_by_source` | 仅 `ensembl_id` | `gene_name` + `source_type` + `source_name` | 三个参数均必需 |
| `alphafold_get_summary` | `uniprot_id` | `qualifier` | 参数名修正 |
| `alphafold_get_prediction` | `uniprot_accession` | `qualifier` | 参数名修正 |
| `InterPro_get_protein_domains` | `uniprot_accession` | `protein_id` | 参数名修正 |
| `GO_get_annotations_for_gene` | `gene_symbol` | `gene_id` | 参数名修正 |
| `gwas_get_snps_for_gene` | `gene_symbol` | `mapped_gene` | 参数名修正 |
| `DGIdb_get_gene_druggability` | `gene_symbol` (字符串) | `genes` (数组) | 数组格式 |
| `drugbank_get_targets_*` | 简单参数 | `query`, `case_sensitive`, `exact_match`, `limit` | 四个参数均必需 |
| `search_clinical_trials` | 多个参数 | `query_term` | 必需参数 |
| `gnomad_get_gene_constraints` | `gene_id` | `gene_symbol` | 使用基因符号 |
| `DepMap_get_gene_dependencies` | `gene_id` | `gene_symbol` | 使用基因符号 |
| `BindingDB_get_ligands_by_uniprot` | 仅 `uniprot` | `uniprot` + `affinity_cutoff` | affinity 单位 nM |
| `Pharos_get_target` | 无 | `gene` 或 `uniprot` | 二选一 |

---

## 后备链

当主工具失败时，按顺序使用后备工具：

| 主工具 | 后备 1 | 后备 2 | 全部失败处理 |
|--------|--------|--------|--------------|
| `OpenTargets_get_diseases_phenotypes_*` | `CTD_get_gene_diseases` | PubMed 检索 | 在报告中注明 |
| `GTEx_get_median_gene_expression` (版本化) | GTEx (非版本化) | `HPA_search_genes_by_query` | 记录数据缺口 |
| `ChEMBL_get_target_activities` | `BindingDB_get_ligands_by_uniprot` | `DGIdb_get_gene_info` | 在报告中注明 |
| `gnomad_get_gene_constraints` | `OpenTargets_get_target_constraint_info_*` | - | 注明不可用 |
| `Reactome_map_uniprot_to_pathways` | `OpenTargets_get_target_gene_ontology_*` | - | 仅使用GO |
| `STRING_get_protein_interactions` | `intact_get_interactions` | `OpenTargets interactions` | 在报告中注明 |
| `ProteinsPlus_predict_binding_sites` | `alphafold_get_prediction` | 文献口袋信息 | 注明局限性 |

---

## 各阶段工具列表

### Phase 0: 靶点消歧解析

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `MyGene_query_genes` | 初始ID解析 | `query` |
| `UniProt_get_entry_by_accession` | 蛋白详情 | `accession` |
| `ensembl_lookup_gene` | Ensembl ID + 版本 | `gene_id`, `species="homo_sapiens"` |
| `ensembl_get_xrefs` | 交叉引用 | `id` |
| `OpenTargets_get_target_id_description_by_name` | OT 靶点信息 | `name` |
| `ChEMBL_search_targets` | ChEMBL 靶点 ID | `target_name` |
| `UniProt_get_function_by_accession` | 功能摘要 | `accession` |
| `UniProt_get_alternative_names_by_accession` | 别名（碰撞检测） | `accession` |

### Phase 1: 基础信息收集

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `UniProt_get_entry_by_accession` | 蛋白信息 | `accession` |
| `UniProt_get_sequence_by_accession` | 序列 | `accession` |
| `UniProt_get_subcellular_location_by_accession` | 亚细胞定位 | `accession` |
| `InterPro_get_protein_domains` | 结构域 | `uniprot_accession` |
| `alphafold_get_prediction` | AlphaFold 预测 | `qualifier` |
| `alphafold_get_summary` | AlphaFold 摘要 | `uniprot_id` |
| `get_protein_metadata_by_pdb_id` | PDB 元数据 | `pdb_id` |
| `Reactome_map_uniprot_to_pathways` | 通路映射 | `id` |
| `GO_get_annotations_for_gene` | GO 注释 | `gene_symbol` |
| `STRING_get_protein_interactions` | PPI 网络 | `protein_ids` (数组), `species=9606` |
| `intact_get_interactions` | 实验PPI | `identifier` (UniProt) |
| `GTEx_get_median_gene_expression` | 组织表达 | `gencode_id`, `operation="median"` |
| `HPA_get_comprehensive_gene_details_by_ensembl_id` | HPA 综合信息 | `ensembl_id` |

### Phase 2: 疾病关联分析

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `OpenTargets_get_diseases_phenotypes_by_target_ensemblId` | 疾病关联 | `ensemblId` |
| `OpenTargets_target_disease_evidence` | 详细证据 | `efoId`, `ensemblId` |
| `gwas_get_snps_for_gene` | GWAS SNP | `gene_symbol` |
| `gwas_search_studies` | GWAS 研究 | `query` |
| `gnomad_get_gene_constraints` | 遗传约束 | `gene_symbol` |
| `clinvar_search_variants` | ClinVar 变异 | `gene` |
| `DisGeNET_search_gene` | 疾病关联分数 | `gene` |
| `CTD_get_gene_diseases` | CTD 疾病关联 | `gene_symbol` |

### Phase 3: 可药性评估

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `OpenTargets_get_target_tractability_by_ensemblId` | 可药性评估 | `ensemblId` |
| `OpenTargets_get_target_classes_by_ensemblId` | 靶点分类 | `ensemblId` |
| `Pharos_get_target` | TDL 分类 | `gene` 或 `uniprot` |
| `DGIdb_get_gene_druggability` | 可药性类别 | `gene_symbol` |
| `ChEMBL_search_targets` | ChEMBL 靶点搜索 | `target_name` |
| `ChEMBL_get_target_activities` | 生物活性数据 | `target_chembl_id__exact` |
| `BindingDB_get_ligands_by_uniprot` | 配体数据 | `uniprot`, `affinity_cutoff` |
| `PubChem_search_assays_by_target_gene` | HTS 测定 | `gene_symbol` |
| `OpenTargets_get_chemical_probes_by_target_ensemblId` | 化学探针 | `ensemblId` |
| `OpenTargets_get_associated_drugs_by_target_ensemblId` | 已知药物 | `ensemblId`, `size` |
| `DepMap_get_gene_dependencies` | 必需性筛选 | `gene_symbol` |

### Phase 4: 安全性评估

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `OpenTargets_get_target_safety_profile_by_ensemblId` | 安全性档案 | `ensemblId` |
| `GTEx_get_median_gene_expression` | 组织表达 | `gencode_id`, `operation="median"` |
| `HPA_search_genes_by_query` | HPA 基因搜索 | `search_query` |
| `OpenTargets_get_biological_mouse_models_by_ensemblId` | KO 表型 | `ensemblId` |
| `OpenTargets_get_target_homologues_by_ensemblId` | 同源物 | `ensemblId` |
| `FDA_get_adverse_reactions_by_drug_name` | 不良反应 | `drug_name` |
| `FDA_get_boxed_warning_info_by_drug_name` | 黑框警告 | `drug_name` |

### Phase 5: 文献分析

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `PubMed_search_articles` | 文献检索 | `query`, `limit` |
| `PubMed_get_related` | 相关文献 | `pmid`, `limit` |
| `EuropePMC_search_articles` | 扩展检索 | `query` |
| `openalex_search_works` | 引用指标 | `query` |
| `OpenTargets_get_publications_by_target_ensemblId` | OT 文献 | `entityId` |

---

## 模式特定工具重点

### 小分子
- 重点: 结合口袋、ChEMBL化合物、Lipinski合规性
- 可药性: OpenTargets SM tractability bucket
- 结构: 与小分子配体的共晶结构
- 化合物: ChEMBL/BindingDB 的 IC50/Ki/Kd 数据

### 抗体
- 重点: 胞外结构域、细胞表面表达、糖基化
- 可药性: OpenTargets AB tractability bucket
- 结构: 胞外结构域结构、表位定位
- 表达: 疾病vs正常组织的表面表达

### PROTAC
- 重点: 胞内靶点、表面赖氨酸、E3连接酶邻近性
- 可药性: OpenTargets PROTAC tractability
- 结构: 连接子设计的全长结构
- 化合物: 已知结合剂 + E3连接酶结合剂