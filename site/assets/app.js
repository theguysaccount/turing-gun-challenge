// Human-or-AI game UI. Logic lives in core.js. Nothing is stored or sent.
import { pickGame, grade, rating, shareParams, readShare, randomSeed, isoWeek } from "./core.js";

const CFG = JSON.parse(document.getElementById("site-config").textContent);
const DATA = JSON.parse(document.getElementById("rounds").textContent);
const share = readShare(location.search);
const $ = (sel, el = document) => el.querySelector(sel);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
// Answers sit inside <button>s, which may only hold inline content: one block-styled span per line.
const lines = (t) => esc(t).split("\n").map((l) => `<span class="line">${l}</span>`).join("");

function track(name, detail) {
  try {
    if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({ path: `event/${name}${detail ? "/" + detail : ""}`, title: name, event: true });
  } catch (e) { /* never break the game */ }
}

class Game {
  constructor(root) {
    this.root = root;
    this.intro = $("[data-intro]", root);
    this.stage = $("[data-stage]", root);
    root.querySelectorAll("[data-start]").forEach((b) => b.addEventListener("click", () => this.start()));
  }

  start(seed) {
    this.weekly = !seed && (!share.seed || share.seed === `w-${isoWeek()}`);
    this.seed = seed || share.seed || `w-${isoWeek()}`;
    this.rounds = pickGame(DATA.items, { seed: this.seed });
    this.answers = [];
    this.i = 0;
    this.intro.hidden = true;
    this.stage.hidden = false;
    track("game_start");
    this.render();
  }

  get round() { return this.rounds[this.i]; }

  render() {
    const { item, aiSide } = this.round;
    const left = aiSide === "left" ? item.ai : item.human;
    const right = aiSide === "left" ? item.human : item.ai;
    const n = this.rounds.length;
    this.stage.innerHTML = `
      <div class="qhead"><span>Round ${this.i + 1} of ${n}</span><span>${this.i ? `${grade(this.answers).score} right so far` : ""}</span></div>
      <div class="progress" aria-hidden="true"><span style="width:${(this.i / n) * 100}%"></span></div>
      <p class="asked">Someone asked:</p>
      <blockquote class="prompt">${esc(item.prompt)}</blockquote>
      <p class="ask" id="ask-${this.i}">Which answer did the AI write?</p>
      <div class="answers" role="group" aria-labelledby="ask-${this.i}">
        <button type="button" class="answer" data-side="left" aria-label="Answer A: ${esc(left)}"><span class="tag">Answer A</span>${lines(left)}</button>
        <button type="button" class="answer" data-side="right" aria-label="Answer B: ${esc(right)}"><span class="tag">Answer B</span>${lines(right)}</button>
      </div>
      <div data-feedback aria-live="polite"></div>`;
    this.stage.querySelectorAll("[data-side]").forEach((b) => b.addEventListener("click", () => this.guess(b.dataset.side)));
    if (this.i > 0 && this.stage.getBoundingClientRect().top < 0) this.stage.scrollIntoView({ block: "start" });
  }

  guess(side) {
    if (this.answers.length > this.i) return;
    const round = this.round;
    this.answers.push({ round, guess: side });
    const ok = side === round.aiSide;
    this.stage.querySelectorAll("[data-side]").forEach((b) => {
      const isAI = b.dataset.side === round.aiSide;
      b.disabled = true;
      b.classList.add(isAI ? "was-ai" : "was-human");
      if (b.dataset.side === side) b.classList.add("picked");
      b.querySelector(".tag").textContent = isAI ? `AI · ${DATA.ai.model.replace(/ \(.*\)/, "")}` : "Human · Dolly contributor";
      b.setAttribute("aria-label", `${b.querySelector(".tag").textContent}: ${isAI ? round.item.ai : round.item.human}`);
    });
    const last = this.i === this.rounds.length - 1;
    const fb = $("[data-feedback]", this.stage);
    fb.innerHTML = `
      <div class="feedback ${ok ? "right" : "wrong"}" data-result="${ok ? "right" : "wrong"}">
        <h3>${ok ? "✓ You spotted the AI." : "✗ The AI fooled you."}</h3>
        <p>${esc(round.item.tell)}</p>
        <button class="btn" type="button" data-next>${last ? "See my score →" : "Next round →"}</button>
      </div>`;
    const next = $("[data-next]", fb);
    next.addEventListener("click", () => this.next());
    next.focus({ preventScroll: true });
  }

