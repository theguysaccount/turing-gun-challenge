"""Monthly: re-verify the human answers against their source and check the license and links.

    python3 scripts/check_sources.py

Downloads databricks-dolly-15k (about 13 MB) from Hugging Face, checks that its dataset card still says
CC BY-SA 3.0, that every human answer and prompt in data/rounds.json still matches its row word for
word, and that the source and license links resolve. Exits 1 on a mismatch or a license change; a
download that fails is reported as a failure too, since nothing could be verified.
"""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "TuringGunQuiz/1.0 (+https://github.com/theguysaccount/turing-gun-challenge)"
CARD = "https://huggingface.co/datasets/databricks/databricks-dolly-15k/resolve/main/README.md"


def get(url, timeout=120):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout) as r:
        return r.read().decode("utf-8")


def main():
    data = json.loads((ROOT / "data" / "rounds.json").read_text(encoding="utf-8"))
    problems = []
    card = get(CARD)
    if "license: cc-by-sa-3.0" not in card:
        problems.append("the dataset card no longer says license: cc-by-sa-3.0")
    rows = [json.loads(line) for line in get(data["source"]["file"], timeout=300).splitlines() if line.strip()]
    for it in data["items"]:
        row = rows[it["dolly_index"]] if it["dolly_index"] < len(rows) else None
        if not row or row["response"].strip() != it["human"] or row["instruction"].strip() != it["prompt"]:
            problems.append(f"{it['id']}: no longer matches Dolly row {it['dolly_index']}")
    for url in (data["source"]["url"], data["source"]["license_url"]):
        try:
            get(url, timeout=60)
        except Exception as e:
            problems.append(f"link {url}: {e}")
    print(f"{len(rows)} Dolly rows; {len(data['items'])} rounds checked")
    for p in problems:
        print(f"::error::{p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
