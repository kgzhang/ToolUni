#!/usr/bin/env python3
"""
Phase 4: 安全性评估（增强版）
全面评估靶点相关的安全风险，确保所有接口正确获取数据
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tooluniverse import ToolUniverse


def collect_safety_data(tu: ToolUniverse, ids: dict) -> dict:
    """收集安全性数据 - 增强版"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "target": ids.get("symbol"),
        "safety_profile": {
            "liabilities": [],
            "adverse_events": [],
            "toxicity_data": []
        },
        "mouse_models": [],
        "homologues": [],
        "paralogs": [],
        "crispr_phenotypes": [],
        "tissue_expression_safety": {},
        "essentiality": {},
        "safety_score": {
            "risk_level": "Unknown",
            "factors": []
        },
        "collection_log": []
    }

    ensembl_id = ids.get("ensembl")
    gene_symbol = ids.get("symbol")
    uniprot_id = ids.get("uniprot")

    # ==================== OpenTargets安全性档案 ====================
    if ensembl_id:
        try:
            safety_result = tu.tools.OpenTargets_get_target_safety_profile_by_ensemblID(
                ensemblId=ensembl_id
            )
            if safety_result and safety_result.get("data"):
                safety_data = safety_result["data"]
                if isinstance(safety_data, list):
                    results["safety_profile"]["liabilities"] = safety_data
                    results["collection_log"].append(f"✓ OpenTargets安全性: {len(safety_data)} 个风险项")
                elif isinstance(safety_data, dict):
                    results["safety_profile"]["liabilities"] = safety_data.get("liabilities", [])
                    results["collection_log"].append("✓ OpenTargets安全性档案: 已获取")
        except Exception as e:
            results["collection_log"].append(f"✗ OpenTargets安全性获取失败: {str(e)}")

    # ==================== 小鼠模型表型 ====================
    if ensembl_id:
        try:
            models_result = tu.tools.OpenTargets_get_biological_mouse_models_by_ensemblID(
                ensemblId=ensembl_id
            )
            if models_result and models_result.get("data"):
                models_data = models_result["data"]
                if isinstance(models_data, list):
                    for model in models_data:
                        results["mouse_models"].append({
                            "model_id": model.get("id", ""),
                            "phenotype": model.get("phenotype", ""),
                            "allele_symbol": model.get("alleleSymbol", ""),
                            "genetic_background": model.get("geneticBackground", ""),
                            "source": model.get("source", "")
                        })
                    results["collection_log"].append(f"✓ 小鼠模型: {len(results['mouse_models'])} 个")
        except Exception as e:
            results["collection_log"].append(f"✗ 小鼠模型获取失败: {str(e)}")

    # ==================== 同源物 ====================
    if ensembl_id:
        try:
            homologues_result = tu.tools.OpenTargets_get_target_homologues_by_ensemblID(
                ensemblId=ensembl_id
            )
            if homologues_result and homologues_result.get("data"):
                homologues_data = homologues_result["data"]
                if isinstance(homologues_data, list):
                    for hom in homologues_data:
                        results["homologues"].append({
                            "homologue_id": hom.get("homologueId", ""),
                            "species": hom.get("species", ""),
                            "type": hom.get("type", ""),
                            "sequence_similarity": hom.get("sequenceSimilarity", 0)
                        })
                    results["collection_log"].append(f"✓ 同源物: {len(results['homologues'])} 个")
        except Exception as e:
            results["collection_log"].append(f"✗ 同源物获取失败: {str(e)}")

    # ==================== 旁系同源 ====================
    if ensembl_id:
        try:
            paralogs_result = tu.tools.OpenTargets_get_target_paralogs_by_ensemblID(
                ensemblId=ensembl_id
            )
            if paralogs_result and paralogs_result.get("data"):
                paralogs_data = paralogs_result["data"]
                if isinstance(paralogs_data, list):
                    results["paralogs"] = paralogs_data
                    results["collection_log"].append(f"✓ 旁系同源: {len(paralogs_data)} 个")
        except Exception as e:
            results["collection_log"].append(f"✗ 旁系同源获取失败: {str(e)}")

    # ==================== DepMap必需性 ====================
    if gene_symbol:
        try:
            depmap_result = tu.tools.DepMap_get_gene_dependencies(gene_symbol=gene_symbol)
            if depmap_result and depmap_result.get("data"):
                depmap_data = depmap_result["data"]
                results["essentiality"] = depmap_data
                results["collection_log"].append("✓ DepMap必需性: 已获取")
        except Exception as e:
            results["collection_log"].append(f"✗ DepMap获取失败: {str(e)}")

    # ==================== GTEx表达（用于安全性评估） ====================
    ensembl_versioned = ids.get("ensembl_versioned") or ensembl_id
    if ensembl_versioned:
        try:
            gtex_result = tu.tools.GTEx_get_median_gene_expression(
                gencode_id=ensembl_versioned,
                operation="get_median_gene_expression"
            )
            if gtex_result and gtex_result.get("data"):
                expression_data = gtex_result["data"]
                if isinstance(expression_data, list):
                    critical_tissues = [
                        "Heart", "Liver", "Kidney", "Brain", "Lung",
                        "Pancreas", "Spleen", "Stomach", "Colon", "Artery"
                    ]
                    for expr in expression_data:
                        tissue = expr.get("tissueSiteDetailId", "")
                        tpm = expr.get("median", 0)
                        if tpm > 5:  # 只关注高表达组织
                            results["tissue_expression_safety"][tissue] = {
                                "median_tpm": tpm,
                                "mean_tpm": expr.get("mean", 0),
                                "is_critical": any(ct.lower() in tissue.lower() for ct in critical_tissues)
                            }
                    results["collection_log"].append(f"✓ GTEx表达（安全性）: {len(results['tissue_expression_safety'])} 个高表达组织")
        except Exception as e:
            results["collection_log"].append(f"✗ GTEx表达获取失败: {str(e)}")

    # ==================== 计算安全性风险等级 ====================
    risk_factors = []

    # 检查安全性档案
    if results["safety_profile"]["liabilities"]:
        risk_factors.append(f"存在 {len(results['safety_profile']['liabilities'])} 个已知安全风险")

    # 检查小鼠模型致死表型
    lethal_phenotypes = [m for m in results["mouse_models"] if
                        "lethal" in m.get("phenotype", "").lower() or
                        "embryonic" in m.get("phenotype", "").lower()]
    if lethal_phenotypes:
        risk_factors.append(f"小鼠模型显示 {len(lethal_phenotypes)} 个致死/胚胎表型")

    # 检查必需性
    if results["essentiality"]:
        results["essentiality"].get("common_essential_count", 0)
        # 如果多个细胞系依赖，提示风险
        if results["essentiality"].get("essential_count", 0) > 10:
            risk_factors.append("DepMap显示多个细胞系依赖此基因")

    # 检查关键组织表达
    critical_expr = {k: v for k, v in results["tissue_expression_safety"].items() if v.get("is_critical")}
    if critical_expr:
        risk_factors.append(f"{len(critical_expr)} 个关键组织高表达")

    results["safety_score"]["factors"] = risk_factors

    # 确定风险等级
    if len(risk_factors) >= 3:
        results["safety_score"]["risk_level"] = "High"
    elif len(risk_factors) >= 1:
        results["safety_score"]["risk_level"] = "Medium"
    else:
        results["safety_score"]["risk_level"] = "Low"

    return results


