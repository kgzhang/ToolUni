#!/usr/bin/env python3
"""
Report Generator Module for Target Validation

Generates comprehensive markdown reports with:
- Simplified Chinese (default) and English support
- Section summaries with detailed data
- No emoji, Sources info, or Appendices
- Proper data filling (no Unknown/N/A issues)
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class ReportGenerator:
    """
    Generates comprehensive target validation reports.

    Supports Chinese (zh) and English (en) languages.
    Default language is Chinese (zh).
    """

    TRANSLATIONS = {
        'zh': {
            # Report titles
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
            'safety_analysis': '安全性深度分析',
            'clinical_precedent': '临床先例',
            'validation_evidence': '验证证据',
            'validation_scorecard': '验证评分卡',
            'validation_roadmap': '验证路线图',
            'tool_compounds': '工具化合物',
            'biomarker_strategy': '生物标志物策略',
            'risks_mitigations': '关键风险与缓解措施',

            # Table headers
            'identifier_type': '标识符类型',
            'value': '值',
            'database': '数据库',
            'gene_symbol': '基因符号',
            'uniprot_accession': 'UniProt登录号',
            'ensembl_id': 'Ensembl基因ID',
            'entrez_id': 'Entrez基因ID',
            'chembl_id': 'ChEMBL靶点ID',
            'confidence_level': '置信度',
            'aliases': '别名',

            # Protein info
            'recommended_name': '推荐名称',
            'alternative_names': '替代名称',
            'gene_name': '基因名称',
            'organism': '物种',
            'protein_length': '蛋白长度',
            'amino_acids': '氨基酸',
            'protein_function': '蛋白功能',
            'subcellular_location': '亚细胞定位',

            # Structure
            'pdb_structures': 'PDB结构',
            'resolution': '分辨率',
            'method': '方法',
            'total_entries': '总条目数',
            'best_resolution': '最佳分辨率',
            'alphafold_prediction': 'AlphaFold预测',
            'domain_architecture': '结构域架构',
            'structural_druggability': '结构成药性',

            # Scoring
            'dimension': '维度',
            'score': '分数',
            'max': '满分',
            'percentage': '百分比',
            'priority_tier': '优先级等级',
            'recommendation': '建议',
            'total': '总计',

            # Tiers
            'tier1': '一级',
            'tier2': '二级',
            'tier3': '三级',
            'tier4': '四级',
            'go': '通过',
            'conditional_go': '条件通过',
            'caution': '谨慎',
            'no_go': '不通过',

            # Misc
            'not_available': '暂无数据',
            'high': '高',
            'medium': '中',
            'low': '低',
            'summary': '摘要',
            'details': '详细信息',
            'visualization': '可视化',
            'key_findings': '关键发现',
            'critical_risks': '关键风险',
            'key_strengths': '主要优势',
            'bottom_line': '结论',

            # Disease
            'disease': '疾病',
            'association_score': '关联评分',
            'evidence_tier': '证据等级',
            'genetic_evidence': '遗传证据',
            'literature_evidence': '文献证据',
            'pathway_evidence': '通路证据',

            # Safety
            'tissue_expression_selectivity': '组织表达选择性',
            'genetic_validation': '遗传验证',
            'adverse_events': '不良事件',
            'safety_liabilities': '安全隐患',

            # Clinical
            'approved_drugs': '已批准药物',
            'clinical_trials': '临床试验',
            'phase': '阶段',
            'indication': '适应症',
            'status': '状态',

            # Risk
            'risk_category': '风险类别',
            'probability': '概率',
            'impact': '影响',
            'mitigation': '缓解策略',
            'key_challenges': '主要挑战',
        },
        'en': {
            # Report titles
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
            'safety_analysis': 'Safety Deep Analysis',
            'clinical_precedent': 'Clinical Precedent',
            'validation_evidence': 'Validation Evidence',
            'validation_scorecard': 'Validation Scorecard',
            'validation_roadmap': 'Validation Roadmap',
            'tool_compounds': 'Tool Compounds',
            'biomarker_strategy': 'Biomarker Strategy',
            'risks_mitigations': 'Key Risks & Mitigations',

            # Table headers
            'identifier_type': 'Identifier Type',
            'value': 'Value',
            'database': 'Database',
            'gene_symbol': 'Gene Symbol',
            'uniprot_accession': 'UniProt Accession',
            'ensembl_id': 'Ensembl Gene ID',
            'entrez_id': 'Entrez Gene ID',
            'chembl_id': 'ChEMBL Target ID',
            'confidence_level': 'Confidence',
            'aliases': 'Aliases',

            # Protein info
            'recommended_name': 'Recommended Name',
            'alternative_names': 'Alternative Names',
            'gene_name': 'Gene Name',
            'organism': 'Organism',
            'protein_length': 'Protein Length',
            'amino_acids': 'amino acids',
            'protein_function': 'Protein Function',
            'subcellular_location': 'Subcellular Location',

            # Structure
            'pdb_structures': 'PDB Structures',
            'resolution': 'Resolution',
            'method': 'Method',
            'total_entries': 'Total Entries',
            'best_resolution': 'Best Resolution',
            'alphafold_prediction': 'AlphaFold Prediction',
            'domain_architecture': 'Domain Architecture',
            'structural_druggability': 'Structural Druggability',

            # Scoring
            'dimension': 'Dimension',
            'score': 'Score',
            'max': 'Max',
            'percentage': 'Percentage',
            'priority_tier': 'Priority Tier',
            'recommendation': 'Recommendation',
            'total': 'TOTAL',

            # Tiers
            'tier1': 'Tier 1',
            'tier2': 'Tier 2',
            'tier3': 'Tier 3',
            'tier4': 'Tier 4',
            'go': 'GO',
            'conditional_go': 'CONDITIONAL GO',
            'caution': 'CAUTION',
            'no_go': 'NO-GO',

            # Misc
            'not_available': 'Not available',
            'high': 'High',
            'medium': 'Medium',
            'low': 'Low',
            'summary': 'Summary',
            'details': 'Details',
            'visualization': 'Visualization',
            'key_findings': 'Key Findings',
            'critical_risks': 'Critical Risks',
            'key_strengths': 'Key Strengths',
            'bottom_line': 'Bottom Line',

            # Disease
            'disease': 'Disease',
            'association_score': 'Association Score',
            'evidence_tier': 'Evidence Tier',
            'genetic_evidence': 'Genetic Evidence',
            'literature_evidence': 'Literature Evidence',
            'pathway_evidence': 'Pathway Evidence',

            # Safety
            'tissue_expression_selectivity': 'Tissue Expression Selectivity',
            'genetic_validation': 'Genetic Validation',
            'adverse_events': 'Adverse Events',
            'safety_liabilities': 'Safety Liabilities',

            # Clinical
            'approved_drugs': 'Approved Drugs',
            'clinical_trials': 'Clinical Trials',
            'phase': 'Phase',
            'indication': 'Indication',
            'status': 'Status',

            # Risk
            'risk_category': 'Risk Category',
            'probability': 'Probability',
            'impact': 'Impact',
            'mitigation': 'Mitigation Strategy',
            'key_challenges': 'Key Challenges',
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
        Generate comprehensive markdown report.
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

        # Build report sections
        report = self._build_header(symbol, name, ids, date, phases)
        report += self._build_executive_summary(composite, ids, phases)
        report += self._build_target_intelligence(ids, phases)
        report += self._build_validation_assessment(phases, composite)
        report += self._build_synthesis(results)

        # Save report
        report_file = self.output_dir / f"{symbol}_validation_report.md"
        with open(report_file, 'w') as f:
            f.write(report)

        return str(report_file)

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
        """Build executive summary section."""
        scores = composite.get('score_breakdown', {})
        total = composite.get('total_score', 0)
        tier = composite.get('tier', 4)
        rec = composite.get('recommendation', 'NO-GO')

        # Translate recommendation
        rec_translated = {
            'GO': self._t('go'),
            'CONDITIONAL GO': self._t('conditional_go'),
            'CAUTION': self._t('caution'),
            'NO-GO': self._t('no_go')
        }.get(rec, rec)

        # Gather evidence
        evidence = []
        for phase_key in ['phase8', 'phase9', 'phase10', 'phase11', 'phase12']:
            phase_evidence = phases.get('phases8-12', {}).get('results', {}).get(phase_key, {}).get('evidence', [])
            evidence.extend(phase_evidence[:3])

        section = f"""## 1. {self._t('executive_summary')}

