#!/usr/bin/env python3
"""
Phase 2: 疾病关联分析（增强版）
量化靶点-疾病关联强度，确保所有接口正确获取数据
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tooluniverse import ToolUniverse


def collect_disease_associations(tu: ToolUniverse, ids: dict, disease_context: str = None) -> dict:
    """收集疾病关联数据 - 增强版"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "target": ids.get("symbol"),
        "disease_context": disease_context,
        "opentargets_diseases": [],
        "genetic_constraints": {},
        "gwas_snps": [],
        "clinvar_variants": {
            "pathogenic": [],
            "likely_pathogenic": [],
            "benign": [],
            "uncertain": []
        },
        "cancer_mutations": [],
        "disgenet_associations": [],
        "collection_log": []
    }

    ensembl_id = ids.get("ensembl")
    gene_symbol = ids.get("symbol")

    # ==================== OpenTargets疾病关联 ====================
    if ensembl_id:
        try:
            diseases_result = tu.tools.OpenTargets_get_diseases_phenotypes_by_target_ensembl(
                ensemblId=ensembl_id
            )
            if diseases_result and diseases_result.get("data"):
                diseases_data = diseases_result["data"]
                if isinstance(diseases_data, list):
                    for d in diseases_data:
                        results["opentargets_diseases"].append({
                            "disease_id": d.get("id", ""),
                            "disease_name": d.get("name", ""),
                            "score": d.get("score", 0),
                            "therapeutic_areas": d.get("therapeuticAreas", []),
                            "efo_id": d.get("id", "")
                        })
                    # 按分数排序
                    results["opentargets_diseases"].sort(key=lambda x: x.get("score", 0), reverse=True)
                    results["collection_log"].append(f"✓ OpenTargets疾病关联: {len(results['opentargets_diseases'])} 个")
        except Exception as e:
            results["collection_log"].append(f"✗ OpenTargets疾病关联获取失败: {str(e)}")

    # ==================== 遗传约束(gnomAD) ====================
    if gene_symbol:
        try:
            constraints_result = tu.tools.gnomad_get_gene_constraints(gene_symbol=gene_symbol)
            if constraints_result and constraints_result.get("data"):
                constraint_data = constraints_result["data"]
                results["genetic_constraints"] = {
                    "pli": constraint_data.get("pLI", 0),
                    "loeuf": constraint_data.get("oe_lof_upper", 0),
                    "missense_z": constraint_data.get("mis_z", 0),
                    "pRec": constraint_data.get("pRec", 0),
                    "oe_lof": constraint_data.get("oe_lof", 0),
                    "oe_mis": constraint_data.get("oe_mis", 0),
                    "oe_lof_lower": constraint_data.get("oe_lof_lower", 0),
                    "oe_mis_lower": constraint_data.get("oe_mis_lower", 0),
                    "oe_mis_upper": constraint_data.get("oe_mis_upper", 0)
                }
                results["collection_log"].append(f"✓ gnomAD遗传约束: pLI={results['genetic_constraints']['pli']:.3f}, LOEUF={results['genetic_constraints']['loeuf']:.3f}")
        except Exception as e:
            results["collection_log"].append(f"✗ gnomAD遗传约束获取失败: {str(e)}")

    # ==================== GWAS SNP ====================
    if gene_symbol:
        try:
            gwas_result = tu.tools.gwas_get_snps_for_gene(mapped_gene=gene_symbol, size=100)
            if gwas_result and gwas_result.get("data"):
                gwas_data = gwas_result["data"]
                if isinstance(gwas_data, list):
                    for snp in gwas_data:
                        results["gwas_snps"].append({
                            "rs_id": snp.get("rsId", ""),
                            "chromosome": snp.get("chromosome", ""),
                            "position": snp.get("position", 0),
                            "p_value": snp.get("pValue", 0),
                            "trait": snp.get("traitName", ""),
                            "odds_ratio": snp.get("oddsRatio", 0),
                            "beta": snp.get("beta", 0),
                            "risk_allele": snp.get("riskAllele", "")
                        })
                    results["collection_log"].append(f"✓ GWAS SNP: {len(results['gwas_snps'])} 个")
        except Exception as e:
            results["collection_log"].append(f"✗ GWAS SNP获取失败: {str(e)}")

    # ==================== ClinVar变异 ====================
    if gene_symbol:
        try:
            clinvar_result = tu.tools.clinvar_search_variants(gene=gene_symbol)
            if clinvar_result and clinvar_result.get("data"):
                variants_data = clinvar_result["data"]
                if isinstance(variants_data, list):
                    for v in variants_data:
                        sig = v.get("clinicalSignificance", "").lower()
                        variant_info = {
                            "variant_id": v.get("id", ""),
                            "name": v.get("name", ""),
                            "clinical_significance": v.get("clinicalSignificance", ""),
                            "review_status": v.get("reviewStatus", ""),
                            "condition": v.get("condition", ""),
                            "allele_id": v.get("alleleId", "")
                        }
                        if "pathogenic" in sig and "likely" not in sig:
                            results["clinvar_variants"]["pathogenic"].append(variant_info)
                        elif "likely pathogenic" in sig:
                            results["clinvar_variants"]["likely_pathogenic"].append(variant_info)
                        elif "benign" in sig:
                            results["clinvar_variants"]["benign"].append(variant_info)
                        else:
                            results["clinvar_variants"]["uncertain"].append(variant_info)
                    total_variants = sum(len(v) for v in results["clinvar_variants"].values())
                    results["collection_log"].append(f"✓ ClinVar变异: {total_variants} 个 (致病:{len(results['clinvar_variants']['pathogenic'])}, 可能致病:{len(results['clinvar_variants']['likely_pathogenic'])})")
        except Exception as e:
            results["collection_log"].append(f"✗ ClinVar变异获取失败: {str(e)}")

    # ==================== OpenTargets遗传约束（备用） ====================
    if ensembl_id and not results["genetic_constraints"]:
        try:
            ot_constraints = tu.tools.OpenTargets_get_target_constraint_info_by_ensemblID(
                ensemblId=ensembl_id
            )
            if ot_constraints and ot_constraints.get("data"):
                constraint_data = ot_constraints["data"]
                if isinstance(constraint_data, dict):
                    results["genetic_constraints"] = {
                        "pli": constraint_data.get("pLI", 0),
                        "loeuf": constraint_data.get("oeLof", {}).get("upper", 0),
                        "missense_z": constraint_data.get("misZ", 0),
                        "source": "OpenTargets"
                    }
                    results["collection_log"].append("✓ OpenTargets遗传约束（备用）: 已获取")
        except Exception as e:
            results["collection_log"].append(f"✗ OpenTargets遗传约束获取失败: {str(e)}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Phase 2: 疾病关联分析（增强版）")
    parser.add_argument("--input_dir", required=True, help="输入目录")
    parser.add_argument("--output_dir", required=True, help="输出目录")
    parser.add_argument("--disease", default=None, help="疾病上下文")
    args = parser.parse_args()

    import sys
    sys.stdout.flush()

    print("=" * 60, flush=True)
    print("Phase 2: 疾病关联分析（增强版）", flush=True)
    print(f"时间: {datetime.now().isoformat()}", flush=True)
    print("=" * 60, flush=True)

    # 读取Phase 0结果
    phase0_file = Path(args.input_dir) / "phase0_disambiguation.json"
    if not phase0_file.exists():
        # 尝试raw_data目录
        phase0_file = Path(args.input_dir) / "raw_data" / "phase0_disambiguation.json"

    with open(phase0_file, "r", encoding="utf-8") as f:
        ids = json.load(f)

    print(f"靶点: {ids.get('symbol')}")

    tu = ToolUniverse()
    results = collect_disease_associations(tu, ids, args.disease)

    # 打印摘要
    print("\n" + "=" * 40)
    print("收集结果摘要")
    print("=" * 40)
    print(f"OpenTargets疾病: {len(results['opentargets_diseases'])} 个")
    print(f"遗传约束: {'✓' if results['genetic_constraints'] else '✗'}")
    print(f"GWAS SNP: {len(results['gwas_snps'])} 个")
    print(f"ClinVar变异: 致病={len(results['clinvar_variants']['pathogenic'])}, 可能致病={len(results['clinvar_variants']['likely_pathogenic'])}")

    print("\n收集日志:")
    for log in results["collection_log"]:
        print(f"  {log}")

    # 保存结果
    output_path = Path(args.output_dir)
    raw_data_path = output_path / "raw_data"
    raw_data_path.mkdir(parents=True, exist_ok=True)

    output_file = raw_data_path / "phase2_disease_association.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n结果已保存到: {output_file}")

    # ==================== 生成解读提示 ====================
    from prompt_utils import generate_prompt, save_prompt

    print("\n" + "=" * 40)
    print("生成解读提示")
    print("=" * 40)

    # 06_疾病关联提示
    prompt = generate_prompt(
        section_key="disease",
        raw_data={
            "opentargets_diseases": results["opentargets_diseases"],
            "genetic_constraints": results["genetic_constraints"],
            "gwas_snps": results["gwas_snps"],
            "clinvar_variants": results["clinvar_variants"]
        }
    )
    prompt_file = save_prompt(output_path, "phase2_disease", prompt)
    print(f"  ✓ 疾病关联解读提示: {prompt_file}")

    print("\nPhase 2 完成")


if __name__ == "__main__":
    main()