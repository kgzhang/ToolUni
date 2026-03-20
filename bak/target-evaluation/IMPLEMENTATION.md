# Target Validation - Implementation Guide

Implementation guidance for the target validation pipeline. All code is located in `scripts/` directory.

---

## Script Structure

Scripts are organized by report sections. Each script is independent and outputs raw data to the intermediate layer.

```
scripts/
├── section1_identifiers.py      # Section 1: Target Identifiers
├── section2_basic_info.py       # Section 2: Basic Information
├── section3_structure.py        # Section 3: Structural Biology
├── section4_pathways.py         # Section 4: Function & Pathways
├── section5_ppi.py              # Section 5: Protein Interactions
├── section6_expression.py       # Section 6: Expression Profile
├── section7_genetics.py         # Section 7: Genetic Variation
├── open_targets_foundation.py   # Open Targets Foundation Data
├── section8_disease_scoring.py  # Section 8: Disease Association Scoring
├── section9_druggability_scoring.py  # Section 9: Druggability Assessment
├── section10_safety_scoring.py  # Section 10: Safety Analysis
├── section11_clinical_scoring.py     # Section 11: Clinical Precedent
├── section12_validation_scoring.py  # Section 12: Validation Evidence
├── section13_composite_scoring.py    # Section 13: Composite Score
├── visualization.py             # Matplotlib visualizations
├── report_generator.py          # Report generation
└── run_validation.py            # Main pipeline runner
```

---

## Running the Pipeline

```bash
cd skills/target-evaluation/scripts
uv run python run_validation.py EGFR
uv run python run_validation.py KRAS --disease "pancreatic cancer"
uv run python run_validation.py EGFR --output ./reports/custom_run
```

---

## Data Flow

```
User Input → Section Scripts → Raw Data (JSON) → Visualization → Report
                ↓
         Intermediate Layer
         (section*.json files)
```

---

## Key Principles

1. **独立性**: 每个section脚本独立运行，不依赖其他section的执行结果
2. **原始数据**: 工具输出直接保存，不做二次加工
3. **章节拆分**: 数据获取按报告章节拆分，不合并
4. **中文输出**: 报告生成时英文内容通过LLM转换为中文

---

## Output Files

Each section outputs two types of files:

1. **Raw Data JSON**: `section{n}_{name}.json`
   - `data`: Raw tool output
   - `raw_tool_calls`: All tool calls made

2. **Report Markdown**: Generated separately by `report_generator.py`

---

## Tool Parameter Reference

See [TOOL_REFERENCE.md](TOOL_REFERENCE.md) for correct parameter usage.

---

## Scoring Reference

See [SCORING_CRITERIA.md](SCORING_CRITERIA.md) for scoring details.

---

## Evidence Grading

See [EVIDENCE_GRADING.md](EVIDENCE_GRADING.md) for T1-T4 definitions.

---

## Extending the Pipeline

To add a new section:

1. Create `section{n}_{name}.py` in `scripts/`
2. Implement data collection function
3. Save raw data to JSON
4. Update `run_validation.py` to call the new section
5. Update `report_generator.py` to include in report

---

## Error Handling

Each script handles errors independently:
- Tool failures are logged in `raw_tool_calls` with error message
- Empty/null results are stored as-is
- Fallback chains are implemented within each script