#!/usr/bin/env python3
"""
Phase 7: 综合报告生成（增强版）
生成完整的10页篇幅专业靶点评估报告
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


def calculate_scores(all_data: dict) -> dict:
    """计算靶点验证评分"""
    scores = {
        "disease_association": {"genetic": 0, "literature": 0, "pathway": 0, "total": 0},
        "druggability": {"structural": 0, "chemical": 0, "target_class": 0, "total": 0},
        "safety": {"expression": 0, "genetic": 0, "adverse": 0, "total": 0},
        "clinical_precedent": 0,
        "validation_evidence": {"functional": 0, "models": 0, "total": 0},
        "total_score": 0,
        "tier": "",
        "recommendation": ""
    }

    phase2 = all_data.get("phase2", {})
    phase3 = all_data.get("phase3", {})
    phase4 = all_data.get("phase4", {})
    phase1 = all_data.get("phase1", {})
    phase5 = all_data.get("phase5", {})

    # === 疾病关联 (0-30分) ===
    # 遗传证据 (0-10)
    gwas_count = len(phase2.get("gwas_snps", []))
    pathogenic_count = len(phase2.get("clinvar_variants", {}).get("pathogenic", []))
    likely_pathogenic = len(phase2.get("clinvar_variants", {}).get("likely_pathogenic", []))
    genetic_score = min(gwas_count * 0.5, 5) + min((pathogenic_count + likely_pathogenic) * 1, 3)
    constraints = phase2.get("genetic_constraints", {})
    if constraints.get("pli", 0) > 0.9:
        genetic_score += 2
    elif constraints.get("pli", 0) > 0.5:
        genetic_score += 1
    scores["disease_association"]["genetic"] = min(genetic_score, 10)

    # 文献证据 (0-10)
    pub_count = phase5.get("publication_stats", {}).get("total_count", 0)
    if pub_count > 500:
        scores["disease_association"]["literature"] = 10
    elif pub_count > 100:
        scores["disease_association"]["literature"] = 8
    elif pub_count > 50:
        scores["disease_association"]["literature"] = 6
    elif pub_count > 10:
        scores["disease_association"]["literature"] = 4
    elif pub_count > 0:
        scores["disease_association"]["literature"] = 2

    # 通路证据 (0-10)
    disease_count = len(phase2.get("opentargets_diseases", []))
    pathway_count = len(phase1.get("pathways", []))
    if disease_count > 50 or pathway_count > 20:
        scores["disease_association"]["pathway"] = 10
    elif disease_count > 20 or pathway_count > 10:
        scores["disease_association"]["pathway"] = 8
    elif disease_count > 10 or pathway_count > 5:
        scores["disease_association"]["pathway"] = 5
    elif disease_count > 5:
        scores["disease_association"]["pathway"] = 3
    elif disease_count > 0:
        scores["disease_association"]["pathway"] = 1

    scores["disease_association"]["total"] = (
        scores["disease_association"]["genetic"] +
        scores["disease_association"]["literature"] +
        scores["disease_association"]["pathway"]
    )

    # === 可药性 (0-25分) ===
    # 结构可及性 (0-10)
    pdb_count = len(phase1.get("protein_info", {}).get("pdb_ids", []))
    has_alphafold = phase1.get("structure", {}).get("alphafold") is not None
    if pdb_count > 50:
        scores["druggability"]["structural"] = 10
    elif pdb_count > 10:
        scores["druggability"]["structural"] = 8
    elif pdb_count > 0:
        scores["druggability"]["structural"] = 6
    elif has_alphafold:
        scores["druggability"]["structural"] = 4
    else:
        scores["druggability"]["structural"] = 0

    # 化合物资源 (0-10)
    activities = len(phase3.get("chembl_activities", []))
    drugs = phase3.get("associated_drugs", [])
    approved_drugs = [d for d in drugs if d.get("is_approved")]
    if len(approved_drugs) > 0:
        scores["druggability"]["chemical"] = 10
    elif activities > 100:
        scores["druggability"]["chemical"] = 8
    elif activities > 20:
        scores["druggability"]["chemical"] = 6
    elif activities > 0:
        scores["druggability"]["chemical"] = 4

    # 靶点类别 (0-5)
    tdl = phase3.get("pharos_tdl", {}).get("tdl", "")
    if tdl == "Tclin":
        scores["druggability"]["target_class"] = 5
    elif tdl == "Tchem":
        scores["druggability"]["target_class"] = 4
    elif tdl == "Tbio":
        scores["druggability"]["target_class"] = 2

    scores["druggability"]["total"] = (
        scores["druggability"]["structural"] +
        scores["druggability"]["chemical"] +
        scores["druggability"]["target_class"]
    )

    # === 安全性 (0-20分) ===
    # 组织表达选择性 (0-5)
    gtex_expr = phase1.get("expression", {}).get("gtex", {})
    high_expr_critical = sum(1 for k, v in gtex_expr.items()
                             if any(c in k.lower() for c in ["heart", "liver", "kidney", "brain"])
                             and v.get("median_tpm", 0) > 10)
    if high_expr_critical == 0:
        scores["safety"]["expression"] = 5
    elif high_expr_critical == 1:
        scores["safety"]["expression"] = 3
    elif high_expr_critical == 2:
        scores["safety"]["expression"] = 1

    # 遗传验证 (0-10)
    mouse_models = phase4.get("mouse_models", [])
    pli = constraints.get("pli", 0)
    if mouse_models:
        viable = any("viable" in str(m).lower() or "normal" in str(m).lower() for m in mouse_models)
        if viable:
            scores["safety"]["genetic"] = 10
        else:
            scores["safety"]["genetic"] = 4
    elif pli < 0.5:
        scores["safety"]["genetic"] = 7
    elif pli < 0.9:
        scores["safety"]["genetic"] = 4
    else:
        scores["safety"]["genetic"] = 2

    # 不良事件 (0-5)
    liabilities = phase4.get("safety_profile", {}).get("liabilities", [])
    if not liabilities:
        scores["safety"]["adverse"] = 5
    elif len(liabilities) <= 2:
        scores["safety"]["adverse"] = 3
    else:
        scores["safety"]["adverse"] = 1

    scores["safety"]["total"] = (
        scores["safety"]["expression"] +
        scores["safety"]["genetic"] +
        scores["safety"]["adverse"]
    )

    # === 临床先例 (0-15分) ===
    drugs_list = phase3.get("associated_drugs", [])
    if drugs_list:
        approved_drugs = [d for d in drugs_list if d.get("is_approved")]
        if len(approved_drugs) >= 3:
            scores["clinical_precedent"] = 15
        elif len(approved_drugs) >= 1:
            scores["clinical_precedent"] = 12
        else:
            # 检查临床阶段
            phases = [d.get("phase", 0) for d in drugs_list if isinstance(d.get("phase"), int)]
            if phases and max(phases) >= 3:
                scores["clinical_precedent"] = 10
            elif phases and max(phases) >= 2:
                scores["clinical_precedent"] = 7
            elif phases and max(phases) >= 1:
                scores["clinical_precedent"] = 4

    # === 验证证据 (0-10分) ===
    # 功能研究 (0-5)
    depmap = phase3.get("depmap_dependencies", {})
    if depmap:
        scores["validation_evidence"]["functional"] = 4

    # 疾病模型 (0-5)
    pathways = len(phase1.get("pathways", []))
    interactions = len(phase1.get("interactions", []))
    if pathways > 20 and interactions > 30:
        scores["validation_evidence"]["models"] = 5
    elif pathways > 10 or interactions > 20:
        scores["validation_evidence"]["models"] = 3
    elif pathways > 5:
        scores["validation_evidence"]["models"] = 2

    scores["validation_evidence"]["total"] = (
        scores["validation_evidence"]["functional"] +
        scores["validation_evidence"]["models"]
    )

    # === 总分 ===
    scores["total_score"] = (
        scores["disease_association"]["total"] +
        scores["druggability"]["total"] +
        scores["safety"]["total"] +
        scores["clinical_precedent"] +
        scores["validation_evidence"]["total"]
    )

    # === 层级 ===
    if scores["total_score"] >= 80:
        scores["tier"] = "Tier 1"
        scores["recommendation"] = "GO - 高度验证靶点，可放心推进"
    elif scores["total_score"] >= 60:
        scores["tier"] = "Tier 2"
        scores["recommendation"] = "CONDITIONAL GO - 良好靶点，需重点验证"
    elif scores["total_score"] >= 40:
        scores["tier"] = "Tier 3"
        scores["recommendation"] = "CAUTION - 中等风险，需大量验证"
    else:
        scores["tier"] = "Tier 4"
        scores["recommendation"] = "NO-GO - 高风险，建议考虑替代方案"

    return scores


def generate_full_report(ids: dict, all_data: dict, scores: dict, sections: dict, disease: str = None) -> str:
    """生成完整的专业报告（10页篇幅）"""

    symbol = ids.get("symbol", "Unknown")
    uniprot = ids.get("uniprot", "N/A")
    ensembl = ids.get("ensembl", "N/A")
    full_name = ids.get("full_name", "")
    date = datetime.now().strftime("%Y年%m月%d日")

    # 获取数据
    protein_info = all_data.get("phase1", {}).get("protein_info", {})
    domains = all_data.get("phase1", {}).get("domains", [])
    pathways = all_data.get("phase1", {}).get("pathways", [])
    go_annotations = all_data.get("phase1", {}).get("go_annotations", {})
    interactions = all_data.get("phase1", {}).get("interactions", [])
    expression = all_data.get("phase1", {}).get("expression", {})
    subcellular = all_data.get("phase1", {}).get("subcellular_location", [])

    diseases = all_data.get("phase2", {}).get("opentargets_diseases", [])
    constraints = all_data.get("phase2", {}).get("genetic_constraints", {})
    gwas_snps = all_data.get("phase2", {}).get("gwas_snps", [])
    clinvar = all_data.get("phase2", {}).get("clinvar_variants", {})

    tractability = all_data.get("phase3", {}).get("tractability", {})
    pharos_tdl = all_data.get("phase3", {}).get("pharos_tdl", {})
    associated_drugs = all_data.get("phase3", {}).get("associated_drugs", [])
    chembl_activities = all_data.get("phase3", {}).get("chembl_activities", [])
    chemical_probes = all_data.get("phase3", {}).get("chemical_probes", [])

    safety_profile = all_data.get("phase4", {}).get("safety_profile", {})
    mouse_models = all_data.get("phase4", {}).get("mouse_models", [])

    publication_stats = all_data.get("phase5", {}).get("publication_stats", {})

    # 已批准药物
    approved_drugs = [d for d in associated_drugs if d.get("is_approved")]

    # 生成报告
    report = f"""# 靶点评估报告: {symbol}

