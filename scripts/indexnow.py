#!/usr/bin/env python3
"""Notify IndexNow (Bing, Yandex, Seznam, Naver, Yep) about changed pages.

Usage:
  indexnow.py <base-sha> <head-sha>   submit pages changed between two commits
  indexnow.py --all                   submit every page in sitemap.xml

The key is the <32 hex>.txt file at the site root; IndexNow fetches it to verify ownership.
"""
import glob
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

HOST = "db9v12.co.uk"
SITE = f"https://{HOST}/"
ENDPOINT = "https://api.indexnow.org/indexnow"
SKIP = {"db9_diagnostic_summary_redacted.html"}   # canonical points at misfire-diagnostic.html
DATA_PAGES = {"mot-history.json": "mot-history.html"}  # data files that change a page's content


def key():
    files = [f for f in glob.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}\.txt", f)]
    if len(files) != 1:
        sys.exit(f"expected exactly one IndexNow key file, found {files}")
    return files[0][:-4]


def url_for(path):
    return SITE if path == "index.html" else SITE + path


def changed_urls(base, head):
    out = subprocess.run(["git", "diff", "--name-only", "--diff-filter=AM", base, head],
                         check=True, capture_output=True, text=True).stdout.split()
    pages = set()
    for f in out:
        f = DATA_PAGES.get(f, f)
        if "/" not in f and f.endswith(".html") and f not in SKIP:
            pages.add(f)
    return sorted(url_for(p) for p in pages)


def sitemap_urls():
    return re.findall(r"<loc>([^<]+)</loc>", open("sitemap.xml").read())


def submit(urls):
    if not urls:
        print("No page changes to submit.")
        return
    k = key()
    body = json.dumps({"host": HOST, "key": k, "keyLocation": f"{SITE}{k}.txt", "urlList": urls}).encode()
    req = urllib.request.Request(ENDPOINT, data=body, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"IndexNow {r.status}: submitted {len(urls)} URL(s)")
    except urllib.error.HTTPError as e:
        sys.exit(f"IndexNow rejected the submission: HTTP {e.code} {e.read().decode(errors='replace')[:300]}")
    for u in urls:
        print("  " + u)


if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    if sys.argv[1:] == ["--all"]:
        submit(sitemap_urls())
    elif len(sys.argv) == 3:
        submit(changed_urls(sys.argv[1], sys.argv[2]))
    else:
        sys.exit(__doc__)
