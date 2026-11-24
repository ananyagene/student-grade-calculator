import os
import tempfile
import unittest
from pathlib import Path

from auth import AuthenticationManager, hash_password
from database import StudentDatabase
from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).with_name("app.py")


class FirstAdminSetupAppTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_directory.name) / "app.sqlite3"
        self.original_database_path = os.environ.get("SRMS_DATABASE_PATH")
        os.environ["SRMS_DATABASE_PATH"] = str(self.database_path)
        self.database = StudentDatabase(self.database_path)
        self.database.initialize()

    def tearDown(self):
        if self.original_database_path is None:
            os.environ.pop("SRMS_DATABASE_PATH", None)
        else:
            os.environ["SRMS_DATABASE_PATH"] = self.original_database_path
        self.temp_directory.cleanup()

    def run_app(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=10).run()
        self.assertFalse(app.exception)
        return app

    def test_setup_form_handles_existing_student_and_redirects_after_creation(self):
        salt, password_hash, iterations = hash_password("StudentPassword123")
        self.assertTrue(
            self.database.create_account(
                "existing_student",
                salt,
                password_hash,
                iterations,
                "STUDENT",
            )
        )

        app = self.run_app()
        self.assertIn("Create Admin Account", [item.value for item in app.subheader])
        self.assertEqual(
            [item.label for item in app.form_submit_button],
            ["Create Account"],
        )

        app.text_input[0].set_value("new_admin")
        app.text_input[1].set_value("SecurePassword123")
        app.text_input[2].set_value("DifferentPassword123")
        app.form_submit_button[0].click().run()
        self.assertEqual(self.database.admin_count(), 0)
        self.assertIn("Passwords do not match.", [item.value for item in app.error])

        app.text_input[1].set_value("short")
        app.text_input[2].set_value("short")
        app.form_submit_button[0].click().run()
        self.assertEqual(self.database.admin_count(), 0)
        self.assertIn(
            "Password must contain at least 8 characters.",
            [item.value for item in app.error],
        )

        app.text_input[1].set_value("SecurePassword123")
        app.text_input[2].set_value("SecurePassword123")
        app.form_submit_button[0].click().run()
        self.assertEqual(self.database.admin_count(), 1)
        self.assertIn("Sign in", [item.value for item in app.subheader])
        self.assertIn(
            "Administrator account created. Please sign in.",
            [item.value for item in app.success],
        )
        self.assertFalse(app.form_submit_button)

    def test_existing_admin_sees_only_login_form(self):
        auth = AuthenticationManager(self.database)
        self.assertTrue(auth.create_admin("existing_admin", "SecurePassword123"))

        app = self.run_app()

        self.assertIn("Sign in", [item.value for item in app.subheader])
        self.assertNotIn(
            "Create Admin Account",
            [item.value for item in app.subheader],
        )
        self.assertFalse(app.form_submit_button)
        self.assertIn("Login", [item.label for item in app.button])


if __name__ == "__main__":
    unittest.main()
