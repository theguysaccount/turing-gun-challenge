// End-to-end self-test, loaded only with ?selftest=1: plays a full game through the real buttons
// (one deliberate miss) and checks the reveal, the score and the challenge link.
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
async function until(fn, what, ms = 10000) {
  const t0 = Date.now();
  while (Date.now() - t0 < ms) {
    const v = fn();
    if (v) return v;
    await wait(20);
  }
  throw new Error("timed out waiting for " + what);
}

export async function run(game, data) {
  const log = [];
  try {
    document.querySelector("[data-start]").click();
    await until(() => game.rounds && game.stage.querySelector("[data-side]"), "round 1");
    const n = game.rounds.length;
    if (n !== 10) throw new Error(`expected 10 rounds, got ${n}`);
    for (let i = 0; i < n; i++) {
      const r = game.round;
      const shownLeft = game.stage.querySelector('[data-side="left"]').textContent;
      const aiText = r.item.ai.split("\n")[0];
      if (!shownLeft.includes(aiText) === (r.aiSide === "left")) throw new Error(`round ${i + 1}: sides don't match the data`);
      const miss = i === 0;
      const pick = miss ? (r.aiSide === "left" ? "right" : "left") : r.aiSide;
      game.stage.querySelector(`[data-side="${pick}"]`).click();
      const fb = await until(() => game.stage.querySelector("[data-result]"), "feedback");
      if (fb.dataset.result !== (miss ? "wrong" : "right")) throw new Error(`round ${i + 1}: feedback ${fb.dataset.result}`);
      if (!game.stage.querySelector(".was-ai") || !game.stage.querySelector(".was-human")) throw new Error("answers not revealed");
      game.stage.querySelector("[data-next]").click();
    }
    const score = await until(() => game.stage.querySelector("[data-score]"), "score");
    if (score.dataset.score !== String(n - 1)) throw new Error(`score ${score.dataset.score}, expected ${n - 1}`);
    const link = game.stage.querySelector("[data-link]").value;
    if (!link.includes(`t=${encodeURIComponent(game.seed)}`) || !link.includes(`s=${n - 1}-${n}`)) throw new Error("challenge link: " + link);
    for (const el of document.querySelectorAll("button")) {
      if (el.offsetParent && !el.textContent.trim()) throw new Error("a visible button has no label");
    }
    log.push(`seed ${game.seed}, score ${n - 1}/${n}, ${data.items.length} rounds in the pool`);
    document.body.dataset.selftest = "pass";
  } catch (e) {
    document.body.dataset.selftest = "fail: " + e.message;
  }
  const pre = document.createElement("pre");
  pre.id = "selftest";
  pre.textContent = document.body.dataset.selftest + "\n" + log.join("\n");
  document.body.appendChild(pre);
}

// Screenshot helper: ?demo=0 shows round 1; ?demo=1 answers it; ?demo=end plays to the score.
export async function demo(game, what) {
  document.querySelector("[data-start]").click();
  const n = what === "end" ? game.rounds.length : Number(what) || 0;
  for (let i = 0; i < n; i++) {
    game.stage.querySelector(`[data-side="${i % 3 ? game.round.aiSide : game.round.aiSide === "left" ? "right" : "left"}"]`).click();
    if (i < n - 1 || what === "end") game.stage.querySelector("[data-next]").click();
  }
  window.scrollTo(0, 0);
}
