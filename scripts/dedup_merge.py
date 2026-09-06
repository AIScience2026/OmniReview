#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OmniReview — 多源检索结果归并去重脚本（零第三方依赖）

用法:
  python dedup_merge.py --inputs _working/search/*.csv --out _working/merged/merged_dedup.csv --strategy-log 文献检索报告.md

去重键: 优先 DOI（规范化小写），无 DOI 时用标题规范化（小写去符号）+ 首作者 + 年份。
合并策略: 保留字段最完整的一条记录；其余来源名合并进 source 列（分号连接）。
同时生成 文献检索报告.md 的检索留档段落（追加模式，建议传项目根目录路径）。
"""
import argparse
import csv
import glob
import hashlib
import os
import re
import sys

FIELDS = ["doi", "title", "authors", "year", "venue", "type", "cited_by",
          "abstract", "oa_url", "source", "query", "retrieved_at"]


def norm_doi(doi):
    return (doi or "").strip().lower().replace("https://doi.org/", "")


def norm_title(title):
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", (title or "").lower())


def completeness(row):
    return sum(1 for k in FIELDS if row.get(k))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--inputs", nargs="+", required=True, help="CSV 文件或通配符")
    p.add_argument("--out", required=True)
    p.add_argument("--strategy-log", default=None,
                   help="检索式留档 md（默认写到 out 同目录 文献检索报告.md；建议传项目根目录路径）")
    args = p.parse_args()

    files = []
    for pat in args.inputs:
        files.extend(glob.glob(pat))
    if not files:
        print("[err] 未找到输入文件", file=sys.stderr)
        sys.exit(1)

    index = {}   # key -> row（最完整者）
    stats = {}   # source -> count
    total_in = 0

    for fp in sorted(files):
        with open(fp, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                if not (row.get("title") or "").strip():
                    continue
                total_in += 1
                src = row.get("source", "unknown")
                stats[src] = stats.get(src, 0) + 1
                doi = norm_doi(row.get("doi"))
                key = f"doi:{doi}" if doi else (
                    f"t:{norm_title(row.get('title'))}"
                    f":{(row.get('authors') or '').split(';')[0].strip().lower()}"
                    f":{row.get('year', '')}")
                if key not in index:
                    row = dict(row)
                    row.setdefault("sources_merged", src)
                    index[key] = row
                else:
                    kept = index[key]
                    kept["sources_merged"] = f"{kept.get('sources_merged', kept.get('source'))};{src}"
                    if completeness(row) > completeness(kept):
                        merged_src = kept["sources_merged"]
                        row = dict(row)
                        row["sources_merged"] = merged_src
                        index[key] = row

    out_fields = FIELDS + ["sources_merged"]
    rows = sorted(index.values(), key=lambda r: (-int(r.get("cited_by") or 0), r.get("title", "")))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    # 文献检索报告.md 追加留档
    log_path = args.strategy_log or os.path.join(
        os.path.dirname(os.path.abspath(args.out)), "文献检索报告.md")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n## 合并批次 {os.path.basename(args.out)}\n")
        f.write(f"- 输入: {', '.join(sorted(files))}\n")
        f.write(f"- 各源命中: {stats}\n")
        f.write(f"- 合并前 {total_in} 条 -> 去重后 {len(rows)} 条（重复 {total_in - len(rows)}）\n")

    print(f"[ok] 输入 {total_in} 条（{stats}）-> 去重后 {len(rows)} 条 -> {args.out}")
    print(f"[ok] 检索留档已追加 -> {log_path}")


if __name__ == "__main__":
    main()
