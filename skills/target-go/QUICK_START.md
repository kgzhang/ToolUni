# Target-GO 快速开始指南

快速上手使用靶点全方位评估系统。

## 安装要求

- Python 3.10+
- ToolUniverse 已安装并配置

## 基本使用

### 运行完整流程

```bash
# 进入项目目录
cd /Users/biomap/Code/2026/work/ToolUniverse

# 使用虚拟环境运行完整流程
.venv/bin/python skills/target-go/scripts/run_pipeline.py --target EGFR --disease "非小细胞肺癌"
```

### 运行单个阶段

```bash
# 创建输出目录
mkdir -p reports/run_EGFR_$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="reports/run_EGFR_$(date +%Y%m%d_%H%M%S)"

# Phase 0: 靶点消歧
.venv/bin/python skills/target-go/scripts/phase0_disambiguation.py \
    --target EGFR \
    --output_dir $OUTPUT_DIR

# Phase 1: 基础信息收集
.venv/bin/python skills/target-go/scripts/phase1_basic_info.py \
    --input_dir $OUTPUT_DIR \
    --output_dir $OUTPUT_DIR

# Phase 2: 疾病关联分析
.venv/bin/python skills/target-go/scripts/phase2_disease_association.py \
    --input_dir $OUTPUT_DIR \
    --output_dir $OUTPUT_DIR

# Phase 3: 可药性评估
.venv/bin/python skills/target-go/scripts/phase3_druggability.py \
    --input_dir $OUTPUT_DIR \
    --output_dir $OUTPUT_DIR

# Phase 4: 安全性评估
.venv/bin/python skills/target-go/scripts/phase4_safety.py \
    --input_dir $OUTPUT_DIR \
    --output_dir $OUTPUT_DIR

# Phase 5: 文献分析
.venv/bin/python skills/target-go/scripts/phase5_literature.py \
    --input_dir $OUTPUT_DIR \
    --output_dir $OUTPUT_DIR

# 生成报告
.venv/bin/python skills/target-go/scripts/generate_report.py \
    --input_dir $OUTPUT_DIR \
    --output_dir $OUTPUT_DIR
```

## 输入参数

| 参数 | 必需 | 描述 | 示例 |
|------|------|------|------|
| `--target` | 是 | 基因符号、UniProt ID 或蛋白名称 | EGFR, P00533 |
| `--disease` | 否 | 疾病名称用于上下文分析 | 非小细胞肺癌 |
| `--modality` | 否 | 治疗模式偏好 | 小分子, 抗体 |
| `--output_dir` | 是 | 输出目录路径 | reports/run_EGFR_20260320 |

## 输出文件

运行完成后，输出目录将包含：

```
reports/run_{target}_{timestamp}/
├── phase0_disambiguation.json      # 标识符解析结果
├── phase1_basic_info.json          # 基础信息数据
├── phase2_disease_association.json # 疾病关联数据
├── phase3_druggability.json        # 可药性数据
├── phase4_safety.json              # 安全性数据
├── phase5_literature.json          # 文献数据
├── validation_scores.json          # 评分结果
└── target_report.md                # 简体中文综合报告
```

## 测试工具接口

在运行流程前，可以先测试工具接口：

```bash
# 测试所有工具接口
.venv/bin/python skills/target-go/scripts/test_tools.py

# 测试特定靶点
.venv/bin/python skills/target-go/scripts/test_tools.py --target EGFR
```

## 常见问题

### Q: 某个工具返回空数据怎么办？

A: 每个阶段脚本都有后备机制。如果主工具失败，会自动尝试后备工具。所有失败和后备都会记录在输出JSON中。

### Q: 如何处理GTEx版本化ID问题？

A: 脚本会自动尝试版本化和非版本化ID，并记录成功的方式。

### Q: 报告语言是什么？

A: 报告默认使用简体中文生成，便于中文用户阅读。

### Q: 如何自定义评分权重？

A: 修改 `SCORING_CRITERIA.md` 中的评分标准，或直接修改 `generate_report.py` 中的评分逻辑。

## 示例输出

### 评分卡示例

```
靶点验证评分: EGFR (非小细胞肺癌)

| 维度 | 得分 | 满分 |
|------|------|------|
| 疾病关联 | 28 | 30 |
| 可药性 | 24 | 25 |
| 安全性 | 14 | 20 |
| 临床先例 | 15 | 15 |
| 验证证据 | 9 | 10 |
| 总分 | 90 | 100 |

优先层级: Tier 1
建议: GO - 高度验证靶点，可放心推进
```

## 更多资源

- 详细工具参数: [TOOL_REFERENCE.md](TOOL_REFERENCE.md)
- 评分标准: [SCORING_CRITERIA.md](SCORING_CRITERIA.md)
- 报告模板: [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md)