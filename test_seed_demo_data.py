import tempfile
import unittest
from pathlib import Path

from database import StudentDatabase, SyntheticSeedConflict
from seed_demo_data import build_synthetic_results


class SyntheticSeedTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_directory.name) / "seed.sqlite3"
        self.database = StudentDatabase(self.database_path)
        self.database.initialize()

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_build_five_synthetic_results(self):
        results = build_synthetic_results()
        self.assertEqual(len(results), 5)
        expected = [
            ("Aarav Sharma", "DEMO101", 467, 93.4),
            ("Diya Mehta", "DEMO102", 425, 85.0),
            ("Kabir Verma", "DEMO103", 360, 72.0),
            ("Ananya Rao", "DEMO104", 309, 61.8),
            ("Rohan Gupta", "DEMO105", 238, 47.6),
        ]
        for result, expected_values in zip(results, expected):
            name, roll, total, percentage = expected_values
            self.assertEqual(result["student_name"], name)
            self.assertEqual(result["roll_number"], roll)
            self.assertEqual(result["total_marks"], total)
            self.assertEqual(result["percentage"], percentage)

    def test_seed_is_idempotent(self):
        first = self.database.seed_synthetic_results(build_synthetic_results())
        second = self.database.seed_synthetic_results(build_synthetic_results())
        self.assertEqual(first["inserted"], 5)
        self.assertEqual(first["skipped"], 0)
        self.assertEqual(second["inserted"], 0)
        self.assertEqual(second["skipped"], 5)
        self.assertEqual(len(self.database.get_active_results()), 5)

    def test_existing_real_roll_is_not_replaced(self):
        real = build_synthetic_results()[0]
        real["student_name"] = "Real Student"
        real["is_synthetic"] = 0
        self.database.save_active_result(real)

        with self.assertRaises(SyntheticSeedConflict):
            self.database.seed_synthetic_results(build_synthetic_results())
        active = self.database.get_active_results()
        matching = [
            student
            for student in active
            if student["roll_number"] == "DEMO101"
        ]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["student_name"], "Real Student")

    def test_seeded_records_persist_after_reconnect(self):
        self.database.seed_synthetic_results(build_synthetic_results())
        reconnected = StudentDatabase(self.database_path)
        reconnected.initialize()
        active = reconnected.get_active_results()
        self.assertEqual(len(active), 5)

    def test_seeded_records_are_marked_synthetic(self):
        self.database.seed_synthetic_results(build_synthetic_results())
        active = self.database.get_active_results()
        for student in active:
            self.assertIn("is_synthetic", student)
            self.assertTrue(student["is_synthetic"])
