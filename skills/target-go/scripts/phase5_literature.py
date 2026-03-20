#!/usr/bin/env python3
"""
Phase 5: 文献与知识图谱分析（增强版）
全面的文献检索和知识网络分析，确保所有接口正确获取数据
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tooluniverse import ToolUniverse


def collect_literature_data(tu: ToolUniverse, ids: dict, disease_context: str = None, max_papers: int = 100) -> dict:
    """收集文献数据 - 增强版"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "target": ids.get("symbol"),
        "disease_context": disease_context,
        "pubmed_papers": [],
        "opentargets_publications": [],
        "europepmc_papers": [],
        "semantic_scholar_papers": [],
        "publication_stats": {
            "total_count": 0,
            "last_5_years": 0,
            "last_10_years": 0,
            "key_papers": [],
            "trending_topics": [],
            "collaboration_network": []
        },
        "patents": [],
        "clinical_guidelines": [],
        "knowledge_graph": {
            "related_targets": [],
            "related_diseases": [],
            "related_drugs": []
        },
        "collection_log": []
    }

    symbol = ids.get("symbol")
    full_name = ids.get("full_name", "")
    ensembl_id = ids.get("ensembl")

    # ==================== PubMed文献检索 ====================
    if symbol:
        try:
            # 构建精确查询，避免名称碰撞
            query_parts = [f"{symbol}[Gene/Protein]"]
            if full_name:
                query_parts.append(f'"{full_name}"')

            query = " OR ".join(query_parts[:2])
            if disease_context:
                query = f"({query}) AND {disease_context}"

            pubmed_result = tu.tools.PubMed_search_articles(query=query, limit=max_papers)
            if pubmed_result and isinstance(pubmed_result, list):
                for paper in pubmed_result:
                    results["pubmed_papers"].append({
                        "pmid": paper.get("pmid", ""),
                        "title": paper.get("title", ""),
                        "authors": paper.get("authors", [])[:5],
                        "journal": paper.get("journal", ""),
                        "year": paper.get("year", 0),
                        "doi": paper.get("doi", ""),
                        "abstract": paper.get("abstract", "")[:500] if paper.get("abstract") else ""
                    })
                results["collection_log"].append(f"✓ PubMed: {len(pubmed_result)} 篇文献")
        except Exception as e:
            results["collection_log"].append(f"✗ PubMed检索失败: {str(e)}")

    # ==================== OpenTargets出版物 ====================
    if ensembl_id:
        try:
            pubs_result = tu.tools.OpenTargets_get_publications_by_target_ensemblID(
                entityId=ensembl_id
            )
            if pubs_result and pubs_result.get("data"):
                pubs_data = pubs_result["data"]
                if isinstance(pubs_data, list):
                    for pub in pubs_data[:50]:
                        results["opentargets_publications"].append({
                            "pmid": pub.get("pmid", ""),
                            "title": pub.get("title", ""),
                            "year": pub.get("year", 0),
                            "journal": pub.get("journal", ""),
                            "source": pub.get("source", "")
                        })
                    results["collection_log"].append(f"✓ OpenTargets出版物: {len(pubs_data)} 篇")
        except Exception as e:
            results["collection_log"].append(f"✗ OpenTargets出版物获取失败: {str(e)}")

    # ==================== Europe PMC检索 ====================
    if symbol:
        try:
            # Europe PMC查询
            ePMC_result = tu.tools.europePMC_search_publications(
                query=f"TITLE:({symbol}) OR ABSTRACT:({symbol})",
                pageSize=50
            )
            if ePMC_result and ePMC_result.get("data"):
                epmc_data = ePMC_result["data"]
                if isinstance(epmc_data, list):
                    for paper in epmc_data:
                        results["europepmc_papers"].append({
                            "pmid": paper.get("pmid", ""),
                            "pmcid": paper.get("pmcid", ""),
                            "title": paper.get("title", ""),
                            "year": paper.get("pubYear", ""),
                            "journal": paper.get("journalTitle", ""),
                            "doi": paper.get("doi", ""),
                            "isOpenAccess": paper.get("isOpenAccess", "N") == "Y"
                        })
                    results["collection_log"].append(f"✓ Europe PMC: {len(epmc_data)} 篇")
        except Exception as e:
            results["collection_log"].append(f"✗ Europe PMC检索失败: {str(e)}")

    # ==================== Semantic Scholar ====================
    if symbol:
        try:
            ss_result = tu.tools.SemanticScholar_search_papers(
                query=f"{symbol} protein",
                limit=30
            )
            if ss_result and ss_result.get("data"):
                ss_data = ss_result["data"]
                if isinstance(ss_data, list):
                    for paper in ss_data:
                        results["semantic_scholar_papers"].append({
                            "paper_id": paper.get("paperId", ""),
                            "title": paper.get("title", ""),
                            "year": paper.get("year", 0),
                            "citation_count": paper.get("citationCount", 0),
                            "influential_citation_count": paper.get("influentialCitationCount", 0),
                            "journal": paper.get("journal", {}).get("name", "") if paper.get("journal") else ""
                        })
                    results["collection_log"].append(f"✓ Semantic Scholar: {len(ss_data)} 篇")
        except Exception as e:
            results["collection_log"].append(f"✗ Semantic Scholar检索失败: {str(e)}")

    # ==================== 临床指南 ====================
    if symbol:
        try:
            guidelines_result = tu.tools.search_clinical_guidelines(query=symbol)
            if guidelines_result and guidelines_result.get("data"):
                guidelines_data = guidelines_result["data"]
                if isinstance(guidelines_data, list):
                    for guideline in guidelines_data[:20]:
                        results["clinical_guidelines"].append({
                            "title": guideline.get("title", ""),
                            "source": guideline.get("source", ""),
                            "year": guideline.get("year", ""),
                            "url": guideline.get("url", "")
                        })
                    results["collection_log"].append(f"✓ 临床指南: {len(guidelines_data)} 条")
        except Exception as e:
            results["collection_log"].append(f"✗ 临床指南获取失败: {str(e)}")

    # ==================== 统计分析 ====================
    all_papers = results["pubmed_papers"] + results["opentargets_publications"] + results["europepmc_papers"]
    all_years = [p.get("year", 0) for p in all_papers if p.get("year")]

    current_year = datetime.now().year
    results["publication_stats"]["total_count"] = len(all_papers)
    results["publication_stats"]["last_5_years"] = len([y for y in all_years if y >= current_year - 5])
    results["publication_stats"]["last_10_years"] = len([y for y in all_years if y >= current_year - 10])

    # 识别关键论文
    high_impact_journals = [
        "Nature", "Science", "Cell", "Nature Medicine", "Cancer Cell",
        "NEJM", "Lancet", "JAMA", "Nature Genetics", "Nature Communications"
    ]

    for paper in all_papers:
        journal = paper.get("journal", "")
        year = paper.get("year", 0)
        if journal in high_impact_journals and year >= current_year - 10:
            results["publication_stats"]["key_papers"].append(paper)

    # 按引用数排序Semantic Scholar论文
    if results["semantic_scholar_papers"]:
        sorted_ss = sorted(results["semantic_scholar_papers"], key=lambda x: x.get("citation_count", 0), reverse=True)
        results["publication_stats"]["key_papers"].extend(sorted_ss[:10])

    results["collection_log"].append(
        f"✓ 统计分析: 总计 {results['publication_stats']['total_count']} 篇, "
        f"近5年 {results['publication_stats']['last_5_years']} 篇, "
        f"关键论文 {len(results['publication_stats']['key_papers'])} 篇"
    )

    return results


