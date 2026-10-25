# Decisions

1. **A paired-answer quiz, not live chat.** The evaluator's fastest path was a five-minute chat game, which needs a server, opted-in humans online at the same time, and moderation. The machine-runnable version asks the same question (can you tell?) with fixed, sourced pairs. It also avoids the deceptive "AI chatbot on Omegle" variant from the note.
2. **Human answers from databricks-dolly-15k.** It's openly licensed (CC BY-SA 3.0), written by people who were told not to use generative AI, and full of short everyday answers with real human texture. Answers are quoted verbatim with their row index; a monthly job re-verifies them.
3. **The AI writes as a person would.** That's the Turing test framing in the note ("fake it or make it"). The instruction is published on the Sources page and in the data.
4. **No sensitive topics.** Medical, financial, legal, religious and political questions were excluded, even though Dolly has many, so wrong human answers can't mislead anyone on something that matters.
5. **Lengths kept comparable.** AI answers average about 33 words against 45 for the humans; a test caps any pair's ratio at 2.6. Future rounds should match lengths more closely.
6. **One explanation per round.** Each reveal says what gave the AI (or the human) away, so a game teaches, not just scores.
7. **Weekly seeded game.** Same reasoning as the scam test: shared scores are only fair if everyone plays the same rounds.
8. **"Turing.gun" as the logo, plain words in titles.** Search titles lead with "Human or AI?" and "spot AI writing", which is what people type. Settles "is Turing.gun a domain you hold?": no, and it can't be (no .gun top-level domain).
9. **The $1M prize is a key, not a promise.** Settles "who pays and who wins?" for v1: nobody, until a sponsor funds a round with written, skill-based rules (OPERATIONS.md).