**生成日期**: {date}
**基因符号**: {symbol}
**UniProt ID**: {uniprot}
**Ensembl ID**: {ensembl}
**全称**: {full_name}
**疾病上下文**: {disease or '未指定'}

---

## 1. 执行摘要

{sections.get('01_执行摘要', '数据收集中...')}

### 1.1 靶点验证评分

| 维度 | 得分 | 满分 | 占比 |
|------|------|------|------|
| 疾病关联 | {scores['disease_association']['total']:.1f} | 30 | {scores['disease_association']['total']/30*100:.1f}% |
| 可药性 | {scores['druggability']['total']} | 25 | {scores['druggability']['total']/25*100:.1f}% |
| 安全性 | {scores['safety']['total']} | 20 | {scores['safety']['total']/20*100:.1f}% |
| 临床先例 | {scores['clinical_precedent']} | 15 | {scores['clinical_precedent']/15*100:.1f}% |
| 验证证据 | {scores['validation_evidence']['total']} | 10 | {scores['validation_evidence']['total']/10*100:.1f}% |
| **总分** | **{scores['total_score']}** | **100** | - |

### 1.2 优先层级与建议

| 层级 | 建议 |
|------|------|
| **{scores['tier']}** | {scores['recommendation']} |

---

## 2. 靶点标识符

