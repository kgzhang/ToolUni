"""
Target-GO 核心工具模块
提供工具调用的统一接口和后备机制
"""

import json
import time
from pathlib import Path
from typing import Any, Optional
from datetime import datetime


class ToolResult:
    """工具调用结果封装"""
    def __init__(self, success: bool, data: Any = None, error: str = None, source: str = None):
        self.success = success
        self.data = data
        self.error = error
        self.source = source

    def to_dict(self):
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "source": self.source
        }


class TargetGOTools:
    """靶点评估工具集"""

    # 已知参数修正映射
    PARAM_CORRECTIONS = {
        "Reactome_map_uniprot_to_pathways": {"uniprot_id": "id"},
        "ensembl_get_xrefs": {"gene_id": "id"},
        "GTEx_get_median_gene_expression": {"requires_operation": True},
        "OpenTargets": {"ensemblID": "ensemblId"},
        "STRING_get_protein_interactions": {"array_param": "protein_ids"},
        "ChEMBL_get_target_activities": {"double_underscore": "target_chembl_id__exact"},
        "search_clinical_trials": {"required": "query_term"},
        "gnomad_get_gene_constraints": {"param": "gene_symbol"},
        "DepMap_get_gene_dependencies": {"param": "gene_symbol"},
    }

    def __init__(self, tu_client):
        """
        初始化工具集

        Args:
            tu_client: ToolUniverse 客户端实例
        """
        self.tu = tu_client
        self.call_log = []

    def _log_call(self, tool_name: str, params: dict, result: Any, success: bool):
        """记录工具调用"""
        self.call_log.append({
            "tool": tool_name,
            "params": params,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })

    def call_tool(self, tool_name: str, params: dict, fallback_tools: list = None) -> ToolResult:
        """
        调用工具，支持后备机制

        Args:
            tool_name: 工具名称
            params: 参数字典
            fallback_tools: 后备工具列表

        Returns:
            ToolResult 对象
        """
        # 尝试主工具
        result = self._single_call(tool_name, params)
        if result.success:
            return result

        # 尝试后备工具
        if fallback_tools:
            for fallback in fallback_tools:
                result = self._single_call(fallback["tool"], fallback.get("params", params))
                if result.success:
                    return result

        return result

    def _single_call(self, tool_name: str, params: dict) -> ToolResult:
        """单次工具调用"""
        try:
            tool = getattr(self.tu.tools, tool_name)
            result = tool(**params)

            # 检查结果有效性
            if result is None:
                self._log_call(tool_name, params, None, False)
                return ToolResult(False, None, "返回空结果", tool_name)

            # 处理不同返回格式
            if isinstance(result, dict):
                if result.get("error"):
                    self._log_call(tool_name, params, result, False)
                    return ToolResult(False, result, result.get("error"), tool_name)
                if result.get("status") == "error":
                    self._log_call(tool_name, params, result, False)
                    return ToolResult(False, result, result.get("message"), tool_name)

            self._log_call(tool_name, params, result, True)
            return ToolResult(True, result, None, tool_name)

        except Exception as e:
            self._log_call(tool_name, params, str(e), False)
            return ToolResult(False, None, str(e), tool_name)


class DataStorage:
    """数据存储管理"""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_json(self, filename: str, data: dict):
        """保存JSON数据"""
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        return filepath

    def load_json(self, filename: str) -> Optional[dict]:
        """加载JSON数据"""
        filepath = self.output_dir / filename
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def save_report(self, content: str, filename: str = "target_report.md"):
        """保存报告"""
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath


def format_evidence_tier(tier: str) -> str:
    """格式化证据层级"""
    tiers = {
        "T1": "★★★ [T1: 直接机制证据]",
        "T2": "★★ [T2: 功能研究验证]",
        "T3": "★ [T3: 关联研究]",
        "T4": "○ [T4: 文献提及]"
    }
    return tiers.get(tier, tier)


def interpret_pli(pli: float) -> str:
    """解释 pLI 值"""
    if pli is None:
        return "数据不可用"
    if pli >= 0.9:
        return "高度必需基因 (pLI ≥ 0.9)"
    elif pli >= 0.5:
        return "中等必需基因 (0.5 ≤ pLI < 0.9)"
    else:
        return "非必需基因 (pLI < 0.5)"


def interpret_loeuf(loeuf: float) -> str:
    """解释 LOEUF 值"""
    if loeuf is None:
        return "数据不可用"
    if loeuf <= 0.35:
        return "强负选择 (LOEUF ≤ 0.35)"
    elif loeuf <= 0.7:
        return "中等负选择 (0.35 < LOEUF ≤ 0.7)"
    else:
        return "弱负选择 (LOEUF > 0.7)"


def interpret_tdl(tdl: str) -> str:
    """解释靶点开发水平"""
    interpretations = {
        "Tclin": "Tclin - 批准药物靶点，最高可药性置信度",
        "Tchem": "Tchem - 有小分子活性，良好的化学可及性",
        "Tbio": "Tbio - 生物学特征已研究，可能需要新模式",
        "Tdark": "Tdark - 研究不足，高新颖性潜力"
    }
    return interpretations.get(tdl, f"TDL: {tdl}")


def score_to_tier(score: int) -> tuple:
    """分数转换为优先层级"""
    if score >= 80:
        return "Tier 1", "GO - 高度验证靶点，可放心推进"
    elif score >= 60:
        return "Tier 2", "CONDITIONAL GO - 良好靶点，需重点验证"
    elif score >= 40:
        return "Tier 3", "CAUTION - 中等风险，需大量验证"
    else:
        return "Tier 4", "NO-GO - 高风险，建议考虑替代方案"