{self._get_target_overview(ids, phases)}

### {self._t('bottom_line')}

{self._get_bottom_line(composite, ids)}

### {self._t('validation_scorecard')}

| {self._t('dimension')} | {self._t('score')} | {self._t('max')} | {self._t('percentage')} |
|-----------|-------|-----|------------|
| {self._t('disease_scoring')} | {scores.get('disease', 0)} | 30 | {scores.get('disease', 0)/30*100:.0f}% |
| {self._t('druggability_assessment')} | {scores.get('druggability', 0)} | 25 | {scores.get('druggability', 0)/25*100:.0f}% |
| {self._t('safety_analysis')} | {scores.get('safety', 0)} | 20 | {scores.get('safety', 0)/20*100:.0f}% |
| {self._t('clinical_precedent')} | {scores.get('clinical', 0)} | 15 | {scores.get('clinical', 0)/15*100:.0f}% |
| {self._t('validation_evidence')} | {scores.get('validation', 0)} | 10 | {scores.get('validation', 0)/10*100:.0f}% |
| **{self._t('total')}** | **{total}** | **100** | **{total}%** |

**{self._t('priority_tier')}**: {self._t(f'tier{tier}')}
**{self._t('recommendation')}**: **{rec_translated}**

### {self._t('visualization')}

