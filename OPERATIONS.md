# Operations

Turing.gun is a static site on GitHub Pages: ten rounds of "which answer did the AI write?", built from real human answers in an openly licensed dataset beside AI answers to the same questions. Guesses never leave the browser. Actions runs the deploy, a weekly self-test and a monthly source check.

**Live:** https://theguysaccount.github.io/turing-gun-challenge/
**Repo:** https://github.com/theguysaccount/turing-gun-challenge

## Automated jobs

| Job | Workflow | When | What it does | How it fails safe |
|---|---|---|---|---|
| Deploy | `pages.yml` | every push to `main` | Round checks (sources, comparable lengths, no "as an AI", no sensitive topics), game logic tests, build, three end-to-end games in headless Chrome (fresh, challenge link with a friend's score, practice set), deploy, the same games live, IndexNow | Any failure stops before deploy; the last good site stays live. |
| Self-test + keep-alive | `selftest.yml` | Saturdays 18:11 UTC | Tests; the three games on the **live** site; every page answers 200 with its canonical; the live rounds equal `data/rounds.json`. Then the keep-alive. | Failure opens or comments on one `ops-alert` issue; GitHub emails the owner. |
| Source and license check | `sources.yml` | the 9th of every month | Downloads databricks-dolly-15k, confirms its card still says CC BY-SA 3.0, re-checks all 40 human answers and prompts word for word against their rows, checks the source and license links | A mismatch, a license change or a failed download fails the run and opens an issue. The site is untouched. |
| Keep-alive | `selftest.yml` → `scripts/keepalive.sh` | weekly | Re-enables every scheduled workflow; empty `[skip ci]` commit after 45 days without commits | Keeps the schedules alive past GitHub's 60-day cutoff. |

## Sources and fairness

- **Human answers:** quoted verbatim (typos included) from [databricks-dolly-15k](https://huggingface.co/datasets/databricks/databricks-dolly-15k), written by Databricks employees told not to use generative AI. CC BY-SA 3.0, so `data/rounds.json` and the served copy are CC BY-SA 3.0 too. Each round records its Dolly row, and the Sources page lists them all.
- **AI answers:** written by Claude Opus 5.5 on 2026-10-25 with the instruction in `data/rounds.json` ("answer the way a person would, in about as many words, without saying you are an AI").
- **Picked rounds** are short everyday questions: no health, money, law, religion or politics. Lengths are kept within a factor of 2.6 so length alone doesn't give the answer away (tested).

## What to watch

- **Open `ops-alert` issues.**
- **Never reorder or edit existing rounds in place.** A challenge link replays a game by seed over the current pool; changing the pool changes which rounds a seed picks. Add rounds in a new release and accept that older links then pick a different set (the score banner still works).

## Keys Jack can turn later

### 1. New AI rounds when new models ship (content routine)

The brief's "new AI rounds each model release" needs a model to write answers, which can't run in Actions. A Claude Code routine (claude.ai/code → Routines), run when a major model ships or monthly:

> In theguysaccount/turing-gun-challenge: add 10 new rounds to data/rounds.json. Pick short everyday prompts from databricks-dolly-15k (categories open_qa, general_qa, brainstorming, creative_writing; no context; 18–65-word responses; no health, money, law, religion or politics), quote the human response verbatim with its row index, and write the AI answer with the newest available model using the instruction stored in data/rounds.json; record the model name per round if it differs from data.ai.model. Write a one-line "tell" for each. Keep word counts within a factor of 2.6. Run python3 -m unittest discover -s tests, node --test tests/js/*.test.mjs, python3 scripts/check_sources.py and scripts/e2e.sh, then commit and push.

### 2. The $1M prize round

The note's hook ("if I can't tell, you get $1m") needs a funder, written contest rules (a skill-based design to stay clear of lottery law), eligibility rules, and a live-chat format with opted-in humans and bots, which needs a server. None of that can be machine-run on Pages. The sponsor slot below is where a funded prize round would be announced.

### 3. Money: sponsor slot

A link under every score and on the Sources page, hidden until set: repo variables `SPONSOR_URL` and `SPONSOR_LABEL` (e.g. "Prize round sponsored by …"). Then `gh workflow run pages.yml -R theguysaccount/turing-gun-challenge`.

### 4. Custom domain

No domain matched in the portfolio; "Turing.gun" isn't a registrable name (there is no .gun top-level domain). Candidates: `turinggun.com` (unregistered on 2026-10-25 per WHOIS, about $11/yr; matches the note's brand), `humanorai.app` (availability not confirmed), or a subdomain of an owned domain such as `turing.persistventures.com` (free; persistventures.com is in the portfolio). DNS: `A @` → `185.199.108.153`–`185.199.111.153` (four records), `AAAA @` → `2606:50c0:8000::153`–`8003::153`, `CNAME www` → `theguysaccount.github.io` (for a subdomain, one CNAME to `theguysaccount.github.io`); Settings → Pages → Custom domain, then Enforce HTTPS; repo variable `SITE_URL`; redeploy.

### 5. Analytics and leaderboard

Analytics are off. Events in the code: `game_start`, `game_complete/<score>` (**activation**), `share/<channel>`. Set `GOATCOUNTER_URL` and redeploy. A public leaderboard of judges and bots needs stored results and so a server; with analytics on, an aggregate "most people fall for round X" page could be built from the event counts.

### 6. Search Console

Verify and submit `/sitemap.xml`. IndexNow runs on every deploy.
