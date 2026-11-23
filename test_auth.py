import tempfile
import unittest
from pathlib import Path

from auth import AuthenticationManager, hash_password, verify_password
from database import StudentDatabase


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_directory.name) / "auth.sqlite3"
        self.database = StudentDatabase(self.database_path)
        self.database.initialize()
        self.auth = AuthenticationManager(self.database)

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_password_hashing_and_verification(self):
        salt, password_hash, iterations = hash_password("SecurePassword123")
        self.assertTrue(verify_password("SecurePassword123", salt, password_hash, iterations))
        self.assertFalse(verify_password("WrongPassword", salt, password_hash, iterations))

    def test_unique_salts(self):
        salt1, hash1, _ = hash_password("SecurePassword123")
        salt2, hash2, _ = hash_password("SecurePassword123")
        self.assertNotEqual(salt1, salt2)
        self.assertNotEqual(hash1, hash2)

    def test_admin_login_success_and_unknown_account(self):
        self.assertTrue(self.auth.create_admin("admin", "SecurePassword123"))
        account = self.auth.authenticate("admin", "SecurePassword123", "ADMIN")
        self.assertIsNotNone(account)
        self.assertEqual(account["role"], "ADMIN")
        self.assertIsNone(self.auth.authenticate("unknown", "SecurePassword123", "ADMIN"))

    def test_admin_incorrect_password(self):
        self.auth.create_admin("admin", "SecurePassword123")
        self.assertIsNone(
            self.auth.authenticate("admin", "IncorrectPassword", "ADMIN")
        )

    def test_admin_and_student_permissions(self):
        self.auth.create_admin("admin", "SecurePassword123")
        admin = self.auth.authenticate("admin", "SecurePassword123", "ADMIN")
        student = {"account_id": 2, "username": "001", "role": "STUDENT", "student_id": 1}
        self.assertTrue(self.auth.is_admin(admin))
        self.assertTrue(self.auth.can_manage_results(admin))
        self.assertTrue(self.auth.is_student(student))
        self.assertFalse(self.auth.can_manage_results(student))

    def test_student_own_result_access(self):
        result = {
            "student_name": "Ananya",
            "roll_number": "001",
            "semester": "Semester 1",
            "academic_year": "2026-2027",
            "subject_count": 5,
            "subject_names": ["Python", "Math", "DSA", "Data Science", "Git"],
            "subject_marks": [80, 80, 80, 80, 80],
            "total_marks": 400,
            "average_marks": 80,
            "percentage": 80,
            "overall_grade": "B",
            "overall_result": "Pass",
            "performance_category": "Excellent",
            "remarks": "Good",
        }
        self.database.save_active_result(result)
        student_row = self.database.connect()
        try:
            student = student_row.execute(
                "SELECT student_id FROM students WHERE roll_number = '001'"
            ).fetchone()
        finally:
            student_row.close()

        self.assertTrue(
            self.auth.provision_student(
                "001",
                "StudentPassword123",
                "001",
                "Semester 1",
                "2026-2027",
            )
        )
        account = self.auth.authenticate(
            "001",
            "StudentPassword123",
            "STUDENT",
        )
        own_result = self.database.get_student_result_for_account(account)
        self.assertIsNotNone(own_result)
        self.assertEqual(own_result["roll_number"], "001")

    def test_student_cannot_access_another_result(self):
        for name, roll in (("Ananya", "001"), ("Rohan", "002")):
            result = {
                "student_name": name,
                "roll_number": roll,
                "semester": "Semester 1",
                "academic_year": "2026-2027",
                "subject_count": 5,
                "subject_names": ["Python", "Math", "DSA", "Data Science", "Git"],
                "subject_marks": [80, 80, 80, 80, 80],
                "total_marks": 400,
                "average_marks": 80,
                "percentage": 80,
                "overall_grade": "B",
                "overall_result": "Pass",
                "performance_category": "Excellent",
                "remarks": "Good",
            }
            self.database.save_active_result(result)
        self.auth.provision_student(
            "001",
            "StudentPassword123",
            "001",
            "Semester 1",
            "2026-2027",
        )
        account = self.auth.authenticate("001", "StudentPassword123", "STUDENT")
        own = self.database.get_student_result_for_account(account)
        self.assertEqual(own["roll_number"], "001")
        self.assertNotEqual(own["roll_number"], "002")

    def test_clear_authenticated_session(self):
        session_state = {"authenticated_account": {"role": "ADMIN"}, "auth_role": "ADMIN"}
        self.auth.clear_authenticated_session(session_state)
        self.assertNotIn("authenticated_account", session_state)
        self.assertNotIn("auth_role", session_state)


if __name__ == "__main__":
    unittest.main()