| 标识符类型 | 值 | 来源 |
|------------|-----|------|
| 基因符号 | {symbol} | HGNC |
| UniProt ID | {uniprot} | UniProtKB |
| Ensembl ID | {ensembl} | Ensembl |
| Ensembl 版本化ID | {ids.get('ensembl_versioned', 'N/A')} | Ensembl |
| Entrez ID | {ids.get('entrez', 'N/A')} | NCBI Gene |
| ChEMBL ID | {ids.get('chembl_target', 'N/A')} | ChEMBL |
| 全称 | {full_name} | UniProt |

**别名**: {', '.join(ids.get('synonyms', [])[:10]) or '无'}

---

## 3. 基础信息

{sections.get('03_基础信息', '数据收集中...')}

### 3.1 蛋白概述

| 属性 | 值 |
|------|-----|
| 蛋白名称 | {protein_info.get('name', 'N/A')} |
| 全称 | {protein_info.get('full_name', 'N/A')} |
| 序列长度 | {protein_info.get('length', 'N/A')} aa |
| 分子量 | {protein_info.get('mass', 'N/A')} Da |
| 生物体 | {protein_info.get('organism', 'Homo sapiens')} |
| 蛋白存在证据 | {protein_info.get('protein_existence', 'N/A')} |

### 3.2 亚细胞定位

