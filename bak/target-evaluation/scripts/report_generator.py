#!/usr/bin/env python3
"""
Report Generator
Generates markdown reports in three parts with Chinese translation.
Executive Summary is generated last.
"""

import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime


class ReportGenerator:
    """Generate target validation report in markdown format."""

    def __init__(self, output_dir: Path, translate_func=None):
        """
        Initialize report generator.

        Parameters:
            output_dir: Directory to save reports
            translate_func: Function to translate English to Chinese via LLM
        """
        self.output_dir = Path(output_dir)
        self.reports_dir = self.output_dir / 'reports'
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.translate_func = translate_func

    def translate_text(self, text: str) -> str:
        """Translate English text to Chinese using LLM if available."""
        if self.translate_func and text:
            try:
                return self.translate_func(text)
            except Exception:
                return text
        return text

    def format_table(self, headers: List[str], rows: List[List[Any]],
                     min_rows_for_table: int = 2) -> str:
        """
        Format data as markdown table or prose summary.

        Parameters:
            headers: Table headers
            rows: Table rows
            min_rows_for_table: Minimum rows to use table format

        Returns:
            Markdown formatted string
        """
        if len(rows) < min_rows_for_table:
            # Use prose format for small data
            if len(rows) == 0:
                return "暂无数据 (No data available)\n"
            elif len(rows) == 1:
                parts = []
                for h, v in zip(headers, rows[0]):
                    parts.append(f"- **{h}**: {v}")
                return "\n".join(parts) + "\n"

        # Use table format for larger data
        header_row = "| " + " | ".join(str(h) for h in headers) + " |"
        separator = "| " + " | ".join("-" * len(h) for h in headers) + " |"
        data_rows = []
        for row in rows:
            data_rows.append("| " + " | ".join(str(v) if v is not None else "N/A" for v in row) + " |")

        return header_row + "\n" + separator + "\n" + "\n".join(data_rows) + "\n"

    def generate_part_a(self, ids: Dict[str, Any], all_data: Dict[str, Any],
                        viz_paths: Dict[str, Path]) -> str:
        """
        Generate Part A: Target Intelligence report.

        Parameters:
            ids: Target identifiers
            all_data: All collected data
            viz_paths: Visualization file paths

        Returns:
            Markdown report content
        """
        lines = []

        lines.append(f"# Part A: 靶点情报 (Target Intelligence)\n")
        lines.append(f"**生成时间 (Generated)**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Section 1: Target Identifiers
        lines.append("## 1. 靶点标识符 (Target Identifiers)\n")

        identifier_rows = [
            ["基因符号 (Gene Symbol)", ids.get('symbol', 'N/A'), "HGNC"],
            ["UniProt登录号 (UniProt Accession)", ids.get('uniprot', 'N/A'), "UniProtKB"],
            ["Ensembl基因ID (Ensembl Gene ID)", ids.get('ensembl', 'N/A'), "Ensembl"],
            ["Entrez基因ID (Entrez Gene ID)", ids.get('entrez', 'N/A'), "NCBI Gene"],
            ["ChEMBL靶点ID (ChEMBL Target ID)", ids.get('chembl_target', 'N/A'), "ChEMBL"],
        ]

        lines.append(self.format_table(
            ["标识符类型 (Identifier Type)", "值 (Value)", "数据库 (Database)"],
            identifier_rows
        ))

        if ids.get('synonyms'):
            lines.append(f"\n**别名 (Aliases)**: {', '.join(ids['synonyms'][:5])}\n")

        # Section 2: Basic Information
        lines.append("## 2. 基本信息 (Basic Information)\n")

        uniprot_data = all_data.get('section2_basic_info', {}).get('data', {})

        lines.append("### 2.1 蛋白描述 (Protein Description)\n")

        functions = uniprot_data.get('functions', [])
        if functions:
            if isinstance(functions, list):
                for func in functions[:2]:
                    lines.append(f"- {self.translate_text(str(func))}\n")
            else:
                lines.append(f"- {self.translate_text(str(functions))}\n")

        location = uniprot_data.get('location', {})
        if location:
            lines.append("### 2.2 亚细胞定位 (Subcellular Localization)\n")
            if isinstance(location, dict):
                loc_data = location.get('data', location)
                if isinstance(loc_data, list):
                    for loc in loc_data[:3]:
                        if isinstance(loc, dict):
                            lines.append(f"- {loc.get('location', 'N/A')}\n")
                else:
                    lines.append(f"- {str(loc_data)}\n")
            else:
                lines.append(f"- {str(location)}\n")

        # Section 3: Structural Biology
        lines.append("## 3. 结构生物学 (Structural Biology)\n")

        structure_data = all_data.get('section3_structure', {}).get('data', {})

        # PDB structures
        pdb_refs = uniprot_data.get('pdb_cross_references', [])
        if pdb_refs:
            lines.append("### 3.1 实验结构 (Experimental Structures - PDB)\n")
            pdb_rows = []
            for pdb in pdb_refs[:10]:
                pdb_rows.append([
                    pdb.get('pdb_id', 'N/A'),
                    pdb.get('resolution', 'N/A'),
                    pdb.get('method', 'N/A')
                ])
            lines.append(self.format_table(
                ["PDB ID", "分辨率 (Resolution)", "方法 (Method)"],
                pdb_rows
            ))
            lines.append(f"\n**PDB条目总数 (Total PDB Entries)**: {len(pdb_refs)}\n")
        else:
            lines.append("### 3.1 实验结构 (Experimental Structures - PDB)\n")
            lines.append("暂无PDB结构数据 (No PDB structure data available)\n")

        # AlphaFold
        alphafold_summary = structure_data.get('alphafold_summary', {})
        if alphafold_summary:
            lines.append("### 3.2 AlphaFold预测 (AlphaFold Prediction)\n")
            if isinstance(alphafold_summary, dict):
                mean_plddt = alphafold_summary.get('mean_plddt', 'N/A')
                lines.append(f"- **平均pLDDT**: {mean_plddt}\n")
                if mean_plddt and isinstance(mean_plddt, (int, float)):
                    if mean_plddt > 70:
                        lines.append("- **置信度**: 高 (High)\n")
                    elif mean_plddt > 50:
                        lines.append("- **置信度**: 中 (Medium)\n")
                    else:
                        lines.append("- **置信度**: 低 (Low)\n")

        # Domains
        domains = structure_data.get('domains', [])
        if domains:
            lines.append("### 3.3 结构域架构 (Domain Architecture)\n")
            domain_rows = []
            # Handle domains as list or dict
            domains_list = domains if isinstance(domains, list) else [domains]
            # If it's a dict with results, extract the list
            if isinstance(domains, dict) and 'results' in domains:
                domains_list = domains['results']
            for dom in domains_list[:10]:
                if isinstance(dom, dict):
                    domain_rows.append([
                        dom.get('name', dom.get('type', 'N/A')),
                        f"{dom.get('start', '-')}-{dom.get('end', '-')}",
                        dom.get('accession', 'N/A')
                    ])
            if domain_rows:
                lines.append(self.format_table(
                    ["结构域 (Domain)", "位置 (Position)", "ID"],
                    domain_rows
                ))

        # Section 4: Function & Pathways
        lines.append("## 4. 功能与通路 (Function & Pathways)\n")

        pathway_data = all_data.get('section4_pathways', {}).get('data', {})

        # Reactome
        reactome = pathway_data.get('reactome', [])
        if reactome:
            lines.append("### 4.1 Reactome通路\n")
            reactome_rows = []
            for pw in reactome[:10]:
                if isinstance(pw, dict):
                    reactome_rows.append([
                        pw.get('displayName', pw.get('name', 'N/A')),
                        pw.get('stId', 'N/A')
                    ])
            if reactome_rows:
                lines.append(self.format_table(
                    ["通路名称 (Pathway Name)", "ID"],
                    reactome_rows
                ))
            else:
                lines.append("暂无Reactome通路数据 (No Reactome pathway data)\n")

        # GO annotations
        go = pathway_data.get('go', [])
        if go:
            lines.append("### 4.2 GO注释 (GO Annotations)\n")
            if isinstance(go, list):
                for go_term in go[:5]:
                    if isinstance(go_term, dict):
                        lines.append(f"- {go_term.get('term', '')} ({go_term.get('id', '')})\n")

        # Section 5: Protein Interactions
        lines.append("## 5. 蛋白相互作用 (Protein-Protein Interactions)\n")

        ppi_data = all_data.get('section5_ppi', {}).get('data', {})
        interactors = ppi_data.get('interactors', [])
        source = all_data.get('section5_ppi', {}).get('source', 'N/A')

        lines.append(f"**数据来源 (Source)**: {source}\n")
        lines.append(f"**相互作用蛋白数量 (Total Interactors)**: {len(interactors)}\n")

        if interactors and len(interactors) >= 2:
            lines.append("\n### 5.1 主要相互作用伙伴 (Top Interacting Partners)\n")
            interactor_rows = []
            for inter in interactors[:10]:
                if isinstance(inter, dict):
                    interactor_rows.append([
                        inter.get('partner', inter.get('symbol', inter.get('name', 'N/A'))),
                        inter.get('score', 'N/A'),
                        inter.get('type', 'N/A')
                    ])
            if interactor_rows:
                lines.append(self.format_table(
                    ["相互作用蛋白 (Partner)", "分数 (Score)", "类型 (Type)"],
                    interactor_rows
                ))
        elif interactors:
            lines.append("\n### 5.1 相互作用概述\n")
            for inter in interactors[:3]:
                if isinstance(inter, dict):
                    lines.append(f"- {inter.get('partner', inter.get('symbol', 'Unknown'))}\n")

        # Section 6: Expression Profile
        lines.append("## 6. 表达谱 (Expression Profile)\n")

        expression_data = all_data.get('section6_expression', {}).get('data', {})
        gtex = expression_data.get('gtex', {})

        # Add visualization if available
        if 'tissue_expression' in viz_paths:
            lines.append(f"\n![组织表达热图](visualizations/tissue_expression_heatmap.png)\n")

        lines.append("### 6.1 组织表达 (Tissue Expression)\n")

        if isinstance(gtex, dict) and 'data' in gtex:
            tissue_rows = []
            for tissue_data in gtex['data'][:10]:
                if isinstance(tissue_data, dict):
                    tissue_rows.append([
                        tissue_data.get('tissue', 'N/A'),
                        f"{tissue_data.get('median', 0):.2f}",
                        "高" if tissue_data.get('median', 0) > 50 else "中" if tissue_data.get('median', 0) > 20 else "低"
                    ])
            if tissue_rows:
                lines.append(self.format_table(
                    ["组织 (Tissue)", "TPM", "表达水平 (Level)"],
                    tissue_rows
                ))

        # Critical tissue expression
        critical_tissues = ['heart', 'liver', 'kidney', 'brain', 'bone marrow']
        lines.append("\n### 6.2 关键组织表达 (Critical Tissue Expression)\n")
        if isinstance(gtex, dict) and 'data' in gtex:
            for tissue_data in gtex['data']:
                if isinstance(tissue_data, dict):
                    tissue = tissue_data.get('tissue', '').lower()
                    if any(c in tissue for c in critical_tissues):
                        tpm = tissue_data.get('median', 0)
                        level = "**高** ⚠️" if tpm > 50 else "中" if tpm > 20 else "低"
                        lines.append(f"- **{tissue_data.get('tissue')}**: {tpm:.1f} TPM ({level})\n")

        # Section 7: Genetic Variation
        lines.append("## 7. 遗传变异 (Genetic Variation)\n")

        genetics_data = all_data.get('section7_genetics', {}).get('data', {})

        # Constraint scores
        constraints = genetics_data.get('constraints', {})
        if constraints:
            lines.append("### 7.1 遗传约束评分 (Genetic Constraint Scores)\n")

            constraint_rows = [
                ["pLI", f"{constraints.get('pLI', 'N/A'):.3f}" if isinstance(constraints.get('pLI'), (int, float)) else "N/A",
                 "高度约束 (>0.9)" if constraints.get('pLI', 0) > 0.9 else "耐受"],
                ["LOEUF", f"{constraints.get('LOEUF', 'N/A'):.3f}" if isinstance(constraints.get('LOEUF'), (int, float)) else "N/A",
                 "约束 (<0.35)" if constraints.get('LOEUF', 1) < 0.35 else "正常"],
                ["Missense Z", f"{constraints.get('missense_z', 'N/A'):.2f}" if isinstance(constraints.get('missense_z'), (int, float)) else "N/A",
                 "约束 (>3)" if constraints.get('missense_z', 0) > 3 else "正常"],
            ]
            lines.append(self.format_table(
                ["指标 (Metric)", "值 (Value)", "解释 (Interpretation)"],
                constraint_rows
            ))

        # ClinVar variants
        clinvar = genetics_data.get('clinvar', [])
        if clinvar:
            lines.append("\n### 7.2 临床变异 (ClinVar Variants)\n")
            if isinstance(clinvar, list):
                pathogenic = [v for v in clinvar if 'pathogenic' in str(v.get('clinical_significance', '')).lower()]
                lines.append(f"**致病变异数量 (Pathogenic Variants)**: {len(pathogenic)}\n")

        # Save Part A
        report_path = self.reports_dir / 'part_a_target_intelligence.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        return ''.join(lines)

    def generate_part_b(self, scoring_results: Dict[str, Any],
                        viz_paths: Dict[str, Path]) -> str:
        """
        Generate Part B: Validation Assessment report.

        Parameters:
            scoring_results: All scoring results
            viz_paths: Visualization file paths

        Returns:
            Markdown report content
        """
        lines = []

        lines.append("# Part B: 验证评估 (Validation Assessment)\n")

        # Add validation score visualization
        if 'validation_score' in viz_paths:
            lines.append("\n![验证评分图表](visualizations/validation_score_chart.png)\n")

        # Section 8: Disease Association Scoring
        lines.append("## 8. 疾病关联评分 (Disease Association Scoring) - 0-30分\n")

        disease_scores = scoring_results.get('disease_association', {})
        scores = disease_scores.get('scores', {})

        lines.append("### 8.1 遗传证据 (Genetic Evidence)\n")
        genetic_score = scores.get('genetic', 0)
        lines.append(f"**得分**: {genetic_score}/10\n")

        # Section 9: Druggability Assessment
        lines.append("## 9. 可成药性评估 (Druggability Assessment) - 0-25分\n")

        druggability = scoring_results.get('druggability', {})
        drug_scores = druggability.get('scores', {})

        drug_rows = [
            ["结构可及性 (Structural)", drug_scores.get('structural', 0), 10],
            ["化学物质 (Chemical Matter)", drug_scores.get('chemical', 0), 10],
            ["靶点类别加成 (Target Class)", drug_scores.get('target_class', 0), 5],
        ]
        lines.append(self.format_table(
            ["维度 (Dimension)", "得分 (Score)", "满分 (Max)"],
            drug_rows
        ))

        total_drug = drug_scores.get('total', 0)
        lines.append(f"\n**可成药性总分**: {total_drug}/25\n")

        # Section 10: Safety Analysis
        lines.append("## 10. 安全性分析 (Safety Analysis) - 0-20分\n")

        safety = scoring_results.get('safety', {})
        safety_scores = safety.get('scores', {})

        safety_rows = [
            ["表达选择性 (Expression Selectivity)", safety_scores.get('expression', 0), 5],
            ["遗传验证 (Genetic Validation)", safety_scores.get('genetic', 0), 10],
            ["已知不良反应 (Known ADRs)", safety_scores.get('adverse', 0), 5],
        ]
        lines.append(self.format_table(
            ["维度 (Dimension)", "得分 (Score)", "满分 (Max)"],
            safety_rows
        ))

        safety_flags = safety.get('safety_flags', [])
        if safety_flags:
            lines.append("\n### 安全警示 (Safety Flags)\n")
            for flag in safety_flags:
                lines.append(f"- ⚠️ {flag}\n")

        # Section 11: Clinical Precedent
        lines.append("## 11. 临床先例 (Clinical Precedent) - 0-15分\n")

        clinical = scoring_results.get('clinical_precedent', {})
        clinical_score = clinical.get('score', 0)
        approved_drugs = clinical.get('approved_drugs', [])

        lines.append(f"**临床先例得分**: {clinical_score}/15\n")

        if approved_drugs:
            lines.append("\n### 已批准药物 (Approved Drugs)\n")
            drug_rows = [[d.get('name', 'N/A'), d.get('indication', 'N/A')] for d in approved_drugs[:5]]
            lines.append(self.format_table(
                ["药物名称 (Drug Name)", "适应症 (Indication)"],
                drug_rows
            ))

        # Add clinical timeline visualization
        if 'clinical_timeline' in viz_paths:
            lines.append(f"\n![临床开发现状](visualizations/clinical_timeline.png)\n")

        # Section 12: Validation Evidence
        lines.append("## 12. 验证证据 (Validation Evidence) - 0-10分\n")

        validation = scoring_results.get('validation_evidence', {})
        val_scores = validation.get('scores', {})

        lines.append(f"**验证证据总分**: {val_scores.get('total', 0)}/10\n")

        # Section 13: Composite Score
        lines.append("## 13. 综合评分 (Composite Score)\n")

        composite = scoring_results.get('composite', {})

        composite_rows = []
        components = composite.get('components', {})
        for name, data in components.items():
            name_cn = {
                'disease_association': '疾病关联',
                'druggability': '可成药性',
                'safety': '安全性',
                'clinical_precedent': '临床先例',
                'validation_evidence': '验证证据'
            }.get(name, name)
            composite_rows.append([
                name_cn,
                data.get('score', 0),
                data.get('max', 0),
                f"{data.get('score', 0)/data.get('max', 1)*100:.0f}%" if data.get('max', 0) > 0 else 'N/A'
            ])

        lines.append(self.format_table(
            ["维度 (Dimension)", "得分 (Score)", "满分 (Max)", "百分比 (%)"],
            composite_rows
        ))

        total = composite.get('total', 0)
        tier = composite.get('tier', 4)
        recommendation = composite.get('recommendation', '')

        lines.append(f"\n### 优先层级 (Priority Tier)\n")
        lines.append(f"**层级**: Tier {tier}\n")
        lines.append(f"**总分**: {total}/100\n")
        lines.append(f"**建议**: {recommendation}\n")

        # Save Part B
        report_path = self.reports_dir / 'part_b_validation_assessment.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        return ''.join(lines)

    def generate_part_c(self, ids: Dict[str, Any], scoring_results: Dict[str, Any],
                        all_data: Dict[str, Any]) -> str:
        """
        Generate Part C: Synthesis & Recommendations report.

        Parameters:
            ids: Target identifiers
            scoring_results: All scoring results
            all_data: All collected data

        Returns:
            Markdown report content
        """
        lines = []

        lines.append("# Part C: 综合与建议 (Synthesis & Recommendations)\n")

        composite = scoring_results.get('composite', {})
        total = composite.get('total', 0)
        tier = composite.get('tier', 4)
        safety_flags = scoring_results.get('safety', {}).get('safety_flags', [])

        # Section 14: Validation Roadmap
        lines.append("## 14. 验证路线图 (Validation Roadmap)\n")

        lines.append("### 推荐验证实验 (Recommended Validation Experiments)\n")

        # Generate recommendations based on score gaps
        components = composite.get('components', {})

        recommendations = []

        # Disease association gap
        disease_score = components.get('disease_association', {}).get('score', 0)
        if disease_score < 20:
            recommendations.append(("高", "GWAS关联验证", "加强遗传证据支持", "2-3个月"))

        # Druggability gap
        drug_score = components.get('druggability', {}).get('score', 0)
        if drug_score < 15:
            recommendations.append(("高", "先导化合物筛选", "建立化学物质基础", "3-6个月"))

        # Safety gap
        safety_score = components.get('safety', {}).get('score', 0)
        if safety_score < 10:
            recommendations.append(("中", "安全性评估", "评估靶点特异性毒性风险", "3-6个月"))

        # Validation evidence gap
        val_score = components.get('validation_evidence', {}).get('score', 0)
        if val_score < 5:
            recommendations.append(("中", "功能验证研究", "建立疾病模型验证", "6-12个月"))

        if recommendations:
            rec_rows = [[p, e, r, t] for p, e, r, t in recommendations]
            lines.append(self.format_table(
                ["优先级 (Priority)", "实验 (Experiment)", "理由 (Rationale)", "时间线 (Timeline)"],
                rec_rows
            ))
        else:
            lines.append("靶点验证充分，建议推进至开发阶段。\n")

        # Section 15: Tool Compounds
        lines.append("## 15. 工具化合物 (Tool Compounds)\n")

        chemical_probes = all_data.get('ot_foundation', {}).get('data', {}).get('chemical_probes', {})
        if chemical_probes:
            probes_list = chemical_probes if isinstance(chemical_probes, list) else chemical_probes.get('data', [])
            if probes_list:
                lines.append("### 推荐化学探针\n")
                for probe in probes_list[:3]:
                    if isinstance(probe, dict):
                        lines.append(f"- **{probe.get('name', 'Unknown')}**: {probe.get('source', 'N/A')}\n")

        # Section 16: Biomarker Strategy
        lines.append("## 16. 生物标志物策略 (Biomarker Strategy)\n")

        lines.append("### 预测性生物标志物 (Predictive Biomarkers)\n")
        lines.append("根据疾病关联和表达数据确定患者分层策略。\n")

        # Section 17: Key Risks & Mitigations
        lines.append("## 17. 主要风险与缓解措施 (Key Risks & Mitigations)\n")

        lines.append("### 风险评估 (Risk Assessment)\n")

        risk_rows = []

        if safety_flags:
            risk_rows.append(["安全性", ", ".join(safety_flags), "中", "高"])

        expression_data = all_data.get('section6_expression', {}).get('data', {})
        gtex = expression_data.get('gtex', {})
        if isinstance(gtex, dict) and 'data' in gtex:
            critical_high = []
            for tissue_data in gtex['data']:
                if isinstance(tissue_data, dict):
                    tissue = tissue_data.get('tissue', '').lower()
                    tpm = tissue_data.get('median', 0)
                    if any(c in tissue for c in ['heart', 'liver', 'kidney', 'brain']) and tpm > 50:
                        critical_high.append(tissue)
            if critical_high:
                risk_rows.append(["毒性", f"关键组织高表达: {', '.join(critical_high)}", "高", "高"])

        if not risk_rows:
            risk_rows.append(["整体", "未识别重大风险", "低", "低"])

        lines.append(self.format_table(
            ["风险类别 (Risk Category)", "风险 (Risk)", "概率 (Probability)", "影响 (Impact)"],
            risk_rows
        ))

        # Key strengths
        lines.append("\n### 关键优势 (Key Strengths)\n")
        if total >= 80:
            lines.append("1. 靶点验证充分，具有强有力证据支持\n")
            lines.append("2. 已有临床先例，开发风险较低\n")
        elif total >= 60:
            lines.append("1. 具有良好的成药性基础\n")
            lines.append("2. 存在一定的验证证据\n")
        else:
            lines.append("1. 靶点新颖，可能具有差异化潜力\n")

        # Save Part C
        report_path = self.reports_dir / 'part_c_synthesis_recommendations.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        return ''.join(lines)

    def generate_executive_summary(self, ids: Dict[str, Any],
                                   scoring_results: Dict[str, Any],
                                   viz_paths: Dict[str, Path]) -> str:
        """
        Generate Executive Summary (generated last).

        Parameters:
            ids: Target identifiers
            scoring_results: All scoring results
            viz_paths: Visualization file paths

        Returns:
            Markdown report content
        """
        lines = []

        lines.append(f"# Executive Summary\n")
        lines.append(f"**靶点 (Target)**: {ids.get('symbol', 'Unknown')} ({ids.get('full_name', ids.get('symbol', 'Unknown'))})\n")
        lines.append(f"**生成时间 (Generated)**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Add validation score visualization
        if 'validation_score' in viz_paths:
            lines.append("\n![验证评分概览](visualizations/validation_score_chart.png)\n")

        # Scorecard
        lines.append("## 验证评分卡 (Target Validation Scorecard)\n")

        # Get composite from section13
        composite = scoring_results.get('section13', {})
        components = composite.get('components', {})

        # Extract individual scores from sections
        section8 = scoring_results.get('section8', {})
        section9 = scoring_results.get('section9', {})
        section10 = scoring_results.get('section10', {})
        section11 = scoring_results.get('section11', {})
        section12 = scoring_results.get('section12', {})

        # Get scores from either components or direct section results
        disease_score = components.get('disease_association', {}).get('score', section8.get('scores', {}).get('total', 0))
        druggability_score = components.get('druggability', {}).get('score', section9.get('scores', {}).get('total', 0))
        safety_score = components.get('safety', {}).get('score', section10.get('scores', {}).get('total', 0))
        clinical_score = components.get('clinical_precedent', {}).get('score', section11.get('score', 0))
        validation_score = components.get('validation_evidence', {}).get('score', section12.get('scores', {}).get('total', 0))

        scorecard_rows = [
            ["疾病关联 (Disease Association)", disease_score, 30],
            ["可成药性 (Druggability)", druggability_score, 25],
            ["安全性 (Safety)", safety_score, 20],
            ["临床先例 (Clinical Precedent)", clinical_score, 15],
            ["验证证据 (Validation Evidence)", validation_score, 10],
        ]

        lines.append(self.format_table(
            ["维度 (Dimension)", "得分 (Score)", "满分 (Max)"],
            scorecard_rows
        ))

        total = composite.get('total', 0)
        tier = composite.get('tier', 4)
        recommendation = composite.get('recommendation', '')

        lines.append(f"\n| **总分 (Total)** | **{total}** | **100** |\n")
        lines.append(f"\n**优先层级 (Priority Tier)**: Tier {tier}\n")
        lines.append(f"**GO/NO-GO建议**: {recommendation}\n")

        # Key Findings
        lines.append("\n## 主要发现 (Key Findings)\n")

        findings = []

        # Disease association finding
        disease = scoring_results.get('disease_association', {}).get('disease', '')
        if disease:
            disease_score = components.get('disease_association', {}).get('score', 0)
            findings.append(f"1. 与{disease}存在{'强' if disease_score >= 20 else '中等' if disease_score >= 10 else '弱'}关联 [T3]\n")

        # Druggability finding
        drug_score = components.get('druggability', {}).get('score', 0)
        if drug_score >= 20:
            findings.append("2. 靶点具有良好的可成药性，已有化学物质和结构信息支持 [T1/T2]\n")
        elif drug_score >= 10:
            findings.append("2. 靶点具有一定的可成药性，需进一步优化 [T2/T3]\n")
        else:
            findings.append("2. 靶点可成药性有限，需探索新型药物模式 [T3/T4]\n")

        # Clinical finding
        clinical_score = components.get('clinical_precedent', {}).get('score', 0)
        approved_drugs = scoring_results.get('clinical_precedent', {}).get('approved_drugs', [])
        if clinical_score >= 15:
            findings.append(f"3. 已有{len(approved_drugs)}个FDA批准药物，临床验证充分 [T1]\n")
        elif clinical_score >= 5:
            findings.append("3. 存在临床开发项目，具有一定临床验证 [T2]\n")
        else:
            findings.append("3. 暂无临床开发先例，为新型靶点 [T4]\n")

        lines.extend(findings)

        # Critical Risks
        lines.append("\n## 关键风险 (Critical Risks)\n")

        safety_flags = scoring_results.get('safety', {}).get('safety_flags', [])
        if safety_flags:
            for flag in safety_flags:
                lines.append(f"- ⚠️ {flag}\n")
        else:
            lines.append("- 未识别重大安全风险\n")

        # Recommendation
        lines.append("\n## 建议 (Recommendation)\n")

        if tier == 1:
            lines.append("**GO** - 靶点验证充分，建议推进至药物开发阶段。重点关注差异化策略和竞争优势。\n")
        elif tier == 2:
            lines.append("**CONDITIONAL GO** - 靶点具有潜力，但需完成关键验证实验后再推进。建议重点关注数据补全计划。\n")
        elif tier == 3:
            lines.append("**CAUTION** - 靶点存在一定风险，建议谨慎评估。需进行充分的早期验证研究。\n")
        else:
            lines.append("**NO-GO** - 靶点验证不足或风险过高，建议考虑替代靶点或重新评估策略。\n")

        # Save Executive Summary
        report_path = self.reports_dir / 'executive_summary.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        return ''.join(lines)

    def generate_combined_report(self, ids: Dict[str, Any],
                                 all_data: Dict[str, Any],
                                 scoring_results: Dict[str, Any],
                                 viz_paths: Dict[str, Path]) -> Path:
        """
        Generate combined full report with all parts.
        Executive Summary is placed first but generated last.

        Parameters:
            ids: Target identifiers
            all_data: All collected data
            scoring_results: All scoring results
            viz_paths: Visualization file paths

        Returns:
            Path to combined report
        """
        # Generate parts in order (Executive Summary last)
        exec_summary = self.generate_executive_summary(ids, scoring_results, viz_paths)
        part_a = self.generate_part_a(ids, all_data, viz_paths)
        part_b = self.generate_part_b(scoring_results, viz_paths)
        part_c = self.generate_part_c(ids, scoring_results, all_data)

        # Combine (Executive Summary first)
        composite = scoring_results.get('section13', {})
        combined = f"# 靶点验证报告 (Target Validation Report)\n\n"
        combined += f"**靶点 (Target)**: {ids.get('symbol', 'Unknown')}\n"
        combined += f"**生成时间 (Generated)**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        combined += f"**总分 (Total Score)**: {composite.get('total', 0)}/100\n"
        combined += f"**层级 (Tier)**: Tier {composite.get('tier', 4)}\n\n"
        combined += "---\n\n"

        # Add Executive Summary first
        combined += exec_summary
        combined += "\n---\n\n"

        # Add Part A
        combined += part_a
        combined += "\n---\n\n"

        # Add Part B
        combined += part_b
        combined += "\n---\n\n"

        # Add Part C
        combined += part_c

        # Save combined report
        report_path = self.reports_dir / f'{ids.get("symbol", "target")}_validation_report.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(combined)

        return report_path


if __name__ == "__main__":
    # Test report generation
    from pathlib import Path

    output_dir = Path('./reports/test_run')

    generator = ReportGenerator(output_dir)

    test_ids = {'symbol': 'EGFR', 'uniprot': 'P00533', 'ensembl': 'ENSG00000146648'}
    test_scoring = {
        'composite': {
            'total': 88,
            'tier': 1,
            'recommendation': 'GO',
            'components': {
                'disease_association': {'score': 28, 'max': 30},
                'druggability': {'score': 24, 'max': 25},
                'safety': {'score': 12, 'max': 20},
                'clinical_precedent': {'score': 15, 'max': 15},
                'validation_evidence': {'score': 9, 'max': 10}
            }
        },
        'safety': {'safety_flags': []},
        'clinical_precedent': {'score': 15, 'approved_drugs': [{'name': 'Erlotinib', 'indication': 'NSCLC'}]}
    }

    exec_summary = generator.generate_executive_summary(test_ids, test_scoring, {})
    print("Executive Summary generated")