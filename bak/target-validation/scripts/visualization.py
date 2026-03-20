#!/usr/bin/env python3
"""
Visualization Module for Target Validation Reports

Generates matplotlib figures with proper chart types:
- Radar chart for Validation Scorecard
- Bar chart for Disease Associations and Tissue Expression
- Pie chart for Clinical Precedent
- Radar chart for Safety Dashboard

Supports both Chinese (default) and English languages.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Configure matplotlib for Chinese characters
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ValidationVisualizer:
    """Generate publication-quality visualizations for target validation reports."""

    # Color scheme
    COLORS = {
        'primary': '#2E86AB',
        'secondary': '#A23B72',
        'success': '#28A745',
        'warning': '#FFC107',
        'danger': '#DC3545',
        'neutral': '#6C757D',
        'tiers': {
            1: '#28A745',  # Green - GO
            2: '#17A2B8',  # Cyan - CONDITIONAL GO
            3: '#FFC107',  # Yellow - CAUTION
            4: '#DC3545',  # Red - NO-GO
        }
    }

    # Language translations
    TRANSLATIONS = {
        'zh': {
            'validation_score': '验证评分雷达图',
            'disease_association': '疾病关联性评分',
            'tissue_expression': '组织表达谱',
            'clinical_pipeline': '临床开发管线',
            'safety_dashboard': '安全性评估仪表盘',
            'score': '分数',
            'tier': '等级',
            'recommendation': '建议',
            'disease_assoc': '疾病关联性',
            'druggability': '成药性',
            'safety': '安全性',
            'clinical': '临床先例',
            'validation': '验证证据',
            'strong': '强',
            'moderate': '中',
            'weak': '弱',
            'approved': '已批准',
            'phase3': 'III期',
            'phase2': 'II期',
            'phase1': 'I期',
            'preclinical': '临床前',
            'total_compounds': '化合物总数',
            'breakdown': '分布',
            'critical_tissue': '关键组织表达',
            'genetic_validation': '遗传验证',
            'safety_flags': '安全性警示',
            'overall_safety': '综合安全性评估',
            'mouse_ko': '小鼠KO',
            'viable': '可存活',
            'lethal': '致死',
            'unknown': '未知',
            'no_data': '无数据',
            'no_safety_flags': '无安全性警示',
            'go': '通过',
            'conditional_go': '条件通过',
            'caution': '谨慎',
            'no_go': '不通过',
        },
        'en': {
            'validation_score': 'Validation Score Radar',
            'disease_association': 'Disease Association Score',
            'tissue_expression': 'Tissue Expression Profile',
            'clinical_pipeline': 'Clinical Development Pipeline',
            'safety_dashboard': 'Safety Profile Dashboard',
            'score': 'Score',
            'tier': 'Tier',
            'recommendation': 'Recommendation',
            'disease_assoc': 'Disease Association',
            'druggability': 'Druggability',
            'safety': 'Safety Profile',
            'clinical': 'Clinical Precedent',
            'validation': 'Validation Evidence',
            'strong': 'Strong',
            'moderate': 'Moderate',
            'weak': 'Weak',
            'approved': 'Approved',
            'phase3': 'Phase III',
            'phase2': 'Phase II',
            'phase1': 'Phase I',
            'preclinical': 'Preclinical',
            'total_compounds': 'Total Compounds',
            'breakdown': 'Breakdown',
            'critical_tissue': 'Critical Tissue Expression',
            'genetic_validation': 'Genetic Validation',
            'safety_flags': 'Safety Flags',
            'overall_safety': 'Overall Safety Assessment',
            'mouse_ko': 'MOUSE KO',
            'viable': 'Viable',
            'lethal': 'Lethal',
            'unknown': 'Unknown',
            'no_data': 'No data',
            'no_safety_flags': 'No Safety Flags',
            'go': 'GO',
            'conditional_go': 'CONDITIONAL GO',
            'caution': 'CAUTION',
            'no_go': 'NO-GO',
        }
    }

    def __init__(self, output_dir: str = ".", language: str = 'zh'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.language = language
        self.t = self.TRANSLATIONS.get(language, self.TRANSLATIONS['zh'])

    def _t(self, key: str) -> str:
        """Get translation for key."""
        return self.t.get(key, key)

    def plot_validation_score(self, composite: Dict, save: bool = True) -> str:
        """
        Generate validation score RADAR chart with tier indicator.
        """
        # Data preparation
        categories = [
            self._t('disease_assoc'),
            self._t('druggability'),
            self._t('safety'),
            self._t('clinical'),
            self._t('validation')
        ]
        max_scores = [30, 25, 20, 15, 10]
        scores = [
            composite.get('score_breakdown', {}).get('disease', 0),
            composite.get('score_breakdown', {}).get('druggability', 0),
            composite.get('score_breakdown', {}).get('safety', 0),
            composite.get('score_breakdown', {}).get('clinical', 0),
            composite.get('score_breakdown', {}).get('validation', 0),
        ]
        percentages = [s/m*100 if m > 0 else 0 for s, m in zip(scores, max_scores)]

        # Create figure with two subplots
        fig = plt.figure(figsize=(14, 7))
        gs = fig.add_gridspec(1, 2, width_ratios=[1.2, 1], wspace=0.3)

        # Left plot: Radar chart
        ax1 = fig.add_subplot(gs[0], projection='polar')

        # Number of variables
        num_vars = len(categories)
        angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
        angles += angles[:1]  # Complete the loop

        # Add values to complete the loop
        values = percentages + percentages[:1]
        max_values = [100] * (num_vars + 1)

        # Plot the max values (background)
        ax1.plot(angles, max_values, 'o-', linewidth=1, color='#E9ECEF', alpha=0.5)
        ax1.fill(angles, max_values, color='#E9ECEF', alpha=0.1)

        # Plot the actual values
        ax1.plot(angles, values, 'o-', linewidth=2.5, color=self.COLORS['primary'], markersize=8)
        ax1.fill(angles, values, color=self.COLORS['primary'], alpha=0.25)

        # Set the labels
        ax1.set_xticks(angles[:-1])
        ax1.set_xticklabels(categories, fontsize=11, fontweight='bold')

        # Set y-axis limits
        ax1.set_ylim(0, 100)
        ax1.set_yticks([25, 50, 75, 100])
        ax1.set_yticklabels(['25%', '50%', '75%', '100%'], fontsize=8, color='gray')

        # Add score labels at each point
        for angle, value, score, max_score in zip(angles[:-1], percentages, scores, max_scores):
            ax1.annotate(f'{score}/{max_score}',
                        xy=(angle, value),
                        xytext=(angle, value + 12),
                        ha='center', va='bottom',
                        fontsize=10, fontweight='bold',
                        color=self.COLORS['primary'])

        ax1.set_title(self._t('validation_score'), fontsize=14, fontweight='bold', pad=20)

        # Right plot: Tier gauge
        ax2 = fig.add_subplot(gs[1])
        total_score = composite.get('total_score', 0)
        tier = composite.get('tier', 4)

        # Translate recommendation
        rec_key = {
            'GO': 'go',
            'CONDITIONAL GO': 'conditional_go',
            'CAUTION': 'caution',
            'NO-GO': 'no_go'
        }.get(composite.get('recommendation', 'NO-GO'), 'no_go')

        # Create a circular gauge
        ax2.set_xlim(-1.5, 1.5)
        ax2.set_ylim(-1.5, 1.5)
        ax2.set_aspect('equal')
        ax2.axis('off')

        # Draw gauge background
        theta = np.linspace(0, 2*np.pi, 100)
        ax2.plot(np.cos(theta), np.sin(theta), color='#E9ECEF', linewidth=30, solid_capstyle='round')

        # Draw gauge fill based on score
        fill_angle = (total_score / 100) * 2 * np.pi
        theta_fill = np.linspace(0, fill_angle, 100)
        ax2.plot(np.sin(theta_fill), np.cos(theta_fill),
                color=self.COLORS['tiers'].get(tier, self.COLORS['neutral']),
                linewidth=30, solid_capstyle='round')

        # Center text
        ax2.text(0, 0.15, f'{total_score}', fontsize=48, ha='center', va='center',
                fontweight='bold', color=self.COLORS['tiers'].get(tier, self.COLORS['neutral']))
        ax2.text(0, -0.3, f"{self._t('tier')} {tier}", fontsize=20, ha='center', va='center', fontweight='bold')
        ax2.text(0, -0.6, self._t(rec_key), fontsize=16, ha='center', va='center',
                color=self.COLORS['tiers'].get(tier, self.COLORS['neutral']), fontweight='bold')

        # Add legend
        legend_elements = [
            mpatches.Patch(color=self.COLORS['success'], label=f">=70% ({self._t('strong')})"),
            mpatches.Patch(color=self.COLORS['warning'], label=f"40-70% ({self._t('moderate')})"),
            mpatches.Patch(color=self.COLORS['danger'], label=f"<40% ({self._t('weak')})"),
        ]
        ax2.legend(handles=legend_elements, loc='lower center', frameon=False, ncol=3, fontsize=9)

        plt.tight_layout()

        filepath = str(self.output_dir / 'validation_score.png')
        if save:
            plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return filepath

    def plot_disease_associations(self, diseases: List[Dict], save: bool = True) -> str:
        """
        Generate disease association BAR chart.
        """
        if not diseases:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, self._t('no_data'), ha='center', va='center',
                   fontsize=14, color=self.COLORS['neutral'])
            ax.axis('off')
            filepath = str(self.output_dir / 'disease_associations.png')
            if save:
                plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            return filepath

        # Sort by score and take top 10
        sorted_diseases = sorted(diseases, key=lambda x: x.get('score', 0), reverse=True)[:10]

        fig, ax = plt.subplots(figsize=(12, 8))

        names = [d.get('name', 'Unknown')[:35] for d in sorted_diseases]
        scores = [d.get('score', 0) for d in sorted_diseases]

        # Color by evidence tier
        colors = []
        for s in scores:
            if s > 0.8:
                colors.append(self.COLORS['success'])
            elif s > 0.5:
                colors.append('#17A2B8')
            elif s > 0.2:
                colors.append(self.COLORS['warning'])
            else:
                colors.append(self.COLORS['neutral'])

        y_pos = np.arange(len(names))
        bars = ax.barh(y_pos, scores, color=colors, edgecolor='white', linewidth=1.5)

        # Add tier labels
        for i, (bar, score) in enumerate(zip(bars, scores)):
            ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                   f'{score:.2f}', va='center', fontsize=10)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, fontsize=10)
        ax.set_xlabel(self._t('score'), fontsize=12, fontweight='bold')
        ax.set_xlim(0, 1.15)
        ax.axvline(x=0.8, color=self.COLORS['success'], linestyle='--', alpha=0.5)
        ax.axvline(x=0.5, color='#17A2B8', linestyle='--', alpha=0.5)
        ax.axvline(x=0.2, color=self.COLORS['warning'], linestyle='--', alpha=0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_title(self._t('disease_association'), fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()

        filepath = str(self.output_dir / 'disease_associations.png')
        if save:
            plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return filepath

    def plot_tissue_expression(self, expression_data: Dict, save: bool = True) -> str:
        """
        Generate tissue expression BAR chart.
        """
        tissues = expression_data.get('tissues', [])
        if not tissues:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, self._t('no_data'), ha='center', va='center',
                   fontsize=14, color=self.COLORS['neutral'])
            ax.axis('off')
            filepath = str(self.output_dir / 'tissue_expression.png')
            if save:
                plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            return filepath

        # Sort by TPM
        sorted_tissues = sorted(tissues, key=lambda x: x.get('tpm', 0), reverse=True)[:15]

        fig, ax = plt.subplots(figsize=(12, 8))

        names = [t.get('tissue', 'Unknown')[:25] for t in sorted_tissues]
        tpms = [t.get('tpm', 0) for t in sorted_tissues]
        critical = expression_data.get('critical_tissues', [])
        critical_lower = [c.lower() for c in critical]

        # Color bars - highlight critical tissues
        colors = []
        for t in sorted_tissues:
            tissue_name = t.get('tissue', '').lower()
            if any(c in tissue_name for c in critical_lower):
                colors.append(self.COLORS['danger'])
            else:
                colors.append(self.COLORS['primary'])

        y_pos = np.arange(len(names))
        bars = ax.barh(y_pos, tpms, color=colors, edgecolor='white', linewidth=1.5)

        # Add value labels
        for bar, tpm in zip(bars, tpms):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                   f'{tpm:.1f}', va='center', fontsize=10)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, fontsize=10)
        ax.set_xlabel('TPM', fontsize=12, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_title(self._t('tissue_expression'), fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()

        filepath = str(self.output_dir / 'tissue_expression.png')
        if save:
            plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return filepath

    def plot_clinical_timeline(self, drugs: List[Dict], save: bool = True) -> str:
        """
        Generate clinical precedent PIE chart.
        """
        if not drugs:
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.text(0.5, 0.5, self._t('no_data'), ha='center', va='center',
                   fontsize=14, color=self.COLORS['neutral'])
            ax.axis('off')
            filepath = str(self.output_dir / 'clinical_timeline.png')
            if save:
                plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            return filepath

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

        # Categorize drugs by phase
        approved = [d for d in drugs if d.get('phase', 0) == 4 or d.get('is_approved', False)]
        phase3 = [d for d in drugs if d.get('phase', 0) == 3 and not d.get('is_approved', False)]
        phase2 = [d for d in drugs if d.get('phase', 0) == 2 and not d.get('is_approved', False)]
        phase1 = [d for d in drugs if d.get('phase', 0) == 1 and not d.get('is_approved', False)]
        preclinical = [d for d in drugs if d.get('phase', 0) == 0 and not d.get('is_approved', False)]

        # Left plot: Pie chart
        labels = []
        sizes = []
        colors = []

        if approved:
            labels.append(f"{self._t('approved')} ({len(approved)})")
            sizes.append(len(approved))
            colors.append(self.COLORS['success'])
        if phase3:
            labels.append(f"{self._t('phase3')} ({len(phase3)})")
            sizes.append(len(phase3))
            colors.append('#20C997')
        if phase2:
            labels.append(f"{self._t('phase2')} ({len(phase2)})")
            sizes.append(len(phase2))
            colors.append('#17A2B8')
        if phase1:
            labels.append(f"{self._t('phase1')} ({len(phase1)})")
            sizes.append(len(phase1))
            colors.append(self.COLORS['warning'])
        if preclinical:
            labels.append(f"{self._t('preclinical')} ({len(preclinical)})")
            sizes.append(len(preclinical))
            colors.append(self.COLORS['neutral'])

        if sizes:
            wedges, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                                                startangle=90, colors=colors,
                                                explode=[0.02]*len(sizes),
                                                wedgeprops={'edgecolor': 'white', 'linewidth': 2})
            for text in texts:
                text.set_fontsize(11)
                text.set_fontweight('bold')
            for autotext in autotexts:
                autotext.set_fontsize(10)
                autotext.set_color('white')
                autotext.set_fontweight('bold')

        ax1.set_title(self._t('clinical_pipeline'), fontsize=14, fontweight='bold', pad=20)

        # Right plot: Summary
        ax2.axis('off')

        summary_lines = [
            f"{self._t('total_compounds')}: {len(drugs)}",
            "",
            f"{self._t('breakdown')}:",
            f"  {self._t('approved')}: {len(approved)}",
            f"  {self._t('phase3')}: {len(phase3)}",
            f"  {self._t('phase2')}: {len(phase2)}",
            f"  {self._t('phase1')}: {len(phase1)}",
            f"  {self._t('preclinical')}: {len(preclinical)}",
        ]

        y_start = 0.95
        for i, line in enumerate(summary_lines):
            weight = 'bold' if self._t('total_compounds') in line or self._t('breakdown') in line else 'normal'
            ax2.text(0.1, y_start - i*0.06, line, fontsize=11, fontweight=weight,
                    transform=ax2.transAxes, verticalalignment='top')

        ax2.set_title(self._t('breakdown'), fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()

        filepath = str(self.output_dir / 'clinical_timeline.png')
        if save:
            plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return filepath

    def plot_safety_dashboard(self, safety_data: Dict, save: bool = True) -> str:
        """
        Generate simplified safety profile visualization.
        Only shows critical tissue expression bar chart.
        """
        fig, ax = plt.subplots(figsize=(12, 8))

        # Critical Tissue Expression Bar Chart
        critical_tissues = ['心脏', '肝脏', '肾脏', '大脑', '骨髓']
        expr_levels = [safety_data.get('expression', {}).get(t, 0)
                       for t in ['heart', 'liver', 'kidney', 'brain', 'bone marrow']]

        colors = [self.COLORS['danger'] if e > 10 else
                  self.COLORS['warning'] if e > 5 else
                  self.COLORS['success'] for e in expr_levels]

        bars = ax.barh(critical_tissues, expr_levels, color=colors, edgecolor='white', linewidth=2)

        # Add value labels
        for bar, tpm in zip(bars, expr_levels):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                   f'{tpm:.1f} TPM', va='center', fontsize=11, fontweight='bold')

        ax.set_xlabel('TPM (Transcripts Per Million)', fontsize=12, fontweight='bold')
        ax.set_title(self._t('critical_tissue'), fontweight='bold', fontsize=14, pad=20)

        # Add threshold lines
        ax.axvline(x=10, color=self.COLORS['danger'], linestyle='--', alpha=0.7, linewidth=2)
        ax.axvline(x=5, color=self.COLORS['warning'], linestyle='--', alpha=0.7, linewidth=2)

        # Add legend
        legend_elements = [
            mpatches.Patch(color=self.COLORS['danger'], label=f"> 10 TPM ({self._t('high')})"),
            mpatches.Patch(color=self.COLORS['warning'], label=f"5-10 TPM ({self._t('medium')})"),
            mpatches.Patch(color=self.COLORS['success'], label=f"< 5 TPM ({self._t('low')})"),
        ]
        ax.legend(handles=legend_elements, loc='lower right', frameon=True, fontsize=10)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Add safety score annotation
        safety_score = safety_data.get('score', 0)
        ax.text(0.98, 0.02, f"安全性评分: {safety_score}/20",
                transform=ax.transAxes, fontsize=12, fontweight='bold',
                ha='right', va='bottom',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        plt.tight_layout()

        filepath = str(self.output_dir / 'safety_dashboard.png')
        if save:
            plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return filepath


def main():
    """Test visualizations with sample data."""
    import argparse
    parser = argparse.ArgumentParser(description='Test visualizations')
    parser.add_argument('--output-dir', default='.', help='Output directory')
    parser.add_argument('--language', default='zh', choices=['zh', 'en'], help='Language')
    args = parser.parse_args()

    viz = ValidationVisualizer(args.output_dir, language=args.language)

    # Test data
    test_composite = {
        'total_score': 78,
        'tier': 2,
        'recommendation': 'CONDITIONAL GO',
        'score_breakdown': {
            'disease': 25,
            'druggability': 20,
            'safety': 15,
            'clinical': 10,
            'validation': 8
        }
    }

    viz.plot_validation_score(test_composite)
    print(f"Generated visualization in {args.output_dir}")


if __name__ == '__main__':
    main()