#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OmniReview — Crossref 检索脚本（零第三方依赖）

⚠️ Crossref 的正确用法（2026-09-12 实测结论，务必读）:

  1) Crossref 是 **DOI 注册库**，不是全文/主题索引。`query` / `query.bibliographic`
     都是**模糊相关性**匹配：实测 `query.bibliographic="social navigation robot"`
     返回 total-results **1,822,058** —— 这个数字毫无筛选意义，不能当命中数用。
  2) Crossref 的摘要由**出版商自愿**随 DOI 提交（JATS XML）。付费墙期刊常常**不提交摘要**，
     所以 Crossref 在"高质量期刊摘要"上并不比 OpenAlex 强（OpenAlex 已 ingest Crossref
     元数据，并额外补充 MAG/PubMed 等来源）。
  3) 因此 Crossref 最有价值的用法是 **按期刊枚举（venue sweep）**：
     `/journals/{ISSN}/works` 精确取某刊全部作品，再用 `--terms` 在**本地做精确 AND 过滤**，
     从而"保证旗舰期刊不漏"。这才是"用上 Crossref"的正解。

用法:
  # A. 主题式（模糊，谨慎使用；结果首条即可能离题）
  python search_crossref.py --query "perceived autonomy HRI" --since 2019 --limit 120 \
      --out _working/search/crossref_q1.csv

  # B. 期刊枚举 + 本地精确 AND（推荐，用于补齐旗舰期刊覆盖）
  python search_crossref.py --issn "2573-9522,1875-4791" --terms "robot|trust" \
      --since 2019 --max-scan 3000 --out _working/search/crossref_journals.csv

  # C. 期刊枚举，不做主题过滤（取某刊 2019 以来全部作品）
  python search_crossref.py --issn "2470-9476" --since 2019 --limit 0 \
      --out _working/search/crossref_scibrob.csv

说明: 摘要仅部分出版商提供（JATS XML 已剥离标签）；缺失属正常，不代表该刊无价值。
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

MAX_SAFE = 10000
MAX_SCAN_SAFE = 20000
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
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:  # 未知 ISSN / 无该刊作品
                return {"_404": True}
            print(f"[warn] {e}，重试 {attempt + 1}/{retries}", file=sys.stderr)
            time.sleep(2 ** attempt * 3)
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


def to_row(it, query_label):
    titles = it.get("title") or [""]
    links = it.get("link") or []
    oa_url = next((l.get("URL", "") for l in links if l.get("content-type") == "application/pdf"), "")
    return {
        "doi": it.get("DOI") or "",
        "title": strip_jats(titles[0] if titles else ""),
        "authors": "; ".join(f"{a.get('given', '')} {a.get('family', '')}".strip()
                             for a in it.get("author") or []),
        "year": pick_year(it),
        "venue": strip_jats((it.get("container-title") or [""])[0]),
        "type": it.get("type") or "",
        "cited_by": it.get("is-referenced-by-count") or 0,
        "abstract": strip_jats(it.get("abstract") or ""),
        "oa_url": oa_url,
        "source": "crossref",
        "query": query_label,
        "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--query", default=None, help="模糊主题检索（不推荐用于精确综述）")
    p.add_argument("--issn", default=None, help="期刊枚举：逗号分隔 ISSN（如 2573-9522,1875-4791）")
    p.add_argument("--terms", default=None,
                   help="本地精确 AND 过滤：用 | 分隔词组；仅保留 title+abstract 同时含全部词组的记录")
    p.add_argument("--max-scan", type=int, default=MAX_SCAN_SAFE,
                   help="本地过滤时最多扫描的记录数（默认 %d）" % MAX_SCAN_SAFE)
    p.add_argument("--since", default=None)
    p.add_argument("--until", default=None)
    p.add_argument("--limit", type=int, default=0,
                   help="每库最多返回条数（每页100）；0=取全部匹配（硬上限 %d）" % MAX_SAFE)
    p.add_argument("--email", default="omnireview@example.com")
    p.add_argument("--out", required=True)
    global ARGS
    ARGS = p.parse_args()

    if not (ARGS.query or ARGS.issn):
        p.error("至少提供 --query 或 --issn")
    terms = [t.strip().lower() for t in (ARGS.terms or "").split("|") if t.strip()]
    eff_limit = MAX_SAFE if ARGS.limit == 0 else ARGS.limit
    scan_cap = ARGS.max_scan if terms else (eff_limit if ARGS.issn else eff_limit)

    filters = []
    if ARGS.since:
        filters.append(f"from-pub-date:{ARGS.since}-01-01")
    if ARGS.until:
        filters.append(f"until-pub-date:{ARGS.until}-12-31")
    filt = ",".join(filters)

    bases = []
    if ARGS.issn:
        for issn in [x.strip() for x in ARGS.issn.split(",") if x.strip()]:
            bases.append(f"https://api.crossref.org/journals/{issn}/works")
        query_label = ("issn:" + ARGS.issn) + ((" AND " + ",".join(terms)) if terms else "")
    else:
        bases.append(API)
        query_label = ARGS.query + ((" AND " + ",".join(terms)) if terms else "")

    rows, scanned, total_available = [], 0, None
    for base in bases:
        offset = 0
        while len(rows) < eff_limit and scanned < scan_cap:
            params = {"rows": min(100, eff_limit - len(rows)), "offset": offset,
                      "mailto": ARGS.email}
            if filt:
                params["filter"] = filt
            if base == API:
                params["query.bibliographic"] = ARGS.query
            data = fetch(f"{base}?{urllib.parse.urlencode(params)}")
            if not data:
                break
            if data.get("_404"):
                print(f"[warn] ISSN 无作品或不存在: {base}", file=sys.stderr)
                break
            msg = data.get("message") or {}
            if total_available is None:
                total_available = msg.get("total-results")
            items = msg.get("items") or []
            if not items:
                break
            for it in items:
                scanned += 1
                row = to_row(it, query_label)
                if terms:
                    blob = (row["title"] + " " + row["abstract"]).lower()
                    if not all(t in blob for t in terms):
                        continue
                rows.append(row)
                if len(rows) >= eff_limit:
                    break
            offset += len(items)
            if len(items) < 100:
                break
            time.sleep(0.5)

    with open(ARGS.out, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    capped = ARGS.limit != 0
    print(f"[stats] source=crossref mode={'issn-sweep' if ARGS.issn else 'query'} "
          f"query={query_label!r} scanned={scanned} retrieved={len(rows)} "
          f"total_available={total_available} capped={str(capped).lower()}")
    print(f"[ok] Crossref 命中 {len(rows)} 条（扫描 {scanned} 条，数据库真实命中 {total_available} 条）-> {ARGS.out}")


if __name__ == "__main__":
    main()
