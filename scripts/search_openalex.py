#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OmniReview — OpenAlex 检索脚本（零第三方依赖，标准库实现）

用法:
  python search_openalex.py --query "perceived agency robots" --since 2015 --limit 200 \
      --out _working/search/openalex_q1.csv --email you@example.com

输出统一 schema:
  doi,title,authors,year,venue,type,cited_by,abstract,oa_url,source,query,retrieved_at
"""
import argparse
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

FIELDS = ["doi", "title", "authors", "year", "venue", "type", "cited_by",
          "abstract", "oa_url", "source", "query", "retrieved_at"]
API = "https://api.openalex.org/works"
MAX_SAFE = 10000  # fetch-all 模式下单库硬上限，防止粗放 query 失控


def rebuild_abstract(inv_idx):
    """OpenAlex 摘要为倒排索引，重建为可读文本。"""
    if not inv_idx:
        return ""
    positions = []
    for word, idxs in inv_idx.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return " ".join(w for _, w in positions)


def parse_authors(authorships):
    return "; ".join(a.get("author", {}).get("display_name", "") for a in authorships or [])


def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "OmniReview/1.0 (mailto:%s)" % ARGS.email})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # 网络异常/限流：指数退避
            wait = 2 ** attempt * 3
            print(f"[warn] 请求失败({e})，{wait}s 后重试 {attempt + 1}/{retries}", file=sys.stderr)
            time.sleep(wait)
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--query", required=True)
    p.add_argument("--since", default=None, help="起始年份，如 2015")
    p.add_argument("--until", default=None, help="截止年份")
    p.add_argument("--limit", type=int, default=0,
                   help="每库最多返回条数（每页100）；0=取全部匹配（硬上限 %d）" % MAX_SAFE)
    p.add_argument("--email", default="omnireview@example.com", help="polite pool 邮箱")
    p.add_argument("--out", required=True)
    global ARGS
    ARGS = p.parse_args()

    filters = []
    if ARGS.since:
        filters.append(f"from_publication_date:{ARGS.since}-01-01")
    if ARGS.until:
        filters.append(f"to_publication_date:{ARGS.until}-12-31")

    eff_limit = MAX_SAFE if ARGS.limit == 0 else ARGS.limit
    rows, cursor, total_available = [], "*", None
    while len(rows) < eff_limit:
        params = {"search": ARGS.query, "per-page": min(100, eff_limit - len(rows)),
                  "cursor": cursor, "mailto": ARGS.email}
        if filters:
            params["filter"] = ",".join(filters)
        url = f"{API}?{urllib.parse.urlencode(params)}"
        data = fetch(url)
        if not data or not data.get("results"):
            break
        total_available = data.get("meta", {}).get("count")
        for w in data["results"]:
            oa = w.get("open_access") or {}
            rows.append({
                "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
                "title": w.get("display_name") or "",
                "authors": parse_authors(w.get("authorships")),
                "year": w.get("publication_year") or "",
                "venue": (w.get("primary_location") or {}).get("source", {}) or {},
                "type": w.get("type") or "",
                "cited_by": w.get("cited_by_count") or 0,
                "abstract": rebuild_abstract(w.get("abstract_inverted_index")),
                "oa_url": oa.get("oa_url") or "",
                "source": "openalex",
                "query": ARGS.query,
                "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })
            rows[-1]["venue"] = (rows[-1]["venue"] or {}).get("display_name", "")
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break
        time.sleep(0.15)

    with open(ARGS.out, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    capped = ARGS.limit != 0
    print(f"[stats] source=openalex query={ARGS.query!r} retrieved={len(rows)} "
          f"total_available={total_available} capped={str(capped).lower()}")
    print(f"[ok] OpenAlex 命中 {len(rows)} 条（数据库真实命中 {total_available} 条）-> {ARGS.out}")


if __name__ == "__main__":
    main()