![Validation Score](figures/validation_score.png)

### {self._t('key_findings')}

"""
        for i, e in enumerate(evidence[:5], 1):
            section += f"{i}. {e}\n"

        # Add safety flags
        safety_flags = phases.get('phases8-12', {}).get('results', {}).get('phase10', {}).get('safety_flags', [])
        section += f"\n### {self._t('critical_risks')}\n\n"
        if safety_flags:
            for flag in safety_flags[:3]:
                section += f"- {flag}\n"
        else:
            section += f"- {self._t('not_available')}\n"

        # Key strengths
        section += f"\n### {self._t('key_strengths')}\n\n"
        strengths = self._identify_strengths(composite, phases)
        for i, s in enumerate(strengths, 1):
            section += f"{i}. {s}\n"

        section += "\n---\n\n"
        return section

    def _get_target_overview(self, ids: Dict, phases: Dict) -> str:
        """Generate target overview paragraph."""
        name = ids.get('name', ids.get('symbol', 'Unknown'))
        symbol = ids.get('symbol', 'Unknown')

        # Get function info
        functions = phases.get('phases2-7', {}).get('results', {}).get('phase2', {}).get('data', {}).get('function', [])
        func_desc = functions[0][:200] if functions else self._t('not_available')

        # Get clinical info
        drugs = phases.get('phases8-12', {}).get('results', {}).get('phase11', {}).get('drugs', [])
        clinical_status = f"({len(drugs)} {self._t('clinical_trials')})" if drugs else f"({self._t('not_available')})"

        return f"""**{name} ({symbol})** - {func_desc}... {clinical_status}"""

    def _get_bottom_line(self, composite: Dict, ids: Dict) -> str:
        """Generate bottom line recommendation."""
        tier = composite.get('tier', 4)
        total = composite.get('total_score', 0)
        symbol = ids.get('symbol', 'this target')

        if tier == 1:
            return f"{symbol} {self._t('tier1')} - {self._t('score')}: {total}/100. {self._t('go')}."
        elif tier == 2:
            return f"{symbol} {self._t('tier2')} - {self._t('score')}: {total}/100. {self._t('conditional_go')}."
        elif tier == 3:
            return f"{symbol} {self._t('tier3')} - {self._t('score')}: {total}/100. {self._t('caution')}."
        else:
            return f"{symbol} {self._t('tier4')} - {self._t('score')}: {total}/100. {self._t('no_go')}."

    def _identify_strengths(self, composite: Dict, phases: Dict) -> List[str]:
        """Identify key strengths based on scores."""
        strengths = []
        scores = composite.get('score_breakdown', {})

        if scores.get('disease', 0) >= 20:
            strengths.append(f"{self._t('disease_scoring')} {self._t('high')}")
        if scores.get('druggability', 0) >= 18:
            strengths.append(f"{self._t('druggability_assessment')} {self._t('high')}")
        if scores.get('clinical', 0) >= 10:
            strengths.append(f"{self._t('clinical_precedent')} {self._t('high')}")
        if scores.get('safety', 0) >= 15:
            strengths.append(f"{self._t('safety_analysis')} {self._t('high')}")

        if not strengths:
            strengths.append(f"{self._t('validation_scorecard')} {self._t('medium')}")

        return strengths

    def _build_target_intelligence(self, ids: Dict, phases: Dict) -> str:
        """Build target intelligence sections (2-8)."""
        phase1 = phases.get('phase1', {})
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
        """Build Section 2: Target Identifiers."""
        symbol = ids.get('symbol', self._t('not_available'))
        name = ids.get('name', symbol)

        section = f"""## 2. {self._t('target_identifiers')}

