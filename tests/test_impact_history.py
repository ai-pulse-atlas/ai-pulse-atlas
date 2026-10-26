import copy
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate import check_impact_history


class ImpactHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        schema = json.loads((ROOT / "schema/event.schema.json").read_text())
        cls.validator = Draft202012Validator(schema["properties"]["impact_history"])

    def setUp(self):
        self.ev = {
            "id": "2026-10-01-example", "impact": "A",
            "impact_history": [
                {"from": "C", "to": "B", "at": "2026-10-01T12:00+08:00",
                 "reason": "补充依据", "ref": "https://example.org/review", "by": "maintainer"},
                {"from": "B", "to": "A", "at": "2026-10-01T12:00:01+08:00",
                 "reason": "确认影响", "ref": "http://example.org/update", "by": "bot"},
            ],
        }

    def assert_rejected(self, message, index=1, schema=False):
        errors = check_impact_history(self.ev)
        self.assertTrue(errors)
        self.assertTrue(any(message in error for error in errors), errors)
        for error in errors:
            self.assertIn(self.ev["id"], error)
            self.assertIn(f"第 {index} 条", error)
        if schema:
            self.assertFalse(self.validator.is_valid(self.ev["impact_history"]))

    def test_valid(self):
        original = copy.deepcopy(self.ev)
        self.assertEqual(check_impact_history(self.ev), [])
        self.validator.validate(self.ev["impact_history"])
        self.assertEqual(self.ev, original)

    def test_missing_required(self):
        for field in ("reason", "at", "from", "to"):
            with self.subTest(field=field):
                value = self.ev["impact_history"][0].pop(field)
                self.assert_rejected(f"缺少必填字段 {field}", schema=True)
                self.ev["impact_history"][0][field] = value

    def test_unknown_field(self):
        self.ev["impact_history"][0]["foo"] = "未知"
        self.assert_rejected("未知字段 foo", schema=True)

    def test_ref_not_http(self):
        for value in ("ftp://example.org", "javascript:alert(1)", "https://example.org/a b"):
            with self.subTest(value=value):
                self.ev["impact_history"][0]["ref"] = value
                self.assert_rejected("ref 必须", schema=True)

    def test_out_of_order(self):
        self.ev["impact_history"][1]["at"] = "2026-10-01T11:59+08:00"
        self.assert_rejected("严格升序", index=2)

    def test_equal_times(self):
        self.ev["impact_history"][1]["at"] = "2026-10-01T12:00:00+08:00"
        self.assert_rejected("严格升序", index=2)

    def test_chain_broken_or_last_mismatch(self):
        self.ev["impact_history"][1]["from"] = "C"
        self.assert_rejected("首尾相接", index=2)

    def test_last_mismatch(self):
        self.ev["impact"] = "S"
        self.assert_rejected("最后一条 to", index=2)

    def test_invalid_by(self):
        self.ev["impact_history"][0]["by"] = "admin"
        self.assert_rejected("by 必须", schema=True)

    def test_invalid_at(self):
        for value in ("2026-02-30T12:00+08:00", "2026-10-01T12:00+00:00", None):
            with self.subTest(value=value):
                self.ev["impact_history"][0]["at"] = value
                self.assert_rejected("at 必须")

    def test_invalid_reason(self):
        for value in ("", None, 1):
            with self.subTest(value=value):
                self.ev["impact_history"][0]["reason"] = value
                self.assert_rejected("reason 必须", schema=True)

    def test_invalid_level(self):
        self.ev["impact_history"][0]["from"] = "D"
        self.assert_rejected("from 必须", schema=True)

    def test_optional_history(self):
        for ev in ({"id": self.ev["id"]}, {"id": self.ev["id"], "impact_history": []}):
            self.assertEqual(check_impact_history(ev), [])


if __name__ == "__main__":
    unittest.main()