def main():
    parser = argparse.ArgumentParser(description="Phase 4: 安全性评估（增强版）")
    parser.add_argument("--input_dir", required=True, help="输入目录")
    parser.add_argument("--output_dir", required=True, help="输出目录")
    args = parser.parse_args()

    print("=" * 60)
    print("Phase 4: 安全性评估（增强版）")
    print(f"时间: {datetime.now().isoformat()}")
    print("=" * 60)

    # 读取Phase 0结果
    input_path = Path(args.input_dir)
    phase0_file = input_path / "phase0_disambiguation.json"
    if not phase0_file.exists():
        phase0_file = input_path / "raw_data" / "phase0_disambiguation.json"

    with open(phase0_file, "r", encoding="utf-8") as f:
        ids = json.load(f)

    print(f"靶点: {ids.get('symbol')}")

    tu = ToolUniverse()
    results = collect_safety_data(tu, ids)

    # 打印摘要
    print("\n" + "=" * 40)
    print("收集结果摘要")
    print("=" * 40)
    print(f"安全性风险: {len(results['safety_profile']['liabilities'])} 个")
    print(f"小鼠模型: {len(results['mouse_models'])} 个")
    print(f"同源物: {len(results['homologues'])} 个")
    print(f"关键组织表达: {len([k for k, v in results['tissue_expression_safety'].items() if v.get('is_critical')])} 个")
    print(f"风险等级: {results['safety_score']['risk_level']}")

    print("\n收集日志:")
    for log in results["collection_log"]:
        print(f"  {log}")

    # 保存结果
    output_path = Path(args.output_dir)
    raw_data_path = output_path / "raw_data"
    raw_data_path.mkdir(parents=True, exist_ok=True)

    output_file = raw_data_path / "phase4_safety.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n结果已保存到: {output_file}")

    # ==================== 生成解读提示 ====================
    from prompt_utils import generate_prompt, save_prompt

    print("\n" + "=" * 40)
    print("生成解读提示")
    print("=" * 40)

    # 08_安全性评估提示
    prompt = generate_prompt(
        section_key="safety",
        raw_data={
            "safety_profile": results["safety_profile"],
            "mouse_models": results["mouse_models"],
            "homologues": results["homologues"],
            "tissue_expression_safety": results["tissue_expression_safety"],
            "essentiality": results["essentiality"],
            "safety_score": results["safety_score"]
        }
    )
    prompt_file = save_prompt(output_path, "phase4_safety", prompt)
    print(f"  ✓ 安全性评估解读提示: {prompt_file}")

    print("\nPhase 4 完成")


if __name__ == "__main__":
    main()