#!/usr/bin/env python3
"""
Visualization Module
Generates matplotlib visualizations for the report.
Replaces ASCII charts with proper matplotlib renderings.
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


def create_validation_score_chart(composite_score: Dict[str, Any], output_dir: Path) -> Path:
    """
    Create validation score bar chart.

    Parameters:
        composite_score: Composite scoring data
        output_dir: Directory to save visualization

    Returns:
        Path to saved image
    """
    components = composite_score.get('components', {})

    categories = ['疾病关联\nDisease Association', '可成药性\nDruggability',
                  '安全性\nSafety', '临床先例\nClinical Precedent', '验证证据\nValidation Evidence']
    scores = [
        components.get('disease_association', {}).get('score', 0),
        components.get('druggability', {}).get('score', 0),
        components.get('safety', {}).get('score', 0),
        components.get('clinical_precedent', {}).get('score', 0),
        components.get('validation_evidence', {}).get('score', 0)
    ]
    max_scores = [30, 25, 20, 15, 10]
    percentages = [s/m*100 if m > 0 else 0 for s, m in zip(scores, max_scores)]

    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(categories))
    width = 0.6

    # Color based on percentage
    colors = ['#2ecc71' if p >= 80 else '#f1c40f' if p >= 60 else '#e74c3c' if p >= 40 else '#95a5a6' for p in percentages]

    bars = ax.bar(x, scores, width, color=colors, edgecolor='black', linewidth=1.2)

    # Add max score lines
    for i, (bar, max_score) in enumerate(zip(bars, max_scores)):
        ax.axhline(y=max_score, xmin=(i-0.3)/len(categories), xmax=(i+0.3)/len(categories),
                   color='gray', linestyle='--', linewidth=1)

    # Add score labels
    for bar, score, max_score, pct in zip(bars, scores, max_scores, percentages):
        height = bar.get_height()
        ax.annotate(f'{score}/{max_score}\n({pct:.0f}%)',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_ylabel('分数 (Score)', fontsize=12)
    ax.set_title('靶点验证评分概览\nTarget Validation Score Breakdown', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylim(0, max(max_scores) + 5)

    # Add total score annotation
    total = composite_score.get('total', 0)
    tier = composite_score.get('tier', 4)
    recommendation = composite_score.get('recommendation', '')

    fig.text(0.5, 0.02, f'总分 (Total): {total}/100 | 层级 (Tier): {tier} | 建议 (Recommendation): {recommendation}',
             ha='center', fontsize=12, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout(rect=[0, 0.08, 1, 1])

    output_path = output_dir / 'validation_score_chart.png'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    return output_path


def create_tissue_expression_heatmap(expression_data: Dict[str, Any], output_dir: Path) -> Optional[Path]:
    """
    Create tissue expression heatmap.

    Parameters:
        expression_data: Expression data from GTEx/HPA
        output_dir: Directory to save visualization

    Returns:
        Path to saved image or None
    """
    gtex = expression_data.get('gtex', {})

    # Extract tissue expression data
    tissues = []
    tpm_values = []

    if isinstance(gtex, dict) and 'data' in gtex:
        for item in gtex['data']:
            if isinstance(item, dict):
                tissues.append(item.get('tissue', 'Unknown'))
                tpm_values.append(item.get('median', 0))

    if not tissues:
        return None

    # Sort by TPM
    sorted_data = sorted(zip(tissues, tpm_values), key=lambda x: x[1], reverse=True)
    tissues, tpm_values = zip(*sorted_data) if sorted_data else ([], [])
    tissues, tpm_values = list(tissues)[:15], list(tpm_values)[:15]  # Top 15

    # Critical tissues
    critical_tissues = ['heart', 'liver', 'kidney', 'brain', 'bone marrow']

    fig, ax = plt.subplots(figsize=(10, 8))

    y_pos = np.arange(len(tissues))
    max_tpm = max(tpm_values) if tpm_values else 1

    # Color bars
    colors = []
    for tissue, tpm in zip(tissues, tpm_values):
        tissue_lower = tissue.lower()
        if any(c in tissue_lower for c in critical_tissues):
            if tpm > 50:
                colors.append('#e74c3c')  # Red for high expression in critical
            else:
                colors.append('#f1c40f')  # Yellow for moderate
        else:
            colors.append('#3498db')  # Blue for non-critical

    bars = ax.barh(y_pos, tpm_values, color=colors, edgecolor='black', linewidth=0.5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(tissues, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('TPM (Transcripts Per Million)', fontsize=11)
    ax.set_title('组织表达谱 (Tissue Expression Profile)', fontsize=13, fontweight='bold')

    # Legend
    legend_elements = [
        mpatches.Patch(color='#e74c3c', label='关键组织高表达 (High in Critical)'),
        mpatches.Patch(color='#f1c40f', label='关键组织中表达 (Moderate in Critical)'),
        mpatches.Patch(color='#3498db', label='其他组织 (Other Tissues)')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=8)

    # Add TPM labels
    for bar, tpm in zip(bars, tpm_values):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f'{tpm:.1f}', va='center', fontsize=8)

    plt.tight_layout()

    output_path = output_dir / 'tissue_expression_heatmap.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    return output_path


def create_disease_association_chart(diseases_data: List[Dict[str, Any]], output_dir: Path) -> Optional[Path]:
    """
    Create disease association bar chart.

    Parameters:
        diseases_data: List of disease associations
        output_dir: Directory to save visualization

    Returns:
        Path to saved image or None
    """
    if not diseases_data:
        return None

    # Sort by score
    sorted_diseases = sorted(diseases_data, key=lambda x: x.get('score', 0), reverse=True)[:10]

    if not sorted_diseases:
        return None

    diseases = [d.get('name', 'Unknown') for d in sorted_diseases]
    scores = [d.get('score', 0) for d in sorted_diseases]

    fig, ax = plt.subplots(figsize=(10, 6))

    y_pos = np.arange(len(diseases))

    # Color by score threshold
    colors = ['#2ecc71' if s >= 0.8 else '#f1c40f' if s >= 0.5 else '#e74c3c' for s in scores]

    bars = ax.barh(y_pos, scores, color=colors, edgecolor='black', linewidth=0.5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(diseases, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('关联分数 (Association Score)', fontsize=11)
    ax.set_title('疾病关联排名 (Top Disease Associations)', fontsize=13, fontweight='bold')
    ax.set_xlim(0, 1.1)

    # Add score labels
    for bar, score in zip(bars, scores):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                f'{score:.2f}', va='center', fontsize=9)

    # Add threshold lines
    ax.axvline(x=0.8, color='green', linestyle='--', linewidth=1, alpha=0.7, label='强关联 (>0.8)')
    ax.axvline(x=0.5, color='orange', linestyle='--', linewidth=1, alpha=0.7, label='中等关联 (0.5-0.8)')

    ax.legend(loc='lower right', fontsize=8)

    plt.tight_layout()

    output_path = output_dir / 'disease_association_chart.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    return output_path


def create_clinical_timeline(clinical_data: Dict[str, Any], output_dir: Path) -> Optional[Path]:
    """
    Create clinical development timeline visualization.

    Parameters:
        clinical_data: Clinical precedent data
        output_dir: Directory to save visualization

    Returns:
        Path to saved image or None
    """
    approved_drugs = clinical_data.get('approved_drugs', [])
    clinical_trials = clinical_data.get('clinical_trials', [])

    if not approved_drugs and not clinical_trials:
        return None

    fig, ax = plt.subplots(figsize=(12, 4))

    # Plot approved drugs
    for i, drug in enumerate(approved_drugs[:8]):
        ax.scatter(2000 + i*2, 1, s=200, c='#2ecc71', marker='D', edgecolors='black', linewidths=1, zorder=3)
        ax.text(2000 + i*2, 0.7, drug.get('name', 'Unknown'), ha='center', fontsize=8, rotation=45)
        ax.text(2000 + i*2, 1.2, '已批准\nApproved', ha='center', fontsize=7, color='green')

    # Plot clinical trials
    trial_colors = {3: '#f1c40f', 2: '#e67e22', 1: '#e74c3c'}
    for i, trial in enumerate(clinical_trials[:5]):
        phase = trial.get('phase', 1)
        ax.scatter(2000 + i*2 + 1, 0, s=150, c=trial_colors.get(phase, '#95a5a6'),
                   marker='o', edgecolors='black', linewidths=1, zorder=3)
        ax.text(2000 + i*2 + 1, -0.2, trial.get('name', 'Unknown'), ha='center', fontsize=7, rotation=45)

    ax.set_xlim(1998, 2025)
    ax.set_ylim(-0.5, 1.5)
    ax.set_xlabel('年份 (Year)', fontsize=10)
    ax.set_title('临床开发现状 (Clinical Development Status)', fontsize=12, fontweight='bold')
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['临床试验\nClinical Trials', '已批准药物\nApproved Drugs'])
    ax.axhline(y=0.5, color='gray', linestyle='-', linewidth=0.5)

    plt.tight_layout()

    output_path = output_dir / 'clinical_timeline.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    return output_path


def create_modality_comparison_chart(modality_scores: Dict[str, int], output_dir: Path) -> Path:
    """
    Create modality comparison radar/bar chart.

    Parameters:
        modality_scores: Dictionary of modality scores
        output_dir: Directory to save visualization

    Returns:
        Path to saved image
    """
    if not modality_scores:
        modality_scores = {
            '小分子\nSmall Molecule': 75,
            '抗体\nAntibody': 60,
            'PROTAC': 55,
            '基因治疗\nGene Therapy': 40,
            'RNA药物\nRNA Therapeutic': 50
        }

    modalities = list(modality_scores.keys())
    scores = list(modality_scores.values())

    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(modalities))

    colors = ['#3498db' if s >= 70 else '#f1c40f' if s >= 50 else '#e74c3c' for s in scores]

    bars = ax.bar(x, scores, color=colors, edgecolor='black', linewidth=1)

    ax.set_ylabel('适应性分数 (Suitability Score)', fontsize=11)
    ax.set_title('药物模式比较 (Modality Comparison)', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(modalities, fontsize=9)
    ax.set_ylim(0, 100)

    # Add score labels
    for bar, score in zip(bars, scores):
        ax.annotate(f'{score}',
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Add threshold lines
    ax.axhline(y=70, color='green', linestyle='--', linewidth=1, alpha=0.7, label='推荐 (Recommended)')
    ax.axhline(y=50, color='orange', linestyle='--', linewidth=1, alpha=0.7, label='可行 (Feasible)')

    ax.legend(loc='upper right', fontsize=8)

    plt.tight_layout()

    output_path = output_dir / 'modality_comparison_chart.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    return output_path


def generate_all_visualizations(scoring_results: Dict[str, Any], all_data: Dict[str, Any], output_dir: Path) -> Dict[str, Path]:
    """
    Generate all visualizations for the report.

    Parameters:
        scoring_results: All scoring results
        all_data: All collected data
        output_dir: Directory to save visualizations

    Returns:
        Dictionary of visualization paths
    """
    viz_dir = output_dir / 'visualizations'
    viz_dir.mkdir(parents=True, exist_ok=True)

    viz_paths = {}

    # Validation score chart
    composite = scoring_results.get('composite', {})
    if composite:
        viz_paths['validation_score'] = create_validation_score_chart(composite, viz_dir)

    # Tissue expression heatmap
    expression_data = all_data.get('section6_expression', {}).get('data', {})
    if expression_data:
        viz_paths['tissue_expression'] = create_tissue_expression_heatmap(expression_data, viz_dir)

    # Disease association chart
    diseases = all_data.get('ot_foundation', {}).get('data', {}).get('auto_discovered_diseases', [])
    if diseases:
        viz_paths['disease_association'] = create_disease_association_chart(diseases, viz_dir)

    # Clinical timeline
    clinical = scoring_results.get('clinical_precedent', {})
    if clinical:
        viz_paths['clinical_timeline'] = create_clinical_timeline(clinical, viz_dir)

    return viz_paths


if __name__ == "__main__":
    # Test visualization
    test_composite = {
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
    }

    output_dir = Path('./reports/test_run')
    create_validation_score_chart(test_composite, output_dir)
    print("Visualization created")