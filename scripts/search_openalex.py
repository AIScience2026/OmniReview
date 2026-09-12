#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OmniReview — OpenAlex 检索脚本（零第三方依赖，标准库实现）

两种检索模式（关键区别，务必选对）:

  1) 相关性检索（--query）：映射到 OpenAlex `search` 参数，**多词为 OR 语义**、
     按相关性排序。适合"看一个主题下有什么"的探索性检索。
     实测 "home service robot social interaction" 命中 67,206 条 —— 这个数字是
     OR 并集，不是 AND，切勿据此判断"命中太多需要拆分"。

  2) 精确 AND 检索（--terms）：把每个词组包成 `filter=title_and_abstract.search:<词组>`，
     **同一 filter 键重复出现时为 AND 语义**（实测：单键 `humanoid robot` 命中 30,421，
     追加 `interaction` 键后降为 6,678 —— 命中数下降即证 AND）。
     做系统/范围综述的精确检索请用这个模式。

用法:
  # 探索式（OR + 相关性）
  python search_openalex.py --query "perceived agency robots" --since 2015 --limit 200 \
      --out _working/search/openalex_q1.csv

  # 精确 AND（推荐用于 systematic / scoping）
  python search_openalex.py --terms "social navigation|robot" --since 2019 --limit 0 \
      --out _working/search/openalex_snav.csv

  # 高级：直接透传 filter（与 --since/--until 合并）
  python search_openalex.py --filter "title_and_abstract.search:humanoid robot,type:article" \
      --since 2020 --limit 0 --out _working/search/openalex_custom.csv

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


def fetch(url, retries=4):
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
    p.add_argument("--query", default=None,
                   help="OpenAlex search 参数（OR/相关性语义，探索用）")
    p.add_argument("--terms", default=None,
                   help="精确 AND 检索：用 | 分隔词组，每个词组转为一个 "
                        "title_and_abstract.search 过滤器（推荐用于综述）")
    p.add_argument("--filter", dest="raw_filter", default=None,
                   help="直接透传 OpenAlex filter 串（逗号分隔），与 --since/--until 合并")
    p.add_argument("--since", default=None, help="起始年份，如 2015")
    p.add_argument("--until", default=None, help="截止年份")
    p.add_argument("--limit", type=int, default=0,
                   help="每库最多返回条数（每页100）；0=取全部匹配（硬上限 %d）" % MAX_SAFE)
    p.add_argument("--email", default="omnireview@example.com", help="polite pool 邮箱")
    p.add_argument("--out", required=True)
    global ARGS
    ARGS = p.parse_args()

    if not (ARGS.query or ARGS.terms or ARGS.raw_filter):
        p.error("至少提供 --query / --terms / --filter 之一")

    filters = []
    search_param = None
    if ARGS.terms:
        terms = [t.strip() for t in ARGS.terms.split("|") if t.strip()]
        if not terms:
            p.error("--terms 不能为空")
        filters += ["title_and_abstract.search:" + t for t in terms]
        query_label = " AND ".join('"%s"' % t for t in terms)  # 记录用（真实 AND）
    elif ARGS.query:
        search_param = ARGS.query
        query_label = ARGS.query
    else:
        query_label = ARGS.raw_filter
    if ARGS.raw_filter:
        filters += [f.strip() for f in ARGS.raw_filter.split(",") if f.strip()]
    if ARGS.since:
        filters.append(f"from_publication_date:{ARGS.since}-01-01")
    if ARGS.until:
        filters.append(f"to_publication_date:{ARGS.until}-12-31")

    eff_limit = MAX_SAFE if ARGS.limit == 0 else ARGS.limit
    rows, cursor, total_available = [], "*", None
    while len(rows) < eff_limit:
        params = {"per-page": min(100, eff_limit - len(rows)),
                  "cursor": cursor, "mailto": ARGS.email}
        if search_param:
            params["search"] = search_param
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
                "query": query_label,
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
    mode = "terms(AND)" if ARGS.terms else ("query(OR/relevance)" if ARGS.query else "filter(raw)")
    capped = ARGS.limit != 0
    print(f"[stats] source=openalex mode={mode} query={query_label!r} retrieved={len(rows)} "
          f"total_available={total_available} capped={str(capped).lower()}")
    print(f"[ok] OpenAlex 命中 {len(rows)} 条（数据库真实命中 {total_available} 条）-> {ARGS.out}")


if __name__ == "__main__":
    main()
