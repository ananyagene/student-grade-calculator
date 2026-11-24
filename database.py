import sqlite3
from datetime import datetime
from pathlib import Path


class SyntheticSeedConflict(Exception):
    pass


class StudentDatabase:
    def __init__(self, database_path):
        self.database_path = str(database_path)

    def connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self):
        connection = self.connect()
        try:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS students (
                    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    roll_number TEXT NOT NULL,
                    semester TEXT NOT NULL,
                    academic_year TEXT NOT NULL,
                    is_synthetic INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE (roll_number, semester, academic_year)
                );

                CREATE TABLE IF NOT EXISTS active_results (
                    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL UNIQUE,
                    subject_count INTEGER NOT NULL CHECK (subject_count BETWEEN 3 AND 10),
                    total_marks INTEGER NOT NULL,
                    percentage REAL NOT NULL,
                    average_marks REAL NOT NULL,
                    overall_grade TEXT NOT NULL,
                    overall_result TEXT NOT NULL,
                    performance_category TEXT NOT NULL,
                    remarks TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS active_subjects (
                    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    result_id INTEGER NOT NULL,
                    position INTEGER NOT NULL,
                    subject_name TEXT NOT NULL,
                    marks INTEGER NOT NULL,
                    grade TEXT NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY (result_id) REFERENCES active_results(result_id)
                        ON DELETE CASCADE,
                    UNIQUE (result_id, position)
                );

                CREATE TABLE IF NOT EXISTS accounts (
                    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_salt BLOB NOT NULL,
                    password_hash BLOB NOT NULL,
                    iterations INTEGER NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('ADMIN', 'STUDENT')),
                    student_id INTEGER UNIQUE,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                        ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS result_history (
                    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    version INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    student_name TEXT NOT NULL,
                    roll_number TEXT NOT NULL,
                    semester TEXT NOT NULL,
                    academic_year TEXT NOT NULL,
                    subject_count INTEGER NOT NULL,
                    total_marks INTEGER NOT NULL,
                    percentage REAL NOT NULL,
                    average_marks REAL NOT NULL,
                    overall_grade TEXT NOT NULL,
                    overall_result TEXT NOT NULL,
                    performance_category TEXT NOT NULL,
                    remarks TEXT NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                        ON DELETE CASCADE,
                    UNIQUE (student_id, version)
                );

                CREATE TABLE IF NOT EXISTS history_subjects (
                    history_subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    history_id INTEGER NOT NULL,
                    position INTEGER NOT NULL,
                    subject_name TEXT NOT NULL,
                    marks INTEGER NOT NULL,
                    grade TEXT NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY (history_id) REFERENCES result_history(history_id)
                        ON DELETE CASCADE,
                    UNIQUE (history_id, position)
                );

                CREATE INDEX IF NOT EXISTS idx_students_identity
                    ON students(roll_number, semester, academic_year);
                CREATE INDEX IF NOT EXISTS idx_active_results_percentage
                    ON active_results(percentage);
                CREATE INDEX IF NOT EXISTS idx_result_history_student
                    ON result_history(student_id, version);
                """
            )
            student_columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(students)")
            }
            if "is_synthetic" not in student_columns:
                connection.execute(
                    "ALTER TABLE students "
                    "ADD COLUMN is_synthetic INTEGER NOT NULL DEFAULT 0"
                )
            connection.commit()
        finally:
            connection.close()

    def _now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def account_count(self):
        connection = self.connect()
        try:
            row = connection.execute(
                "SELECT COUNT(*) AS account_count FROM accounts"
            ).fetchone()
            return int(row["account_count"])
        finally:
            connection.close()

    def create_account(
        self,
        username,
        password_salt,
        password_hash,
        iterations,
        role,
        student_id=None,
    ):
        connection = self.connect()
        timestamp = self._now()
        try:
            connection.execute("BEGIN")
            connection.execute(
                """
                INSERT INTO accounts (
                    username, password_salt, password_hash, iterations,
                    role, student_id, is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
                """,
                (
                    username.strip().lower(),
                    password_salt,
                    password_hash,
                    iterations,
                    role,
                    student_id,
                    timestamp,
                    timestamp,
                ),
            )
            connection.commit()
            return True
        except sqlite3.IntegrityError:
            connection.rollback()
            return False
        finally:
            connection.close()

    def get_account_by_username(self, username):
        connection = self.connect()
        try:
            row = connection.execute(
                """
                SELECT account_id, username, password_salt, password_hash,
                       iterations, role, student_id, is_active
                FROM accounts
                WHERE username = ? AND is_active = 1
                """,
                (username.strip().lower(),),
            ).fetchone()
            if not row:
                return None
            return dict(row)
        finally:
            connection.close()

    def get_account_by_id(self, account_id):
        connection = self.connect()
        try:
            row = connection.execute(
                """
                SELECT account_id, username, role, student_id, is_active
                FROM accounts
                WHERE account_id = ? AND is_active = 1
                """,
                (account_id,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            connection.close()

    def save_active_result_for_account(self, account, result):
        if not account or account["role"] != "ADMIN":
            return False
        return self.save_active_result(result)

    def update_active_result_for_account(self, account, result):
        if not account or account["role"] != "ADMIN":
            return False
        return self.update_active_result(result)

    def get_student_result_for_account(self, account):
        if not account or account["role"] != "STUDENT":
            return None
        if not account["student_id"]:
            return None
        connection = self.connect()
        try:
            row = connection.execute(
                """
                SELECT
                    s.student_id, s.student_name, s.roll_number,
                    s.semester, s.academic_year, s.is_synthetic,
                    ar.result_id, ar.subject_count, ar.total_marks,
                    ar.percentage, ar.average_marks, ar.overall_grade,
                    ar.overall_result, ar.performance_category, ar.remarks,
                    ar.version, ar.created_at, ar.updated_at
                FROM students s
                JOIN active_results ar ON ar.student_id = s.student_id
                WHERE s.student_id = ?
                """,
                (account["student_id"],),
            ).fetchone()
            if not row:
                return None
            subjects = connection.execute(
                """
                SELECT position, subject_name, marks, grade, status
                FROM active_subjects
                WHERE result_id = ?
                ORDER BY position
                """,
                (row["result_id"],),
            ).fetchall()
            return {
                "student_name": row["student_name"],
                "roll_number": row["roll_number"],
                "semester": row["semester"],
                "academic_year": row["academic_year"],
                "subject_count": row["subject_count"],
                "subject_names": [subject["subject_name"] for subject in subjects],
                "subject_marks": [subject["marks"] for subject in subjects],
                "total_marks": row["total_marks"],
                "percentage": row["percentage"],
                "average_marks": row["average_marks"],
                "overall_grade": row["overall_grade"],
                "overall_result": row["overall_result"],
                "performance_category": row["performance_category"],
                "remarks": row["remarks"],
                "version": row["version"],
            }
        finally:
            connection.close()

    def provision_student_account(self, username, password_salt, password_hash,
                                  iterations, roll_number, semester, academic_year):
        connection = self.connect()
        timestamp = self._now()
        try:
            connection.execute("BEGIN")
            student = connection.execute(
                """
                SELECT student_id
                FROM students
                WHERE roll_number = ? AND semester = ? AND academic_year = ?
                """,
                (
                    roll_number.strip().upper(),
                    semester.strip(),
                    academic_year.strip(),
                ),
            ).fetchone()
            if not student:
                connection.rollback()
                return False
            connection.execute(
                """
                INSERT INTO accounts (
                    username, password_salt, password_hash, iterations,
                    role, student_id, is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, 'STUDENT', ?, 1, ?, ?)
                """,
                (
                    username.strip().lower(),
                    password_salt,
                    password_hash,
                    iterations,
                    student["student_id"],
                    timestamp,
                    timestamp,
                ),
            )
            connection.commit()
            return True
        except sqlite3.IntegrityError:
            connection.rollback()
            return False
        finally:
            connection.close()

    def save_active_result(self, result):
        if not self._validate_result(result):
            raise ValueError("Invalid active result data")
        timestamp = self._now()
        connection = self.connect()
        try:
            connection.execute("BEGIN")
            existing = connection.execute(
                """
                SELECT student_id
                FROM students
                WHERE roll_number = ? AND semester = ? AND academic_year = ?
                """,
                (
                    result["roll_number"].strip().upper(),
                    result["semester"].strip(),
                    result["academic_year"].strip(),
                ),
            ).fetchone()
            if existing:
                connection.rollback()
                return False

            cursor = connection.execute(
                """
                INSERT INTO students (
                    student_name, roll_number, semester, academic_year,
                    is_synthetic, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result["student_name"].strip(),
                    result["roll_number"].strip().upper(),
                    result["semester"].strip(),
                    result["academic_year"].strip(),
                    int(result.get("is_synthetic", 0)),
                    timestamp,
                    timestamp,
                ),
            )
            student_id = cursor.lastrowid
            cursor = connection.execute(
                """
                INSERT INTO active_results (
                    student_id, subject_count, total_marks, percentage,
                    average_marks, overall_grade, overall_result,
                    performance_category, remarks, version, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                """,
                (
                    student_id,
                    int(result["subject_count"]),
                    int(result["total_marks"]),
                    float(result["percentage"]),
                    float(result["average_marks"]),
                    result["overall_grade"],
                    result["overall_result"],
                    result["performance_category"],
                    result["remarks"],
                    timestamp,
                    timestamp,
                ),
            )
            result_id = cursor.lastrowid
            subject_names = result["subject_names"]
            subject_marks = result["subject_marks"]
            for position, (subject_name, marks) in enumerate(
                zip(subject_names, subject_marks),
                start=1,
            ):
                connection.execute(
                    """
                    INSERT INTO active_subjects (
                        result_id, position, subject_name, marks, grade, status
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        result_id,
                        position,
                        subject_name.strip(),
                        int(marks),
                        self._grade_for_percentage(int(marks)),
                        "Pass" if int(marks) >= 40 else "Fail",
                    ),
                )
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _validate_result(self, result):
        subject_count = int(result["subject_count"])
        if subject_count < 3 or subject_count > 10:
            return False
        subject_names = result["subject_names"]
        subject_marks = result["subject_marks"]
        if len(subject_names) != subject_count or len(subject_marks) != subject_count:
            return False
        for name in subject_names:
            if not isinstance(name, str) or name.strip() == "":
                return False
        for marks in subject_marks:
            if isinstance(marks, bool):
                return False
            try:
                numeric_marks = float(marks)
            except (TypeError, ValueError):
                return False
            if numeric_marks < 0 or numeric_marks > 100:
                return False
        return True

    def _grade_for_percentage(self, percentage):
        if percentage >= 90:
            return "A"
        if percentage >= 80:
            return "B"
        if percentage >= 70:
            return "C"
        if percentage >= 60:
            return "D"
        if percentage >= 40:
            return "E"
        return "F"

    def get_active_results(self):
        connection = self.connect()
        try:
            rows = connection.execute(
                """
                SELECT
                    s.student_id, s.student_name, s.roll_number,
                    s.semester, s.academic_year, s.is_synthetic,
                    ar.result_id, ar.subject_count, ar.total_marks,
                    ar.percentage, ar.average_marks, ar.overall_grade,
                    ar.overall_result, ar.performance_category, ar.remarks,
                    ar.version, ar.created_at, ar.updated_at
                FROM students s
                JOIN active_results ar ON ar.student_id = s.student_id
                ORDER BY s.student_name COLLATE NOCASE, s.roll_number
                """
            ).fetchall()

            results = []
            for row in rows:
                subject_rows = connection.execute(
                    """
                    SELECT position, subject_name, marks, grade, status
                    FROM active_subjects
                    WHERE result_id = ?
                    ORDER BY position
                    """,
                    (row["result_id"],),
                ).fetchall()
                results.append({
                    "student_name": row["student_name"],
                    "roll_number": row["roll_number"],
                    "semester": row["semester"],
                    "academic_year": row["academic_year"],
                    "is_synthetic": bool(row["is_synthetic"]),
                    "subject_count": row["subject_count"],
                    "subject_names": [
                        subject["subject_name"] for subject in subject_rows
                    ],
                    "subject_marks": [
                        subject["marks"] for subject in subject_rows
                    ],
                    "total_marks": row["total_marks"],
                    "percentage": row["percentage"],
                    "average_marks": row["average_marks"],
                    "overall_grade": row["overall_grade"],
                    "overall_result": row["overall_result"],
                    "performance_category": row["performance_category"],
                    "remarks": row["remarks"],
                    "version": row["version"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                })
            return results
        finally:
            connection.close()

    def update_active_result(self, new_result):
        if not self._validate_result(new_result):
            raise ValueError("Invalid active result data")
        timestamp = self._now()
        connection = self.connect()
        try:
            connection.execute("BEGIN")
            student = connection.execute(
                """
                SELECT student_id
                FROM students
                WHERE roll_number = ? AND semester = ? AND academic_year = ?
                """,
                (
                    new_result["roll_number"].strip().upper(),
                    new_result["semester"].strip(),
                    new_result["academic_year"].strip(),
                ),
            ).fetchone()
            if not student:
                connection.rollback()
                return False

            student_id = student["student_id"]
            active = connection.execute(
                """
                SELECT
                    ar.*, s.student_name, s.roll_number,
                    s.semester, s.academic_year
                FROM active_results ar
                JOIN students s ON s.student_id = ar.student_id
                WHERE ar.student_id = ?
                """,
                (student_id,),
            ).fetchone()

            subject_rows = connection.execute(
                """
                SELECT position, subject_name, marks, grade, status
                FROM active_subjects
                WHERE result_id = ?
                ORDER BY position
                """,
                (active["result_id"],),
            ).fetchall()

            history_version = int(active["version"])
            next_version = history_version + 1
            history_cursor = connection.execute(
                """
                INSERT INTO result_history (
                    student_id, version, timestamp, student_name, roll_number,
                    semester, academic_year, subject_count,
                    total_marks, percentage, average_marks, overall_grade,
                    overall_result, performance_category, remarks
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    student_id,
                    history_version,
                    timestamp,
                    active["student_name"],
                    active["roll_number"],
                    active["semester"],
                    active["academic_year"],
                    active["subject_count"],
                    active["total_marks"],
                    active["percentage"],
                    active["average_marks"],
                    active["overall_grade"],
                    active["overall_result"],
                    active["performance_category"],
                    active["remarks"],
                ),
            )
            history_id = history_cursor.lastrowid
            for subject in subject_rows:
                connection.execute(
                    """
                    INSERT INTO history_subjects (
                        history_id, position, subject_name, marks, grade, status
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        history_id,
                        subject["position"],
                        subject["subject_name"],
                        subject["marks"],
                        subject["grade"],
                        subject["status"],
                    ),
                )

            connection.execute(
                """
                UPDATE students
                SET student_name = ?, updated_at = ?
                WHERE student_id = ?
                """,
                (
                    new_result["student_name"].strip(),
                    timestamp,
                    student_id,
                ),
            )
            connection.execute(
                """
                UPDATE active_results
                SET subject_count = ?, total_marks = ?, percentage = ?,
                    average_marks = ?, overall_grade = ?, overall_result = ?,
                    performance_category = ?, remarks = ?, version = ?,
                    updated_at = ?
                WHERE result_id = ?
                """,
                (
                    int(new_result["subject_count"]),
                    int(new_result["total_marks"]),
                    float(new_result["percentage"]),
                    float(new_result["average_marks"]),
                    new_result["overall_grade"],
                    new_result["overall_result"],
                    new_result["performance_category"],
                    new_result["remarks"],
                    next_version,
                    timestamp,
                    active["result_id"],
                ),
            )
            connection.execute(
                "DELETE FROM active_subjects WHERE result_id = ?",
                (active["result_id"],),
            )
            for position, (subject_name, marks) in enumerate(
                zip(new_result["subject_names"], new_result["subject_marks"]),
                start=1,
            ):
                connection.execute(
                    """
                    INSERT INTO active_subjects (
                        result_id, position, subject_name, marks, grade, status
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        active["result_id"],
                        position,
                        subject_name.strip(),
                        int(marks),
                        self._grade_for_percentage(int(marks)),
                        "Pass" if int(marks) >= 40 else "Fail",
                    ),
                )
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def delete_result_for_account(self, account, roll_number, semester, academic_year):
        """Delete one academic result; preserve student accounts and reject unauthorized calls."""
        if not account or account.get("role") != "ADMIN":
            return False
        connection = self.connect()
        try:
            connection.execute("BEGIN")
            student = connection.execute(
                "SELECT student_id FROM students WHERE roll_number = ? "
                "AND semester = ? AND academic_year = ?",
                (roll_number, semester, academic_year),
            ).fetchone()
            if student is None:
                connection.rollback()
                return False
            student_id = student["student_id"]
            # Remove academic data, but keep the identity if a login account references it.
            connection.execute("DELETE FROM active_results WHERE student_id = ?", (student_id,))
            connection.execute("DELETE FROM result_history WHERE student_id = ?", (student_id,))
            account_exists = connection.execute(
                "SELECT 1 FROM accounts WHERE student_id = ?", (student_id,)
            ).fetchone()
            if not account_exists:
                connection.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def get_result_history(self, roll_number, semester, academic_year):
        connection = self.connect()
        try:
            rows = connection.execute(
                """
                SELECT
                    rh.history_id, rh.version, rh.timestamp,
                    rh.student_name, rh.roll_number, rh.semester,
                    rh.academic_year, rh.subject_count, rh.total_marks,
                    rh.percentage, rh.average_marks, rh.overall_grade,
                    rh.overall_result, rh.performance_category, rh.remarks
                FROM result_history rh
                WHERE rh.roll_number = ? AND rh.semester = ? AND rh.academic_year = ?
                ORDER BY rh.version
                """,
                (roll_number.strip().upper(), semester.strip(), academic_year.strip()),
            ).fetchall()
            history = []
            for row in rows:
                history.append({
                    "history_id": row["history_id"],
                    "version": row["version"],
                    "timestamp": row["timestamp"],
                    "student_name": row["student_name"],
                    "roll_number": row["roll_number"],
                    "semester": row["semester"],
                    "academic_year": row["academic_year"],
                    "subject_count": row["subject_count"],
                    "total_marks": row["total_marks"],
                    "percentage": row["percentage"],
                    "average_marks": row["average_marks"],
                    "overall_grade": row["overall_grade"],
                    "overall_result": row["overall_result"],
                    "performance_category": row["performance_category"],
                    "remarks": row["remarks"],
                })
            return history
        finally:
            connection.close()

    def seed_synthetic_results(self, results):
        inserted = 0
        skipped = 0
        timestamp = self._now()
        connection = self.connect()
        try:
            connection.execute("BEGIN")
            for result in results:
                if not self._validate_result(result):
                    raise SyntheticSeedConflict(
                        "Synthetic student data contains invalid subjects or marks."
                    )

                roll_number = result["roll_number"].strip().upper()
                semester = result["semester"].strip()
                academic_year = result["academic_year"].strip()
                existing = connection.execute(
                    """
                    SELECT student_id, student_name, is_synthetic
                    FROM students
                    WHERE roll_number = ? AND semester = ? AND academic_year = ?
                    """,
                    (roll_number, semester, academic_year),
                ).fetchone()
                if existing:
                    if not existing["is_synthetic"]:
                        raise SyntheticSeedConflict(
                            f"Roll Number {roll_number} already belongs to "
                            "a non-synthetic student record."
                        )
                    skipped += 1
                    continue

                cursor = connection.execute(
                    """
                    INSERT INTO students (
                        student_name, roll_number, semester, academic_year,
                        is_synthetic, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, 1, ?, ?)
                    """,
                    (
                        result["student_name"].strip(),
                        roll_number,
                        semester,
                        academic_year,
                        timestamp,
                        timestamp,
                    ),
                )
                student_id = cursor.lastrowid
                cursor = connection.execute(
                    """
                    INSERT INTO active_results (
                        student_id, subject_count, total_marks, percentage,
                        average_marks, overall_grade, overall_result,
                        performance_category, remarks, version, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                    """,
                    (
                        student_id,
                        int(result["subject_count"]),
                        int(result["total_marks"]),
                        float(result["percentage"]),
                        float(result["average_marks"]),
                        result["overall_grade"],
                        result["overall_result"],
                        result["performance_category"],
                        result["remarks"],
                        timestamp,
                        timestamp,
                    ),
                )
                result_id = cursor.lastrowid
                for position, (subject_name, marks) in enumerate(
                    zip(result["subject_names"], result["subject_marks"]),
                    start=1,
                ):
                    marks = int(marks)
                    connection.execute(
                        """
                        INSERT INTO active_subjects (
                            result_id, position, subject_name, marks, grade, status
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            result_id,
                            position,
                            subject_name.strip(),
                            marks,
                            self._grade_for_percentage(marks),
                            "Pass" if marks >= 40 else "Fail",
                        ),
                    )
                inserted += 1
            connection.commit()
            return {"inserted": inserted, "skipped": skipped}
        except SyntheticSeedConflict:
            connection.rollback()
            raise
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def import_session_snapshot(self, saved_students, result_history):
        imported_active = 0
        for student in saved_students:
            if self.save_active_result(student):
                imported_active += 1

        connection = self.connect()
        try:
            connection.execute("BEGIN")
            for entry in result_history:
                student = connection.execute(
                    """
                    SELECT student_id
                    FROM students
                    WHERE roll_number = ? AND semester = ? AND academic_year = ?
                    """,
                    (
                        entry["roll_number"].strip().upper(),
                        entry["semester"].strip(),
                        entry["academic_year"].strip(),
                    ),
                ).fetchone()
                if not student:
                    continue
                existing = connection.execute(
                    """
                    SELECT history_id
                    FROM result_history
                    WHERE student_id = ? AND version = ?
                    """,
                    (student["student_id"], int(entry["version"])),
                ).fetchone()
                if existing:
                    continue
                connection.execute(
                    """
                    INSERT INTO result_history (
                        student_id, version, timestamp, student_name, roll_number,
                        semester, academic_year, subject_count,
                        total_marks, percentage, average_marks, overall_grade,
                        overall_result, performance_category, remarks
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        student["student_id"],
                        int(entry["version"]),
                        entry["timestamp"],
                        entry["student_name"],
                        entry["roll_number"].strip().upper(),
                        entry["semester"].strip(),
                        entry["academic_year"].strip(),
                        int(entry.get("subject_count", 5)),
                        int(entry["total_marks"]),
                        float(entry["percentage"]),
                        float(entry.get("average_marks", entry["total_marks"] / 5)),
                        entry["overall_grade"],
                        entry["overall_result"],
                        entry.get("performance_category", ""),
                        entry.get("remarks", ""),
                    ),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return imported_active
