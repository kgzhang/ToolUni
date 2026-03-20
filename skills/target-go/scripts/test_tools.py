#!/usr/bin/env python3
"""
Target-GO 工具测试脚本
测试所有将使用的 ToolUniverse 工具，确保参数正确且能获取数据
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tooluniverse import ToolUniverse


class ToolTester:
    """工具测试器"""

    def __init__(self):
        self.tu = ToolUniverse()
        self.results = []
        self.passed = 0
        self.failed = 0

    def test_tool(self, tool_name: str, params: dict, description: str, check_field: str = None) -> bool:
        """测试单个工具"""
        print(f"\n测试: {description}")
        print(f"  工具: {tool_name}")
        print(f"  参数: {params}")

        try:
            tool = getattr(self.tu.tools, tool_name)
            result = tool(**params)

            # 检查结果
            if result is None:
                print(f"  ❌ 失败: 返回空结果")
                self.failed += 1
                self.results.append({
                    "tool": tool_name,
                    "params": params,
                    "status": "FAILED",
                    "error": "返回空结果"
                })
                return False

            # 检查特定字段
            if check_field and isinstance(result, dict):
                if check_field not in result and not any(check_field in str(k) for k in result.keys()):
                    print(f"  ⚠️ 警告: 未找到期望字段 '{check_field}'")

            # 检查错误状态
            if isinstance(result, dict):
                if result.get("error") or result.get("status") == "error":
                    print(f"  ❌ 失败: {result.get('error') or result.get('message')}")
                    self.failed += 1
                    self.results.append({
                        "tool": tool_name,
                        "params": params,
                        "status": "FAILED",
                        "error": result.get("error") or result.get("message")
                    })
                    return False

            # 成功
            result_type = type(result).__name__
            if isinstance(result, list):
                size = len(result)
                print(f"  ✓ 成功: 返回列表，包含 {size} 项")
            elif isinstance(result, dict):
                keys = list(result.keys())[:5]
                print(f"  ✓ 成功: 返回字典，键: {keys}...")
            else:
                print(f"  ✓ 成功: 返回 {result_type}")

            self.passed += 1
            self.results.append({
                "tool": tool_name,
                "params": params,
                "status": "PASSED",
                "result_type": result_type
            })
            return True

        except Exception as e:
            print(f"  ❌ 异常: {str(e)}")
            self.failed += 1
            self.results.append({
                "tool": tool_name,
                "params": params,
                "status": "ERROR",
                "error": str(e)
            })
            return False

    def run_all_tests(self, test_target: str = "EGFR"):
        """运行所有测试"""
        print("=" * 60)
        print("Target-GO 工具接口测试")
        print(f"测试靶点: {test_target}")
        print(f"时间: {datetime.now().isoformat()}")
        print("=" * 60)

        # ============ Phase 0: 靶点消歧 ============
        print("\n" + "=" * 40)
        print("Phase 0: 靶点消歧工具测试")
        print("=" * 40)

        self.test_tool(
            "MyGene_query_genes",
            {"query": test_target},
            "MyGene 基因查询",
            "hits"
        )

        self.test_tool(
            "UniProt_get_entry_by_accession",
            {"accession": "P00533"},
            "UniProt 蛋白条目",
            "uniProtKBCrossReferences"
        )

        self.test_tool(
            "ensembl_lookup_gene",
            {"gene_id": "ENSG00000146648", "species": "homo_sapiens"},
            "Ensembl 基因查询",
            "id"
        )

        self.test_tool(
            "OpenTargets_get_target_id_description_by_name",
            {"targetName": test_target},  # 正确参数名
            "OpenTargets 靶点ID",
            "id"
        )

        self.test_tool(
            "ChEMBL_search_targets",
            {"target_name": test_target},
            "ChEMBL 靶点搜索",
            "targets"
        )

        self.test_tool(
            "UniProt_get_function_by_accession",
            {"accession": "P00533"},
            "UniProt 功能信息"
        )

        # ============ Phase 1: 基础信息 ============
        print("\n" + "=" * 40)
        print("Phase 1: 基础信息工具测试")
        print("=" * 40)

        self.test_tool(
            "InterPro_get_protein_domains",
            {"protein_id": "P00533"},  # 正确参数名
            "InterPro 结构域",
            "results"
        )

        self.test_tool(
            "alphafold_get_summary",
            {"qualifier": "P00533"},  # 正确参数名
            "AlphaFold 摘要",
            "summary"
        )

        self.test_tool(
            "alphafold_get_prediction",
            {"qualifier": "P00533"},  # 正确参数名
            "AlphaFold 预测",
            "pdbUrl"
        )

        self.test_tool(
            "Reactome_map_uniprot_to_pathways",
            {"uniprot_id": "P00533"},  # 正确参数名
            "Reactome 通路映射",
            "pathways"
        )

        self.test_tool(
            "GO_get_annotations_for_gene",
            {"gene_id": test_target},  # 正确参数名
            "GO 注释",
            "annotations"
        )

        self.test_tool(
            "STRING_get_protein_interactions",
            {"protein_ids": ["P00533"], "species": 9606},
            "STRING 蛋白相互作用",
            "interactions"
        )

        self.test_tool(
            "GTEx_get_median_gene_expression",
            {"gencode_id": "ENSG00000146648", "operation": "get_median_gene_expression"},  # 正确operation值
            "GTEx 基因表达",
            "data"
        )

        self.test_tool(
            "HPA_search_genes_by_query",
            {"search_query": test_target},
            "HPA 基因搜索",
            "results"
        )

        # ============ Phase 2: 疾病关联 ============
        print("\n" + "=" * 40)
        print("Phase 2: 疾病关联工具测试")
        print("=" * 40)

        self.test_tool(
            "OpenTargets_get_diseases_phenotypes_by_target_ensembl",  # 正确工具名
            {"ensemblId": "ENSG00000146648"},
            "OpenTargets 疾病关联",
            "diseases"
        )

        self.test_tool(
            "gnomad_get_gene_constraints",
            {"gene_symbol": test_target},
            "gnomAD 遗传约束",
            "constraint"
        )

        self.test_tool(
            "gwas_get_snps_for_gene",
            {"mapped_gene": test_target},  # 正确参数名
            "GWAS SNP 关联",
            "snps"
        )

        self.test_tool(
            "clinvar_search_variants",
            {"gene": test_target},
            "ClinVar 变异搜索",
            "variants"
        )

        # ============ Phase 3: 可药性 ============
        print("\n" + "=" * 40)
        print("Phase 3: 可药性工具测试")
        print("=" * 40)

        self.test_tool(
            "OpenTargets_get_target_tractability_by_ensemblID",  # 正确工具名(大写ID)
            {"ensemblId": "ENSG00000146648"},
            "OpenTargets 可药性",
            "tractability"
        )

        self.test_tool(
            "OpenTargets_get_target_classes_by_ensemblID",  # 正确工具名(大写ID)
            {"ensemblId": "ENSG00000146648"},
            "OpenTargets 靶点类别",
            "classes"
        )

        self.test_tool(
            "Pharos_get_target",
            {"gene": test_target},
            "Pharos 靶点信息",
            "tdl"
        )

        self.test_tool(
            "DGIdb_get_gene_druggability",
            {"genes": [test_target]},  # 正确参数名和格式(数组)
            "DGIdb 可药性",
            "druggability"
        )

        self.test_tool(
            "ChEMBL_get_target_activities",
            {"target_chembl_id__exact": "CHEMBL203"},
            "ChEMBL 靶点活性",
            "activities"
        )

        self.test_tool(
            "BindingDB_get_ligands_by_uniprot",
            {"uniprot": "P00533", "affinity_cutoff": 10000},
            "BindingDB 配体",
            "ligands"
        )

        self.test_tool(
            "OpenTargets_get_chemical_probes_by_target_ensemblID",  # 正确工具名(大写ID)
            {"ensemblId": "ENSG00000146648"},
            "OpenTargets 化学探针",
            "probes"
        )

        self.test_tool(
            "OpenTargets_get_associated_drugs_by_target_ensemblID",  # 正确工具名(大写ID)
            {"ensemblId": "ENSG00000146648", "size": 50},
            "OpenTargets 关联药物",
            "drugs"
        )

        self.test_tool(
            "DepMap_get_gene_dependencies",
            {"gene_symbol": test_target},
            "DepMap 基因依赖",
            "dependencies"
        )

        # ============ Phase 4: 安全性 ============
        print("\n" + "=" * 40)
        print("Phase 4: 安全性工具测试")
        print("=" * 40)

        self.test_tool(
            "OpenTargets_get_target_safety_profile_by_ensemblID",  # 正确工具名(大写ID)
            {"ensemblId": "ENSG00000146648"},
            "OpenTargets 安全性档案",
            "safety"
        )

        self.test_tool(
            "OpenTargets_get_biological_mouse_models_by_ensemblID",  # 正确工具名(大写ID)
            {"ensemblId": "ENSG00000146648"},
            "OpenTargets 小鼠模型",
            "models"
        )

        self.test_tool(
            "OpenTargets_get_target_homologues_by_ensemblID",  # 正确工具名(大写ID)
            {"ensemblId": "ENSG00000146648"},
            "OpenTargets 同源物",
            "homologues"
        )

        # ============ Phase 5: 文献 ============
        print("\n" + "=" * 40)
        print("Phase 5: 文献工具测试")
        print("=" * 40)

        self.test_tool(
            "PubMed_search_articles",
            {"query": f"{test_target} AND cancer", "limit": 10},
            "PubMed 文献搜索",
            "pmid"
        )

        self.test_tool(
            "OpenTargets_get_publications_by_target_ensemblID",  # 正确工具名(大写ID)
            {"entityId": "ENSG00000146648"},
            "OpenTargets 文献",
            "publications"
        )

        # ============ 汇总 ============
        print("\n" + "=" * 60)
        print("测试汇总")
        print("=" * 60)
        print(f"通过: {self.passed}")
        print(f"失败: {self.failed}")
        print(f"总计: {self.passed + self.failed}")

        if self.failed > 0:
            print("\n失败的工具:")
            for r in self.results:
                if r["status"] != "PASSED":
                    print(f"  - {r['tool']}: {r.get('error', 'Unknown error')}")

        return self.failed == 0

    def save_results(self, output_path: str):
        """保存测试结果"""
        output = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "passed": self.passed,
                "failed": self.failed,
                "total": self.passed + self.failed
            },
            "results": self.results
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"\n测试结果已保存到: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="测试 Target-GO 工具接口")
    parser.add_argument("--target", default="EGFR", help="测试靶点 (默认: EGFR)")
    parser.add_argument("--output", default=None, help="输出文件路径")
    args = parser.parse_args()

    tester = ToolTester()
    success = tester.run_all_tests(args.target)

    if args.output:
        tester.save_results(args.output)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()