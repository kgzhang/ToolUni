#!/usr/bin/env python3
"""
Phase 3: 可药性评估（增强版）
评估靶点的成药可能性，确保所有接口正确获取数据
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tooluniverse import ToolUniverse


def collect_druggability_data(tu: ToolUniverse, ids: dict) -> dict:
    """收集可药性数据 - 增强版"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "target": ids.get("symbol"),
        "tractability": {
            "small_molecule": None,
            "antibody": None,
            "protac": None,
            "other": None
        },
        "target_classes": [],
        "pharos_tdl": {},
        "dgidb_druggability": [],
        "chembl_activities": [],
        "bindingdb_ligands": [],
        "chemical_probes": [],
        "associated_drugs": [],
        "clinical_trials": [],
        "depmap_dependencies": {},
        "collection_log": []
    }

    ensembl_id = ids.get("ensembl")
    gene_symbol = ids.get("symbol")
    uniprot_id = ids.get("uniprot")
    chembl_target = ids.get("chembl_target")

    # ==================== OpenTargets可药性 ====================
    if ensembl_id:
        try:
            tract_result = tu.tools.OpenTargets_get_target_tractability_by_ensemblID(
                ensemblId=ensembl_id
            )
            if tract_result and tract_result.get("data"):
                tract_data = tract_result["data"]
                if isinstance(tract_data, list):
                    for t in tract_data:
                        modality = t.get("label", "").lower()
                        tract_info = {
                            "bucket": t.get("value", ""),
                            "is_tractable": t.get("value", "") in ["1", "2", "3", "4", "5", "6", "7"],
                            "evidence": t.get("data", {})
                        }
                        if "small molecule" in modality or "sm" in modality:
                            results["tractability"]["small_molecule"] = tract_info
                        elif "antibody" in modality or "ab" in modality:
                            results["tractability"]["antibody"] = tract_info
                        elif "protac" in modality or "pr" in modality:
                            results["tractability"]["protac"] = tract_info
                        else:
                            results["tractability"]["other"] = tract_info
                    results["collection_log"].append(f"✓ OpenTargets可药性: SM={results['tractability']['small_molecule'] is not None}, AB={results['tractability']['antibody'] is not None}")
        except Exception as e:
            results["collection_log"].append(f"✗ OpenTargets可药性获取失败: {str(e)}")

    # ==================== 靶点类别 ====================
    if ensembl_id:
        try:
            classes_result = tu.tools.OpenTargets_get_target_classes_by_ensemblID(
                ensemblId=ensembl_id
            )
            if classes_result and classes_result.get("data"):
                classes_data = classes_result["data"]
                if isinstance(classes_data, list):
                    results["target_classes"] = classes_data
                    results["collection_log"].append(f"✓ 靶点类别: {len(classes_data)} 个")
        except Exception as e:
            results["collection_log"].append(f"✗ 靶点类别获取失败: {str(e)}")

    # ==================== Pharos TDL ====================
    if gene_symbol:
        try:
            pharos_result = tu.tools.Pharos_get_target(gene=gene_symbol)
            if pharos_result and pharos_result.get("data"):
                pharos_data = pharos_result["data"]
                results["pharos_tdl"] = {
                    "tdl": pharos_data.get("tdl", ""),
                    "family": pharos_data.get("fam", ""),
                    "name": pharos_data.get("name", ""),
                    "novelty": pharos_data.get("novelty", 0),
                    "publication_count": pharos_data.get("publicationCount", 0),
                    "description": pharos_data.get("description", "")
                }
                results["collection_log"].append(f"✓ Pharos TDL: {results['pharos_tdl'].get('tdl', 'N/A')}")
        except Exception as e:
            results["collection_log"].append(f"✗ Pharos获取失败: {str(e)}")

    # ==================== DGIdb可药性 ====================
    if gene_symbol:
        try:
            dgidb_result = tu.tools.DGIdb_get_gene_druggability(genes=[gene_symbol])
            if dgidb_result and dgidb_result.get("data"):
                dgidb_data = dgidb_result["data"]
                if isinstance(dgidb_data, list):
                    results["dgidb_druggability"] = dgidb_data
                    categories = [d.get("name", "") for d in dgidb_data]
                    results["collection_log"].append(f"✓ DGIdb可药性类别: {', '.join(categories[:5])}")
        except Exception as e:
            results["collection_log"].append(f"✗ DGIdb获取失败: {str(e)}")

    # ==================== ChEMBL活性数据 ====================
    if chembl_target:
        try:
            chembl_result = tu.tools.ChEMBL_get_target_activities(
                target_chembl_id__exact=chembl_target
            )
            if chembl_result and chembl_result.get("data"):
                activities_data = chembl_result["data"]
                if isinstance(activities_data, dict):
                    activities = activities_data.get("activities", [])
                    for a in activities[:50]:
                        results["chembl_activities"].append({
                            "molecule_chembl_id": a.get("molecule_chembl_id", ""),
                            "canonical_smiles": a.get("canonical_smiles", ""),
                            "standard_type": a.get("standard_type", ""),
                            "standard_value": a.get("standard_value", 0),
                            "standard_units": a.get("standard_units", ""),
                            "pchembl_value": a.get("pchembl_value", 0),
                            "assay_chembl_id": a.get("assay_chembl_id", "")
                        })
                    results["collection_log"].append(f"✓ ChEMBL活性: {len(results['chembl_activities'])} 条记录")
        except Exception as e:
            results["collection_log"].append(f"✗ ChEMBL活性获取失败: {str(e)}")

    # ==================== 关联药物 ====================
    if ensembl_id:
        try:
            drugs_result = tu.tools.OpenTargets_get_associated_drugs_by_target_ensemblID(
                ensemblId=ensembl_id,
                size=100
            )
            if drugs_result and drugs_result.get("data"):
                drugs_data = drugs_result["data"]
                if isinstance(drugs_data, list):
                    for drug in drugs_data:
                        results["associated_drugs"].append({
                            "drug_id": drug.get("id", ""),
                            "drug_name": drug.get("name", ""),
                            "chembl_id": drug.get("id", "").replace("chembl:", ""),
                            "mechanism_of_action": drug.get("mechanismOfAction", ""),
                            "phase": drug.get("phase", 0),
                            "is_approved": drug.get("isApproved", False),
                            "indications": drug.get("indications", []),
                            "synonyms": drug.get("synonyms", [])
                        })
                    approved_count = sum(1 for d in results["associated_drugs"] if d.get("is_approved"))
                    results["collection_log"].append(f"✓ 关联药物: {len(results['associated_drugs'])} 个 (已批准:{approved_count})")
        except Exception as e:
            results["collection_log"].append(f"✗ 关联药物获取失败: {str(e)}")

    # ==================== 化学探针 ====================
    if ensembl_id:
        try:
            probes_result = tu.tools.OpenTargets_get_chemical_probes_by_target_ensemblID(
                ensemblId=ensembl_id
            )
            if probes_result and probes_result.get("data"):
                probes_data = probes_result["data"]
                if isinstance(probes_data, list):
                    results["chemical_probes"] = probes_data
                    results["collection_log"].append(f"✓ 化学探针: {len(probes_data)} 个")
        except Exception as e:
            results["collection_log"].append(f"✗ 化学探针获取失败: {str(e)}")

    # ==================== DepMap依赖性 ====================
    if gene_symbol:
        try:
            depmap_result = tu.tools.DepMap_get_gene_dependencies(gene_symbol=gene_symbol)
            if depmap_result and depmap_result.get("data"):
                depmap_data = depmap_result["data"]
                results["depmap_dependencies"] = depmap_data
                results["collection_log"].append("✓ DepMap依赖性: 已获取")
        except Exception as e:
            results["collection_log"].append(f"✗ DepMap获取失败: {str(e)}")

    # ==================== 临床试验 ====================
    if gene_symbol:
        try:
            trials_result = tu.tools.search_clinical_trials(query_term=gene_symbol)
            if trials_result and trials_result.get("data"):
                trials_data = trials_result["data"]
                if isinstance(trials_data, list):
                    for trial in trials_data[:20]:
                        results["clinical_trials"].append({
                            "nct_id": trial.get("nctId", ""),
                            "title": trial.get("title", ""),
                            "phase": trial.get("phase", ""),
                            "status": trial.get("status", ""),
                            "condition": trial.get("condition", "")
                        })
                    results["collection_log"].append(f"✓ 临床试验: {len(results['clinical_trials'])} 个")
        except Exception as e:
            results["collection_log"].append(f"✗ 临床试验获取失败: {str(e)}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Phase 3: 可药性评估（增强版）")
    parser.add_argument("--input_dir", required=True, help="输入目录")
    parser.add_argument("--output_dir", required=True, help="输出目录")
    args = parser.parse_args()

    print("=" * 60)
    print("Phase 3: 可药性评估（增强版）")
    print(f"时间: {datetime.now().isoformat()}")
    print("=" * 60)

    # 读取Phase 0结果
    phase0_file = Path(args.input_dir) / "phase0_disambiguation.json"
    if not phase0_file.exists():
        phase0_file = Path(args.input_dir) / "raw_data" / "phase0_disambiguation.json"

    with open(phase0_file, "r", encoding="utf-8") as f:
        ids = json.load(f)

    print(f"靶点: {ids.get('symbol')}")

    tu = ToolUniverse()
    results = collect_druggability_data(tu, ids)

    # 打印摘要
    print("\n" + "=" * 40)
    print("收集结果摘要")
    print("=" * 40)
    print(f"可药性: SM={results['tractability']['small_molecule'] is not None}, AB={results['tractability']['antibody'] is not None}")
    print(f"Pharos TDL: {results['pharos_tdl'].get('tdl', 'N/A')}")
    print(f"ChEMBL活性: {len(results['chembl_activities'])} 条")
    print(f"关联药物: {len(results['associated_drugs'])} 个")
    print(f"化学探针: {len(results['chemical_probes'])} 个")
    print(f"临床试验: {len(results['clinical_trials'])} 个")

    print("\n收集日志:")
    for log in results["collection_log"]:
        print(f"  {log}")

    # 保存结果
    output_path = Path(args.output_dir)
    raw_data_path = output_path / "raw_data"
    raw_data_path.mkdir(parents=True, exist_ok=True)

    output_file = raw_data_path / "phase3_druggability.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n结果已保存到: {output_file}")

    # ==================== 生成解读提示 ====================
    from prompt_utils import generate_prompt, save_prompt

    print("\n" + "=" * 40)
    print("生成解读提示")
    print("=" * 40)

    # 07_可药性评估提示
    prompt = generate_prompt(
        section_key="druggability",
        raw_data={
            "tractability": results["tractability"],
            "pharos_tdl": results["pharos_tdl"],
            "associated_drugs": results["associated_drugs"],
            "chembl_activities": results["chembl_activities"],
            "chemical_probes": results["chemical_probes"],
            "clinical_trials": results["clinical_trials"],
            "depmap_dependencies": results["depmap_dependencies"]
        }
    )
    prompt_file = save_prompt(output_path, "phase3_druggability", prompt)
    print(f"  ✓ 可药性评估解读提示: {prompt_file}")

    # 12_竞争格局提示（基于可药性数据）
    prompt = generate_prompt(
        section_key="recommendations",
        raw_data={
            "approved_drugs": [d for d in results["associated_drugs"] if d.get("is_approved")],
            "clinical_drugs": results["associated_drugs"],
            "chembl_activities": results["chembl_activities"][:20]
        }
    )
    prompt_file = save_prompt(output_path, "phase3_competition", prompt)
    print(f"  ✓ 竞争格局解读提示: {prompt_file}")

    print("\nPhase 3 完成")


if __name__ == "__main__":
    main()