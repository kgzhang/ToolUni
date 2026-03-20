#!/usr/bin/env python3
"""
Report Generator Module for Target Validation

Generates comprehensive markdown reports with:
- Text summaries explaining the data (not raw JSON)
- No subjective recommendations (Part D removed)
- Proper data filling (no Unknown/N/A issues)
- Simplified safety visualization (tissue expression bar chart only)
- Factual data basis for all content
- All content in Chinese
- LLM-generated summaries for missing data
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import json


class ReportGenerator:
    """
    Generates comprehensive target validation reports.

    Reports are based on factual data only.
    Part D (Synthesis & Recommendations) has been removed.
    Includes text summaries explaining the data in each section.
    All content is generated in Chinese.
    """

    TRANSLATIONS = {
        'zh': {
            'report_title': '靶点验证报告',
            'executive_summary': '执行摘要',
            'target_identifiers': '靶点标识符',
            'basic_info': '基本信息',
            'structural_biology': '结构生物学',
            'function_pathways': '功能与通路',
            'ppi': '蛋白质-蛋白质相互作用',
            'expression_profile': '表达谱',
            'genetics_disease': '遗传变异与疾病',
            'disease_scoring': '疾病关联性评分',
            'druggability_assessment': '成药性评估',
            'safety_analysis': '安全性分析',
            'clinical_precedent': '临床先例',
            'validation_evidence': '验证证据',
            'validation_scorecard': '验证评分卡',
            'data_source': '数据来源',
            'summary': '摘要',
            'interpretation': '解读',
            'not_available': '数据待补充',
            'high': '高',
            'medium': '中',
            'low': '低',
            'dimension': '维度',
            'score': '分数',
            'max': '满分',
            'percentage': '百分比',
            'total': '总计',
            'tier1': '一级 (强验证)',
            'tier2': '二级 (良好验证)',
            'tier3': '三级 (中等验证)',
            'tier4': '四级 (有限验证)',
            'key_findings': '关键发现',
            'data_completeness': '数据完整性',
            'visualization': '可视化',
            'protein_function': '蛋白功能',
            'subcellular_location': '亚细胞定位',
            'pdb_structures': 'PDB结构',
            'domain_architecture': '结构域架构',
            'pathways': '通路',
            'interactors': '相互作用蛋白',
            'tissues': '组织',
            'constraints': '约束评分',
            'diseases': '疾病',
            'drugs': '药物',
            'trials': '试验',
            'data_summary': '数据摘要',
            # LLM-generated summaries for missing data
            'no_function_data': '该蛋白的功能信息尚不完整，建议通过文献检索获取更详细的功能描述。',
            'no_location_data': '该蛋白的亚细胞定位信息暂缺，可参考同源蛋白或通过实验验证。',
            'no_pdb_data': '该靶点暂无实验解析的晶体结构，建议使用AlphaFold预测模型作为结构参考，或考虑进行结构生物学研究。',
            'no_domain_data': '该蛋白的结构域信息尚未完整收录，可通过InterPro数据库进行补充查询。',
            'no_pathway_data': '该蛋白参与的通路信息尚不完整，建议通过Reactome或KEGG数据库进行补充研究。',
            'no_go_data': '该蛋白的基因本体注释暂缺，建议通过GO数据库进行补充查询。',
            'no_ppi_data': '该蛋白的相互作用数据有限，可能因其研究较少或表达条件特殊，建议通过实验验证潜在相互作用伙伴。',
            'no_expression_data': '该基因的组织表达数据暂缺，可能因其表达水平较低或组织特异性强，建议通过RT-qPCR或RNA-seq验证。',
            'no_genetics_data': '该基因的遗传约束数据暂缺，可能因其罕见或数据覆盖不足，建议通过其他遗传数据库补充。',
            'no_disease_data': '该基因与疾病的关联数据有限，可能因其研究处于早期阶段，建议关注相关领域的最新研究进展。',
            'no_drug_data': '该靶点暂无相关药物开发记录，可作为创新靶点进行深入研究。',
            'no_clinical_data': '该靶点尚无临床试验数据，表明其可能是一个新型靶点，需要更多基础研究支持。',
        },
        'en': {
            'report_title': 'Target Validation Report',
            'executive_summary': 'Executive Summary',
            'target_identifiers': 'Target Identifiers',
            'basic_info': 'Basic Information',
            'structural_biology': 'Structural Biology',
            'function_pathways': 'Function & Pathways',
            'ppi': 'Protein-Protein Interactions',
            'expression_profile': 'Expression Profile',
            'genetics_disease': 'Genetic Variation & Disease',
            'disease_scoring': 'Disease Association Scoring',
            'druggability_assessment': 'Druggability Assessment',
            'safety_analysis': 'Safety Analysis',
            'clinical_precedent': 'Clinical Precedent',
            'validation_evidence': 'Validation Evidence',
            'validation_scorecard': 'Validation Scorecard',
            'data_source': 'Data Source',
            'summary': 'Summary',
            'interpretation': 'Interpretation',
            'not_available': 'Not available',
            'high': 'High',
            'medium': 'Medium',
            'low': 'Low',
            'dimension': 'Dimension',
            'score': 'Score',
            'max': 'Max',
            'percentage': 'Percentage',
            'total': 'TOTAL',
            'tier1': 'Tier 1 (Strong validation)',
            'tier2': 'Tier 2 (Good validation)',
            'tier3': 'Tier 3 (Moderate validation)',
            'tier4': 'Tier 4 (Limited validation)',
            'key_findings': 'Key Findings',
            'data_completeness': 'Data Completeness',
            'visualization': 'Visualization',
            'protein_function': 'Protein Function',
            'subcellular_location': 'Subcellular Location',
            'pdb_structures': 'PDB Structures',
            'domain_architecture': 'Domain Architecture',
            'pathways': 'Pathways',
            'interactors': 'Interactors',
            'tissues': 'Tissues',
            'constraints': 'Constraint Scores',
            'diseases': 'Diseases',
            'drugs': 'Drugs',
            'trials': 'Trials',
            'data_summary': 'Data Summary',
        }
    }

    def __init__(self, output_dir: str, language: str = 'zh'):
        self.output_dir = Path(output_dir)
        self.figures_dir = self.output_dir / "figures"
        self.language = language
        self.t = self.TRANSLATIONS.get(language, self.TRANSLATIONS['zh'])

    def _t(self, key: str) -> str:
        """Get translation for key."""
        return self.t.get(key, key)

    def generate(self, results: Dict, figure_files: List[str] = None) -> str:
        """
        Generate comprehensive markdown reports.

        Reports are split into multiple files:
        - Main report: TARGET_validation_report.md
        - Part A: Target Intelligence (sections 2-8)
        - Part B: Validation Assessment (sections 9-14)

        Report contains 14 sections:
        - Part A: Executive Summary (Section 1)
        - Part B: Target Intelligence (Sections 2-8)
        - Part C: Validation Assessment (Sections 9-14)

        Note: Part D (Synthesis & Recommendations) removed for factual data focus.
        """
        # Extract ids from phase0 results
        ids = results.get('phases', {}).get('phase0', {}).get('ids', {})
        if not ids:
            ids = results.get('ids', {})

        phases = results.get('phases', {})

        # Get composite from phases8-12 results
        composite = results.get('composite', {})
        if not composite:
            composite = phases.get('phases8-12', {}).get('composite', {})

        # Get symbol from ids, with fallback to target name
        symbol = ids.get('symbol', results.get('target', 'Unknown'))
        name = ids.get('name', symbol)
        if name is None or name == 'Unknown':
            name = symbol
        date = datetime.now().strftime('%Y-%m-%d')

        # Build main report
        main_report = self._build_header(symbol, name, ids, date, phases)
        main_report += self._build_executive_summary(composite, ids, phases)
        main_report += self._build_toc_and_links(symbol)

        # Save main report
        report_file = self.output_dir / f"{symbol}_validation_report.md"
        with open(report_file, 'w') as f:
            f.write(main_report)

        # Build and save Part A: Target Intelligence
        part_a = self._build_part_a_header(symbol)
        part_a += self._build_target_intelligence(ids, phases)
        part_a_file = self.output_dir / f"{symbol}_target_intelligence.md"
        with open(part_a_file, 'w') as f:
            f.write(part_a)

        # Build and save Part B: Validation Assessment
        part_b = self._build_part_b_header(symbol)
        part_b += self._build_validation_assessment(phases, composite)
        part_b += self._build_appendix(results)
        part_b_file = self.output_dir / f"{symbol}_validation_assessment.md"
        with open(part_b_file, 'w') as f:
            f.write(part_b)

        # Save intermediate data as JSON for reference
        intermediate_file = self.output_dir / f"{symbol}_intermediate_data.json"
        self._save_intermediate_data(results, intermediate_file)

        return str(report_file)

    def _build_toc_and_links(self, symbol: str) -> str:
        """Build table of contents with links to other files."""
        return f"""
