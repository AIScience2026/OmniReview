#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OmniReview — 报告规范清单审计引擎（注册表驱动，零第三方依赖）

职责分工: 本脚本负责清单加载、校验、审计表脚手架与汇总一致性检查；
逐条目的证据定位与 Reported/Partial/Missing 判定由 AI 依据稿文完成。

用法:
  python audit_checklist.py --list
  python audit_checklist.py --checklist prisma-scr --scaffold --out audit.md
  python audit_checklist.py --checklist prisma-scr,amstar-2 --scaffold --out audit.md
  python audit_checklist.py --checklist prisma-scr --report audit_filled.json --out audit_final.md
      （audit_filled.json 由 AI 填写: [{"id":"1","status":"Reported","evidence":"原句...","fix":""}, ...]）
"""
import argparse
import glob
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKLIST_DIR = os.path.normpath(os.path.join(HERE, "..", "references"))
VALID = ("Reported", "Partial", "Missing", "N/A")


def load_all():
    reg = {}
    for fp in sorted(glob.glob(os.path.join(CHECKLIST_DIR, "checklist-*.json"))):
        name = os.path.basename(fp)
        if name == "checklist-stub-registry.json":
            continue
        with open(fp, encoding="utf-8") as f:
            data = json.load(f)
        reg[data["guideline"]] = data
    stub_fp = os.path.join(CHECKLIST_DIR, "checklist-stub-registry.json")
    if os.path.exists(stub_fp):
        with open(stub_fp, encoding="utf-8") as f:
            reg["_stubs"] = json.load(f)
    return reg


def scaffold(cl, out_path, adapted=False):
    lines = [
        f"# 审计报告（{cl['name']}）",
        f"- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"- 规范来源: {cl['source']}",
        f"- 条目数: {len(cl['items'])}" + ("（adapted 适配版）" if adapted or cl.get("condensed") else ""),
        "",
        "> 填写规则：status ∈ Reported/Partial/Missing/N/A（仅 optional 条目可用 N/A）；",
        "> evidence 必须引用稿文原句；找不到证据判 Missing，不臆断。",
        "",
        "| 条目 | 状态 | 稿文证据（原句） | 修复建议 |",
        "| --- | --- | --- | --- |",
    ]
    for it in cl["items"]:
        label = it["label"] + ("（可选）" if it.get("optional") else "")
        lines.append(f"| {it['id']} {label} |  |  |  |")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[ok] 审计脚手架 -> {out_path}")


def finalize(cl, report_path, out_path):
    with open(report_path, encoding="utf-8") as f:
        results = {r["id"]: r for r in json.load(f)}
    counts = {"Reported": 0, "Partial": 0, "Missing": 0, "N/A": 0}
    applicable = 0
    lines = [f"# 审计报告（{cl['name']}）",
             f"- 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
             f"- 依据: {cl['citation']}",
             "",
             "| 条目 | 状态 | 证据 | 修复建议 |", "| --- | --- | --- | --- |"]
    for it in cl["items"]:
        r = results.get(it["id"], {"status": "Missing", "evidence": "未填写", "fix": ""})
        status = r["status"] if r["status"] in VALID else "Missing"
        counts[status] += 1
        if status != "N/A":
            applicable += 1
        evidence = (r.get("evidence") or "").replace("|", "\\|").replace("\n", " ")
        fix = (r.get("fix") or "").replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {it['id']} {it['label']} | {status} | {evidence} | {fix} |")
    total = applicable
    lines += ["", "## 汇总",
              f"- Reported: {counts['Reported']}/{total} ({counts['Reported'] * 100 // max(total,1)}%)",
              f"- Partial: {counts['Partial']}  Missing: {counts['Missing']}  N/A: {counts['N/A']}"]
    if cl.get("condensed"):
        lines.append("- ⚠️ 本清单为摘要版（condensed），投稿前必须对照官方文件逐条核对。")
    priority = [f"{r['id']} {results[r['id']].get('fix', '')}" for r in results.values()
                if r["status"] == "Missing"]
    if priority:
        lines += ["", "## 修复优先级（Missing 条目，影响最优先）"] + [f"- {p}" for p in priority]
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[ok] 审计终稿 -> {out_path}（{counts}）")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--list", action="store_true")
    p.add_argument("--checklist", help="guideline id，逗号分隔可多个")
    p.add_argument("--scaffold", action="store_true")
    p.add_argument("--report", help="AI 已填写的判定 JSON")
    p.add_argument("--out", default=None)
    p.add_argument("--adapted", action="store_true", help="标记为适配版")
    args = p.parse_args()
    if args.list and not args.out:
        args.out = "-"

    reg = load_all()

    if args.list:
        print("已注册完整清单:")
        for gid, cl in reg.items():
            if gid == "_stubs":
                continue
            print(f"  {gid:16s} {len(cl['items']):3d} 条  {cl['name']}")
        print("\n桩（需补全后使用）:")
        for sid, s in reg.get("_stubs", {}).get("stubs", {}).items():
            print(f"  {sid:16s} {s.get('item_count', '?'):>3} 条  {s['name']}")
        return

    if not args.checklist:
        p.error("需要 --checklist 或 --list")
    for gid in args.checklist.split(","):
        gid = gid.strip()
        if gid not in reg or gid == "_stubs":
            if gid in reg.get("_stubs", {}).get("stubs", {}):
                print(f"[err] {gid} 尚为桩（{reg['_stubs']['stubs'][gid]['source']}），请先补全条目再审计",
                      file=sys.stderr)
            else:
                print(f"[err] 未注册清单: {gid}", file=sys.stderr)
            sys.exit(1)
        cl = reg[gid]
        if args.report:
            finalize(cl, args.report, args.out)
        elif args.scaffold:
            scaffold(cl, args.out, adapted=args.adapted)


if __name__ == "__main__":
    main()