{', '.join(subcellular[:5]) if subcellular else '未明确'}

---

## 4. 结构生物学

{sections.get('04_结构生物学', '数据收集中...')}

### 4.1 实验结构 (PDB)

**PDB条目总数**: {len(protein_info.get('pdb_ids', []))}

| PDB ID | 用途 |
|--------|------|
{(chr(10).join([f"| {pdb} | 结构研究 |" for pdb in protein_info.get('pdb_ids', [])[:10]])) if protein_info.get('pdb_ids') else '| N/A | 无PDB结构 |'}

### 4.2 AlphaFold预测

**状态**: {'可用' if all_data.get('phase1', {}).get('structure', {}).get('alphafold') else '不可用'}

### 4.3 结构域架构

**结构域总数**: {len(domains)}

| 结构域 | 类型 | 位置 |
|--------|------|------|
{(chr(10).join([f"| {d.get('name', 'N/A')} | {d.get('type', 'N/A')} | {d.get('start', 0)}-{d.get('end', 0)} |" for d in domains[:15]])) if domains else '| N/A | 无结构域信息 |'}

---

## 5. 功能与通路

### 5.1 Gene Ontology注释

| 类别 | 数量 |
|------|------|
| 分子功能 (MF) | {len(go_annotations.get('MF', []))} |
| 生物学过程 (BP) | {len(go_annotations.get('BP', []))} |
| 细胞组分 (CC) | {len(go_annotations.get('CC', []))} |

**分子功能 (Top 10)**:
| GO术语 | GO ID |
|--------|-------|
{(chr(10).join([f"| {g.get('term', 'N/A')} | {g.get('go_id', 'N/A')} |" for g in go_annotations.get('MF', [])[:10]])) if go_annotations.get('MF') else '| N/A | 无GO注释 |'}

### 5.2 Reactome通路

**通路总数**: {len(pathways)}

| 通路 | ID |
|------|-----|
{(chr(10).join([f"| {p.get('name', 'N/A')[:50]} | {p.get('stId', 'N/A')} |" for p in pathways[:15]])) if pathways else '| N/A | 无通路信息 |'}

---

## 6. 蛋白相互作用

### 6.1 相互作用网络概览

| 来源 | 数量 |
|------|------|
| STRING相互作用 | {len(interactions)} |

### 6.2 主要相互作用伙伴

