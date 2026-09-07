#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OmniReview — DeepXiv 检索脚本（依赖 deepxiv-sdk，见下方安装说明）

DeepXiv（智源研究院开源）：arXiv 全量 + PMC，混合检索（BM25+向量），
每日增量更新。免费令牌 1000 请求/天：https://data.rag.ac.cn/register

安装（隔离 venv）:
  python -m venv <env> && <env>/Scripts/pip install deepxiv-sdk

令牌配置（三选一，脚本自动探测）:
  1. 环境变量  DEEPXIV_TOKEN=xxx
  2. 当前目录 .env 文件一行:  DEEPXIV_TOKEN=xxx
  3. 家目录    ~/.env   一行:  DEEPXIV_TOKEN=xxx

用法:
  python search_deepxiv.py --query "perceived agency robot" --since 2023 \
      --limit 100 --out _working/search/deepxiv_q1.csv

输出统一 schema（doi 统一为 10.48550/arXiv.<id>，可与三库直接去重合并）:
  doi,title,authors,year,venue,type,cited_by,abstract,oa_url,source,query,retrieved_at
"""
import argparse
import csv
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

MAX_SAFE = 10000  # fetch-all 模式下单库硬上限，防止粗放 query 失控
FIELDS = ["doi", "title", "authors", "year", "venue", "type", "cited_by",
          "abstract", "oa_url", "source", "query", "retrieved_at"]


def load_token():
    tok = os.environ.get("DEEPXIV_TOKEN", "").strip()
    if tok:
        return tok
    for env_file in (Path.cwd() / ".env", Path.home() / ".env"):
        try:
            if env_file.exists():
                for line in env_file.read_text(encoding="utf-8").splitlines():
                    # BOM 容错：PS5.1 等工具写 UTF-8 会在文件头加 U+FEFF，
                    # 使首行键名变成 \ufeffDEEPXIV_TOKEN，startswith 会失配
                    line = line.lstrip("\ufeff")
                    if line.strip().startswith("DEEPXIV_TOKEN="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except OSError:
            pass
    # Windows 兜底：父进程可能早于 setx 启动，读不到新环境变量，直接查注册表
    if sys.platform == "win32":
        try:
            import winreg
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment")
            val, _ = winreg.QueryValueEx(k, "DEEPXIV_TOKEN")
            return str(val).strip()
        except OSError:
            pass
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--query", required=True)
    p.add_argument("--since", default=None, help="起始年份，如 2023")
    p.add_argument("--until", default=None, help="截止年份")
    p.add_argument("--limit", type=int, default=0,
                   help="每库最多返回条数；0=取全部匹配（硬上限 %d）" % MAX_SAFE)
    p.add_argument("--source", default="arxiv", help="检索源：arxiv（默认）或 pmc")
    p.add_argument("--out", required=True)
    args = p.parse_args()

    try:
        from deepxiv_sdk import Reader
    except ImportError:
        print("[err] 未安装 deepxiv-sdk。请在隔离 venv 中执行: pip install deepxiv-sdk",
              file=sys.stderr)
        sys.exit(2)

    token = load_token()
    if not token:
        print("[err] 未找到 DeepXiv 令牌。免费注册: https://data.rag.ac.cn/register\n"
              "      配置方式: 设置环境变量 DEEPXIV_TOKEN，或在 ~/.env 写一行 "
              "DEEPXIV_TOKEN=你的令牌", file=sys.stderr)
        sys.exit(2)

    reader = Reader(token=token)
    eff_limit = MAX_SAFE if args.limit == 0 else args.limit
    kwargs = {"size": min(eff_limit, 100), "source": args.source}
    if args.since:
        kwargs["date_from"] = f"{args.since}-01-01"
    if args.until:
        kwargs["date_to"] = f"{args.until}-12-31"

    try:
        res = reader.search(args.query, **kwargs)
    except Exception as e:
        print(f"[err] DeepXiv 检索失败: {type(e).__name__}: {str(e)[:200]}", file=sys.stderr)
        sys.exit(1)

    results = res.get("result", []) if isinstance(res, dict) else (res or [])
    rows = []
    total_available = None  # DeepXiv 检索接口不直接返回命中总数，仅能报告实际取回数
    for item in results:
        arxiv_id = (item.get("arxiv_id") or item.get("id") or "").strip()
        pub = item.get("date") or item.get("publish_at") or item.get("published") or ""
        year = str(pub)[:4] if pub else ""
        rows.append({
            "doi": f"10.48550/arXiv.{arxiv_id}" if arxiv_id else "",
            "title": item.get("title") or "",
            "authors": "; ".join(
                (a.get("name") if isinstance(a, dict) else str(a)) or ""
                for a in (item.get("authors") or [])),
            "year": year,
            "venue": item.get("venue") or ("arXiv" + (f" ({','.join(item.get('categories') or [])})"
                                                       if item.get("categories") else "")),
            "type": "preprint",
            "cited_by": item.get("citation_count") or item.get("citations") or 0,
            "abstract": item.get("abstract") or "",
            "oa_url": item.get("url") or (f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""),
            "source": "deepxiv",
            "query": args.query,
            "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })

    # 按年份过滤兜底（API 不支持时间过滤时）
    if args.since:
        rows = [r for r in rows if r["year"] >= args.since]
    if args.until:
        rows = [r for r in rows if r["year"] <= args.until]
    rows = rows[:eff_limit]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    capped = args.limit != 0
    print(f"[stats] source=deepxiv query={args.query!r} retrieved={len(rows)} "
          f"total_available={total_available} capped={str(capped).lower()}")
    print(f"[ok] DeepXiv 命中 {len(rows)} 条 -> {out}")


if __name__ == "__main__":
    main()
