"""Build the Turing.gun static site into dist/. Standard library only (Python 3.9+).

    python3 pipeline/build.py [--out dist]

Optional environment (GitHub repository variables in CI; see OPERATIONS.md):
    SITE_URL         canonical origin + path, no trailing slash (default: the GitHub Pages URL)
    GOATCOUNTER_URL  e.g. https://turinggun.goatcounter.com/count -> cookieless analytics on
    SPONSOR_URL      sponsor link shown under results (with SPONSOR_LABEL), e.g. a prize-round sponsor
    BUILD_DATE       YYYY-MM-DD, to reproduce a build
"""
import argparse
import datetime as dt
import hashlib
import html
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SITE_URL = "https://theguysaccount.github.io/turing-gun-challenge"
REPO_URL = "https://github.com/theguysaccount/turing-gun-challenge"
INDEXNOW_KEY = (ROOT / "site" / "indexnow-key.txt").read_text().strip()
BRAND = "Turing.gun"
e = html.escape


def attr(s):
    return html.escape(str(s), quote=True)


def paras(t):
    return "".join(f"<p>{e(line)}</p>" for line in t.split("\n"))


class Site:
    def __init__(self, out, today):
        self.out, self.today = out, today
        self.site_url = os.environ.get("SITE_URL", DEFAULT_SITE_URL).rstrip("/")
        self.goatcounter = os.environ.get("GOATCOUNTER_URL", "").strip()
        self.sponsor_url = os.environ.get("SPONSOR_URL", "").strip()
        self.sponsor_label = os.environ.get("SPONSOR_LABEL", "").strip()
        self.data = json.loads((ROOT / "data" / "rounds.json").read_text(encoding="utf-8"))
        self.items = self.data["items"]
        self.pages = []
        h = hashlib.sha1()
        for p in sorted((ROOT / "site" / "assets").rglob("*")):
            if p.is_file() and "og" not in p.parts:
                h.update(p.name.encode() + p.read_bytes())
        h.update((ROOT / "data" / "rounds.json").read_bytes())
        self.ver = h.hexdigest()[:10]

    def url(self, path):
        return f"{self.site_url}/{path}"

    def write(self, path, text):
        f = self.out / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")

    def layout(self, path, title, description, body, *, og="home", jsonld=None, noindex=False, current="", root=None, app=False):
        if root is None:
            depth = path.count("/")
            root = "../" * depth if depth else "./"
        here = ' aria-current="page"'
        nav = "".join(f'<a href="{root}{p}"{here if p == current else ""}>{t}</a>' for p, t in
                      [("", "Play"), ("how-to-spot-ai-writing/", "How to spot AI writing"), ("sources/", "Sources")])
        ld = "".join('<script type="application/ld+json">%s</script>\n' % json.dumps(b, ensure_ascii=False).replace("</", "<\\/")
                     for b in (jsonld or []))
        scripts = ""
        if app:
            cfg = json.dumps({"root": root, "siteUrl": self.site_url, "sponsorUrl": self.sponsor_url, "sponsorLabel": self.sponsor_label})
            rounds = json.dumps(self.data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
            scripts = (f'<script type="application/json" id="site-config">{cfg}</script>\n'
                       f'<script type="application/json" id="rounds">{rounds}</script>\n'
                       f'<script type="module" src="{root}assets/app.js?v={self.ver}"></script>\n')
        gc = (f'<script data-goatcounter="{attr(self.goatcounter)}" async src="https://gc.zgo.at/count.js"></script>\n'
              if self.goatcounter else "")
        privacy = ("Visits are counted with GoatCounter (no cookies, no personal data). " if self.goatcounter else "") + \
            "Your guesses stay in your browser. Nothing is stored."
        return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{attr(description)}">
<link rel="canonical" href="{self.url(path)}">
{'<meta name="robots" content="noindex">' if noindex else ''}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{attr(title)}">
<meta property="og:description" content="{attr(description)}">
<meta property="og:url" content="{self.url(path)}">
<meta property="og:image" content="{self.site_url}/assets/og/{og}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#121a24">
<link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{root}assets/site.css?v={self.ver}">
{ld}{scripts}{gc}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head"><div class="wrap">
<a class="logo" href="{root}">Turing<span>.gun</span></a>
<nav class="nav" aria-label="Main">{nav}</nav>
</div></header>
<main id="main" class="wrap">
{body}
</main>
<footer class="site-foot"><div class="wrap">
<nav aria-label="Footer"><a href="{root}">Play: human or AI?</a><a href="{root}how-to-spot-ai-writing/">How to spot AI writing</a><a href="{root}sources/">Sources, licenses and method</a><a href="{REPO_URL}">Source code</a></nav>
<p>{privacy}</p>
<p>Human answers: <a href="{self.data['source']['url']}">databricks-dolly-15k</a> by Databricks employees, {e(self.data['source']['license'])}. AI answers: {e(self.data['ai']['model'])}. Game data shared under {e(self.data['source']['license'])}.</p>
</div></footer>
</body>
</html>
"""

    def home(self):
        body = f"""
<section>
<h1>Human or AI? Can you spot the machine?</h1>
<p class="lede">Ten questions, two answers each. One was written by a person, one by an AI told to sound like a person. Pick the AI. Most people do about as well as a coin flip.</p>
<p id="share-banner" class="banner" role="status" hidden></p>
<div data-game>
<div data-intro>
<div class="btn-row"><button class="btn" type="button" data-start>Start the game</button></div>
<p class="note">About three minutes. Free, no sign-up, nothing stored. This week's game is the same for everyone, so scores compare fairly.</p>
</div>
<div data-stage hidden></div>
</div>
<noscript><p>The game needs JavaScript. You can still read <a href="how-to-spot-ai-writing/">how to spot AI writing</a>.</p></noscript>
<h2>Where the answers come from</h2>
<p>Every human answer is real and quoted word for word from <a href="{self.data['source']['url']}">databricks-dolly-15k</a>, an open dataset written by thousands of Databricks employees who were told not to use AI. Every AI answer was written by {e(self.data['ai']['model'])}, asked to answer the same question the way a person would, at about the same length. <a href="sources/">Full sources and method →</a></p>
<h2>Why play?</h2>
<p>AI writing is everywhere now: reviews, messages, homework, posts. Seeing how often it passes for human is the fastest way to calibrate how much to trust what you read. After each round you see what gave the AI away, or why it didn't.</p>
</section>
"""
        ld = [{"@context": "https://schema.org", "@type": "Quiz", "name": "Human or AI? Spot the AI-written answer", "url": self.site_url + "/",
               "isAccessibleForFree": True, "inLanguage": "en", "educationalUse": "self-assessment",
               "about": {"@type": "Thing", "name": "AI-generated text detection"},
               "description": "Ten rounds: pick which of two answers was written by an AI."}]
        self.write("index.html", self.layout("", "Human or AI? A free quiz: can you spot AI writing? | Turing.gun",
                                             "Ten rounds of real human answers beside AI ones. Can you tell which is which? Free, no sign-up, scores you can share.",
                                             body, jsonld=ld, current="", app=True))
        self.pages.append("")

    def guide(self):
        root = "../"
        examples = [i for i in self.items if i["id"] in ("d3693", "d13517", "d12992", "d1303")]
        ex_html = "".join(
            f'<h3>“{e(it["prompt"])}”</h3><div class="pair"><div class="h"><b>Human</b>{paras(it["human"])}</div>'
            f'<div class="a"><b>AI</b>{paras(it["ai"])}</div></div><p class="note">{e(it["tell"])}</p>' for it in examples)
        body = f"""
<h1>How to spot AI writing (and why it's getting harder)</h1>
<p class="lede">There's no single giveaway. AI text has habits, and so do people, and in short answers they overlap a lot. Here's what tends to separate them, with real examples from the game.</p>
<h2>Signs a person wrote it</h2>
<ul>
<li><b>Small mistakes.</b> Typos (“Ofcourse”), missing words, odd spacing, run-on sentences. Today's AI rarely makes them unless asked to.</li>
<li><b>Specific, lived-in details.</b> A named team, a hometown, a child's age, a café on a particular road. AI tends to invent tidier, more generic details.</li>
<li><b>Tangents and uneven rhythm.</b> People ramble, repeat a word, or end abruptly. AI answers are usually evenly paced.</li>
<li><b>Jokes that are a bit strange.</b> “It dropped from the sky” is more human than a neatly balanced punchline.</li>
<li><b>Being wrong with confidence.</b> A half-remembered anecdote or a slightly wrong definition is very human.</li>
</ul>
<h2>Signs an AI wrote it</h2>
<ul>
<li><b>Polish everywhere.</b> Clean grammar, parallel lists, items of similar length.</li>
<li><b>Balanced, hedged takes.</b> “It depends… here are both sides… I lean toward…”.</li>
<li><b>Quotable endings.</b> A neat closing line that sounds like a caption.</li>
<li><b>Warm but generic memories.</b> A childhood piano teacher, a camping trip, a parent pointing at stars.</li>
<li><b>Apologetic refusals</b>, though people write those too: in one round the human starts with “Unfortunately, I can't answer that.”</li>
</ul>
<h2>Examples from the game</h2>
{ex_html}
<h2>Don't trust detectors either</h2>
<p>Automated “AI detectors” make the same mistakes people do, and flag real writing, especially from non-native speakers. Treat every sign above as a hint, not proof. The useful habit is to check the claim, not guess the author.</p>
<p><a class="btn" href="{root}">Test yourself: 10 rounds</a></p>
"""
        ld = [{"@context": "https://schema.org", "@type": "Article", "headline": "How to spot AI writing (and why it's getting harder)",
               "dateModified": self.today.isoformat(), "mainEntityOfPage": self.url("how-to-spot-ai-writing/"), "inLanguage": "en",
               "author": {"@type": "Organization", "name": BRAND}, "publisher": {"@type": "Organization", "name": BRAND}}]
        self.write("how-to-spot-ai-writing/index.html", self.layout(
            "how-to-spot-ai-writing/", "How to spot AI writing: signs, examples and limits | Turing.gun",
            "The habits that separate AI-written text from human writing, with real side-by-side examples, and why no sign is proof.",
            body, og="guide", jsonld=ld, current="how-to-spot-ai-writing/"))
        self.pages.append("how-to-spot-ai-writing/")

    def sources(self):
        s, ai = self.data["source"], self.data["ai"]
        rows = "".join(f'<li>Round “{e(it["prompt"])}”: Dolly row {it["dolly_index"]} ({e(it["category"])})</li>' for it in self.items)
        sponsor = (f'<p><a href="{attr(self.sponsor_url)}" rel="noopener sponsored">{e(self.sponsor_label or "Sponsor")}</a></p>' if self.sponsor_url else "")
        body = f"""
<h1>Sources, licenses and method</h1>
<h2>Human answers</h2>
<p>Every human answer is quoted word for word, typos included, from <a href="{s['url']}">databricks-dolly-15k</a>, a dataset of instructions and responses written by thousands of Databricks employees in 2023. The dataset card says contributors were told not to use generative AI. It's licensed <a href="{s['license_url']}">{e(s['license'])}</a>; this game's data file is shared under the same license. Only short answers to everyday questions were used, and none about health, money, law, religion or politics.</p>
<h2>AI answers</h2>
<p>Each AI answer was written by {e(ai['model'])} on {e(ai['written'])}, with this instruction: “{e(ai['instructions'])}” The note shown after each round, on what gave each answer away, was written at the same time.</p>
<p>New AI rounds can be added as new models come out; each set says which model wrote it.</p>
<h2>How a game is chosen</h2>
<p>Each game draws 10 of the {len(self.items)} pairs, and puts the AI answer on the left or right at random. Everyone gets the same game in the same week (it's seeded by the week), so a challenge link replays exactly the same rounds. “Play another set” gives a fresh random set.</p>
<h2>Privacy</h2>
<p>No accounts, no cookies, no stored guesses. A challenge link carries only the game's code and your score.{' Visits are counted with GoatCounter, which collects no personal data.' if self.goatcounter else ''}</p>
<h2>Every round's source</h2>
<ul class="sources">{rows}</ul>
<p>Code: MIT, on <a href="{REPO_URL}">GitHub</a>. Data: {e(s['license'])}. Spotted a problem? <a href="{REPO_URL}/issues/new">Open an issue</a>.</p>
{sponsor}
"""
        self.write("sources/index.html", self.layout("sources/", "Sources, licenses and method | Turing.gun",
                                                     "Where Turing.gun's human answers come from (databricks-dolly-15k, CC BY-SA 3.0), which AI wrote the others, and how games are picked.",
                                                     body, current="sources/"))
        self.pages.append("sources/")

    def not_found(self):
        after = self.site_url.split("://", 1)[1]
        prefix = "/" + after.split("/", 1)[1] + "/" if "/" in after else "/"
        body = f'<h1>Page not found</h1><p>That page doesn\'t exist. (Or does it? A human would say that.)</p><p><a class="btn" href="{prefix}">Play human or AI</a></p>'
        self.write("404.html", self.layout("404.html", "Page not found | Turing.gun", "That page doesn't exist. Play human or AI instead.",
                                           body, noindex=True, root=prefix))

    def meta_files(self):
        lastmod = self.today.isoformat()
        urls = "".join(f"<url><loc>{self.url(p)}</loc><lastmod>{lastmod}</lastmod></url>\n" for p in self.pages)
        self.write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
        self.write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {self.site_url}/sitemap.xml\n")
        self.write(f"{INDEXNOW_KEY}.txt", INDEXNOW_KEY)
        self.write(".nojekyll", "")
        self.write("data/rounds.json", json.dumps(self.data, ensure_ascii=False, indent=1))
        (self.out / "urls.txt").write_text("".join(self.url(p) + "\n" for p in self.pages), encoding="utf-8")

    def build(self):
        if self.out.exists():
            shutil.rmtree(self.out)
        shutil.copytree(ROOT / "site" / "assets", self.out / "assets")
        f = self.out / "assets" / "app.js"
        f.write_text(f.read_text(encoding="utf-8").replace('from "./core.js"', f'from "./core.js?v={self.ver}"')
                     .replace('import("./selftest.js")', f'import("./selftest.js?v={self.ver}")'), encoding="utf-8")
        shutil.copy(ROOT / "site" / "favicon.svg", self.out / "favicon.svg")
        self.home()
        self.guide()
        self.sources()
        self.not_found()
        self.meta_files()
        return self


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "dist"))
    args = ap.parse_args()
    today = dt.date.fromisoformat(os.environ["BUILD_DATE"]) if os.environ.get("BUILD_DATE") else dt.datetime.now(dt.timezone.utc).date()
    site = Site(Path(args.out), today).build()
    print(f"built {len(site.pages)} pages into {args.out}")


if __name__ == "__main__":
    main()
