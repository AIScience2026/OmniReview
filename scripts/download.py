#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OmniReview — Tier 2 PDF 下载调度器（零第三方依赖；外部工具全部可选）

调度链（自动降级）:
  1. scansci-pdf CLI（若已安装）—— 20+ 源竞速，含付费墙通道
  2. auto-paper-harvester CLI（若已安装）
  3. 内置兜底: OpenAlex oa_url / Unpaywall API / arXiv DOI 直映

用法:
  python download.py --included _working/screening/included.csv \
      --merged _working/merged/merged_dedup.csv --out _working/pdfs/ --email you@example.com

产出: pdfs/{FirstAuthor}_{Year}_{TitleShort}_{DOItail}.pdf
      pdfs/unavailable.csv  下载失败清单（供人工走 ILL/机构通道）
"""
import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request

FIELDS = ["doi", "title", "authors", "year", "reason_unavailable"]
UA_STR = "OmniReview/1.0 (mailto:%s)"


def _headers(email):
    return {"User-Agent": UA_STR % email}


def safe_name(row):
    first = (row.get("authors") or "Unknown").split(";")[0].split()[-1] if row.get("authors") else "Unknown"
    first = re.sub(r"[^\w\u4e00-\u9fff]", "", first) or "Unknown"
    year = str(row.get("year") or "NA")
    words = re.findall(r"[\w\u4e00-\u9fff]+", row.get("title") or "")[:6]
    tail = re.sub(r"[^\w]", "", row.get("doi") or "")[-8:]
    return f"{first}_{year}_{'_'.join(words) or 'untitled'}_{tail}.pdf"


def try_scansci(doi, out_dir):
    if not shutil.which("scansci-pdf"):
        return None
    try:
        r = subprocess.run(["scansci-pdf", "get", doi], capture_output=True,
                           text=True, timeout=180)
        if r.returncode == 0:
            # scansci 默认输出 ~/.scansci-pdf/papers，查找最近下载的同 doi 文件
            home_pdf_dir = os.path.join(os.path.expanduser("~"), ".scansci-pdf", "papers")
            if os.path.isdir(home_pdf_dir):
                cand = [os.path.join(home_pdf_dir, f) for f in os.listdir(home_pdf_dir)]
                cand = [c for c in cand if c.endswith(".pdf")]
                if cand:
                    return max(cand, key=os.path.getmtime)
        return None
    except Exception:
        return None


def try_harvester(doi, out_dir):
    if not shutil.which("auto-paper-download") and not shutil.which("paper-download"):
        return None
    try:
        r = subprocess.run(["auto-paper-download", "--doi", doi, "--output-dir", out_dir],
                           capture_output=True, text=True, timeout=180)
        if r.returncode == 0:
            for f in os.listdir(out_dir):
                if f.endswith(".pdf") and re.sub(r"[^\w]", "", doi)[-8:] in re.sub(r"[^\w]", "", f):
                    return os.path.join(out_dir, f)
        return None
    except Exception:
        return None


def try_arxiv(doi):
    """arXiv DOI (10.48550/arXiv.*) 直映为 PDF 链接。"""
    m = re.match(r"(?i)^10\.48550/arxiv\.(.+)$", doi.strip())
    if m:
        return f"https://arxiv.org/pdf/{m.group(1)}"
    return ""


def try_unpaywall(doi, email):
    try:
        url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={email}"
        req = urllib.request.Request(url, headers=_headers(email))
        with urllib.request.urlopen(req, timeout=20) as r:
            import json
            data = json.loads(r.read().decode("utf-8"))
        loc = data.get("best_oa_location") or {}
        return loc.get("url_for_pdf") or loc.get("url") or ""
    except Exception:
        return ""


def try_oa_url(row):
    return (row.get("oa_url") or "").strip()


def download(url, dest, email):
    try:
        req = urllib.request.Request(url, headers=_headers(email))
        with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
            head = r.read(1024)
            if not head.startswith(b"%PDF"):
                return False
            f.write(head)
            while True:
                chunk = r.read(64 * 1024)
                if not chunk:
                    break
                f.write(chunk)
        return os.path.getsize(dest) > 10240  # ≥10KB 视为有效 PDF
    except Exception as e:
        print(f"[warn] 下载异常 {url}: {type(e).__name__} {e}", file=sys.stderr)
        if os.path.exists(dest):
            os.remove(dest)
        return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--included", required=True, help="筛选后的 included.csv")
    p.add_argument("--merged", required=True, help="merged_dedup.csv（取 oa_url）")
    p.add_argument("--out", default="pdfs/")
    p.add_argument("--email", default="omnireview@example.com")
    p.add_argument("--delay", type=float, default=3.0, help="请求间隔秒")
    args = p.parse_args()

    os.makedirs(args.out, exist_ok=True)
    oa_index = {}
    with open(args.merged, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row.get("doi"):
                oa_index[row["doi"].strip().lower()] = row

    missing = []
    ok = 0
    with open(args.included, newline="", encoding="utf-8-sig") as f:
        included = [r for r in csv.DictReader(f) if (r.get("doi") or "").strip()]

    print(f"[info] 待下载 {len(included)} 篇；链路: scansci-pdf -> harvester -> 内置OA兜底")
    for i, row in enumerate(included, 1):
        doi = row["doi"].strip().lower()
        dest = os.path.join(args.out, safe_name(row))
        if os.path.exists(dest):
            ok += 1
            continue
        src_path = try_scansci(doi, args.out)
        if not src_path:
            src_path = try_harvester(doi, args.out)
        if src_path and shutil.copy(src_path, dest):
            ok += 1
            print(f"[{i}/{len(included)}] ok (外部工具): {os.path.basename(dest)}")
            time.sleep(args.delay)
            continue
        url = try_arxiv(doi) or try_oa_url(oa_index.get(doi, {})) or try_unpaywall(doi, args.email)
        if url and download(url, dest, args.email):
            ok += 1
            print(f"[{i}/{len(included)}] ok (OA兜底): {os.path.basename(dest)}")
        else:
            missing.append({"doi": doi, "title": row.get("title", ""),
                            "authors": row.get("authors", ""), "year": row.get("year", ""),
                            "reason_unavailable": "no OA copy / all channels failed"})
            print(f"[{i}/{len(included)}] 不可得: {doi}")
        time.sleep(args.delay)

    if missing:
        with open(os.path.join(args.out, "unavailable.csv"), "w", newline="",
                  encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(missing)

    print(f"[done] 成功 {ok}/{len(included)}；未获取 {len(missing)}（清单: pdfs/unavailable.csv，可走机构通道/ILL）")


if __name__ == "__main__":
    main()
