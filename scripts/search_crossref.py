#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OmniReview — Crossref 检索脚本（零第三方依赖）

用法:
  python search_crossref.py --query "perceived autonomy HRI" --since 2015 \
      --out _working/search/crossref_q1.csv --email you@example.com

说明: Crossref 摘要仅部分出版商提供（JATS XML，脚本剥离标签）。
"""
import argparse
import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

FIELDS = ["doi", "title", "authors", "year", "venue", "type", "cited_by",
          "abstract", "oa_url", "source", "query", "retrieved_at"]
API = "https://api.crossref.org/works"
TAG = re.compile(r"<[^>]+>")


def strip_jats(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", TAG.sub("", text)).strip()


def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "OmniReview/1.0 (mailto:%s)" % ARGS.email})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            print(f"[warn] {e}，重试 {attempt + 1}/{retries}", file=sys.stderr)
            time.sleep(2 ** attempt * 3)
    return None


def pick_year(item):
    for key in ("published-print", "published-online", "issued"):
        parts = (item.get(key) or {}).get("date-parts") or []
        if parts and parts[0]:
            return parts[0][0]
    return ""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--query", required=True)
    p.add_argument("--since", default=None)
    p.add_argument("--rows", type=int, default=200)
    p.add_argument("--email", default="omnireview@example.com")
    p.add_argument("--out", required=True)
    global ARGS
    ARGS = p.parse_args()

    rows = []
    offset = 0
    while offset < ARGS.rows:
        params = {"query": ARGS.query, "rows": min(100, ARGS.rows - offset),
                  "offset": offset, "mailto": ARGS.email}
        if ARGS.since:
            params["filter"] = f"from-pub-date:{ARGS.since}-01-01"
        data = fetch(f"{API}?{urllib.parse.urlencode(params)}")
        if not data:
            break
        items = (data.get("message") or {}).get("items") or []
        if not items:
            break
        for it in items:
            titles = it.get("title") or [""]
            links = it.get("link") or []
            oa_url = ""
            for l in links:
                if l.get("content-type") == "application/pdf":
                    oa_url = l.get("URL", "")
                    break
            rows.append({
                "doi": it.get("DOI") or "",
                "title": strip_jats(titles[0] if titles else ""),
                "authors": "; ".join(
                    f"{a.get('given', '')} {a.get('family', '')}".strip()
                    for a in it.get("author") or []),
                "year": pick_year(it),
                "venue": strip_jats((it.get("container-title") or [""])[0]),
                "type": it.get("type") or "",
                "cited_by": it.get("is-referenced-by-count") or 0,
                "abstract": strip_jats(it.get("abstract") or ""),
                "oa_url": oa_url,
                "source": "crossref",
                "query": ARGS.query,
                "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })
        offset += len(items)
        time.sleep(0.5)

    with open(ARGS.out, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[ok] Crossref 命中 {len(rows)} 条 -> {ARGS.out}")


if __name__ == "__main__":
    main()