### {self._t('summary')}

**{name} ({symbol})** - {self._t('confidence_level')}: {ids.get('confidence', 'unknown').upper()}

| {self._t('identifier_type')} | {self._t('value')} | {self._t('database')} |
|-----------------|-------|----------|
| {self._t('gene_symbol')} | {symbol} | {ids.get('symbol_source', 'N/A')} |
| {self._t('uniprot_accession')} | {ids.get('uniprot', self._t('not_available'))} | UniProtKB |
| {self._t('ensembl_id')} | {ids.get('ensembl', self._t('not_available'))} | Ensembl |
| {self._t('entrez_id')} | {ids.get('entrez', self._t('not_available'))} | NCBI Gene |
| {self._t('chembl_id')} | {ids.get('chembl_target', self._t('not_available'))} | ChEMBL |

**{self._t('aliases')}**: {', '.join(ids.get('aliases', [])[:5]) if ids.get('aliases') else self._t('not_available')}

---

"""
        return section

    def _build_section3_basic_info(self, ids: Dict, phases2_7: Dict) -> str:
        """Build Section 3: Basic Information."""
        phase2 = phases2_7.get('results', {}).get('phase2', {}).get('data', {})
        entry = phase2.get('entry', {})
        functions = phase2.get('function', [])
        location = phase2.get('location', {})

        # Extract protein info
        protein_length = self._t('not_available')
        if entry and isinstance(entry, dict):
            seq = entry.get('sequence', {})
            protein_length = f"{seq.get('length', self._t('not_available'))} {self._t('amino_acids')}"

        symbol = ids.get('symbol', self._t('not_available'))
        name = ids.get('name', symbol)

        section = f"""## 3. {self._t('basic_info')}

### {self._t('summary')}

**{name} ({symbol})** - {len(functions)} {self._t('protein_function')} {self._t('details')}

### 3.1 {self._t('protein_function')}

"""
        if functions:
            for f in functions[:3]:
                section += f"- {f}\n"
        else:
            section += f"- {self._t('not_available')}\n"

        section += f"""
### 3.2 {self._t('subcellular_location')}

- **{self._t('subcellular_location')}**: {self._extract_location(location)}

### 3.3 {self._t('protein_length')}

