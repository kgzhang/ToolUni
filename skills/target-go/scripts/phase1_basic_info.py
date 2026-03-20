#!/usr/bin/env python3
"""
Phase 1: 基础信息收集与LLM解读
收集靶点的基础生物学信息，使用模板进行LLM解读
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tooluniverse import ToolUniverse


def collect_basic_info(tu: ToolUniverse, ids: dict) -> dict:
    """收集基础信息 - 增强版"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "target": ids.get("symbol"),
        "uniprot": ids.get("uniprot"),
        "ensembl": ids.get("ensembl"),
        "protein_info": {},
        "domains": [],
        "structure": {
            "pdb_entries": [],
            "alphafold": None,
            "pockets": []
        },
        "pathways": [],
        "go_annotations": {"MF": [], "BP": [], "CC": []},
        "interactions": [],
        "expression": {"gtex": {}, "hpa": {}},
        "subcellular_location": [],
        "ptm_sites": [],
        "binding_sites": [],
        "collection_log": []
    }

    uniprot_id = ids.get("uniprot")
    ensembl_id = ids.get("ensembl")
    gene_symbol = ids.get("symbol")

    # ==================== 蛋白基本信息 ====================
    if uniprot_id:
        try:
            entry = tu.tools.UniProt_get_entry_by_accession(accession=uniprot_id)
            if entry:
                # 基本信息
                results["protein_info"] = {
                    "accession": entry.get("primaryAccession", ""),
                    "name": entry.get("uniProtkbId", ""),
                    "full_name": "",
                    "length": entry.get("sequence", {}).get("length", 0),
                    "mass": entry.get("sequence", {}).get("mass", 0),
                    "organism": entry.get("organism", {}).get("scientificName", "Homo sapiens"),
                    "taxon_id": entry.get("organism", {}).get("taxonId", 9606),
                    "gene_names": [],
                    "protein_existence": entry.get("proteinExistence", ""),
                    "reviewed": entry.get("entryType", "") == "UniProtKB/Swiss-Prot"
                }

                # 全名
                prot_desc = entry.get("proteinDescription", {})
                if prot_desc.get("recommendedName"):
                    results["protein_info"]["full_name"] = prot_desc["recommendedName"].get("fullName", {}).get("value", "")

                # 基因名
                for gene in entry.get("genes", []):
                    if gene.get("geneName"):
                        results["protein_info"]["gene_names"].append(gene["geneName"].get("value", ""))

                # PDB交叉引用
                xrefs = entry.get("uniProtKBCrossReferences", [])
                pdb_ids = []
                for xref in xrefs:
                    if xref.get("database") == "PDB":
                        pdb_id = xref.get("id")
                        if pdb_id:
                            pdb_ids.append(pdb_id)
                results["protein_info"]["pdb_ids"] = list(set(pdb_ids))

                # 亚细胞定位
                comments = entry.get("comments", [])
                for c in comments:
                    if c.get("commentType") == "SUBCELLULAR LOCATION":
                        for loc in c.get("subcellularLocations", []):
                            loc_val = loc.get("location", {}).get("value", "")
                            if loc_val:
                                results["subcellular_location"].append(loc_val)

                # PTM位点
                for c in comments:
                    if c.get("commentType") == "PTM":
                        results["ptm_sites"].append(c.get("text", ""))

                results["collection_log"].append(f"✓ UniProt蛋白信息: {uniprot_id}, 长度 {results['protein_info']['length']} aa")
        except Exception as e:
            results["collection_log"].append(f"✗ UniProt信息获取失败: {str(e)}")

    # ==================== 功能描述 ====================
    if uniprot_id:
        try:
            functions = tu.tools.UniProt_get_function_by_accession(accession=uniprot_id)
            if functions and isinstance(functions, list):
                results["protein_info"]["function"] = "\n".join(functions)
                results["collection_log"].append(f"✓ 功能描述: {len(functions)} 条")
        except Exception as e:
            results["collection_log"].append(f"✗ 功能描述获取失败: {str(e)}")

    # ==================== 结构域信息 ====================
    if uniprot_id:
        try:
            domains_result = tu.tools.InterPro_get_protein_domains(protein_id=uniprot_id)
            if domains_result and domains_result.get("data"):
                domains_data = domains_result["data"]
                if isinstance(domains_data, list):
                    for d in domains_data:
                        # InterPro returns metadata at top level
                        metadata = d.get("metadata", {})
                        proteins = d.get("proteins", [])

                        domain_info = {
                            "accession": metadata.get("accession", ""),
                            "name": metadata.get("name", ""),
                            "type": metadata.get("type", ""),
                            "start": 0,
                            "end": 0
                        }

                        # Extract start/end from proteins[0].entry_protein_locations
                        if proteins and len(proteins) > 0:
                            locations = proteins[0].get("entry_protein_locations", [])
                            if locations and locations[0].get("fragments"):
                                frag = locations[0]["fragments"][0]
                                domain_info["start"] = frag.get("start", 0)
                                domain_info["end"] = frag.get("end", 0)

                        if domain_info["name"]:  # Only add if we have valid data
                            results["domains"].append(domain_info)

                    results["collection_log"].append(f"✓ InterPro结构域: {len(results['domains'])} 个")
        except Exception as e:
            results["collection_log"].append(f"✗ InterPro获取失败: {str(e)}")

    # ==================== AlphaFold结构 ====================
    if uniprot_id:
        try:
            af_result = tu.tools.alphafold_get_summary(qualifier=uniprot_id)
            if af_result and af_result.get("data"):
                af_data = af_result["data"]
                results["structure"]["alphafold"] = {
                    "uniprot": uniprot_id,
                    "pdb_url": f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb",
                    "summary": af_data
                }
                results["collection_log"].append("✓ AlphaFold结构: 可用")
        except Exception as e:
            results["collection_log"].append(f"✗ AlphaFold获取失败: {str(e)}")

    # ==================== Reactome通路 ====================
    if uniprot_id:
        try:
            pathways_result = tu.tools.Reactome_map_uniprot_to_pathways(uniprot_id=uniprot_id)
            if pathways_result and isinstance(pathways_result, list):
                for p in pathways_result:
                    results["pathways"].append({
                        "stId": p.get("stId", ""),
                        "name": p.get("name", ""),
                        "species": p.get("speciesName", ""),
                        "url": f"https://reactome.org/PathwayBrowser/#{p.get('stId', '')}"
                    })
                results["collection_log"].append(f"✓ Reactome通路: {len(results['pathways'])} 个")
        except Exception as e:
            results["collection_log"].append(f"✗ Reactome通路获取失败: {str(e)}")

    # ==================== GO注释 ====================
    if gene_symbol:
        try:
            go_result = tu.tools.GO_get_annotations_for_gene(gene_id=gene_symbol, rows=100)
            if go_result and isinstance(go_result, list):
                for ann in go_result:
                    category = ann.get("aspect", "")
                    if category in ["MF", "BP", "CC"]:
                        results["go_annotations"][category].append({
                            "go_id": ann.get("id", ""),
                            "term": ann.get("term", ""),
                            "evidence": ann.get("evidence", ""),
                            "reference": ann.get("reference", "")
                        })
                total_go = sum(len(v) for v in results["go_annotations"].values())
                results["collection_log"].append(f"✓ GO注释: {total_go} 个 (MF:{len(results['go_annotations']['MF'])}, BP:{len(results['go_annotations']['BP'])}, CC:{len(results['go_annotations']['CC'])})")
        except Exception as e:
            results["collection_log"].append(f"✗ GO注释获取失败: {str(e)}")

    # ==================== STRING蛋白相互作用 ====================
    if uniprot_id:
        try:
            string_result = tu.tools.STRING_get_protein_interactions(
                protein_ids=[uniprot_id],
                species=9606
            )
            if string_result and string_result.get("data"):
                interactions_data = string_result["data"]
                if isinstance(interactions_data, list):
                    for inter in interactions_data:
                        results["interactions"].append({
                            "partner_id": inter.get("stringIdB", ""),
                            "partner_name": inter.get("preferredNameB", ""),
                            "score": inter.get("combinedScore", 0),
                            "evidence": "STRING"
                        })
                    results["collection_log"].append(f"✓ STRING相互作用: {len(results['interactions'])} 个")
        except Exception as e:
            results["collection_log"].append(f"✗ STRING获取失败: {str(e)}")

    # ==================== GTEx表达 ====================
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
                    for expr in expression_data:
                        tissue = expr.get("tissueSiteDetailId", "")
                        results["expression"]["gtex"][tissue] = {
                            "median_tpm": expr.get("median", 0),
                            "mean_tpm": expr.get("mean", 0),
                            "tissue_name": expr.get("tissueSiteDetailId", "").replace("_", " ")
                        }
                    results["collection_log"].append(f"✓ GTEx表达: {len(results['expression']['gtex'])} 个组织")
        except Exception as e:
            results["collection_log"].append(f"✗ GTEx获取失败: {str(e)}")

    # ==================== HPA表达 ====================
    if gene_symbol:
        try:
            hpa_result = tu.tools.HPA_search_genes_by_query(search_query=gene_symbol)
            if hpa_result and hpa_result.get("genes"):
                genes = hpa_result["genes"]
                if isinstance(genes, list) and len(genes) > 0:
                    results["expression"]["hpa"]["gene_info"] = genes[0]
                    results["collection_log"].append("✓ HPA基因信息: 已获取")
        except Exception as e:
            results["collection_log"].append(f"✗ HPA获取失败: {str(e)}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Phase 1: 基础信息收集（增强版）")
    parser.add_argument("--input_dir", required=True, help="输入目录")
    parser.add_argument("--output_dir", required=True, help="输出目录")
    args = parser.parse_args()

    print("=" * 60)
    print("Phase 1: 基础信息收集（增强版）")
    print(f"时间: {datetime.now().isoformat()}")
    print("=" * 60)

    # 读取Phase 0结果
    phase0_file = Path(args.input_dir) / "phase0_disambiguation.json"
    if not phase0_file.exists():
        print(f"错误: 找不到Phase 0结果文件")
        sys.exit(1)

    with open(phase0_file, "r", encoding="utf-8") as f:
        ids = json.load(f)

    print(f"靶点: {ids.get('symbol')}")
    print(f"UniProt: {ids.get('uniprot')}")
    print(f"Ensembl: {ids.get('ensembl')}")

    # 初始化ToolUniverse
    tu = ToolUniverse()

    # 收集数据
    results = collect_basic_info(tu, ids)

    # 打印摘要
    print("\n" + "=" * 40)
    print("收集结果摘要")
    print("=" * 40)
    print(f"蛋白信息: {'✓ 已获取' if results['protein_info'] else '✗ 未获取'}")
    print(f"结构域: {len(results['domains'])} 个")
    print(f"通路: {len(results['pathways'])} 个")
    print(f"GO注释: MF={len(results['go_annotations']['MF'])}, BP={len(results['go_annotations']['BP'])}, CC={len(results['go_annotations']['CC'])}")
    print(f"相互作用: {len(results['interactions'])} 个")
    print(f"GTEx表达: {len(results['expression']['gtex'])} 个组织")
    print(f"亚细胞定位: {len(results['subcellular_location'])} 个")

    print("\n收集日志:")
    for log in results["collection_log"]:
        print(f"  {log}")

    # 保存结果
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 创建raw_data子目录
    raw_data_path = output_path / "raw_data"
    raw_data_path.mkdir(parents=True, exist_ok=True)

    output_file = raw_data_path / "phase1_basic_info.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n结果已保存到: {output_file}")

    # ==================== 生成解读提示 ====================
    from prompt_utils import generate_prompt, save_prompt

    print("\n" + "=" * 40)
    print("生成解读提示")
    print("=" * 40)

    # 01_靶点标识符提示
    prompt = generate_prompt(
        section_key="identifiers",
        raw_data={"ids": ids}
    )
    prompt_file = save_prompt(output_path, "phase1_identifiers", prompt)
    print(f"  ✓ 靶点标识符解读提示: {prompt_file}")

    # 02_基础信息提示
    prompt = generate_prompt(
        section_key="basic_info",
        raw_data={
            "protein_info": results["protein_info"],
            "domains": results["domains"],
            "structure": results["structure"],
            "subcellular_location": results["subcellular_location"]
        }
    )
    prompt_file = save_prompt(output_path, "phase1_basic_info", prompt)
    print(f"  ✓ 基础信息解读提示: {prompt_file}")

    # 03_功能与通路提示
    prompt = generate_prompt(
        section_key="function_pathways",
        raw_data={
            "go_annotations": results["go_annotations"],
            "pathways": results["pathways"],
            "function": results["protein_info"].get("function", "")
        }
    )
    prompt_file = save_prompt(output_path, "phase1_function", prompt)
    print(f"  ✓ 功能与通解读提示: {prompt_file}")

    # 04_蛋白相互作用提示
    prompt = generate_prompt(
        section_key="interactions",
        raw_data={"interactions": results["interactions"]}
    )
    prompt_file = save_prompt(output_path, "phase1_interactions", prompt)
    print(f"  ✓ 蛋白相互作用解读提示: {prompt_file}")

    # 05_表达谱提示
    prompt = generate_prompt(
        section_key="expression",
        raw_data={
            "gtex_expression": results["expression"]["gtex"],
            "hpa_expression": results["expression"]["hpa"]
        }
    )
    prompt_file = save_prompt(output_path, "phase1_expression", prompt)
    print(f"  ✓ 表达谱解读提示: {prompt_file}")

    print("\nPhase 1 完成")


if __name__ == "__main__":
    main()