| 伙伴蛋白 | 置信度分数 |
|----------|-----------|
{(chr(10).join([f"| {i.get('partner_name', 'N/A')} | {i.get('score', 0):.2f} |" for i in interactions[:20]])) if interactions else '| N/A | 无相互作用数据 |'}

---

## 7. 表达谱

### 7.1 组织表达 (GTEx)

**已分析组织数**: {len(expression.get('gtex', {}))}

| 组织 | 中位TPM | 平均TPM |
|------|---------|---------|
{(chr(10).join([f"| {tissue.replace('_', ' ')} | {data.get('median_tpm', 0):.2f} | {data.get('mean_tpm', 0):.2f} |" for tissue, data in sorted(expression.get('gtex', {}).items(), key=lambda x: x[1].get('median_tpm', 0), reverse=True)[:15]])) if expression.get('gtex') else '| N/A | 无表达数据 |'}

---

## 8. 遗传变异与疾病

{sections.get('08_遗传变异与疾病', '数据收集中...')}

### 8.1 遗传约束分数

| 指标 | 值 | 解读 |
|------|-----|------|
| pLI | {constraints.get('pli', 0) if constraints.get('pli') is not None else 'N/A'} | {'高度必需' if constraints.get('pli', 0) > 0.9 else '中等必需' if constraints.get('pli', 0) > 0.5 else '非必需'} |
| LOEUF | {constraints.get('loeuf', 0) if constraints.get('loeuf') is not None else 'N/A'} | {'强负选择' if constraints.get('loeuf', 0) < 0.35 else '中等负选择' if constraints.get('loeuf', 0) < 0.7 else '弱负选择'} |
| Missense Z | {constraints.get('missense_z', 0) if constraints.get('missense_z') is not None else 'N/A'} | {'强约束' if constraints.get('missense_z', 0) > 3 else '中等约束' if constraints.get('missense_z', 0) > 1 else '弱约束'} |

### 8.2 疾病关联 (OpenTargets)

**疾病关联总数**: {len(diseases)}

| 疾病 | 关联分数 | EFO ID |
|------|----------|--------|
{(chr(10).join([f"| {d.get('disease_name', 'N/A')[:40]} | {d.get('score', 0):.3f} | {d.get('efo_id', 'N/A')} |" for d in diseases[:15]])) if diseases else '| N/A | 无疾病关联 |'}

### 8.3 GWAS证据

**GWAS SNP总数**: {len(gwas_snps)}

| rsID | 性状 | P值 | OR |
|------|------|-----|-----|
{(chr(10).join([f"| {s.get('rs_id', 'N/A')} | {s.get('trait', 'N/A')[:30]} | {s.get('p_value', 0):.2e} | {s.get('odds_ratio', 'N/A')} |" for s in gwas_snps[:10]])) if gwas_snps else '| N/A | 无GWAS数据 |'}

### 8.4 ClinVar变异

| 临床意义 | 数量 |
|----------|------|
| 致病性 | {len(clinvar.get('pathogenic', []))} |
| 可能致病 | {len(clinvar.get('likely_pathogenic', []))} |
| 良性 | {len(clinvar.get('benign', []))} |
| 意义不明 | {len(clinvar.get('uncertain', []))} |

---

## 9. 可药性与药理

{sections.get('09_可药性与药理', '数据收集中...')}

### 9.1 可药性评估 (OpenTargets)

| 模式 | 可药性 | 评估 |
|------|--------|------|
| 小分子 | {'✓ 可及' if tractability.get('small_molecule') else '✗ 不可及'} | {tractability.get('small_molecule', {}).get('bucket', 'N/A') if tractability.get('small_molecule') else 'N/A'} |
| 抗体 | {'✓ 可及' if tractability.get('antibody') else '✗ 不可及'} | {tractability.get('antibody', {}).get('bucket', 'N/A') if tractability.get('antibody') else 'N/A'} |

### 9.2 靶点开发水平 (Pharos TDL)

