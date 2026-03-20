---
name: target-go
description: 靶点全方位评估系统 - 综合靶点基础信息收集和药物靶点验证能力。通过模块化脚本流程完成靶点的全面评估，每个阶段生成原始数据和解读提示，由Agent进行LLM解读生成专业的10页篇幅中文报告。包含14个核心章节、证据分级、定量评分。适用于药物靶点发现、靶点优先级排序、靶点验证等场景。
---

# 靶点全方位评估系统 (Target-GO)

综合靶点基础信息收集和药物靶点验证能力，生成专业的靶点评估报告。

## 核心原则

1. **模块化脚本** - 每个阶段独立运行，生成原始数据和解读提示
2. **模板化解读** - REPORT_TEMPLATE.md定义报告格式，确保输出一致性
3. **Agent驱动** - Agent读取提示文件，进行LLM解读生成章节内容
4. **证据分级** - T1-T4 证据层级
5. **定量评分** - 0-100分验证评分
6. **丰富内容** - 每个章节有最小字数要求
7. **简体中文** - 输出中文报告

## 工作流程

### 步骤1: 运行数据收集阶段

依次执行Phase 0-5脚本，收集原始数据并生成解读提示：

```bash
# 设置输出目录（包含时间戳）
OUTPUT_DIR="reports/run_${TARGET}_$(date +%Y%m%d_%H%M%S)"

# 运行Phase 0: 靶点消歧
.venv/bin/python skills/target-go/scripts/phase0_disambiguation.py --target {TARGET} --output_dir $OUTPUT_DIR

# 运行Phase 1: 基础信息收集
.venv/bin/python skills/target-go/scripts/phase1_basic_info.py --input_dir $OUTPUT_DIR --output_dir $OUTPUT_DIR

# 运行Phase 2: 疾病关联分析
.venv/bin/python skills/target-go/scripts/phase2_disease_association.py --input_dir $OUTPUT_DIR --output_dir $OUTPUT_DIR

# 运行Phase 3: 可药性评估
.venv/bin/python skills/target-go/scripts/phase3_druggability.py --input_dir $OUTPUT_DIR --output_dir $OUTPUT_DIR

# 运行Phase 4: 安全性评估
.venv/bin/python skills/target-go/scripts/phase4_safety.py --input_dir $OUTPUT_DIR --output_dir $OUTPUT_DIR

# 运行Phase 5: 文献分析
.venv/bin/python skills/target-go/scripts/phase5_literature.py --input_dir $OUTPUT_DIR --output_dir $OUTPUT_DIR
```

### 步骤2: Agent解读各章节

每个阶段脚本执行后，会在 `prompts/` 目录生成解读提示文件。Agent需要：

1. **读取解读提示**: 使用Read工具读取 `prompts/{phase}_prompt.md` 文件
2. **参考REPORT_TEMPLATE.md**: 确保输出格式与模板一致
3. **进行LLM解读**: 根据提示内容和模板格式生成专业的章节解读
4. **保存章节报告**: 将解读内容保存到 `sections/{章节编号}_{章节名称}.md`

**章节与提示文件对应关系**:

| 章节 | 提示文件 | 数据来源 |
|------|----------|----------|
| 1. 靶点标识符 | phase1_identifiers_prompt.md | phase0/phase1 |
| 2. 基础信息 | phase1_basic_info_prompt.md | phase1_basic_info.json |
| 3. 通路与功能 | phase1_function_prompt.md | phase1_basic_info.json |
| 4. 蛋白相互作用 | phase1_interactions_prompt.md | phase1_basic_info.json |
| 5. 表达谱 | phase1_expression_prompt.md | phase1_basic_info.json |
| 6. 疾病关联 | phase2_disease_prompt.md | phase2_disease_association.json |
| 7. 可药性评估 | phase3_druggability_prompt.md | phase3_druggability.json |
| 8. 安全性评估 | phase4_safety_prompt.md | phase4_safety.json |
| 9. 文献分析 | phase5_literature_prompt.md | phase5_literature.json |
| 10. 临床开发 | phase5_clinical_prompt.md | phase5_literature.json |

### 步骤3: 生成最终报告

所有章节解读完成后，整合生成最终报告：

```bash
.venv/bin/python skills/target-go/scripts/generate_report.py --input_dir $OUTPUT_DIR --output_dir $OUTPUT_DIR
```

---

## 报告结构（14个章节）

详细格式要求见 [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md)

### 第1章：靶点标识符（200字以上）
### 第2章：基础信息（800字以上）
### 第3章：通路与功能（600字以上）
### 第4章：蛋白相互作用（400字以上）
### 第5章：表达谱（400字以上）
### 第6章：疾病关联（600字以上）
### 第7章：可药性评估（800字以上）
### 第8章：安全性评估（400字以上）
### 第9章：文献分析（400字以上）
### 第10章：临床开发（200字以上）
### 第11章：综合评分卡
### 第12章：建议与下一步（300字以上）
### 第13章：数据来源与方法（300字以上）
### 第14章：数据缺口与局限性

---

## 输出文件结构

```
reports/run_{target}_{timestamp}/
├── raw_data/
│   ├── phase0_disambiguation.json
│   ├── phase1_basic_info.json
│   ├── phase2_disease_association.json
│   ├── phase3_druggability.json
│   ├── phase4_safety.json
│   ├── phase5_literature.json
│   └── validation_scores.json
├── prompts/
│   ├── phase1_identifiers_prompt.md
│   ├── phase1_basic_info_prompt.md
│   ├── phase1_function_prompt.md
│   ├── phase1_interactions_prompt.md
│   ├── phase1_expression_prompt.md
│   ├── phase2_disease_prompt.md
│   ├── phase3_druggability_prompt.md
│   ├── phase4_safety_prompt.md
│   ├── phase5_literature_prompt.md
│   └── phase5_clinical_prompt.md
├── sections/
│   ├── 01_identifiers.md
│   ├── 02_basic_info.md
│   ├── 03_function_pathways.md
│   ├── 04_interactions.md
│   ├── 05_expression.md
│   ├── 06_disease.md
│   ├── 07_druggability.md
│   ├── 08_safety.md
│   ├── 09_literature.md
│   ├── 10_clinical.md
│   ├── 11_scoring.md
│   ├── 12_recommendations.md
│   ├── 13_data_sources.md
│   └── 14_gaps.md
└── target_report.md          # 最终综合报告
```

---

## 证据分级系统

| 层级 | 符号 | 标准 |
|------|------|------|
| T1 | ★★★ | 直接机制证据，人体临床验证 |
| T2 | ★★ | 功能研究，模式生物验证 |
| T3 | ★ | 关联研究，筛选命中 |
| T4 | ○ | 文献提及，计算预测 |

---

## 评分系统（0-100分）

| 维度 | 满分 | 子维度 |
|------|------|--------|
| 疾病关联 | 30 | 遗传(10) + 文献(10) + 通路(10) |
| 可药性 | 25 | 结构(10) + 化合物(10) + 类别(5) |
| 安全性 | 20 | 表达(5) + 遗传(10) + 不良事件(5) |
| 临床先例 | 15 | 临床阶段 |
| 验证证据 | 10 | 功能(5) + 模型(5) |

**层级**：Tier 1 (80-100) | Tier 2 (60-79) | Tier 3 (40-59) | Tier 4 (0-39)

---

## 数据来源

疾病信息通过靶点查询从OpenTargets、DisGeNET等数据库获取，不依赖外部提供。