def main():
    parser = argparse.ArgumentParser(description="Phase 5: 文献与知识图谱分析（增强版）")
    parser.add_argument("--input_dir", required=True, help="输入目录")
    parser.add_argument("--output_dir", required=True, help="输出目录")
    parser.add_argument("--disease", default=None, help="疾病上下文")
    parser.add_argument("--max_papers", type=int, default=100, help="最大文献数量")
    args = parser.parse_args()

    print("=" * 60)
    print("Phase 5: 文献与知识图谱分析（增强版）")
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
    if args.disease:
        print(f"疾病上下文: {args.disease}")

    tu = ToolUniverse()
    results = collect_literature_data(tu, ids, args.disease, args.max_papers)

    # 打印摘要
    print("\n" + "=" * 40)
    print("收集结果摘要")
    print("=" * 40)
    print(f"PubMed文献: {len(results['pubmed_papers'])} 篇")
    print(f"OpenTargets文献: {len(results['opentargets_publications'])} 篇")
    print(f"Europe PMC文献: {len(results['europepmc_papers'])} 篇")
    print(f"Semantic Scholar: {len(results['semantic_scholar_papers'])} 篇")
    print(f"近5年发表: {results['publication_stats']['last_5_years']} 篇")
    print(f"关键论文: {len(results['publication_stats']['key_papers'])} 篇")
    print(f"临床指南: {len(results['clinical_guidelines'])} 条")

    print("\n收集日志:")
    for log in results["collection_log"]:
        print(f"  {log}")

    # 保存结果
    output_path = Path(args.output_dir)
    raw_data_path = output_path / "raw_data"
    raw_data_path.mkdir(parents=True, exist_ok=True)

    output_file = raw_data_path / "phase5_literature.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n结果已保存到: {output_file}")

    # ==================== 生成解读提示 ====================
    from prompt_utils import generate_prompt, save_prompt

    print("\n" + "=" * 40)
    print("生成解读提示")
    print("=" * 40)

    # 09_文献分析提示
    prompt = generate_prompt(
        section_key="literature",
        raw_data={
            "pubmed_papers": results["pubmed_papers"][:20],
            "publication_stats": results["publication_stats"],
            "clinical_guidelines": results["clinical_guidelines"]
        }
    )
    prompt_file = save_prompt(output_path, "phase5_literature", prompt)
    print(f"  ✓ 文献分析解读提示: {prompt_file}")

    # 10_临床开发提示
    prompt = generate_prompt(
        section_key="clinical",
        raw_data={
            "clinical_trials": results.get("clinical_trials", [])
        }
    )
    prompt_file = save_prompt(output_path, "phase5_clinical", prompt)
    print(f"  ✓ 临床开发解读提示: {prompt_file}")

    print("\nPhase 5 完成")


if __name__ == "__main__":
    main()