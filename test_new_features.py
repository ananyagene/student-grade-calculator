import tempfile
import unittest
from pathlib import Path

from database import StudentDatabase
from csv_import import parse_student_csv, csv_template
from seed_demo_data import build_synthetic_results


class NewFeaturesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = StudentDatabase(Path(self.tmp.name) / 'test.sqlite3')
        self.db.initialize()
        self.admin = {'role': 'ADMIN', 'account_id': 12, 'username': 'testadmin'}
        self.student = {'role': 'STUDENT', 'account_id': 13, 'username': 'student'}

    def tearDown(self):
        self.tmp.cleanup()

    def test_csv_template_round_trip(self):
        valid, errors = parse_student_csv(csv_template().encode())
        self.assertEqual(len(valid), 1)
        self.assertEqual(errors, [])
        self.assertEqual(valid[0]['total_marks'], 425)

    def test_csv_invalid_marks(self):
        csv_data = csv_template().replace(',85,', ',105,')
        valid, errors = parse_student_csv(csv_data.encode())
        self.assertEqual(len(valid), 0)
        self.assertEqual(len(errors), 1)

    def test_audit_create_and_restrict_read(self):
        result = build_synthetic_results()[0]
        self.assertTrue(self.db.save_active_result_for_account(self.admin, result))
        self.assertEqual(len(self.db.get_audit_logs_for_account(self.student)), 0)
        events = self.db.get_audit_logs_for_account(self.admin)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['action'], 'CREATE_RESULT')
        self.assertEqual(events[0]['actor_username'], 'testadmin')

    def test_admin_delete_with_audit(self):
        result = build_synthetic_results()[0]
        self.db.save_active_result_for_account(self.admin, result)
        self.assertFalse(self.db.delete_result_for_account(self.student, result['roll_number'], result['semester'], result['academic_year']))
        self.assertEqual(len(self.db.get_active_results()), 1)
        self.assertTrue(self.db.delete_result_for_account(self.admin, result['roll_number'], result['semester'], result['academic_year']))
        self.assertEqual(len(self.db.get_active_results()), 0)
        events = self.db.get_audit_logs_for_account(self.admin)
        self.assertEqual([e['action'] for e in events], ['DELETE_RESULT', 'CREATE_RESULT'])


if __name__ == '__main__':
    unittest.main()
