"""Weekly health check of the live site: python3 scripts/check_live.py https://theguysaccount.github.io/turing-gun-challenge

Every sitemap page answers 200 with its own canonical, and the live rounds equal data/rounds.json.
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "TuringGunHealthCheck/1.0 (+https://github.com/theguysaccount/turing-gun-challenge)"


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30) as r:
        return r.status, r.read().decode("utf-8", errors="replace")


def main(base):
    base = base.rstrip("/")
    problems = []
    urls = re.findall(r"<loc>([^<]+)</loc>", get(f"{base}/sitemap.xml")[1])
    for u in urls:
        try:
            status, page = get(u)
            canon = re.search(r'<link rel="canonical" href="([^"]+)"', page)
            if status != 200 or not canon or canon.group(1) != u:
                problems.append(f"{u}: status {status}")
        except Exception as e:
            problems.append(f"{u}: {e}")
    try:
        live = json.loads(get(f"{base}/data/rounds.json")[1])
        if live != json.loads((ROOT / "data" / "rounds.json").read_text(encoding="utf-8")):
            problems.append("the live rounds differ from data/rounds.json (a deploy failed?)")
    except Exception as e:
        problems.append(f"rounds: {e}")
    print(f"checked {len(urls)} pages")
    for p in problems:
        print(f"::error::{p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
