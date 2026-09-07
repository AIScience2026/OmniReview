#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OmniReview — Semantic Scholar 检索脚本（零第三方依赖）

用法:
  python search_semanticscholar.py --query "gaze cues human-robot interaction" \
      --out _working/search/s2_q1.csv

API key（可选但强推荐，避开免费共享池 429）:
  环境变量 SEMANTIC_SCHOLAR_API_KEY / S2_API_KEY / semantic_api_key，
  或 Windows 注册表 HKCU\\Environment（脚本自动兜底读取，setx 后无需重启）。
  有 key 时请求间隔降为 1.1s；无 key 时 3.5s + 429 指数退避。
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

MAX_SAFE = 10000  # fetch-all 模式下单库硬上限，防止粗放 query 失控

FIELDS = ["doi", "title", "authors", "year", "venue", "type", "cited_by",
          "abstract", "oa_url", "source", "query", "retrieved_at"]
API = "https://api.semanticscholar.org/graph/v1/paper/search"
REQ_FIELDS = "externalIds,title,authors,year,venue,publicationTypes,citationCount,abstract,openAccessPdf"
KEY_NAMES = ["SEMANTIC_SCHOLAR_API_KEY", "S2_API_KEY", "S2APIKEY", "semantic_api_key"]


def load_api_key():
    for name in KEY_NAMES:
        val = os.environ.get(name, "").strip()
        if val:
            return val
    if sys.platform == "win32":
        try:
            import winreg
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment")
            for name in KEY_NAMES:
                try:
                    val, _ = winreg.QueryValueEx(k, name)
                    if str(val).strip():
                        return str(val).strip()
                except OSError:
                    continue
        except OSError:
            pass
    return None


API_KEY = load_api_key()
PAGE_DELAY = 1.1 if API_KEY else 3.5  # 有 key 提速，无 key 遵守免费配额


def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            headers = {"User-Agent": "OmniReview/1.0"}
            if API_KEY:
                headers["x-api-key"] = API_KEY
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 10 * (attempt + 1)
                print(f"[warn] 429 限流，等待 {wait}s 重试", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"[warn] HTTP {e.code}: {e.reason}", file=sys.stderr)
            time.sleep(3)
        except Exception as e:
            print(f"[warn] {e}，重试中", file=sys.stderr)
            time.sleep(2 ** attempt * 3)
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--query", required=True)
    p.add_argument("--limit", type=int, default=0,
                   help="每库最多返回条数（每页100）；0=取全部匹配（硬上限 %d）" % MAX_SAFE)
    p.add_argument("--year", default=None, help="如 2015- 或 2015-2025")
    p.add_argument("--out", required=True)
    args = p.parse_args()
    print(f"[info] Semantic Scholar API key: {'已加载' if API_KEY else '未配置（免费池模式，限流高发）'}")

    eff_limit = MAX_SAFE if args.limit == 0 else args.limit
    rows, offset, total_available = [], 0, None
    while len(rows) < eff_limit:
        params = {"query": args.query, "limit": min(100, eff_limit - len(rows)),
                  "offset": offset, "fields": REQ_FIELDS}
        if args.year:
            params["year"] = args.year
        data = fetch(f"{API}?{urllib.parse.urlencode(params)}")
        if not data or not data.get("data"):
            break
        if total_available is None:
            total_available = data.get("total")
        for w in data["data"]:
            ext = w.get("externalIds") or {}
            oa = w.get("openAccessPdf") or {}
            types = w.get("publicationTypes") or []
            rows.append({
                "doi": ext.get("DOI") or "",
                "title": w.get("title") or "",
                "authors": "; ".join(a.get("name", "") for a in w.get("authors") or []),
                "year": w.get("year") or "",
                "venue": w.get("venue") or "",
                "type": "; ".join(types).lower(),
                "cited_by": w.get("citationCount") or 0,
                "abstract": w.get("abstract") or "",
                "oa_url": oa.get("url") or "",
                "source": "semanticscholar",
                "query": args.query,
                "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })
        total = data.get("total") or 0
        offset += len(data["data"])
        if offset >= total or len(data["data"]) == 0:
            break
        time.sleep(PAGE_DELAY)

    with open(args.out, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    capped = args.limit != 0
    print(f"[stats] source=semanticscholar query={args.query!r} retrieved={len(rows)} "
          f"total_available={total_available} capped={str(capped).lower()}")
    print(f"[ok] Semantic Scholar 命中 {len(rows)} 条（数据库真实命中 {total_available} 条）-> {args.out}")


if __name__ == "__main__":
    main()
