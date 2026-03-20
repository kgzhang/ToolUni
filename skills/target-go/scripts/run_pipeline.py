#!/usr/bin/env python3
"""
Target-GO 主流程运行脚本
按顺序执行所有阶段并生成综合报告
"""

import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


def run_phase(script_path: str, args: list, description: str) -> bool:
    """运行单个阶段脚本"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"时间: {datetime.now().isoformat()}")
    print(f"{'='*60}")

    cmd = [sys.executable, script_path] + args
    result = subprocess.run(cmd, capture_output=False)

    if result.returncode != 0:
        print(f"❌ {description} 失败")
        return False

    print(f"✓ {description} 完成")
    return True


def main():
    parser = argparse.ArgumentParser(description="Target-GO 靶点评估流程")
    parser.add_argument("--target", required=True, help="靶点查询（基因符号、UniProt ID）")
    parser.add_argument("--disease", default=None, help="疾病上下文")
    parser.add_argument("--output_dir", default=None, help="输出目录")
    parser.add_argument("--skip_phases", default="", help="跳过的阶段（逗号分隔）")
    args = parser.parse_args()

    # 创建输出目录（时间戳格式：YYYYMMDD_HHMMSS）
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"reports/run_{args.target}_{timestamp}")

    output_dir.mkdir(parents=True, exist_ok=True)

    # 创建子目录
    raw_data_dir = output_dir / "raw_data"
    raw_data_dir.mkdir(parents=True, exist_ok=True)

    prompts_dir = output_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    sections_dir = output_dir / "sections"
    sections_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Target-GO 靶点全方位评估系统")
    print(f"靶点: {args.target}")
    print(f"疾病上下文: {args.disease or '未指定'}")
    print(f"输出目录: {output_dir}")
    print(f"时间: {datetime.now().isoformat()}")
    print("=" * 60)

    # 脚本目录
    scripts_dir = Path(__file__).parent

    # 跳过的阶段
    skip_phases = set(args.skip_phases.split(",")) if args.skip_phases else set()

    # 运行各阶段
    phases = [
        ("phase0_disambiguation.py",
         ["--target", args.target, "--output_dir", str(output_dir)],
         "Phase 0: 靶点消歧解析"),

        ("phase1_basic_info.py",
         ["--input_dir", str(output_dir), "--output_dir", str(output_dir)],
         "Phase 1: 基础信息收集"),

        ("phase2_disease_association.py",
         ["--input_dir", str(output_dir), "--output_dir", str(output_dir)] +
         (["--disease", args.disease] if args.disease else []),
         "Phase 2: 疾病关联分析"),

        ("phase3_druggability.py",
         ["--input_dir", str(output_dir), "--output_dir", str(output_dir)],
         "Phase 3: 可药性评估"),

        ("phase4_safety.py",
         ["--input_dir", str(output_dir), "--output_dir", str(output_dir)],
         "Phase 4: 安全性评估"),

        ("phase5_literature.py",
         ["--input_dir", str(output_dir), "--output_dir", str(output_dir)] +
         (["--disease", args.disease] if args.disease else []),
         "Phase 5: 文献分析"),

        ("generate_report.py",
         ["--input_dir", str(output_dir), "--output_dir", str(output_dir)] +
         (["--disease", args.disease] if args.disease else []),
         "Phase 6: 生成综合报告"),
    ]

    success_count = 0
    failed_phases = []

    for i, (script, phase_args, description) in enumerate(phases):
        phase_name = f"phase{i}"

        if phase_name in skip_phases:
            print(f"\n跳过: {description}")
            continue

        script_path = scripts_dir / script
        if not script_path.exists():
            print(f"\n⚠️ 脚本不存在: {script}")
            continue

        if run_phase(str(script_path), phase_args, description):
            success_count += 1
        else:
            failed_phases.append(description)

    # 总结
    print("\n" + "=" * 60)
    print("流程完成")
    print("=" * 60)
    print(f"成功阶段: {success_count}/{len(phases)}")

    if failed_phases:
        print(f"\n失败阶段:")
        for phase in failed_phases:
            print(f"  - {phase}")

    print(f"\n输出文件:")
    print(f"  - 原始数据: {raw_data_dir}")
    print(f"  - 解读提示: {prompts_dir}")
    print(f"  - 解读章节: {sections_dir}")
    print(f"  - 最终报告: {output_dir}/target_report.md")

    # 检查报告是否生成
    report_file = output_dir / "target_report.md"
    if report_file.exists():
        import os
        file_size = os.path.getsize(report_file)
        print(f"\n✓ 报告已生成 ({file_size / 1024:.1f} KB)")
    else:
        print("\n⚠️ 报告文件未生成，请完成各章节解读后再运行generate_report.py")

    return 0 if success_count == len(phases) else 1


if __name__ == "__main__":
    sys.exit(main())