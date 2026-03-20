#!/usr/bin/env python3
"""
Phase 0: 靶点消歧解析
解析靶点到所有必要的标识符
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tooluniverse import ToolUniverse


def resolve_target_ids(tu: ToolUniverse, query: str) -> dict:
    """
    解析靶点到所有必要标识符

    Args:
        tu: ToolUniverse 实例
        query: 查询字符串（基因符号、UniProt ID 等）

    Returns:
        包含所有标识符的字典
    """
    ids = {
        "query": query,
        "symbol": None,
        "uniprot": None,
        "ensembl": None,
        "ensembl_versioned": None,
        "entrez": None,
        "chembl_target": None,
        "hgnc": None,
        "full_name": None,
        "synonyms": [],
        "protein_class": None,
        "resolution_log": []
    }

    # Step 1: 检查输入类型
    query_upper = query.upper()

    # UniProt accession 格式检测
    if query_upper.startswith(("P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "Q0", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "O", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N")):
        # 可能是 UniProt accession
        try:
            entry = tu.tools.UniProt_get_entry_by_accession(accession=query_upper)
            if entry and entry.get("primaryAccession"):
                ids["uniprot"] = entry.get("primaryAccession")
                ids["symbol"] = entry.get("uniProtkbId", "").split("_")[0] if entry.get("uniProtkbId") else None
                ids["full_name"] = entry.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", "")
                ids["resolution_log"].append(f"从 UniProt accession 解析: {query} -> {ids['symbol']}")
        except Exception as e:
            ids["resolution_log"].append(f"UniProt accession 查询失败: {str(e)}")

    # Ensembl ID 格式检测
    if query_upper.startswith("ENSG"):
        try:
            gene_info = tu.tools.ensembl_lookup_gene(gene_id=query_upper, species="homo_sapiens")
            if gene_info and gene_info.get("data"):
                data = gene_info["data"]
                ids["ensembl"] = query_upper
                ids["symbol"] = data.get("display_name")
                ids["full_name"] = data.get("description", "").split(" [")[0] if data.get("description") else ""
                ids["resolution_log"].append(f"从 Ensembl ID 解析: {query} -> {ids['symbol']}")
        except Exception as e:
            ids["resolution_log"].append(f"Ensembl ID 查询失败: {str(e)}")

    # Step 2: 如果还没有符号，使用 MyGene 查询
    if not ids["symbol"]:
        try:
            result = tu.tools.MyGene_query_genes(query=query)
            if result and result.get("hits"):
                hit = result["hits"][0]
                ids["symbol"] = hit.get("symbol")
                ids["entrez"] = str(hit.get("_id", "")) if hit.get("_id") else None
                ids["ensembl"] = hit.get("ensembl", {}).get("gene", "") if isinstance(hit.get("ensembl"), dict) else None
                ids["full_name"] = hit.get("name", "")
                ids["resolution_log"].append(f"从 MyGene 解析: {query} -> {ids['symbol']}")
        except Exception as e:
            ids["resolution_log"].append(f"MyGene 查询失败: {str(e)}")

    # Step 3: 获取 UniProt ID（如果还没有）
    if ids["symbol"] and not ids["uniprot"]:
        # 方法1: 使用 UniProt_search 搜索基因名
        try:
            search_result = tu.tools.UniProt_search(
                query=f"gene:{ids['symbol']} AND organism_id:9606 AND reviewed:true",
                size=1
            )
            if search_result and search_result.get("results"):
                results = search_result["results"]
                if isinstance(results, list) and len(results) > 0:
                    # 字段名是 accession 而不是 primaryAccession
                    ids["uniprot"] = results[0].get("accession", "")
                    ids["resolution_log"].append(f"从 UniProt 搜索获取 UniProt ID: {ids['uniprot']}")
        except Exception as e:
            ids["resolution_log"].append(f"UniProt 搜索失败: {str(e)}")

        # 方法2: 如果方法1失败，尝试从 MyGene 结果获取
        if not ids["uniprot"]:
            try:
                result = tu.tools.MyGene_query_genes(query=ids["symbol"])
                if result and result.get("hits"):
                    hit = result["hits"][0]
                    # 检查各种可能的 UniProt 字段
                    if hit.get("uniprot"):
                        if isinstance(hit["uniprot"], dict):
                            ids["uniprot"] = hit["uniprot"].get("Swiss-Prot", "")
                        else:
                            ids["uniprot"] = hit["uniprot"]
                    if ids["uniprot"]:
                        ids["resolution_log"].append(f"从 MyGene 获取 UniProt ID: {ids['uniprot']}")
            except Exception as e:
                ids["resolution_log"].append(f"MyGene UniProt 获取失败: {str(e)}")

    # Step 4: 获取 Ensembl ID 版本
    if ids["ensembl"]:
        try:
            gene_info = tu.tools.ensembl_lookup_gene(gene_id=ids["ensembl"], species="homo_sapiens")
            if gene_info and gene_info.get("data"):
                data = gene_info["data"]
                version = data.get("version")
                if version:
                    ids["ensembl_versioned"] = f"{ids['ensembl']}.{version}"
                if not ids["full_name"]:
                    ids["full_name"] = data.get("description", "").split(" [")[0] if data.get("description") else ""
                ids["resolution_log"].append(f"Ensembl 版本: {ids['ensembl_versioned']}")
        except Exception as e:
            ids["resolution_log"].append(f"Ensembl 版本查询失败: {str(e)}")

    # Step 5: 获取 ChEMBL 靶点 ID
    if ids["symbol"] or ids["uniprot"]:
        search_term = ids["symbol"] or ids["uniprot"]
        try:
            result = tu.tools.ChEMBL_search_targets(target_name=search_term)
            if result and result.get("data"):
                targets = result["data"].get("targets", [])
                if targets:
                    # 优先选择人类靶点
                    for t in targets:
                        if t.get("organism") == "Homo sapiens":
                            ids["chembl_target"] = t.get("target_chembl_id")
                            ids["protein_class"] = t.get("target_type", "")
                            break
                    if not ids["chembl_target"] and targets:
                        ids["chembl_target"] = targets[0].get("target_chembl_id")
                    ids["resolution_log"].append(f"ChEMBL 靶点 ID: {ids['chembl_target']}")
        except Exception as e:
            ids["resolution_log"].append(f"ChEMBL 查询失败: {str(e)}")

    # Step 6: 获取 OpenTargets 靶点 ID
    if ids["symbol"]:
        try:
            result = tu.tools.OpenTargets_get_target_id_description_by_name(targetName=ids["symbol"])
            if result and result.get("data"):
                data = result["data"]
                if isinstance(data, dict):
                    if not ids["ensembl"]:
                        ids["ensembl"] = data.get("id")
                ids["resolution_log"].append(f"OpenTargets 靶点确认: {ids['ensembl']}")
        except Exception as e:
            ids["resolution_log"].append(f"OpenTargets 查询失败: {str(e)}")

    # Step 7: 获取别名
    if ids["uniprot"]:
        try:
            alt_names = tu.tools.UniProt_get_alternative_names_by_accession(accession=ids["uniprot"])
            if alt_names:
                ids["synonyms"] = alt_names if isinstance(alt_names, list) else []
                ids["resolution_log"].append(f"获取 {len(ids['synonyms'])} 个别名")
        except Exception as e:
            ids["resolution_log"].append(f"别名查询失败: {str(e)}")

    return ids


def main():
    parser = argparse.ArgumentParser(description="Phase 0: 靶点消歧解析")
    parser.add_argument("--target", required=True, help="靶点查询（基因符号、UniProt ID、Ensembl ID）")
    parser.add_argument("--output_dir", required=True, help="输出目录")
    args = parser.parse_args()

    print("=" * 60)
    print("Phase 0: 靶点消歧解析")
    print(f"靶点查询: {args.target}")
    print(f"时间: {datetime.now().isoformat()}")
    print("=" * 60)

    # 初始化 ToolUniverse
    tu = ToolUniverse()

    # 解析标识符
    ids = resolve_target_ids(tu, args.target)

    # 打印结果
    print("\n解析结果:")
    print("-" * 40)
    print(f"基因符号: {ids['symbol']}")
    print(f"UniProt ID: {ids['uniprot']}")
    print(f"Ensembl ID: {ids['ensembl']}")
    print(f"Ensembl 版本化ID: {ids['ensembl_versioned']}")
    print(f"Entrez ID: {ids['entrez']}")
    print(f"ChEMBL ID: {ids['chembl_target']}")
    print(f"全称: {ids['full_name']}")
    print(f"别名数量: {len(ids['synonyms'])}")
    print(f"蛋白类别: {ids['protein_class']}")

    print("\n解析日志:")
    for log in ids["resolution_log"]:
        print(f"  - {log}")

    # 保存结果
    output_path = Path(args.output_dir)

    # 同时保存到根目录和raw_data子目录（便于后续脚本读取）
    raw_data_path = output_path / "raw_data"
    raw_data_path.mkdir(parents=True, exist_ok=True)

    # 保存到raw_data目录
    output_file = raw_data_path / "phase0_disambiguation.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ids, f, ensure_ascii=False, indent=2, default=str)

    # 也保存一份到根目录（便于后续脚本查找）
    root_output_file = output_path / "phase0_disambiguation.json"
    with open(root_output_file, "w", encoding="utf-8") as f:
        json.dump(ids, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n结果已保存到: {output_file}")

    return ids


if __name__ == "__main__":
    main()