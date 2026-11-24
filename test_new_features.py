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

class FinalRegressionTests(unittest.TestCase):
    setUp = NewFeaturesTests.setUp
    tearDown = NewFeaturesTests.tearDown
    def test_identity_change_preserves_history(self):
        original = build_synthetic_results()[0]
        self.assertTrue(self.db.save_active_result_for_account(self.admin, original))
        key = tuple(original[k] for k in ('roll_number', 'semester', 'academic_year'))
        edited = dict(original, roll_number='EDIT101')
        self.assertTrue(self.db.update_active_result_for_account(self.admin, edited, key))
        history = self.db.get_result_history('EDIT101', original['semester'], original['academic_year'])
        self.assertEqual(history[0]['roll_number'], original['roll_number'])
        self.assertEqual(self.db.get_result_history(*key), [])

    def test_duplicate_identity_rolls_back(self):
        first, second = build_synthetic_results()[:2]
        for result in (first, second):
            self.assertTrue(self.db.save_active_result_for_account(self.admin, result))
        key = tuple(first[k] for k in ('roll_number', 'semester', 'academic_year'))
        self.assertFalse(self.db.update_active_result_for_account(self.admin, dict(first, roll_number=second['roll_number']), key))
        self.assertEqual(self.db.get_result_history(*key), [])

    def test_auth_audit(self):
        from auth import AuthenticationManager
        manager = AuthenticationManager(self.db)
        self.assertTrue(manager.create_admin('localadmin', 'test-only-password'))
        self.assertIsNone(manager.authenticate('localadmin', 'wrong', 'ADMIN'))
        account = manager.authenticate('localadmin', 'test-only-password', 'ADMIN')
        manager.clear_authenticated_session({'authenticated_account': account})
        events = self.db.get_audit_logs_for_account(account)
        self.assertEqual([e['action'] for e in events], ['ADMIN_LOGOUT', 'ADMIN_LOGIN', 'FAILED_ADMIN_LOGIN'])
        self.assertNotIn('test-only-password', str(events))

    def test_csv_formula_protection(self):
        from csv_import import result_csv
        result = dict(build_synthetic_results()[0], student_name='=1+1')
        self.assertIn("'=1+1", result_csv(result))