- **{self._t('protein_length')}**: {protein_length}

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
        """Build Section 4: Structural Biology."""
        phase3 = phases2_7.get('results', {}).get('phase3', {}).get('data', {})
        pdb_structures = phase3.get('pdb_structures', [])
        domains = phase3.get('domains', [])
        uniprot = ids.get('uniprot', '')

        pdb_count = len(pdb_structures)
        domain_count = len(domains)

        section = f"""## 4. {self._t('structural_biology')}

### {self._t('summary')}

**{pdb_count} {self._t('pdb_structures')}**, **{domain_count}** {self._t('domain_architecture')}

### 4.1 {self._t('pdb_structures')}

| PDB ID | {self._t('resolution')} | {self._t('method')} |
|--------|------------|--------|
"""
        for pdb in pdb_structures[:10]:
            pdb_id = pdb.get('pdb_id', self._t('not_available'))
            resolution = pdb.get('resolution', self._t('not_available'))
            method = pdb.get('method', self._t('not_available'))
            section += f"| {pdb_id} | {resolution} | {method} |\n"

        if not pdb_structures:
            section += f"| {self._t('not_available')} | - | - |\n"

        section += f"""
**{self._t('total_entries')}**: {pdb_count}

### 4.2 {self._t('alphafold_prediction')}

![AlphaFold Model](https://alphafold.ebi.ac.uk/entry/{uniprot})

### 4.3 {self._t('domain_architecture')}

| Domain | Position | InterPro ID |
|--------|----------|-------------|
"""
        for domain in domains[:5]:
            name = domain.get('name', self._t('not_available'))
            pos = f"{domain.get('start', '-')}-{domain.get('end', '-')}"
            ipr = domain.get('accession', self._t('not_available'))
            section += f"| {name} | {pos} | {ipr} |\n"

        if not domains:
            section += f"| {self._t('not_available')} | - | - |\n"

        section += "\n---\n\n"
        return section

    def _build_section5_pathways(self, ids: Dict, phases2_7: Dict) -> str:
        """Build Section 5: Function & Pathways."""
        phase4 = phases2_7.get('results', {}).get('phase4', {}).get('data', {})
        reactome = phase4.get('reactome', [])
        go = phase4.get('go', [])

        pathway_count = len(reactome)
        go_count = len(go)

        section = f"""## 5. {self._t('function_pathways')}

### {self._t('summary')}

**{pathway_count}** Reactome {self._t('function_pathways')}, **{go_count}** GO {self._t('details')}

### 5.1 {self._t('function_pathways')}

| Pathway | Database | Pathway ID |
|---------|----------|------------|
"""
        for p in reactome[:10]:
            name = str(p.get('name', p))[:50]
            st_id = p.get('stId', self._t('not_available'))
            section += f"| {name} | Reactome | {st_id} |\n"

        if not reactome:
            section += f"| {self._t('not_available')} | - | - |\n"

        section += "\n---\n\n"
        return section

    def _build_section6_ppi(self, ids: Dict, phases2_7: Dict) -> str:
        """Build Section 6: Protein-Protein Interactions."""
        phase5 = phases2_7.get('results', {}).get('phase5', {}).get('data', {})
        string_ppi = phase5.get('string', [])
        intact_ppi = phase5.get('intact', [])
        total_ppi = phase5.get('total_count', 0)

        section = f"""## 6. {self._t('ppi')}

### {self._t('summary')}

**{total_ppi}** {self._t('ppi')} (STRING: {len(string_ppi)}, IntAct: {len(intact_ppi)})

### 6.1 {self._t('details')}

| Partner | Score | Database |
|---------|-------|----------|
"""
        for ppi in (string_ppi + intact_ppi)[:10]:
            partner = ppi.get('stringId', ppi.get('interactorId', self._t('not_available')))
            score = ppi.get('combinedScore', ppi.get('intactScore', '-'))
            db = 'STRING' if 'stringId' in ppi else 'IntAct'
            section += f"| {partner} | {score} | {db} |\n"

        if not string_ppi and not intact_ppi:
            section += f"| {self._t('not_available')} | - | - |\n"

        section += "\n---\n\n"
        return section

    def _build_section7_expression(self, ids: Dict, phases2_7: Dict) -> str:
        """Build Section 7: Expression Profile."""
        phase6 = phases2_7.get('results', {}).get('phase6', {}).get('data', {})
        gtex = phase6.get('gtex', [])

        section = f"""## 7. {self._t('expression_profile')}

### {self._t('summary')}

**{len(gtex)}** {self._t('expression_profile')} {self._t('details')}

### 7.1 {self._t('visualization')}

![Tissue Expression](figures/tissue_expression.png)

### 7.2 {self._t('details')}

| Tissue | TPM | Level |
|--------|-----|-------|
"""
        sorted_gtex = sorted(gtex, key=lambda x: x.get('median', 0), reverse=True)[:10]
        for expr in sorted_gtex:
            tissue = expr.get('tissue', {}).get('name', self._t('not_available'))
            tpm = expr.get('median', 0)
            level = self._t('high') if tpm > 50 else self._t('medium') if tpm > 10 else self._t('low')
            section += f"| {tissue} | {tpm:.1f} | {level} |\n"

        if not gtex:
            section += f"| {self._t('not_available')} | - | - |\n"

        section += "\n---\n\n"
        return section

    def _build_section8_genetics(self, ids: Dict, phases: Dict) -> str:
        """Build Section 8: Genetic Variation & Disease."""
        phases2_7 = phases.get('phases2-7', {})
        phase7 = phases2_7.get('results', {}).get('phase7', {}).get('data', {})
        gnomad = phase7.get('gnomad', {})

        phase1 = phases.get('phase1', {}).get('data', {})
        diseases = phase1.get('diseases', {}).get('associatedDiseases', {}).get('rows', [])

        pli = gnomad.get('pLI')
        loeuf = gnomad.get('LOEUF')

        section = f"""## 8. {self._t('genetics_disease')}

### {self._t('summary')}

**{len(diseases)}** {self._t('disease')} {self._t('association_score')}

### 8.1 {self._t('genetic_evidence')}

| Metric | Value | {self._t('details')} |
|--------|-------|----------------|
| pLI | {pli if pli is not None else self._t('not_available')} | {self._t('high') if pli and pli > 0.9 else self._t('medium') if pli and pli > 0.5 else self._t('low')} |
| LOEUF | {loeuf if loeuf is not None else self._t('not_available')} | - |

### 8.2 {self._t('disease')} {self._t('association_score')}

![Disease Associations](figures/disease_associations.png)

| {self._t('disease')} | {self._t('association_score')} | {self._t('evidence_tier')} |
|---------|-------------------|---------------|
"""
        for row in diseases[:10]:
            disease = row.get('disease', {})
            scores = row.get('datasourceScores', [])
            max_score = max([s.get('score', 0) for s in scores]) if scores else 0
            tier = 'T1' if max_score > 0.8 else 'T2' if max_score > 0.5 else 'T3'
            section += f"| {disease.get('name', self._t('not_available'))} | {max_score:.2f} | {tier} |\n"

        if not diseases:
            section += f"| {self._t('not_available')} | - | - |\n"

        section += "\n---\n\n"
        return section

    def _build_validation_assessment(self, phases: Dict, composite: Dict) -> str:
        """Build validation assessment sections (9-14)."""
        phases8_12 = phases.get('phases8-12', {})

        section = ""

        # Section 9: Disease Association Scoring
        section += self._build_section9_disease(phases8_12)

        # Section 10: Druggability Assessment
        section += self._build_section10_druggability(phases8_12)

        # Section 11: Safety Deep Analysis
        section += self._build_section11_safety(phases8_12)

        # Section 12: Clinical Precedent
        section += self._build_section12_clinical(phases8_12)

        # Section 13: Validation Evidence
        section += self._build_section13_validation(phases8_12)

        # Section 14: Validation Scorecard
        section += self._build_section14_scorecard(composite)

        return section

    def _build_section9_disease(self, phases8_12: Dict) -> str:
        """Build Section 9: Disease Association Scoring."""
        phase8 = phases8_12.get('results', {}).get('phase8', {})
        scores = phase8.get('scores', {})

        section = f"""## 9. {self._t('disease_scoring')} (0-30 pts)

### {self._t('summary')}

**{scores.get('total', 0)}/30** - {self._t('genetic_evidence')}: {scores.get('genetic', 0)}, {self._t('pathway_evidence')}: {scores.get('pathway', 0)}

| {self._t('dimension')} | {self._t('score')} |
|---------------|--------|
| {self._t('genetic_evidence')} | {scores.get('genetic', 0)}/10 |
| {self._t('literature_evidence')} | {scores.get('literature', 0)}/10 |
| {self._t('pathway_evidence')} | {scores.get('pathway', 0)}/10 |
| **{self._t('total')}** | **{scores.get('total', 0)}/30** |

---

"""
        return section

    def _build_section10_druggability(self, phases8_12: Dict) -> str:
        """Build Section 10: Druggability Assessment."""
        phase9 = phases8_12.get('results', {}).get('phase9', {})
        scores = phase9.get('scores', {})

        section = f"""## 10. {self._t('druggability_assessment')} (0-25 pts)

### {self._t('summary')}

**{scores.get('total', 0)}/25** - {self._t('structural_druggability')}: {scores.get('structural', 0)}, {self._t('details')}: {scores.get('chemical', 0)}

| {self._t('dimension')} | {self._t('score')} |
|---------------|--------|
| {self._t('structural_druggability')} | {scores.get('structural', 0)}/10 |
| Chemical Matter | {scores.get('chemical', 0)}/10 |
| Target Class Bonus | {scores.get('target_class', 0)}/5 |
| **{self._t('total')}** | **{scores.get('total', 0)}/25** |

---

"""
        return section

    def _build_section11_safety(self, phases8_12: Dict) -> str:
        """Build Section 11: Safety Deep Analysis."""
        phase10 = phases8_12.get('results', {}).get('phase10', {})
        scores = phase10.get('scores', {})
        safety_flags = phase10.get('safety_flags', [])

        section = f"""## 11. {self._t('safety_analysis')} (0-20 pts)

### {self._t('summary')}

**{scores.get('total', 0)}/20** - {len(safety_flags)} {self._t('safety_liabilities')}

### {self._t('visualization')}

![Safety Dashboard](figures/safety_dashboard.png)

| {self._t('dimension')} | {self._t('score')} |
|---------------|--------|
| {self._t('tissue_expression_selectivity')} | {scores.get('expression', 0)}/5 |
| {self._t('genetic_validation')} | {scores.get('genetic', 0)}/10 |
| {self._t('adverse_events')} | {scores.get('adverse', 0)}/5 |
| **{self._t('total')}** | **{scores.get('total', 0)}/20** |

### {self._t('safety_liabilities')}

| {self._t('safety_liabilities')} |
|----------------|
"""
        if safety_flags:
            for flag in safety_flags[:5]:
                section += f"| {flag} |\n"
        else:
            section += f"| {self._t('not_available')} |\n"

        section += "\n---\n\n"
        return section

    def _build_section12_clinical(self, phases8_12: Dict) -> str:
        """Build Section 12: Clinical Precedent."""
        phase11 = phases8_12.get('results', {}).get('phase11', {})
        score = phase11.get('score', 0)
        drugs = phase11.get('drugs', [])

        section = f"""## 12. {self._t('clinical_precedent')} (0-15 pts)

### {self._t('summary')}

**{score}/15** - {len(drugs)} {self._t('clinical_trials')}

### {self._t('visualization')}

![Clinical Timeline](figures/clinical_timeline.png)

### {self._t('approved_drugs')}

| Drug | {self._t('status')} |
|-----------|--------|
"""
        for drug in drugs[:5]:
            section += f"| {drug} | {self._t('clinical_trials')} |\n"

        if not drugs:
            section += f"| {self._t('not_available')} | - |\n"

        section += "\n---\n\n"
        return section

    def _build_section13_validation(self, phases8_12: Dict) -> str:
        """Build Section 13: Validation Evidence."""
        phase12 = phases8_12.get('results', {}).get('phase12', {})
        scores = phase12.get('scores', {})

        section = f"""## 13. {self._t('validation_evidence')} (0-10 pts)

### {self._t('summary')}

**{scores.get('total', 0)}/10**

| {self._t('dimension')} | {self._t('score')} |
|---------------|--------|
| Publications | {scores.get('publications', 0)}/4 |
| PPI Network | {scores.get('ppi', 0)}/3 |
| Structures | {scores.get('structure', 0)}/3 |
| **{self._t('total')}** | **{scores.get('total', 0)}/10** |

---

"""
        return section

    def _build_section14_scorecard(self, composite: Dict) -> str:
        """Build Section 14: Validation Scorecard."""
        scores = composite.get('score_breakdown', {})
        total = composite.get('total_score', 0)
        tier = composite.get('tier', 4)
        rec = composite.get('recommendation', 'NO-GO')

        rec_translated = {
            'GO': self._t('go'),
            'CONDITIONAL GO': self._t('conditional_go'),
            'CAUTION': self._t('caution'),
            'NO-GO': self._t('no_go')
        }.get(rec, rec)

        section = f"""## 14. {self._t('validation_scorecard')}

| {self._t('dimension')} | {self._t('score')} | {self._t('max')} | {self._t('percentage')} |
|-----------|-------|-----|------------|
| {self._t('disease_scoring')} | {scores.get('disease', 0)} | 30 | {scores.get('disease', 0)/30*100:.0f}% |
| {self._t('druggability_assessment')} | {scores.get('druggability', 0)} | 25 | {scores.get('druggability', 0)/25*100:.0f}% |
| {self._t('safety_analysis')} | {scores.get('safety', 0)} | 20 | {scores.get('safety', 0)/20*100:.0f}% |
| {self._t('clinical_precedent')} | {scores.get('clinical', 0)} | 15 | {scores.get('clinical', 0)/15*100:.0f}% |
| {self._t('validation_evidence')} | {scores.get('validation', 0)} | 10 | {scores.get('validation', 0)/10*100:.0f}% |
| **{self._t('total')}** | **{total}** | **100** | **{total}%** |

**{self._t('priority_tier')}**: {tier}
**{self._t('recommendation')}**: **{rec_translated}**

---

"""
        return section

    def _build_synthesis(self, results: Dict) -> str:
        """Build synthesis sections (15-18)."""
        composite = results.get('composite', {})
        phases = results.get('phases', {})
        phases8_12 = phases.get('phases8-12', {})

        section = ""

        # Section 15: Validation Roadmap
        section += self._build_section15_roadmap(results)

        # Section 16: Tool Compounds
        section += self._build_section16_tool_compounds(phases8_12)

        # Section 17: Biomarker Strategy
        section += self._build_section17_biomarkers()

        # Section 18: Key Risks & Mitigations
        section += self._build_section18_risks(composite, phases8_12)

        return section

    def _build_section15_roadmap(self, results: Dict) -> str:
        """Build Section 15: Validation Roadmap."""
        section = f"""## 15. {self._t('validation_roadmap')}

| Priority | Experiment | Rationale | Timeline |
|----------|------------|-----------|----------|
| HIGH | CRISPR knockout | Confirm target essentiality | 2-4 weeks |
| HIGH | Phenotypic screening | Validate disease relevance | 4-8 weeks |
| MEDIUM | Tool compound screening | Pharmacological validation | 4-6 weeks |
| MEDIUM | Extended safety pharmacology | Characterize safety profile | 8-12 weeks |
| LOW | Biomarker development | Support clinical translation | 12-16 weeks |

---

"""
        return section

    def _build_section16_tool_compounds(self, phases8_12: Dict) -> str:
        """Build Section 16: Tool Compounds."""
        drugs = phases8_12.get('results', {}).get('phase11', {}).get('drugs', [])

        section = f"""## 16. {self._t('tool_compounds')}

| Compound | Source | Use |
|----------|--------|-----|
"""
        for drug in drugs[:5]:
            section += f"| {drug} | ChEMBL | Tool compound |\n"

        if not drugs:
            section += f"| {self._t('not_available')} | - | - |\n"

        section += "\n---\n\n"
        return section

    def _build_section17_biomarkers(self) -> str:
        """Build Section 17: Biomarker Strategy."""
        return f"""## 17. {self._t('biomarker_strategy')}

| Biomarker | Type | Assay |
|-----------|------|-------|
| Target expression | Genomic | IHC/qPCR |
| Pathway activation | Protein | Western blot |

---

"""

    def _build_section18_risks(self, composite: Dict, phases8_12: Dict) -> str:
        """Build Section 18: Key Risks & Mitigations."""
        safety_flags = phases8_12.get('results', {}).get('phase10', {}).get('safety_flags', [])

        section = f"""## 18. {self._t('risks_mitigations')}

| {self._t('risk_category')} | Risk | {self._t('probability')} | {self._t('impact')} | {self._t('mitigation')} |
|---------------|------|-------------|--------|---------------------|
| Efficacy | Insufficient target engagement | Medium | High | Optimize compound potency |
| Competition | Crowded therapeutic space | Medium | Medium | Differentiation strategy |
"""
        if safety_flags:
            section += f"| Safety | {safety_flags[0]} | Medium | High | Additional preclinical studies |\n"

        section += f"""
### {self._t('key_strengths')}

"""
        strengths = []
        scores = composite.get('score_breakdown', {})
        if scores.get('disease', 0) >= 20:
            strengths.append(f"{self._t('disease_scoring')} {self._t('high')}")
        if scores.get('druggability', 0) >= 18:
            strengths.append(f"{self._t('druggability_assessment')} {self._t('high')}")
        if scores.get('clinical', 0) >= 10:
            strengths.append(f"{self._t('clinical_precedent')} {self._t('high')}")
        if not strengths:
            strengths.append(f"{self._t('validation_scorecard')} completed")

        for i, s in enumerate(strengths, 1):
            section += f"{i}. {s}\n"

        section += f"""
### {self._t('key_challenges')}

1. Additional validation studies required
2. Safety profile needs further characterization
3. Competitive landscape assessment needed

---

*Report generated by ToolUniverse Target Validation Pipeline*
*Date: {datetime.now().strftime('%Y-%m-%d')}*
"""
        return section