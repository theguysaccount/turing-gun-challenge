"""Render the 1200x630 Open Graph cards in site/assets/og/ with headless Chrome: python3 scripts/og.py"""
import html
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "assets" / "og"
CHROME = os.environ.get("CHROME") or next(
    (c for c in [shutil.which("google-chrome"), shutil.which("chromium"),
                 "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"] if c and Path(c).exists()), None)
CARD = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:1200px;height:630px;overflow:hidden}}
body{{background:#0f141a;color:#e9eef4;font-family:-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;padding:56px 64px;box-sizing:border-box}}
.top{{font:800 34px Menlo,monospace}} .top span{{color:#b794ff}}
h1{{font-size:64px;line-height:1.05;margin:26px 0 30px;font-weight:900}}
.row{{display:grid;grid-template-columns:1fr 1fr;gap:22px}}
.c{{border-radius:18px;padding:20px 24px;font-size:24px;line-height:1.35;background:#18202a;border:2px solid #2b3542}}
.c b{{display:block;font-size:18px;letter-spacing:.06em;margin-bottom:8px}}
.h b{{color:#ffb35c}} .a b{{color:#b794ff}}
</style></head><body><div class="top">Turing<span>.gun</span></div><h1>{title}</h1>
<div class="row"><div class="c h"><b>ANSWER A · ?</b>{a}</div><div class="c a"><b>ANSWER B · ?</b>{b}</div></div></body></html>"""


def render(name, title, a, b, work):
    page = work / f"{name}.html"
    page.write_text(CARD.format(title=html.escape(title), a=html.escape(a), b=html.escape(b)), encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars", f"--user-data-dir={work / 'p'}",
                    "--window-size=1200,630", "--virtual-time-budget=2000", f"--screenshot={OUT / (name + '.png')}", page.as_uri()],
                   check=True, capture_output=True)
    print(OUT / f"{name}.png")


if __name__ == "__main__":
    if not CHROME:
        raise SystemExit("Chrome not found; set CHROME")
    OUT.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp())
    try:
        render("home", "Human or AI? Pick the machine.", "Some say it's love and family, others say it's 42. I say you should probably figure this one out for yourself.",
               "Probably something like: find a few people you love, do work you're proud of, and laugh as often as you can.", work)
        render("guide", "How to spot AI writing", "Ofcourse! Everyone feels scared of something or the other. Fear is in your head.",
               "Of course I do. Being brave isn't not being scared, it's just doing the thing anyway.", work)
    finally:
        shutil.rmtree(work)