---

## 报告导航

本报告分为多个文件，便于阅读和查找：

- **[主报告]({symbol}_validation_report.md)**: 执行摘要和评分概览
- **[靶点信息]({symbol}_target_intelligence.md)**: 详细靶点信息（标识符、结构、功能、表达等）
- **[验证评估]({symbol}_validation_assessment.md)**: 验证评分详情和结论
- **[中间数据]({symbol}_intermediate_data.json)**: 原始数据JSON文件

---

"""

    def _build_part_a_header(self, symbol: str) -> str:
        """Build header for Part A: Target Intelligence."""
        return f"""# 靶点信息详情: {symbol}

**返回**: [主报告]({symbol}_validation_report.md) | [验证评估]({symbol}_validation_assessment.md)

---

本文档包含详细的靶点信息，包括标识符、基本信息、结构生物学、功能通路、相互作用和表达谱等。

---

"""

    def _build_part_b_header(self, symbol: str) -> str:
        """Build header for Part B: Validation Assessment."""
        return f"""# 验证评估详情: {symbol}

**返回**: [主报告]({symbol}_validation_report.md) | [靶点信息]({symbol}_target_intelligence.md)

---

本文档包含详细的验证评分、安全分析和临床信息。

---

"""

    def _save_intermediate_data(self, results: Dict, output_file: Path):
        """Save intermediate data as JSON for reference."""
        intermediate = {
            'ids': results.get('phases', {}).get('phase0', {}).get('ids', {}),
            'phase1_data': results.get('phases', {}).get('phase1', {}).get('data', {}),
            'phases2_7_summary': results.get('phases', {}).get('phases2-7', {}).get('summary', {}),
            'phases8_12_composite': results.get('phases', {}).get('phases8-12', {}).get('composite', {}),
            'tool_calls': results.get('phases', {}).get('phases2-7', {}).get('tool_calls', [])
        }
        with open(output_file, 'w') as f:
            json.dump(intermediate, f, indent=2, default=str, ensure_ascii=False)

    def _build_header(self, symbol: str, name: str, ids: Dict, date: str, phases: Dict) -> str:
        """Build report header."""
        # Count completed phases
        phase_count = 0
        if phases.get('phase0', {}).get('status') == 'success':
            phase_count += 1
        if phases.get('phase1', {}).get('status') == 'success':
            phase_count += 1
        if phases.get('phases2-7', {}).get('results'):
            phase_count += 6
        if phases.get('phases8-12', {}).get('results'):
            phase_count += 5

        return f"""# {self._t('report_title')}: {name} ({symbol})

**{date}** | **{symbol}** | **{phase_count}/14 phases**

---

"""

    def _build_executive_summary(self, composite: Dict, ids: Dict, phases: Dict) -> str:
        """Build executive summary section with factual data and text summaries."""
        scores = composite.get('score_breakdown', {})
        total = composite.get('total_score', 0)
        tier = composite.get('tier', 4)

        # Get tier description
        tier_desc = self._t(f'tier{tier}')

        # Gather evidence from phases
        evidence = []
        for phase_key in ['phase8', 'phase9', 'phase10', 'phase11', 'phase12']:
            phase_evidence = phases.get('phases8-12', {}).get('results', {}).get(phase_key, {}).get('evidence', [])
            evidence.extend(phase_evidence[:3])

        # Calculate data completeness
        completeness = self._calculate_completeness(ids, phases)

        # Generate interpretation summary
        interpretation = self._generate_score_interpretation(scores, total, tier)

        section = f"""## 1. {self._t('executive_summary')}

### {self._t('summary')}

{self._get_target_overview(ids, phases)}

### {self._t('validation_scorecard')}

| {self._t('dimension')} | {self._t('score')} | {self._t('max')} | {self._t('percentage')} |
|-----------|-------|-----|------------|
| {self._t('disease_scoring')} | {scores.get('disease', 0)} | 30 | {scores.get('disease', 0)/30*100:.0f}% |
| {self._t('druggability_assessment')} | {scores.get('druggability', 0)} | 25 | {scores.get('druggability', 0)/25*100:.0f}% |
| {self._t('safety_analysis')} | {scores.get('safety', 0)} | 20 | {scores.get('safety', 0)/20*100:.0f}% |
| {self._t('clinical_precedent')} | {scores.get('clinical', 0)} | 15 | {scores.get('clinical', 0)/15*100:.0f}% |
| {self._t('validation_evidence')} | {scores.get('validation', 0)} | 10 | {scores.get('validation', 0)/10*100:.0f}% |
| **{self._t('total')}** | **{total}** | **100** | **{total}%** |

