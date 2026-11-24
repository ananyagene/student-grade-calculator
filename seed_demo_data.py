from pathlib import Path

from calculations import (
    get_average_marks,
    get_grade,
    get_percentage,
    get_subject_status,
    get_total_marks,
)
from database import StudentDatabase, SyntheticSeedConflict


DATABASE_PATH = Path(__file__).resolve().with_name("student_results.sqlite3")
SUBJECT_NAMES = ["Python", "Mathematics", "Data Science", "DSA", "Git & GitHub"]


def get_performance_category(percentage):
    if percentage >= 90:
        return "Outstanding"
    if percentage >= 75:
        return "Excellent"
    if percentage >= 60:
        return "Good"
    if percentage >= 40:
        return "Needs Improvement"
    return "Poor"


def get_remarks(percentage):
    if percentage >= 90:
        return "Excellent"
    if percentage >= 80:
        return "Very Good"
    if percentage >= 70:
        return "Good"
    if percentage >= 60:
        return "Satisfactory"
    if percentage >= 40:
        return "Needs Improvement"
    return "Failed"


def build_synthetic_results():
    students = [
        ("Aarav Sharma", "DEMO101", [95, 92, 90, 94, 96]),
        ("Diya Mehta", "DEMO102", [85, 82, 88, 80, 90]),
        ("Kabir Verma", "DEMO103", [74, 68, 72, 70, 76]),
        ("Ananya Rao", "DEMO104", [62, 58, 65, 60, 64]),
        ("Rohan Gupta", "DEMO105", [45, 38, 52, 48, 55]),
    ]
    results = []
    for student_name, roll_number, marks in students:
        total = get_total_marks(marks)
        percentage = get_percentage(total, 5)
        pass_count = sum(
            1 for subject_marks in marks
            if get_subject_status(subject_marks) == "Pass"
        )
        overall_result = "Pass" if pass_count == len(marks) else "Fail"
        results.append({
            "student_name": student_name,
            "roll_number": roll_number,
            "semester": "Semester 1",
            "academic_year": "2026-2027",
            "subject_count": 5,
            "subject_names": list(SUBJECT_NAMES),
            "subject_marks": list(marks),
            "total_marks": total,
            "average_marks": get_average_marks(total, 5),
            "percentage": percentage,
            "overall_grade": get_grade(percentage),
            "overall_result": overall_result,
            "performance_category": get_performance_category(percentage),
            "remarks": get_remarks(percentage),
            "is_synthetic": 1,
        })
    return results


def seed(database=None):
    if database is None:
        database = StudentDatabase(DATABASE_PATH)
    database.initialize()
    try:
        return database.seed_synthetic_results(build_synthetic_results())
    except SyntheticSeedConflict as error:
        raise SystemExit(str(error))


if __name__ == "__main__":
    result = seed()
    print(
        f"Synthetic student seed complete: "
        f"{result['inserted']} inserted, {result['skipped']} skipped."
    )