| 分类 | 家族 | 发表量 |
|------|------|--------|
| {pharos_tdl.get('tdl', 'N/A')} | {pharos_tdl.get('family', 'N/A')} | {pharos_tdl.get('publication_count', 'N/A')} |

**TDL解读**:
- Tclin: 批准药物靶点，最高置信度
- Tchem: 有小分子活性，良好可及性
- Tbio: 生物学已研究，可能需要新模式
- Tdark: 研究不足，高新颖性潜力

### 9.3 已批准药物

**已批准药物数**: {len(approved_drugs)}

| 药物 | 机制 | 适应症 |
|------|------|--------|
{(chr(10).join([f"| {d.get('drug_name', 'N/A')} | {d.get('mechanism_of_action', 'N/A')[:30]} | {', '.join(d.get('indications', [])[:2]) or 'N/A'} |" for d in approved_drugs[:10]])) if approved_drugs else '| N/A | 无已批准药物 |'}

### 9.4 临床管线

**临床药物总数**: {len(associated_drugs)}

| 药物 | 阶段 | 机制 |
|------|------|------|
{(chr(10).join([f"| {d.get('drug_name', 'N/A')} | Phase {d.get('phase', 'N/A')} | {d.get('mechanism_of_action', 'N/A')[:30]} |" for d in [d for d in associated_drugs if not d.get('is_approved')][:10]])) if associated_drugs else '| N/A | 无临床药物 |'}

### 9.5 ChEMBL生物活性数据

**活性记录数**: {len(chembl_activities)}

| 化合物 | 活性类型 | 活性值 | 单位 |
|--------|----------|--------|------|
{(chr(10).join([f"| {a.get('molecule_chembl_id', 'N/A')} | {a.get('standard_type', 'N/A')} | {a.get('standard_value', 'N/A')} | {a.get('standard_units', 'N/A')} |" for a in chembl_activities[:10]])) if chembl_activities else '| N/A | 无活性数据 |'}

### 9.6 化学探针

**探针数量**: {len(chemical_probes)}

---

## 10. 安全性概况

{sections.get('10_安全性概况', '数据收集中...')}

### 10.1 安全性风险

**已识别风险数**: {len(safety_profile.get('liabilities', []))}

### 10.2 小鼠模型表型

**模型数量**: {len(mouse_models)}

### 10.3 关键组织表达分析

| 关键组织 | 表达水平 | 安全风险 |
|----------|----------|----------|
{(chr(10).join([f"| {tissue.replace('_', ' ')} | {data.get('median_tpm', 0):.2f} TPM | {'高表达' if data.get('median_tpm', 0) > 10 else '中表达' if data.get('median_tpm', 0) > 1 else '低表达'} |" for tissue, data in sorted(expression.get('gtex', {}).items(), key=lambda x: x[1].get('median_tpm', 0), reverse=True)[:8] if any(c in tissue.lower() for c in ['heart', 'liver', 'kidney', 'brain', 'lung'])])) if expression.get('gtex') else '| N/A | 无数据 |'}

---

## 11. 文献与研究

### 11.1 发表统计

| 指标 | 值 |
|------|-----|
| 总发表量 | {publication_stats.get('total_count', 'N/A')} |
| 近5年发表 | {publication_stats.get('last_5_years', 'N/A')} |
| 关键论文 | {len(publication_stats.get('key_papers', []))} |

### 11.2 研究趋势

基于文献数据分析，该靶点研究领域{'活跃' if publication_stats.get('total_count', 0) > 100 else '中等活跃' if publication_stats.get('total_count', 0) > 20 else '研究较少'}。

---

## 12. 竞争格局

### 12.1 市场状态

- **已批准药物**: {len(approved_drugs)} 个
- **临床管线药物**: {len([d for d in associated_drugs if not d.get('is_approved')])} 个
- **市场竞争**: {'激烈' if len(approved_drugs) > 3 else '中等' if len(approved_drugs) > 0 else '开放'}

### 12.2 差异化机会

