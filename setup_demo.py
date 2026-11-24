"""Opt-in local demo database and account provisioning.

Usage: python setup_demo.py --database /path/to/demo.sqlite3
Never run against an existing production database.
"""
import argparse
import secrets
from pathlib import Path
from auth import AuthenticationManager
from database import StudentDatabase
from seed_demo_data import seed, build_synthetic_results


def setup_demo(path):
    path = Path(path).resolve()
    if path.exists():
        raise ValueError('Demo database must be a NEW file to avoid changing existing accounts.')
    if path.name == 'student_results.sqlite3':
        raise ValueError('Choose a separate demo database filename.')
    path.parent.mkdir(parents=True, exist_ok=True)
    database = StudentDatabase(path)
    database.initialize()
    seed(database)
    auth = AuthenticationManager(database)
    credentials = []
    admin_password = secrets.token_urlsafe(18)
    if not auth.create_admin('demo_admin', admin_password):
        raise RuntimeError('Failed to create demo admin')
    credentials.append(('demo_admin', admin_password, 'ADMIN'))
    for result in build_synthetic_results():
        username = result['roll_number'].lower()
        password = secrets.token_urlsafe(18)
        if not auth.provision_student(username, password, result['roll_number'],
                                      result['semester'], result['academic_year']):
            raise RuntimeError('Failed to provision ' + username)
        credentials.append((username, password, 'STUDENT'))
    return credentials


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', required=True, help='Path to NEW isolated demo SQLite file')
    args = parser.parse_args()
    try:
        credentials = setup_demo(args.database)
    except (ValueError, RuntimeError) as error:
        parser.error(str(error))
    print('Local demo accounts created. Store these passwords privately; they are not saved to source control.')
    for username, password, role in credentials:
        print(f'{role} {username}: {password}')
    print('Set SRMS_DATABASE_PATH to the absolute demo database path before starting Streamlit.')
