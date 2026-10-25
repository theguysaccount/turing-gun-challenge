"""The rounds: well-formed, fairly matched, and honest about where each answer came from."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "rounds.json").read_text(encoding="utf-8"))
ITEMS = DATA["items"]


class RoundsTest(unittest.TestCase):
    def test_metadata(self):
        self.assertEqual(DATA["source"]["license"], "CC BY-SA 3.0")
        self.assertTrue(DATA["source"]["url"].startswith("https://huggingface.co/datasets/databricks/databricks-dolly-15k"))
        self.assertTrue(DATA["ai"]["model"] and DATA["ai"]["written"] and DATA["ai"]["instructions"])

    def test_items(self):
        self.assertGreaterEqual(len(ITEMS), 30)
        self.assertEqual(len({i["id"] for i in ITEMS}), len(ITEMS))
        self.assertEqual(len({i["dolly_index"] for i in ITEMS}), len(ITEMS))
        for it in ITEMS:
            with self.subTest(it["id"]):
                self.assertEqual(it["id"], f"d{it['dolly_index']}")
                self.assertIn(it["category"], ("open_qa", "general_qa", "brainstorming", "creative_writing"))
                for k in ("prompt", "human", "ai", "tell"):
                    self.assertTrue(it[k].strip(), k)
                self.assertNotEqual(it["human"].strip(), it["ai"].strip())

    def test_lengths_are_comparable(self):
        # A big length gap would give the answer away.
        for it in ITEMS:
            h, a = len(it["human"].split()), len(it["ai"].split())
            with self.subTest(it["id"], human=h, ai=a):
                self.assertLessEqual(max(h, a) / min(h, a), 2.6)

    def test_ai_never_says_it_is_an_ai(self):
        for it in ITEMS:
            with self.subTest(it["id"]):
                self.assertNotRegex(it["ai"].lower(), r"\b(as an ai|language model|i am an ai|i'm an ai)\b")

    def test_no_sensitive_topics(self):
        bad = re.compile(r"\b(suicide|abortion|religio\w*|politic\w*|cancer|vaccine|mortgage|crypto\w*)\b", re.I)
        for it in ITEMS:
            with self.subTest(it["id"]):
                self.assertIsNone(bad.search(it["prompt"] + " " + it["human"] + " " + it["ai"]))


if __name__ == "__main__":
    unittest.main()
