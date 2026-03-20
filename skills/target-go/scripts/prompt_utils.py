#!/usr/bin/env python3
"""
提示生成工具模块
从REPORT_TEMPLATE.md提取模板，生成包含原始数据的解读提示
"""

import json
import re
from pathlib import Path
from typing import Optional, Any


def get_report_template_path() -> Path:
    """获取报告模板路径"""
    return Path(__file__).parent.parent / "REPORT_TEMPLATE.md"


def load_report_template() -> str:
    """加载报告模板"""
    template_path = get_report_template_path()
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def extract_section(template: str, section_title: str) -> str:
    """
    从模板中提取指定章节

    Args:
        template: 完整模板内容
        section_title: 章节标题（如"1. 靶点标识符"）

    Returns:
        章节内容
    """
    # 匹配章节标题到下一个同级标题
    pattern = rf'(## {re.escape(section_title)}.*?)(?=\n## |\Z)'
    match = re.search(pattern, template, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


# 章节映射：prompt名称 -> REPORT_TEMPLATE.md中的章节标题
SECTION_MAPPING = {
    "identifiers": "1. 靶点标识符",
    "basic_info": "2. 基础信息",
    "function_pathways": "3. 通路与功能",
    "interactions": "4. 蛋白相互作用",
    "expression": "5. 表达谱",
    "disease": "6. 疾病关联",
    "druggability": "7. 可药性评估",
    "safety": "8. 安全性评估",
    "literature": "9. 文献与研究",
    "clinical": "10. 临床开发",
    "scoring": "11. 综合评分卡",
    "recommendations": "12. 建议与下一步",
    "data_sources": "13. 数据来源与方法",
    "gaps": "14. 数据缺口与局限性",
    "executive_summary": "执行摘要",
    "competition": "12. 建议与下一步"  # 竞争格局合并到建议章节
}


def truncate_json(data: Any, max_length: int = 8000) -> str:
    """
    将数据序列化为JSON字符串，必要时进行裁剪

    Args:
        data: 要序列化的数据
        max_length: 最大长度

    Returns:
        JSON字符串
    """
    if data is None:
        return "无数据"

    if isinstance(data, str):
        return data[:max_length] + "..." if len(data) > max_length else data

    json_str = json.dumps(data, ensure_ascii=False, indent=2)

    if len(json_str) > max_length:
        # 尝试裁剪
        if isinstance(data, list) and len(data) > 10:
            truncated = data[:10]
            json_str = json.dumps(truncated, ensure_ascii=False, indent=2)
            json_str += f"\n\n... (共 {len(data)} 条数据，已裁剪显示前10条)"
        elif isinstance(data, dict):
            truncated = {}
            for k, v in data.items():
                if len(json.dumps(truncated, ensure_ascii=False)) > max_length:
                    break
                truncated[k] = v
            json_str = json.dumps(truncated, ensure_ascii=False, indent=2)
            if len(truncated) < len(data):
                json_str += f"\n\n... (数据已裁剪，显示前 {len(truncated)}/{len(data)} 个字段)"

    return json_str


def generate_prompt(
    section_key: str,
    raw_data: dict,
    instructions: str = None
) -> str:
    """
    生成解读提示

    Args:
        section_key: 章节键名（对应SECTION_MAPPING）
        raw_data: 原始数据字典
        instructions: 额外的解读指导

    Returns:
        完整的解读提示
    """
    template = load_report_template()

    # 获取章节标题
    section_title = SECTION_MAPPING.get(section_key, section_key)

    # 提取章节模板
    section_template = extract_section(template, section_title)

    if not section_template:
        section_template = f"章节 '{section_title}' 模板未找到。请根据原始数据生成专业解读。"

    # 构建原始数据JSON
    raw_data_str = ""
    for key, value in raw_data.items():
        truncated = truncate_json(value)
        raw_data_str += f"\n### {key}\n```json\n{truncated}\n```\n"

    # 构建提示
    prompt = f"""# 章节解读任务

## 目标章节
{section_title}

## 章节模板格式
请严格按照以下模板格式生成章节内容：

{section_template}

## 原始数据
以下是该章节相关的原始数据，请基于这些数据填充模板：

{raw_data_str}
"""

    if instructions:
        prompt += f"\n## 解读指导\n{instructions}\n"

    prompt += """
## 输出要求

1. 严格按照模板格式输出，保持表格和结构
2. 使用Markdown格式
3. 数据必须来自原始数据，不要编造
4. 如果某项数据缺失，标注"无数据"或"N/A"
5. 标注证据层级（T1-T4）如有适用
6. 确保内容专业、准确、完整
"""

    return prompt


def save_prompt(output_dir: Path, prompt_name: str, prompt: str) -> Path:
    """保存解读提示文件"""
    prompts_path = output_dir / "prompts"
    prompts_path.mkdir(parents=True, exist_ok=True)

    prompt_file = prompts_path / f"{prompt_name}_prompt.md"
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(prompt)

    return prompt_file


def save_section(output_dir: Path, section_num: int, section_name: str, content: str) -> Path:
    """保存章节报告"""
    sections_path = output_dir / "sections"
    sections_path.mkdir(parents=True, exist_ok=True)

    safe_name = section_name.replace("/", "_").replace(" ", "_")
    section_file = sections_path / f"{section_num:02d}_{safe_name}.md"

    with open(section_file, "w", encoding="utf-8") as f:
        f.write(content)

    return section_file