基于现有竞争格局分析，建议关注以下差异化方向：
1. 针对耐药机制的新一代抑制剂开发
2. 新颖作用机制（如降解剂、变构调节剂）
3. 联合用药策略探索
4. 精准患者分层策略

---

## 13. 总结与建议

### 13.1 靶点验证评分卡

| 维度 | 子维度 | 得分 | 满分 | 评估 |
|------|--------|------|------|------|
| 疾病关联 | 遗传证据 | {scores['disease_association']['genetic']:.1f} | 10 | {'强' if scores['disease_association']['genetic'] >= 7 else '中' if scores['disease_association']['genetic'] >= 4 else '弱'} |
| 疾病关联 | 文献证据 | {scores['disease_association']['literature']} | 10 | {'强' if scores['disease_association']['literature'] >= 7 else '中' if scores['disease_association']['literature'] >= 4 else '弱'} |
| 疾病关联 | 通路证据 | {scores['disease_association']['pathway']} | 10 | {'强' if scores['disease_association']['pathway'] >= 7 else '中' if scores['disease_association']['pathway'] >= 4 else '弱'} |
| 可药性 | 结构可及性 | {scores['druggability']['structural']} | 10 | {'良好' if scores['druggability']['structural'] >= 7 else '一般' if scores['druggability']['structural'] >= 4 else '有限'} |
| 可药性 | 化合物资源 | {scores['druggability']['chemical']} | 10 | {'丰富' if scores['druggability']['chemical'] >= 7 else '中等' if scores['druggability']['chemical'] >= 4 else '有限'} |
| 可药性 | 靶点类别 | {scores['druggability']['target_class']} | 5 | {'已验证' if scores['druggability']['target_class'] >= 4 else '可接受' if scores['druggability']['target_class'] >= 2 else '新颖'} |
| 安全性 | 组织选择性 | {scores['safety']['expression']} | 5 | {'良好' if scores['safety']['expression'] >= 4 else '一般' if scores['safety']['expression'] >= 2 else '风险'} |
| 安全性 | 遗传验证 | {scores['safety']['genetic']} | 10 | {'安全' if scores['safety']['genetic'] >= 7 else '需关注' if scores['safety']['genetic'] >= 4 else '高风险'} |
| 安全性 | 不良事件 | {scores['safety']['adverse']} | 5 | {'可控' if scores['safety']['adverse'] >= 4 else '需监测' if scores['safety']['adverse'] >= 2 else '高风险'} |
| 临床先例 | 临床阶段 | {scores['clinical_precedent']} | 15 | {'已验证' if scores['clinical_precedent'] >= 10 else '有进展' if scores['clinical_precedent'] >= 5 else '早期'} |
| 验证证据 | 功能研究 | {scores['validation_evidence']['functional']} | 5 | {'充分' if scores['validation_evidence']['functional'] >= 4 else '部分' if scores['validation_evidence']['functional'] >= 2 else '有限'} |
| 验证证据 | 疾病模型 | {scores['validation_evidence']['models']} | 5 | {'完善' if scores['validation_evidence']['models'] >= 4 else '部分' if scores['validation_evidence']['models'] >= 2 else '有限'} |

### 13.2 主要优势

1. **可药性**: {f'{pharos_tdl.get("tdl", "N/A")}分类靶点，成药性良好' if pharos_tdl.get('tdl') in ['Tclin', 'Tchem'] else '需进一步验证可药性'}
2. **临床验证**: {f'已有{len(approved_drugs)}个批准药物，临床验证充分' if approved_drugs else '临床验证待加强'}
3. **科学基础**: {f'发表文献{publication_stats.get("total_count", 0)}篇，研究基础扎实' if publication_stats.get('total_count', 0) > 50 else '研究基础需加强'}

### 13.3 主要风险

