// Game logic: node --test tests/js/*.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { isoWeek, pickGame, grade, rating, shareParams, readShare, randomSeed, rng } from "../../site/assets/core.js";

const DATA = JSON.parse(readFileSync(new URL("../../data/rounds.json", import.meta.url)));

test("weeks", () => {
  assert.equal(isoWeek(new Date("2026-10-25T12:00:00Z")), "2026-W43");
  assert.equal(isoWeek(new Date("2027-01-01T12:00:00Z")), "2026-W53");
});

test("a game is 10 distinct rounds, reproducible from its seed", () => {
  const a = pickGame(DATA.items, { seed: "w-2026-W43" });
  const b = pickGame(DATA.items, { seed: "w-2026-W43" });
  assert.equal(a.length, 10);
  assert.equal(new Set(a.map((r) => r.item.id)).size, 10);
  assert.deepEqual(a.map((r) => [r.item.id, r.aiSide]), b.map((r) => [r.item.id, r.aiSide]));
  assert.notDeepEqual(a.map((r) => r.item.id), pickGame(DATA.items, { seed: "w-2026-W44" }).map((r) => r.item.id));
});

test("the AI lands on both sides about equally", () => {
  let left = 0, total = 0;
  for (let k = 0; k < 300; k++) for (const r of pickGame(DATA.items, { seed: "s" + k })) { total++; if (r.aiSide === "left") left++; }
  assert.ok(left / total > 0.45 && left / total < 0.55, `left share ${left / total}`);
});

test("grading and ratings", () => {
  const rounds = pickGame(DATA.items, { seed: "g" });
  const answers = rounds.map((round, i) => ({ round, guess: i < 7 ? round.aiSide : round.aiSide === "left" ? "right" : "left" }));
  assert.deepEqual(grade(answers), { score: 7, total: 10 });
  assert.equal(rating(10, 10).label, "Turing-proof");
  assert.equal(rating(7, 10).label, "Sharp eye");
  assert.equal(rating(5, 10).label, "Coin flip");
  assert.equal(rating(2, 10).label, "The AI fooled you");
});

test("challenge links", () => {
  const q = shareParams({ seed: "w-2026-W43", score: 7, total: 10 });
  assert.deepEqual(readShare("?" + q), { seed: "w-2026-W43", score: 7, total: 10 });
  assert.deepEqual(readShare("?t=<x>&s=12-10"), { seed: null, score: null, total: null });
  assert.match(randomSeed(rng(1)), /^[a-z2-9]{6}$/);
});
