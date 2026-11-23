import sqlite3
import tempfile
import unittest
from pathlib import Path

from database import StudentDatabase


class StudentDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_directory.name) / "test_students.sqlite3"
        self.database = StudentDatabase(self.database_path)
        self.database.initialize()

    def tearDown(self):
        self.temp_directory.cleanup()

    def make_result(self, name="Ananya", roll="001", percentage=80):
        total_marks = int(percentage * 5)
        return {
            "student_name": name,
            "roll_number": roll,
            "semester": "Semester 1",
            "academic_year": "2026-2027",
            "subject_count": 5,
            "subject_names": ["Python", "Math", "DSA", "Data Science", "Git"],
            "subject_marks": [percentage, percentage, percentage, percentage, percentage],
            "total_marks": total_marks,
            "average_marks": float(percentage),
            "percentage": float(percentage),
            "overall_grade": "B" if percentage == 80 else ("A" if percentage >= 90 else "E"),
            "overall_result": "Pass" if percentage >= 40 else "Fail",
            "performance_category": "Excellent" if percentage >= 75 else "Needs Improvement",
            "remarks": "Good",
        }

    def test_database_initialization(self):
        connection = self.database.connect()
        try:
            table_names = {
                row["name"]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            self.assertIn("students", table_names)
            self.assertIn("active_results", table_names)
            self.assertIn("active_subjects", table_names)
            self.assertIn("result_history", table_names)
            self.assertIn("history_subjects", table_names)
            foreign_keys = connection.execute("PRAGMA foreign_keys").fetchone()[0]
            self.assertEqual(foreign_keys, 1)
        finally:
            connection.close()

    def test_save_and_retrieve_student(self):
        result = self.make_result()
        self.assertTrue(self.database.save_active_result(result))
        active = self.database.get_active_results()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0]["student_name"], "Ananya")
        self.assertEqual(active[0]["subject_names"][0], "Python")

    def test_persistent_records_after_reconnect(self):
        self.database.save_active_result(self.make_result())
        reconnected = StudentDatabase(self.database_path)
        reconnected.initialize()
        active = reconnected.get_active_results()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0]["roll_number"], "001")

    def test_duplicate_prevention(self):
        result = self.make_result()
        self.assertTrue(self.database.save_active_result(result))
        self.assertFalse(self.database.save_active_result(result))

    def test_multiple_students(self):
        self.assertTrue(self.database.save_active_result(self.make_result("Ananya", "001", 80)))
        self.assertTrue(self.database.save_active_result(self.make_result("Rohan", "002", 70)))
        self.assertEqual(len(self.database.get_active_results()), 2)

    def test_update_archives_previous_version(self):
        self.database.save_active_result(self.make_result())
        updated = self.make_result(percentage=95)
        updated["student_name"] = "Ananya"
        updated["roll_number"] = "001"
        updated["overall_grade"] = "A"
        updated["subject_marks"] = [95, 95, 95, 95, 95]
        updated["total_marks"] = 475
        updated["average_marks"] = 95.0
        updated["performance_category"] = "Outstanding"

        self.assertTrue(self.database.update_active_result(updated))
        active = self.database.get_active_results()
        self.assertEqual(active[0]["percentage"], 95)
        self.assertEqual(active[0]["version"], 2)

        history = self.database.get_result_history("001", "Semester 1", "2026-2027")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["version"], 1)
        self.assertEqual(history[0]["percentage"], 80)

    def test_update_missing_student(self):
        updated = self.make_result()
        self.assertFalse(self.database.update_active_result(updated))

    def test_foreign_key_enforcement(self):
        connection = self.database.connect()
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    """
                    INSERT INTO active_subjects (
                        result_id, position, subject_name, marks, grade, status
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (999, 1, "Python", 90, "A", "Pass"),
                )
        finally:
            connection.close()

    def test_invalid_result_rolls_back_save(self):
        invalid = self.make_result()
        invalid["subject_marks"] = [90, 90]
        with self.assertRaises(ValueError):
            self.database.save_active_result(invalid)
        self.assertEqual(self.database.get_active_results(), [])

    def test_database_mutations_reject_student_account(self):
        student_account = {
            "account_id": 2,
            "username": "001",
            "role": "STUDENT",
            "student_id": 1,
        }
        result = self.make_result()
        self.assertFalse(
            self.database.save_active_result_for_account(student_account, result)
        )
        self.assertFalse(
            self.database.update_active_result_for_account(student_account, result)
        )
        self.assertEqual(self.database.get_active_results(), [])


if __name__ == "__main__":
    unittest.main()