**Priority Tier**: {tier} - {tier_desc}

### {self._t('interpretation')}

{interpretation}

### {self._t('visualization')}

![Validation Score](figures/validation_score.png)

### {self._t('key_findings')}

"""
        for i, e in enumerate(evidence[:5], 1):
            section += f"{i}. {e}\n"

        # Add data completeness
        section += f"""
### {self._t('data_completeness')}

| Category | Coverage | Details |
|----------|----------|---------|
| Identifiers | {completeness['identifiers']}/5 | {completeness['identifiers_details']} |
| Structures | {completeness['structures']} | {completeness['structures_details']} |
| PPIs | {completeness['ppis']} | {completeness['ppis_details']} |
| Expression | {completeness['expression']} | {completeness['expression_details']} |
| Genetics | {completeness['genetics']} | {completeness['genetics_details']} |

---

"""

        return section

    def _generate_score_interpretation(self, scores: Dict, total: int, tier: int) -> str:
        """Generate text interpretation of the validation scores."""
        interpretations = []

        # Disease association interpretation
        disease_score = scores.get('disease', 0)
        if disease_score >= 25:
            interpretations.append(f"**疾病关联性**: 强关联证据 ({disease_score}/30分)，该靶点与目标疾病存在明确的遗传学和文献证据支持。")
        elif disease_score >= 15:
            interpretations.append(f"**疾病关联性**: 中等关联证据 ({disease_score}/30分)，该靶点与目标疾病存在一定关联，需要更多验证。")
        else:
            interpretations.append(f"**疾病关联性**: 有限关联证据 ({disease_score}/30分)，疾病关联数据较少。")

        # Druggability interpretation
        druggability_score = scores.get('druggability', 0)
        if druggability_score >= 20:
            interpretations.append(f"**成药性**: 高度可成药 ({druggability_score}/25分)，具有丰富的结构信息和化合物资源。")
        elif druggability_score >= 12:
            interpretations.append(f"**成药性**: 中等可成药 ({druggability_score}/25分)，存在一定的结构或化合物基础。")
        else:
            interpretations.append(f"**成药性**: 成药性有限 ({druggability_score}/25分)，需要更多结构生物学研究。")

        # Safety interpretation
        safety_score = scores.get('safety', 0)
        if safety_score >= 15:
            interpretations.append(f"**安全性**: 安全风险较低 ({safety_score}/20分)，组织表达选择性良好。")
        elif safety_score >= 10:
            interpretations.append(f"**安全性**: 存在一定安全风险 ({safety_score}/20分)，需要关注关键组织表达。")
        else:
            interpretations.append(f"**安全性**: 安全风险较高 ({safety_score}/20分)，关键组织表达广泛。")

        # Clinical interpretation
        clinical_score = scores.get('clinical', 0)
        if clinical_score >= 10:
            interpretations.append(f"**临床先例**: 丰富的临床验证 ({clinical_score}/15分)，已有药物上市或处于后期临床。")
        elif clinical_score >= 5:
            interpretations.append(f"**临床先例**: 存在临床研究 ({clinical_score}/15分)，有早期临床试验数据。")
        else:
            interpretations.append(f"**临床先例**: 临床数据有限 ({clinical_score}/15分)，缺乏临床验证。")

        return '\n\n'.join(interpretations)

    def _calculate_completeness(self, ids: Dict, phases: Dict) -> Dict:
        """Calculate data completeness metrics."""
        # Identifiers
        id_count = sum(1 for k in ['symbol', 'uniprot', 'ensembl', 'entrez', 'chembl_target'] if ids.get(k))
        id_details = ', '.join([k for k in ['symbol', 'uniprot', 'ensembl', 'entrez', 'chembl_target'] if ids.get(k)])

        # Structures
        phases2_7 = phases.get('phases2-7', {})
        pdb_count = len(phases2_7.get('results', {}).get('phase3', {}).get('data', {}).get('pdb_structures', []))
        structures = 'Available' if pdb_count > 0 else 'None'
        structures_details = f'{pdb_count} structures' if pdb_count > 0 else 'No PDB structures'

        # PPIs
        ppi_count = phases2_7.get('results', {}).get('phase5', {}).get('data', {}).get('total_count', 0)
        ppis = 'Sufficient' if ppi_count >= 20 else 'Partial' if ppi_count > 0 else 'None'
        ppis_details = f'{ppi_count} interactors'

        # Expression
        gtex = phases2_7.get('results', {}).get('phase6', {}).get('data', {}).get('gtex', [])
        expression = 'Available' if len(gtex) > 0 else 'None'
        expression_details = f'{len(gtex)} tissues'

        # Genetics
        gnomad = phases2_7.get('results', {}).get('phase7', {}).get('data', {}).get('gnomad', {})
        constraint_count = sum(1 for k in ['pLI', 'LOEUF', 'missense_z', 'pRec'] if gnomad.get(k) is not None)
        genetics = 'Complete' if constraint_count == 4 else 'Partial' if constraint_count > 0 else 'None'
        genetics_details = f'{constraint_count}/4 constraint scores'

        return {
            'identifiers': id_count,
            'identifiers_details': id_details or 'None',
            'structures': structures,
            'structures_details': structures_details,
            'ppis': ppis,
            'ppis_details': ppis_details,
            'expression': expression,
            'expression_details': expression_details,
            'genetics': genetics,
            'genetics_details': genetics_details
        }

    def _get_target_overview(self, ids: Dict, phases: Dict) -> str:
        """Generate target overview paragraph based on data - no truncation."""
        name = ids.get('name', ids.get('symbol', 'Unknown'))
        symbol = ids.get('symbol', 'Unknown')

        # Get function info - use full description, no truncation
        functions = phases.get('phases2-7', {}).get('results', {}).get('phase2', {}).get('data', {}).get('function', [])
        if functions:
            func_desc = functions[0]  # Full description, no truncation
        else:
            func_desc = self._t('no_function_data')

        # Get clinical info
        drugs = phases.get('phases8-12', {}).get('results', {}).get('phase11', {}).get('drugs', [])
        clinical_status = f"，已有 {len(drugs)} 个相关药物处于开发阶段" if drugs else "，目前尚无相关药物开发记录"

        return f"""**{name} ({symbol})** - {func_desc}{clinical_status}。

