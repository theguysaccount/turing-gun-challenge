# Turing.gun: human or AI?

**Live:** https://theguysaccount.github.io/turing-gun-challenge/ · **Screens:** [docs/screens](docs/screens/)

Ten rounds. Each shows a question and two answers: one written by a person, one by an AI told to sound like a person. Pick the AI. After each round you see which was which and what gave it away. Scores share as a challenge link that replays the same game.

- **Real human answers**, quoted verbatim from [databricks-dolly-15k](https://huggingface.co/datasets/databricks/databricks-dolly-15k) (CC BY-SA 3.0), whose writers were told not to use AI. Each round cites its dataset row.
- **AI answers** written by Claude Opus 5.5 to the same questions, at similar length.
- **Weekly game**: everyone gets the same ten rounds each week, so scores compare.
- **No server, no tracking.** Guesses stay in the browser.

## How it runs

| What | Where | When |
|---|---|---|
| Tests, build, three headless-Chrome games, deploy, live games, IndexNow | `.github/workflows/pages.yml` | every push |
| Live games, page and data checks, keep-alive | `.github/workflows/selftest.yml` | weekly |
| Re-verify human answers against Dolly, license and links | `.github/workflows/sources.yml` | monthly |

Details, fairness rules and the keys (new AI rounds, prize round, sponsor, domain, analytics): [OPERATIONS.md](OPERATIONS.md).

## Run, test, deploy

```bash
python3 pipeline/build.py && python3 -m http.server -d dist 8000
python3 -m unittest discover -s tests
node --test tests/js/*.test.mjs
scripts/e2e.sh
python3 scripts/check_sources.py
```

Deploy is a push to `main`.

## License

Code: MIT. Round data (`data/rounds.json`): CC BY-SA 3.0, because the human answers come from databricks-dolly-15k (CC BY-SA 3.0, © Databricks).
