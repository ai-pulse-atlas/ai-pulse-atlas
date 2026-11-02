import datetime as dt
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate import check_record_times

NOW = dt.datetime(2026, 11, 2, 12, 0, 0, tzinfo=dt.timezone(dt.timedelta(hours=8)))


class RecordTimesTests(unittest.TestCase):
    def setUp(self):
        self.ev = {"id": "2026-11-01-example",
                   "created_at": "2026-11-02T11:07:24+08:00",
                   "updated_at": "2026-11-02T11:07:24+08:00"}

    def assert_rejected(self, message):
        errors = check_record_times(self.ev, now=NOW)
        self.assertTrue(any(message in e for e in errors), errors)
        for e in errors:
            self.assertIn(self.ev["id"], e)

    def test_valid(self):
        self.assertEqual(check_record_times(self.ev, now=NOW), [])

    def test_within_clock_skew(self):
        self.ev["updated_at"] = "2026-11-02T12:09:59+08:00"
        self.assertEqual(check_record_times(self.ev, now=NOW), [])

    def test_missing_seconds(self):
        for field in ("created_at", "updated_at"):
            with self.subTest(field=field):
                self.setUp()
                self.ev[field] = "2026-11-02T11:07+08:00"
                self.assert_rejected(f"{field} 必须是带秒的北京时间")

    def test_bad_format(self):
        for value in ("2026-11-02T03:07:24Z", "2026-11-02T11:07:24", "2026-11-02 11:07:24+08:00",
                      "2026-11-02", "2026-13-02T11:07:24+08:00", 20261102):
            with self.subTest(value=value):
                self.ev["updated_at"] = value
                self.assert_rejected("updated_at 必须是带秒的北京时间")

    def test_future(self):
        self.ev["updated_at"] = "2026-11-02T15:30:00+08:00"
        self.assert_rejected("updated_at 不能晚于当前时间")

    def test_future_created_at(self):
        self.ev["created_at"] = self.ev["updated_at"] = "2026-11-02T12:10:01+08:00"
        self.assert_rejected("created_at 不能晚于当前时间")

    def test_updated_before_created(self):
        self.ev["updated_at"] = "2026-11-01T11:07:24+08:00"
        self.assert_rejected("updated_at 不能早于 created_at")


if __name__ == "__main__":
    unittest.main()
