// Human-or-AI game logic, shared by the browser (app.js) and the Node tests. No DOM access here.

export const ROUNDS_PER_GAME = 10;

export function isoWeek(date = new Date()) {
  const d = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
  const day = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - day);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  return `${d.getUTCFullYear()}-W${String(Math.ceil(((d - yearStart) / 86400000 + 1) / 7)).padStart(2, "0")}`;
}

export function hashString(s) {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

export function rng(seed) {
  let a = typeof seed === "number" ? seed >>> 0 : hashString(String(seed));
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// A game: `size` rounds, each with the AI answer randomly on the left or the right.
// The same seed always gives the same game, so a challenge link replays it exactly.
export function pickGame(items, { seed, size = ROUNDS_PER_GAME } = {}) {
  const rand = rng(seed);
  const pool = items.slice();
  for (let i = pool.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }
  return pool.slice(0, Math.min(size, pool.length)).map((item) => ({ item, aiSide: rand() < 0.5 ? "left" : "right" }));
}

export function grade(answers) {
  const right = answers.filter((a) => a.guess === a.round.aiSide).length;
  return { score: right, total: answers.length };
}

export function rating(score, total) {
  const r = total ? score / total : 0;
  if (r >= 0.9) return { label: "Turing-proof", blurb: "The AI barely fooled you. You notice what most people skim past." };
  if (r >= 0.7) return { label: "Sharp eye", blurb: "You caught the AI most of the time. A few got past you, and they'll get past most people." };
  if (r >= 0.5) return { label: "Coin flip", blurb: "About as good as guessing, which is where most people land. That's the point: AI writing is hard to spot." };
  return { label: "The AI fooled you", blurb: "The AI passed as human more often than not. Don't feel bad: it was asked to do exactly that." };
}

const SEED_RE = /^[A-Za-z0-9-]{1,24}$/;

export function shareParams({ seed, score, total }) {
  const p = new URLSearchParams();
  if (seed) p.set("t", seed);
  if (Number.isInteger(score) && Number.isInteger(total)) p.set("s", `${score}-${total}`);
  return p.toString();
}

export function readShare(search) {
  const p = new URLSearchParams(search || "");
  const out = { seed: null, score: null, total: null };
  if (p.get("t") && SEED_RE.test(p.get("t"))) out.seed = p.get("t");
  const m = /^(\d{1,2})-(\d{1,2})$/.exec(p.get("s") || "");
  if (m && Number(m[2]) > 0 && Number(m[2]) <= 20 && Number(m[1]) <= Number(m[2])) {
    out.score = Number(m[1]);
    out.total = Number(m[2]);
  }
  return out;
}

export function randomSeed(rand = Math.random) {
  let s = "";
  for (let i = 0; i < 6; i++) s += "abcdefghjkmnpqrstuvwxyz23456789"[Math.floor(rand() * 31)];
  return s;
}