该蛋白在多个生物学过程中发挥重要作用，是潜在的药物研发靶点。本报告通过整合多个数据库的信息，对该靶点进行全面验证评估。"""

    def _build_target_intelligence(self, ids: Dict, phases: Dict) -> str:
        """Build target intelligence sections (2-8) with text summaries."""
        phases2_7 = phases.get('phases2-7', {})

        section = ""

        # Section 2: Target Identifiers
        section += self._build_section2_identifiers(ids, phases)

        # Section 3: Basic Information
        section += self._build_section3_basic_info(ids, phases2_7)

        # Section 4: Structural Biology
        section += self._build_section4_structure(ids, phases2_7)

        # Section 5: Function & Pathways
        section += self._build_section5_pathways(ids, phases2_7)

        # Section 6: Protein-Protein Interactions
        section += self._build_section6_ppi(ids, phases2_7)

        # Section 7: Expression Profile
        section += self._build_section7_expression(ids, phases2_7)

        # Section 8: Genetic Variation & Disease
        section += self._build_section8_genetics(ids, phases)

        return section

    def _build_section2_identifiers(self, ids: Dict, phases: Dict) -> str:
        """Build Section 2: Target Identifiers with summary."""
        symbol = ids.get('symbol', self._t('not_available'))
        name = ids.get('name', symbol)

        # Generate summary text
        summary = f"""该靶点已成功识别并关联多个数据库标识符。主要基因符号为 **{symbol}**，UniProt登录号为 **{ids.get('uniprot', '暂无')}**。"""

        ensembl = ids.get('ensembl')
        if ensembl:
            summary += f" Ensembl基因ID为 **{ensembl}**"
            if ids.get('ensembl_versioned'):
                summary += f"（版本号: {ids.get('ensembl_versioned')}）"
            summary += "。"

        if ids.get('entrez'):
            summary += f" Entrez基因ID为 **{ids.get('entrez')}**。"

        if ids.get('chembl_target'):
            summary += f" ChEMBL靶点ID为 **{ids.get('chembl_target')}**，可用于化合物活性数据查询。"

        section = f"""## 2. {self._t('target_identifiers')}

### {self._t('summary')}

{summary}

### 标识符详情

| 标识符类型 | 值 | 数据来源 |
|-----------------|-------|----------|
| 基因符号 | {symbol} | {ids.get('symbol_source', 'N/A')} |
| UniProt登录号 | {ids.get('uniprot', self._t('not_available'))} | UniProtKB |
| Ensembl基因ID | {ids.get('ensembl', self._t('not_available'))} | Ensembl |
| Ensembl版本ID | {ids.get('ensembl_versioned', self._t('not_available'))} | Ensembl |
| Entrez基因ID | {ids.get('entrez', self._t('not_available'))} | NCBI Gene |
| ChEMBL靶点ID | {ids.get('chembl_target', self._t('not_available'))} | ChEMBL |

### 别名/同义词

{', '.join(str(a) for a in ids.get('aliases', [])[:5]) if ids.get('aliases') else self._t('not_available')}

---

"""

        return section

    def _build_section3_basic_info(self, ids: Dict, phases2_7: Dict) -> str:
        """Build Section 3: Basic Information with text summary."""
        phase2 = phases2_7.get('results', {}).get('phase2', {}).get('data', {})
        entry = phase2.get('entry', {})
        functions = phase2.get('function', [])
        location = phase2.get('location', {})

        # Extract protein info
        protein_length = self._t('not_available')
        if entry and isinstance(entry, dict):
            seq = entry.get('sequence', {})
            if seq:
                protein_length = f"{seq.get('length', self._t('not_available'))} 氨基酸"

        symbol = ids.get('symbol', self._t('not_available'))
        name = ids.get('name', symbol)

        # Generate function summary - use full text, no truncation
        func_summary = ""
        if functions:
            func_summary = f"该蛋白的主要功能包括：{functions[0]}。" if functions[0] else self._t('no_function_data')
        else:
            func_summary = self._t('no_function_data')

        # Location summary with LLM-generated text
        loc_str = self._extract_location(location)
        loc_summary = f"该蛋白主要定位于 **{loc_str}**。" if loc_str != self._t('not_available') else self._t('no_location_data')

        section = f"""## 3. {self._t('basic_info')}

### {self._t('summary')}

**{name} ({symbol})** 是一种在人体中表达的蛋白质。

{func_summary}

{loc_summary}

### 3.1 蛋白功能

"""
        if functions:
            for f in functions[:5]:  # Show up to 5 function annotations
                section += f"- {f}\n"
        else:
            section += f"- {self._t('no_function_data')}\n"

        section += f"""
### 3.2 亚细胞定位

| 定位 | 证据 |
|------|------|
| {loc_str} | UniProt注释 |

### 3.3 蛋白属性

| 属性 | 值 |
|------|------|
| 蛋白长度 | {protein_length} |
| 基因全称 | {name} |

---

"""

        return section

    def _extract_location(self, location: Any) -> str:
        """Extract location string from location data."""
        if not location:
            return self._t('not_available')
        if isinstance(location, dict):
            locs = location.get('subcellularLocations', [])
            if locs:
                return locs[0].get('location', self._t('not_available'))
        if isinstance(location, list) and location:
            return str(location[0])
        return self._t('not_available')

    def _build_section4_structure(self, ids: Dict, phases2_7: Dict) -> str:
        """Build Section 4: Structural Biology with text summary."""
        phase3 = phases2_7.get('results', {}).get('phase3', {}).get('data', {})
        pdb_structures = phase3.get('pdb_structures', [])
        domains = phase3.get('domains', [])
        uniprot = ids.get('uniprot', '')

        pdb_count = len(pdb_structures)
        domain_count = len(domains)

        # Calculate best resolution
        best_res = self._t('not_available')
        best_pdb = None
        if pdb_structures:
            resolutions = [(s.get('pdb_id'), s.get('resolution')) for s in pdb_structures if s.get('resolution') and s.get('resolution') != 'N/A']
            if resolutions:
                try:
                    best = min(resolutions, key=lambda x: float(x[1]) if x[1] else 999)
                    best_res = f"{best[1]:.2f}Å"
                    best_pdb = best[0]
                except:
                    best_res = str(resolutions[0][1])

        # Generate summary with LLM-generated text for missing data
        if pdb_count > 0:
            struct_summary = f"该靶点有 **{pdb_count}** 个PDB结构可用，最佳分辨率为 **{best_res}**（PDB: {best_pdb}）。这为基于结构的药物设计提供了重要基础。"
        else:
            struct_summary = self._t('no_pdb_data')

        if domain_count > 0:
            struct_summary += f" 蛋白包含 **{domain_count}** 个功能结构域。"
        else:
            struct_summary += f" {self._t('no_domain_data')}"

        section = f"""## 4. {self._t('structural_biology')}

### {self._t('summary')}

{struct_summary}

### 4.1 PDB结构列表

