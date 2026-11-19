import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from database import get_summary, init_db, save_check


class TestDatabase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.tmp.close()
        self.db_path = self.tmp.name
        init_db(self.db_path)

    def tearDown(self) -> None:
        os.remove(self.db_path)

    def test_summary_calculations(self) -> None:
        save_check(self.db_path, "1.1.1.1", 443, "ONLINE", 10.0)
        save_check(self.db_path, "1.1.1.1", 443, "ONLINE", 20.0)
        save_check(self.db_path, "1.1.1.1", 443, "OFFLINE", None)

        rows = get_summary(self.db_path)
        self.assertEqual(len(rows), 1)

        target, port, total, online, avg_ms, min_ms, max_ms = rows[0]
        self.assertEqual(total, 3)
        self.assertEqual(online, 2)
        self.assertEqual(avg_ms, 15.0)
        self.assertEqual(min_ms, 10.0)
        self.assertEqual(max_ms, 20.0)


if __name__ == "__main__":
    unittest.main()