  next() {
    if (this.i < this.rounds.length - 1) {
      this.i++;
      this.render();
    } else this.results();
  }

  results() {
    const g = grade(this.answers);
    const r = rating(g.score, g.total);
    const url = `${CFG.siteUrl}/?${shareParams({ seed: this.seed, score: g.score, total: g.total })}`;
    const text = `I spotted the AI ${g.score} out of ${g.total} times. Can you beat me?`;
    const enc = encodeURIComponent;
    this.stage.innerHTML = `
      <p class="eyebrow">${this.weekly ? "This week's game" : "Practice game"}</p>
      <p class="score" data-score="${g.score}">${g.score} / ${g.total}</p>
      <p class="verdict">${esc(r.label)}</p>
      <p>${esc(r.blurb)}</p>
      ${share.score !== null && share.seed === this.seed ? `<p class="banner">Your friend got ${share.score} out of ${share.total}. ${g.score > share.score ? "You win." : g.score === share.score ? "It's a tie." : "They win this one."}</p>` : ""}
      <div class="share-box">
        <h2>Challenge a friend</h2>
        <p>They get the same ${g.total} rounds and see your score when they finish.</p>
        <div class="btn-row">
          ${navigator.share ? `<button class="btn small" type="button" data-native>Share…</button>` : ""}
          <a class="btn small secondary" href="sms:?&body=${enc(text + " " + url)}" data-t="sms">Text it</a>
          <a class="btn small secondary" href="https://wa.me/?text=${enc(text + " " + url)}" target="_blank" rel="noopener" data-t="whatsapp">WhatsApp</a>
          <a class="btn small secondary" href="https://bsky.app/intent/compose?text=${enc(text + " " + url)}" target="_blank" rel="noopener" data-t="bluesky">Bluesky</a>
          <button class="btn small secondary" type="button" data-copy>Copy link</button>
        </div>
        <input class="link" readonly value="${esc(url)}" aria-label="Challenge link" data-link>
      </div>
      <div class="btn-row"><button class="btn secondary" type="button" data-again>Play another set</button><a class="btn secondary" href="${CFG.root}how-to-spot-ai-writing/">How to spot AI writing</a></div>
      ${CFG.sponsorUrl ? `<p class="note"><a href="${esc(CFG.sponsorUrl)}" rel="noopener sponsored">${esc(CFG.sponsorLabel || "Support Turing.gun")}</a></p>` : ""}`;
    this.stage.querySelector("[data-native]")?.addEventListener("click", async () => {
      track("share", "native");
      try { await navigator.share({ title: "Can you spot the AI?", text, url }); } catch (e) { /* cancelled */ }
    });
    this.stage.querySelector("[data-copy]").addEventListener("click", async (ev) => {
      track("share", "copy");
      try { await navigator.clipboard.writeText(url); ev.target.textContent = "Copied ✓"; } catch (e) { window.prompt("Copy this link:", url); }
    });
    this.stage.querySelectorAll("[data-t]").forEach((a) => a.addEventListener("click", () => track("share", a.dataset.t)));
    this.stage.querySelector("[data-again]").addEventListener("click", () => this.start(randomSeed()));
    this.result = g;
    if (this.stage.getBoundingClientRect().top < 0) this.stage.scrollIntoView({ block: "start" });
    track("game_complete", `${g.score}-${g.total}`);
  }
}

const banner = $("#share-banner");
if (banner && share.score !== null) {
  banner.textContent = `A friend spotted the AI ${share.score} out of ${share.total} times. You'll get the same rounds. Can you beat them?`;
  banner.hidden = false;
}
const games = [...document.querySelectorAll("[data-game]")].map((el) => new Game(el));

if (/[?&]selftest=1\b/.test(location.search)) {
  import("./selftest.js").then((m) => m.run(games[0], DATA)).catch((e) => { document.body.dataset.selftest = "fail: " + e.message; });
}
const demo = new URLSearchParams(location.search).get("demo");
if (demo && games[0]) import("./selftest.js").then((m) => m.demo(games[0], demo));