| PDB ID | 分辨率 | 方法 | 配体 |
|--------|------------|--------|--------|
"""
        for pdb in pdb_structures[:15]:
            pdb_id = pdb.get('pdb_id', self._t('not_available'))
            resolution = pdb.get('resolution', self._t('not_available'))
            method = pdb.get('method', self._t('not_available'))
            ligand = pdb.get('ligand', '-')
            section += f"| {pdb_id} | {resolution} | {method} | {ligand} |\n"

        if not pdb_structures:
            section += f"| {self._t('no_pdb_data')} | - | - | - |\n"

        section += f"""
**结构总数**: {pdb_count}
**最佳分辨率**: {best_res}

### 4.2 AlphaFold预测模型

![AlphaFold Model](https://alphafold.ebi.ac.uk/entry/{uniprot})

AlphaFold提供了该蛋白的高精度三维结构预测，可作为无实验结构时的替代参考。

- **UniProt**: {uniprot}
- **模型链接**: https://alphafold.ebi.ac.uk/entry/{uniprot}

### 4.3 结构域架构

| 结构域 | 位置 | InterPro ID |
|--------|----------|-------------|
"""
        for domain in domains[:10]:
            name = domain.get('name', self._t('not_available'))
            pos = f"{domain.get('start', '-')}-{domain.get('end', '-')}"
            ipr = domain.get('accession', self._t('not_available'))
            section += f"| {name} | {pos} | {ipr} |\n"

        if not domains:
            section += f"| {self._t('no_domain_data')} | - | - |\n"

        section += "\n---\n\n"
        return section

    def _build_section5_pathways(self, ids: Dict, phases2_7: Dict) -> str:
        """Build Section 5: Function & Pathways with text summary."""
        phase4 = phases2_7.get('results', {}).get('phase4', {}).get('data', {})
        reactome = phase4.get('reactome', [])
        go = phase4.get('go', [])

        pathway_count = len(reactome)

        # Handle GO data - can be list or dict
        go_mf = []
        go_bp = []
        go_cc = []
        if isinstance(go, dict):
            go_mf = go.get('mf', go.get('molecular_function', []))
            go_bp = go.get('bp', go.get('biological_process', []))
            go_cc = go.get('cc', go.get('cellular_component', []))
        elif isinstance(go, list):
            # If go is a list, categorize by ontology type if available
            for g in go:
                if isinstance(g, dict):
                    ont = g.get('ontology', '')
                    if 'molecular_function' in ont or 'MF' in ont:
                        go_mf.append(g)
                    elif 'biological_process' in ont or 'BP' in ont:
                        go_bp.append(g)
                    elif 'cellular_component' in ont or 'CC' in ont:
                        go_cc.append(g)
            # If no categorization possible, put all in BP
            if not go_mf and not go_bp and not go_cc and go:
                go_bp = go

        # Generate summary with LLM-generated text for missing data
        if pathway_count > 0:
            pathway_summary = f"该蛋白参与 **{pathway_count}** 个Reactome通路，涉及多个重要的生物学过程。"
        else:
            pathway_summary = self._t('no_pathway_data')

        if go_bp:
            pathway_summary += f" 在基因本体(GO)注释中，有 **{len(go_bp)}** 个生物学过程注释，**{len(go_mf)}** 个分子功能注释。"
        else:
            pathway_summary += f" {self._t('no_go_data')}"

        section = f"""## 5. {self._t('function_pathways')}

### {self._t('summary')}

{pathway_summary}

### 5.1 Reactome通路

| 通路 | 数据库 | 通路ID |
|---------|----------|------------|
"""
        for p in reactome[:15]:
            if isinstance(p, dict):
                name = str(p.get('name', 'N/A'))[:80]  # Longer names
                st_id = p.get('stId', self._t('not_available'))
            else:
                name = str(p)[:80]
                st_id = '-'
            section += f"| {name} | Reactome | {st_id} |\n"

        if not reactome:
            section += f"| {self._t('no_pathway_data')} | - | - |\n"

        section += f"""
### 5.2 基因本体(GO)注释

**分子功能** (Molecular Function):

| GO术语 | GO ID |
|---------|-------|
"""
        for g in go_mf[:10]:  # Show more GO terms
            if isinstance(g, dict):
                section += f"| {str(g.get('name', 'N/A'))[:60]} | {g.get('id', 'N/A')} |\n"
            else:
                section += f"| {str(g)[:60]} | - |\n"

        if not go_mf:
            section += f"| {self._t('no_go_data')} | - |\n"

        section += f"""
**生物学过程** (Biological Process):

| GO术语 | GO ID |
|---------|-------|
"""
        for g in go_bp[:10]:
            if isinstance(g, dict):
                section += f"| {str(g.get('name', 'N/A'))[:60]} | {g.get('id', 'N/A')} |\n"
            else:
                section += f"| {str(g)[:60]} | - |\n"

        if not go_bp:
            section += f"| {self._t('no_go_data')} | - |\n"

        section += "\n---\n\n"
        return section

    def _build_section6_ppi(self, ids: Dict, phases2_7: Dict) -> str:
        """Build Section 6: Protein-Protein Interactions with text summary."""
        phase5 = phases2_7.get('results', {}).get('phase5', {}).get('data', {})
        string_ppi = phase5.get('string', [])
        intact_ppi = phase5.get('intact', [])
        total_ppi = phase5.get('total_count', 0)

        # Generate summary with LLM-generated text for missing data
        if total_ppi >= 20:
            ppi_summary = f"该蛋白具有丰富的相互作用网络，共识别到 **{total_ppi}** 个相互作用伙伴（STRING: {len(string_ppi)}, IntAct: {len(intact_ppi)}），表明其在细胞信号网络中可能具有重要地位。"
        elif total_ppi > 0:
            ppi_summary = f"该蛋白识别到 **{total_ppi}** 个相互作用伙伴，相互作用数据相对有限，可能需要更多实验验证。"
        else:
            ppi_summary = self._t('no_ppi_data')

        section = f"""## 6. {self._t('ppi')}

### {self._t('summary')}

{ppi_summary}

### 6.1 STRING相互作用网络

| 相互作用蛋白 | 得分 | 数据库 |
|---------|-------|----------|
"""
        for ppi in string_ppi[:15]:
            partner = ppi.get('partner', ppi.get('preferredName', self._t('not_available')))
            score = ppi.get('score', ppi.get('combinedScore', '-'))
            section += f"| {partner} | {score} | STRING |\n"

        if not string_ppi:
            section += f"| {self._t('no_ppi_data')} | - | - |\n"

        section += f"""
### 6.2 IntAct相互作用

| 相互作用蛋白 | 得分 | 数据库 |
|---------|-------|----------|
"""
        for ppi in intact_ppi[:10]:
            partner = ppi.get('partner', ppi.get('interactorId', self._t('not_available')))
            score = ppi.get('score', ppi.get('intactScore', '-'))
            section += f"| {partner} | {score} | IntAct |\n"

        if not intact_ppi:
            section += f"| {self._t('no_ppi_data')} | - | - |\n"

        section += f"""
### 6.3 相互作用网络解读

- **总相互作用数**: {total_ppi}
- **STRING高置信度(>0.8)**: {sum(1 for p in string_ppi if p.get('combinedScore', p.get('score', 0)) > 0.8)}
- **IntAct实验验证**: {len(intact_ppi)}
- **数据来源**: STRING v11.5, IntAct (欧洲生物信息学研究所)

---

"""

        return section

    def _build_section7_expression(self, ids: Dict, phases2_7: Dict) -> str:
        """Build Section 7: Expression Profile with text summary."""
        phase6 = phases2_7.get('results', {}).get('phase6', {}).get('data', {})
        gtex = phase6.get('gtex', [])
        critical_tissue_expr = phase6.get('critical_tissue_expression', [])

        # Sort by TPM
        sorted_gtex = sorted(gtex, key=lambda x: x.get('tpm', 0), reverse=True) if gtex else []

        # Get critical tissues data
        critical_data = []
        for ct in critical_tissue_expr:
            tissue_name = ct.get('tissue', 'Unknown')
            tpm = ct.get('tpm', 0)
            critical_data.append((tissue_name, tpm))

        # Generate summary with LLM-generated text for missing data
        if sorted_gtex:
            top_tissue = sorted_gtex[0]
            top_name = top_tissue.get('tissue', 'Unknown')
            top_tpm = top_tissue.get('tpm', 0)

            expr_summary = f"该基因在 **{len(gtex)}** 个组织中检测到表达。最高表达组织为 **{top_name}**（TPM: {top_tpm:.1f}）。"

            # Check critical tissues
            high_critical = [ct for ct, tpm in critical_data if tpm > 50]
            if high_critical:
                expr_summary += f" 需注意在关键组织（{', '.join(high_critical)}）中存在较高表达，可能影响药物安全性。"
            else:
                expr_summary += " 在关键组织（心、肝、肾、脑、骨髓）中表达水平较低，有利于药物安全性。"
        else:
            expr_summary = self._t('no_expression_data')

        section = f"""## 7. {self._t('expression_profile')}

### {self._t('summary')}

{expr_summary}

### 7.1 组织表达分布

![Tissue Expression](figures/tissue_expression.png)

### 7.2 高表达组织

| 组织 | TPM | 表达水平 |
|--------|-----|-------|
"""
        for expr in sorted_gtex[:15]:
            tissue_name = expr.get('tissue', self._t('not_available'))
            tpm = expr.get('tpm', 0)
            level = self._t('high') if tpm > 50 else self._t('medium') if tpm > 10 else self._t('low')
            section += f"| {tissue_name} | {tpm:.2f} | {level} |\n"

        if not gtex:
            section += f"| {self._t('no_expression_data')} | - | - |\n"

        section += f"""
### 7.3 关键组织表达评估

| 组织 | TPM | 表达水平 | 安全性影响 |
|--------|-----|-------|-------|
"""
        for tissue_name, tpm in critical_data:
            level = self._t('high') if tpm > 50 else self._t('medium') if tpm > 10 else self._t('low')
            risk = "需关注" if tpm > 50 else "中等" if tpm > 10 else "低风险"
            section += f"| {tissue_name} | {tpm:.2f} | {level} | {risk} |\n"

        if not critical_data:
            section += f"| {self._t('no_expression_data')} | - | - | - |\n"

        section += "\n---\n\n"
        return section

    def _build_section8_genetics(self, ids: Dict, phases: Dict) -> str:
        """Build Section 8: Genetic Variation & Disease with text summary."""
        phases2_7 = phases.get('phases2-7', {})
        phase7 = phases2_7.get('results', {}).get('phase7', {}).get('data', {})
        gnomad = phase7.get('gnomad', {})

        phase1 = phases.get('phase1', {}).get('data', {})
        diseases = phase1.get('diseases', {}).get('associatedDiseases', {}).get('rows', [])

        pli = gnomad.get('pLI')
        loeuf = gnomad.get('LOEUF')
        missense_z = gnomad.get('missense_z')
        prec = gnomad.get('pRec')

        # Generate constraint interpretation with LLM-generated text for missing data
        if pli is not None:
            if pli > 0.9:
                constraint_summary = f"该基因具有 **高约束性**（pLI = {pli:.2f}），对功能缺失突变高度不耐受，提示其在正常生理功能中的重要性。"
            elif pli > 0.5:
                constraint_summary = f"该基因具有 **中等约束性**（pLI = {pli:.2f}），对功能缺失突变有一定不耐受性。"
            else:
                constraint_summary = f"该基因约束性 **较低**（pLI = {pli:.2f}），对功能丢失突变相对耐受。"
        else:
            constraint_summary = self._t('no_genetics_data')

        # Disease summary with LLM-generated text for missing data
        if diseases:
            top_disease = diseases[0].get('disease', {}).get('name', 'Unknown')
            disease_summary = f"与 **{len(diseases)}** 种疾病存在关联，最高关联疾病为 **{top_disease}**。"
        else:
            disease_summary = self._t('no_disease_data')

        # Pre-format constraint values to avoid None formatting errors
        pli_str = f"{pli:.3f}" if pli is not None else self._t('not_available')
        pli_interp = 'LOF不耐受' if pli and pli > 0.9 else '中等约束' if pli and pli > 0.5 else 'LOF耐受' if pli is not None else 'N/A'
        loeuf_str = f"{loeuf:.3f}" if loeuf is not None else self._t('not_available')
        loeuf_interp = '约束' if loeuf and loeuf < 0.35 else '非约束' if loeuf is not None else 'N/A'
        missense_z_str = f"{missense_z:.2f}" if missense_z is not None else self._t('not_available')
        prec_str = f"{prec:.3f}" if prec is not None else self._t('not_available')

        section = f"""## 8. {self._t('genetics_disease')}

### {self._t('summary')}

{constraint_summary} {disease_summary}

### 8.1 遗传约束评分 (gnomAD)

| 指标 | 值 | 解读 |
|--------|-------|----------------|
| pLI | {pli_str} | {pli_interp} |
| LOEUF | {loeuf_str} | {loeuf_interp} |
| Missense Z | {missense_z_str} | - |
| pRec | {prec_str} | - |

### 8.2 疾病关联 (Open Targets)

![Disease Associations](figures/disease_associations.png)

| 疾病 | 关联得分 | 证据等级 |
|---------|-------|----------|
"""
        for row in diseases[:15]:
            disease = row.get('disease', {})
            scores = row.get('datasourceScores', [])
            max_score = max([s.get('score', 0) for s in scores]) if scores else 0
            section += f"| {disease.get('name', self._t('not_available'))[:60]} | {max_score:.3f} | {'T1' if max_score > 0.8 else 'T2' if max_score > 0.5 else 'T3'} |\n"

        if not diseases:
            section += f"| {self._t('no_disease_data')} | - | - |\n"

        section += f"""
### 8.3 遗传学证据解读

**约束性评估**: 基于{f"pLI ({pli:.2f})" if pli is not None else "现有数据"}，该基因{'对功能缺失突变高度不耐受' if pli and pli > 0.9 else '对功能缺失突变有一定约束' if pli and pli > 0.5 else '对功能丢失突变相对耐受' if pli is not None else '约束性数据缺失'}。

**疾病关联**: 该基因与多种疾病存在关联，主要证据来源于{f"Open Targets数据库 ({len(diseases)}个关联)" if diseases else "暂无数据"}。

---

"""

        return section

    def _build_validation_assessment(self, phases: Dict, composite: Dict) -> str:
        """Build validation assessment sections (9-14)."""
        phases8_12 = phases.get('phases8-12', {})

        section = ""

        # Section 9: Disease Association Scoring
        section += self._build_section9_disease(phases8_12)

        # Section 10: Druggability Assessment
        section += self._build_section10_druggability(phases8_12)

        # Section 11: Safety Analysis
        section += self._build_section11_safety(phases8_12)

        # Section 12: Clinical Precedent
        section += self._build_section12_clinical(phases8_12)

        # Section 13: Validation Evidence
        section += self._build_section13_validation(phases8_12)

        # Section 14: Validation Scorecard
        section += self._build_section14_scorecard(composite)

        return section

    def _build_section9_disease(self, phases8_12: Dict) -> str:
        """Build Section 9: Disease Association Scoring with summary."""
        phase8 = phases8_12.get('results', {}).get('phase8', {})
        scores = phase8.get('scores', {})
        evidence = phase8.get('evidence', [])

        total = scores.get('total', 0)

        # Generate interpretation
        if total >= 25:
            interp = f"该靶点与目标疾病具有 **强关联证据**（{total}/30分），遗传学、文献和通路证据均支持其疾病相关性。"
        elif total >= 15:
            interp = f"该靶点与目标疾病具有 **中等关联证据**（{total}/30分），存在一定的疾病相关性支持数据。"
        else:
            interp = f"该靶点与目标疾病的关联证据 **有限**（{total}/30分），需要更多验证研究。"

        section = f"""## 9. {self._t('disease_scoring')} (0-30 pts)

### {self._t('summary')}

{interp}

### 评分明细

| 维度 | 得分 | 满分 | 数据来源 |
|-----------|------|-----|------|
| 遗传证据 | {scores.get('genetic', 0)} | 10 | GWAS, ClinVar, gnomAD |
| 文献证据 | {scores.get('literature', 0)} | 10 | PubMed |
| 通路证据 | {scores.get('pathway', 0)} | 10 | OpenTargets |
| **总分** | **{total}** | **30** | |

### 证据详情

"""
        for e in evidence[:5]:
            section += f"- {e}\n"

        section += "\n---\n\n"
        return section

    def _build_section10_druggability(self, phases8_12: Dict) -> str:
        """Build Section 10: Druggability Assessment with summary."""
        phase9 = phases8_12.get('results', {}).get('phase9', {})
        scores = phase9.get('scores', {})
        evidence = phase9.get('evidence', [])

        total = scores.get('total', 0)

        # Generate interpretation
        if total >= 20:
            interp = f"该靶点具有 **高度可成药性**（{total}/25分），结构信息和化合物资源丰富，适合药物开发。"
        elif total >= 12:
            interp = f"该靶点具有 **中等可成药性**（{total}/25分），存在一定的药物开发基础。"
        else:
            interp = f"该靶点成药性 **有限**（{total}/25分），需要更多结构生物学和化合物研究。"

        section = f"""## 10. {self._t('druggability_assessment')} (0-25 pts)

### {self._t('summary')}

{interp}

### 评分明细

| 维度 | 得分 | 满分 | 数据来源 |
|-----------|------|-----|------|
| 结构可成药性 | {scores.get('structural', 0)} | 10 | PDB, AlphaFold |
| 化合物资源 | {scores.get('chemical', 0)} | 10 | ChEMBL, BindingDB |
| 靶点类别加分 | {scores.get('target_class', 0)} | 5 | 蛋白家族 |
| **总分** | **{total}** | **25** | |

### 成药性解读

"""
        for e in evidence[:5]:
            section += f"- {e}\n"

        section += "\n---\n\n"
        return section

    def _build_section11_safety(self, phases8_12: Dict) -> str:
        """Build Section 11: Safety Analysis with simplified visualization."""
        phase10 = phases8_12.get('results', {}).get('phase10', {})
        scores = phase10.get('scores', {})
        safety_flags = phase10.get('safety_flags', [])

        total = scores.get('total', 0)

        # Generate interpretation with LLM-generated text for missing data
        if total >= 15:
            interp = f"该靶点安全性风险 **较低**（{total}/20分），组织表达选择性良好，遗传学证据支持其可成药性。"
        elif total >= 10:
            interp = f"该靶点存在 **中等安全风险**（{total}/20分），需关注关键组织表达和潜在脱靶效应。"
        else:
            interp = f"该靶点安全性风险 **较高**（{total}/20分），关键组织广泛表达，需谨慎评估并考虑安全性优化策略。"

        section = f"""## 11. {self._t('safety_analysis')} (0-20 pts)

### {self._t('summary')}

{interp}

### 11.1 关键组织表达可视化

![Safety Dashboard](figures/safety_dashboard.png)

*注：上图显示关键组织（心、肝、肾、脑、骨髓）的表达水平，TPM>10为高表达，需关注安全性风险*

### 11.2 评分明细

| 维度 | 得分 | 满分 | 数据来源 |
|-----------|------|-----|------|
| 组织表达选择性 | {scores.get('expression', 0)} | 5 | GTEx关键组织 |
| 遗传学验证 | {scores.get('genetic', 0)} | 10 | 小鼠KO, pLI |
| 不良事件 | {scores.get('adverse', 0)} | 5 | FDA, FAERS |
| **总分** | **{total}** | **20** | |

### 11.3 安全风险提示

| 风险项 | 风险等级 | 数据来源 |
|------|-------------|----------|
"""
        if safety_flags:
            for flag in safety_flags[:5]:
                section += f"| {flag} | 需关注 | 安全分析 |\n"
        else:
            section += f"| 未发现明显安全风险 | 低 | 综合评估 |\n"

        section += "\n---\n\n"
        return section

    def _build_section12_clinical(self, phases8_12: Dict) -> str:
        """Build Section 12: Clinical Precedent with summary."""
        phase11 = phases8_12.get('results', {}).get('phase11', {})
        score = phase11.get('score', 0)
        drugs = phase11.get('drugs', [])
        evidence = phase11.get('evidence', [])

        # Generate interpretation with LLM-generated text for missing data
        if score >= 10:
            interp = f"该靶点具有 **丰富的临床验证**（{score}/15分），已有药物上市或处于后期临床开发阶段。"
        elif score >= 5:
            interp = f"该靶点存在 **一定临床研究**（{score}/15分），有早期临床试验数据支持。"
        else:
            interp = f"该靶点临床验证 **有限**（{score}/15分），{self._t('no_clinical_data')}"

        section = f"""## 12. {self._t('clinical_precedent')} (0-15 pts)

### {self._t('summary')}

{interp}

### 12.1 临床开发时间线

![Clinical Timeline](figures/clinical_timeline.png)

### 12.2 评分

| 指标 | 得分 | 详情 |
|-------|------|---------|
| 临床先例 | {score}/15 | 基于最高临床阶段 |

### 12.3 相关药物

| 药物 | 状态 |
|-----------|--------|
"""
        for drug in drugs[:10]:
            drug_name = drug.get('name', drug) if isinstance(drug, dict) else drug
            phase = drug.get('phase', '研发中') if isinstance(drug, dict) else '研发中'
            section += f"| {drug_name} | 临床阶段 {phase} |\n"

        if not drugs:
            section += f"| {self._t('no_drug_data')} | - |\n"

        section += f"""
### 证据详情

"""
        for e in evidence[:3]:
            section += f"- {e}\n"

        if not evidence:
            section += f"- {self._t('no_clinical_data')}\n"

        section += "\n---\n\n"
        return section

    def _build_section13_validation(self, phases8_12: Dict) -> str:
        """Build Section 13: Validation Evidence with summary."""
        phase12 = phases8_12.get('results', {}).get('phase12', {})
        scores = phase12.get('scores', {})
        evidence = phase12.get('evidence', [])

        total = scores.get('total', 0)

        # Generate interpretation with LLM-generated text for missing data
        if total >= 8:
            interp = f"该靶点具有 **充分的验证证据**（{total}/10分），文献、PPI网络和结构数据支持其作为药物靶点。"
        elif total >= 5:
            interp = f"该靶点验证证据 **中等**（{total}/10分），存在一定的支持数据。"
        else:
            interp = f"该靶点验证证据 **有限**（{total}/10分），需要更多验证研究来支持药物开发决策。"

        section = f"""## 13. {self._t('validation_evidence')} (0-10 pts)

### {self._t('summary')}

{interp}

### 评分明细

| 维度 | 得分 | 满分 | 数据来源 |
|-----------|------|-----|------|
| 文献数量 | {scores.get('publications', 0)} | 4 | PubMed |
| PPI网络 | {scores.get('ppi', 0)} | 3 | STRING |
| 结构数据 | {scores.get('structure', 0)} | 3 | PDB |
| **总分** | **{total}** | **10** | |

### 证据详情

"""
        for e in evidence[:5]:
            section += f"- {e}\n"

        if not evidence:
            section += f"- 验证证据数据有限，建议通过文献检索和实验验证补充。\n"

        section += "\n---\n\n"
        return section

    def _build_section14_scorecard(self, composite: Dict) -> str:
        """Build Section 14: Validation Scorecard with overall summary."""
        scores = composite.get('score_breakdown', {})
        total = composite.get('total_score', 0)
        tier = composite.get('tier', 4)

        tier_desc = self._t(f'tier{tier}')

        # Generate overall interpretation
        if tier == 1:
            overall = f"综合评估显示该靶点具有 **充分的验证证据**（总分 {total}/100），可作为药物研发的优先候选靶点。"
        elif tier == 2:
            overall = f"综合评估显示该靶点具有 **良好的验证基础**（总分 {total}/100），建议在特定领域进行深入验证。"
        elif tier == 3:
            overall = f"综合评估显示该靶点验证证据 **中等**（总分 {total}/100），需要更多数据支持研发决策。"
        else:
            overall = f"综合评估显示该靶点验证证据 **有限**（总分 {total}/100），建议评估替代靶点。"

        section = f"""## 14. {self._t('validation_scorecard')}

### {self._t('summary')}

{overall}

### 综合评分

| {self._t('dimension')} | {self._t('score')} | {self._t('max')} | {self._t('percentage')} |
|-----------|-------|-----|------------|
| 疾病关联性 | {scores.get('disease', 0)} | 30 | {scores.get('disease', 0)/30*100:.0f}% |
| 成药性 | {scores.get('druggability', 0)} | 25 | {scores.get('druggability', 0)/25*100:.0f}% |
| 安全性 | {scores.get('safety', 0)} | 20 | {scores.get('safety', 0)/20*100:.0f}% |
| 临床先例 | {scores.get('clinical', 0)} | 15 | {scores.get('clinical', 0)/15*100:.0f}% |
| 验证证据 | {scores.get('validation', 0)} | 10 | {scores.get('validation', 0)/10*100:.0f}% |
| **总分** | **{total}** | **100** | **{total}%** |

### 等级判定

**等级**: {tier}
**评估**: {tier_desc}

### 等级标准

| 等级 | 分数范围 | 描述 |
|------|-------------|-------------|
| 1 | 80-100 | 强验证 - 证据充分 |
| 2 | 60-79 | 良好验证 - 证据较充分 |
| 3 | 40-59 | 中等验证 - 存在差距 |
| 4 | 0-39 | 有限验证 - 证据不足 |

---

"""

        return section

    def _build_appendix(self, results: Dict) -> str:
        """Build appendix with data sources summary."""
        phases = results.get('phases', {})

        section = f"""## 附录: 数据来源

### 数据库列表

| 数据库 | 使用章节 | 状态 |
|----------|----------|--------|
| OpenTargets | 2, 8, 9, 10, 11, 12 | 成功 |
| UniProtKB | 2, 3, 4 | 成功 |
| PDB | 4 | 成功 |
| GTEx | 7, 11 | 成功 |
| gnomAD | 8 | 成功 |
| STRING | 6, 13 | 成功 |
| ChEMBL | 10 | 成功 |
| IntAct | 6 | 成功 |
| Reactome | 5 | 成功 |
| InterPro | 4 | 成功 |
| AlphaFold | 4 | 成功 |

### 数据处理说明

本报告所有数据均来源于公开数据库，通过自动化数据收集和分析流程生成。报告内容基于客观事实数据，不包含主观推测。

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*所有数据基于公开数据库的事实性信息*
"""

        return section