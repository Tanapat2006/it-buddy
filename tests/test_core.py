import tempfile
import unittest
from pathlib import Path

from it_buddy_core import (
    STATUSES,
    diagnose_issue,
    make_record,
    load_records,
    save_records,
    search_knowledge_base,
    summarize_records,
    update_record_status,
)


class TestITBuddyCore(unittest.TestCase):
    def test_diagnose_known_issue(self):
        result = diagnose_issue("wifi_not_connect")
        self.assertEqual(result["category"], "Network")
        self.assertGreaterEqual(len(result["steps"]), 3)

    def test_diagnose_unknown_issue_raises(self):
        with self.assertRaises(ValueError):
            diagnose_issue("not-a-real-issue")

    def test_search_knowledge_base(self):
        results = search_knowledge_base("Printer")
        self.assertTrue(results)
        self.assertTrue(all("Printer" in row["category"] or "Printer" in row["title"] for row in results))

    def test_update_status_and_summary(self):
        record = make_record("no_power")
        updated = update_record_status([record], record["id"], "แก้ไขแล้ว", "ทดสอบแล้ว")
        summary = summarize_records(updated)
        self.assertEqual(updated[0]["status"], "แก้ไขแล้ว")
        self.assertEqual(summary["resolved"], 1)
        self.assertEqual(summary["resolution_rate"], 100.0)

    def test_json_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "records.json"
            record = make_record("app_crash")
            save_records(path, [record])
            loaded = load_records(path)
            self.assertEqual(loaded[0]["id"], record["id"])


if __name__ == "__main__":
    unittest.main()