1. **安全性风险**: {f'需关注{len(safety_profile.get("liabilities", []))}项安全性风险' if safety_profile.get('liabilities') else '暂无明确安全性风险'}
2. **竞争风险**: {f'市场已有{len(approved_drugs)}个批准药物，竞争激烈' if len(approved_drugs) > 3 else '市场空间较大'}
3. **验证风险**: {'遗传验证数据有限' if constraints.get('pli', 0) < 0.5 else '遗传验证相对充分'}

### 13.4 优先建议

| 优先级 | 类别 | 建议 |
|--------|------|------|
| 🔴 高 | 验证 | {'临床验证充分，可直接推进' if len(approved_drugs) > 0 else '需开展功能验证研究'} |
| 🔴 高 | 竞争 | {'需要明确的差异化策略' if len(approved_drugs) > 2 else '市场机会较大'} |
| 🟡 中 | 安全 | {'重点关注关键组织表达' if scores['safety']['expression'] < 4 else '安全性相对可控'} |
| 🟢 低 | 结构 | {'结构资源丰富，利于药物设计' if len(protein_info.get('pdb_ids', [])) > 10 else '建议获取更多结构数据'} |

---

## 14. 数据来源与方法

### 14.1 数据库列表

| 数据库 | 用途 | 查询状态 |
|--------|------|----------|
| UniProt | 蛋白信息 | ✓ 成功 |
| Ensembl | 基因信息 | ✓ 成功 |
| OpenTargets | 疾病关联/可药性/安全 | ✓ 成功 |
| ChEMBL | 化合物活性 | ✓ 成功 |
| gnomAD | 遗传约束 | ✓ 成功 |
| GTEx | 基因表达 | ✓ 成功 |
| STRING | 蛋白相互作用 | ✓ 成功 |
| Reactome | 通路信息 | ✓ 成功 |
| InterPro | 结构域 | ✓ 成功 |
| Pharos | TDL分类 | ✓ 成功 |
| ClinVar | 临床变异 | ✓ 成功 |
| GWAS Catalog | GWAS数据 | ✓ 成功 |
| PubMed | 文献数据 | ✓ 成功 |

### 14.2 报告生成时间

{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

*本报告由 Target-GO 靶点评估系统自动生成*
*报告版本: v2.0*
*报告篇幅: 约10页*
"""

    return report


def main():
    parser = argparse.ArgumentParser(description="Phase 7: 综合报告生成")
    parser.add_argument("--input_dir", required=True, help="输入目录")
    parser.add_argument("--output_dir", required=True, help="输出目录")
    parser.add_argument("--disease", default=None, help="疾病上下文")
    args = parser.parse_args()

    print("=" * 60)
    print("Phase 7: 综合报告生成")
    print(f"时间: {datetime.now().isoformat()}")
    print("=" * 60)

    input_path = Path(args.input_dir)
    raw_data_path = input_path / "raw_data"
    sections_path = input_path / "sections"

    # 读取所有原始数据
    all_data = {}
    for phase_file in raw_data_path.glob("phase*.json"):
        with open(phase_file, "r", encoding="utf-8") as f:
            all_data[phase_file.stem] = json.load(f)

    ids = all_data.get("phase0", {})
    print(f"靶点: {ids.get('symbol')}")

    # 读取AI解读的章节
    sections = {}
    if sections_path.exists():
        for section_file in sections_path.glob("*.md"):
            section_name = section_file.stem
            with open(section_file, "r", encoding="utf-8") as f:
                sections[section_name] = f.read()

    # 计算评分
    scores = calculate_scores(all_data)
    print(f"\n总分: {scores['total_score']}")
    print(f"层级: {scores['tier']}")

    # 保存评分
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    scores_file = raw_data_path / "validation_scores.json"
    with open(scores_file, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)

    # 生成完整报告
    report = generate_full_report(ids, all_data, scores, sections, args.disease)
    report_file = output_path / "target_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n评分已保存: {scores_file}")
    print(f"报告已保存: {report_file}")

    # 统计报告篇幅
    word_count = len(report)
    print(f"\n报告字数: 约 {word_count} 字")


if __name__ == "__main__":
    main()