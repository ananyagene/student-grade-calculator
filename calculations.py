import math
import re
import copy
from datetime import datetime


def get_total_marks(subject_marks):
    return sum(subject_marks)


def get_percentage(total_marks, subject_count=5):
    if not are_subject_count_valid(subject_count):
        raise ValueError("Subject count must be between 3 and 10.")
    return round((total_marks / (subject_count * 100)) * 100, 2)


def get_average_marks(total_marks, subject_count=5):
    if not are_subject_count_valid(subject_count):
        raise ValueError("Subject count must be between 3 and 10.")
    return round(total_marks / subject_count, 2)


def get_grade(marks):
    if marks >= 90:
        return "A"
    elif marks >= 80:
        return "B"
    elif marks >= 70:
        return "C"
    elif marks >= 60:
        return "D"
    elif marks >= 40:
        return "E"
    else:
        return "F"


def get_subject_status(marks):
    if marks >= 40:
        return "Pass"
    else:
        return "Fail"


def get_highest_marks(subject_marks):
    return max(subject_marks)


def get_lowest_marks(subject_marks):
    return min(subject_marks)


def clean_student_name(name):
    if not isinstance(name, str):
        return ""
    return name.strip()


def clean_roll_number(roll_number):
    if not isinstance(roll_number, str):
        return ""
    return roll_number.strip()


def is_valid_academic_year(academic_year):
    if not isinstance(academic_year, str):
        return False

    academic_year = academic_year.strip()
    if not re.fullmatch(r"\d{4}-\d{4}", academic_year):
        return False

    first_year = int(academic_year[:4])
    second_year = int(academic_year[5:])
    return second_year == first_year + 1


def get_semester_options():
    return [f"Semester {semester}" for semester in range(1, 9)]


def clean_subject_names(subject_names):
    cleaned_names = []
    for name in subject_names:
        if isinstance(name, str):
            cleaned_names.append(name.strip())
        else:
            cleaned_names.append("")
    return cleaned_names


def are_subject_names_valid(subject_names):
    if not isinstance(subject_names, list):
        return False
    if not are_subject_count_valid(len(subject_names)):
        return False
    for name in subject_names:
        if not isinstance(name, str) or name.strip() == "":
            return False
    return True


def are_subject_count_valid(subject_count):
    if isinstance(subject_count, bool) or not isinstance(subject_count, int):
        return False
    return 3 <= subject_count <= 10


def are_subject_marks_valid(subject_marks, subject_count=None):
    if subject_count is None:
        subject_count = 5
    if not are_subject_count_valid(subject_count):
        return False
    if len(subject_marks) != subject_count:
        return False

    for marks in subject_marks:
        if isinstance(marks, bool) or not isinstance(marks, (int, float)):
            return False
        if not math.isfinite(marks):
            return False
        if marks < 0 or marks > 100:
            return False

    return True


def get_tied_subject_names(subject_names, subject_marks, target_marks):
    tied_names = []
    for index in range(len(subject_names)):
        if subject_marks[index] == target_marks:
            tied_names.append(subject_names[index])
    return tied_names


def is_duplicate_saved_result(saved_students, student_result):
    roll_number = str(student_result["roll_number"]).strip().upper()
    semester = str(student_result["semester"]).strip()
    academic_year = str(student_result["academic_year"]).strip()

    for saved in saved_students:
        if (
            str(saved["roll_number"]).strip().upper() == roll_number
            and str(saved["semester"]).strip() == semester
            and str(saved["academic_year"]).strip() == academic_year
        ):
            return True
    return False


def save_student_result(saved_students, student_result):
    if is_duplicate_saved_result(saved_students, student_result):
        return False

    saved_students.append(copy.deepcopy(student_result))
    return True


def get_saved_student_table(saved_students):
    table_rows = []
    for student in saved_students:
        table_rows.append({
            "Student Name": student["student_name"],
            "Roll Number": student["roll_number"],
            "Semester": student["semester"],
            "Academic Year": student["academic_year"],
            "Total Marks": student["total_marks"],
            "Percentage": student["percentage"],
            "Overall Grade": student["overall_grade"],
            "Pass/Fail": student["overall_result"],
        })
    return table_rows


def get_class_leaderboard(saved_students):
    if not saved_students:
        return []

    ordered_students = sorted(
        (copy.deepcopy(student) for student in saved_students),
        key=lambda student: (
            -float(student["percentage"]),
            str(student["student_name"]).strip().lower(),
            str(student["roll_number"]).strip().lower(),
        ),
    )

    leaderboard = []
    previous_percentage = None
    current_rank = 0

    for position, student in enumerate(ordered_students, start=1):
        percentage = float(student["percentage"])
        if previous_percentage is None or percentage != previous_percentage:
            current_rank = position

        leaderboard.append({
            "Rank": current_rank,
            "Student Name": student["student_name"],
            "Roll Number": student["roll_number"],
            "Semester": student["semester"],
            "Academic Year": student["academic_year"],
            "Percentage": student["percentage"],
            "Overall Grade": student["overall_grade"],
            "Pass/Fail": student["overall_result"],
        })
        previous_percentage = percentage

    return leaderboard


def get_class_analytics(saved_students):
    if not saved_students:
        return {
            "total_students": 0,
            "class_average": 0.0,
            "highest_percentage": 0.0,
            "lowest_percentage": 0.0,
            "passed_students": 0,
            "failed_students": 0,
            "pass_rate": 0.0,
        }

    percentages = [
        float(student["percentage"])
        for student in saved_students
    ]
    passed_students = 0
    for student in saved_students:
        if str(student["overall_result"]).strip().lower() == "pass":
            passed_students += 1

    total_students = len(saved_students)
    failed_students = total_students - passed_students

    return {
        "total_students": total_students,
        "class_average": round(sum(percentages) / total_students, 2),
        "highest_percentage": round(max(percentages), 2),
        "lowest_percentage": round(min(percentages), 2),
        "passed_students": passed_students,
        "failed_students": failed_students,
        "pass_rate": round((passed_students / total_students) * 100, 2),
    }


def search_saved_students(saved_students, query=""):
    if not saved_students:
        return []

    search_query = str(query).strip().lower()
    if search_query == "":
        return [copy.deepcopy(student) for student in saved_students]

    matches = []
    for student in saved_students:
        student_name = str(student["student_name"]).strip().lower()
        roll_number = str(student["roll_number"]).strip().lower()
        if search_query in student_name or search_query in roll_number:
            matches.append(copy.deepcopy(student))
    return matches


def find_saved_student(saved_students, roll_number, semester, academic_year):
    roll_number = str(roll_number).strip().upper()
    for index, student in enumerate(saved_students):
        if (
            str(student["roll_number"]).strip().upper() == roll_number
            and str(student["semester"]).strip() == str(semester).strip()
            and str(student["academic_year"]).strip() == str(academic_year).strip()
        ):
            return index
    return None


def get_student_history(result_history, roll_number, semester, academic_year):
    identity = (
        str(roll_number).strip().upper(),
        str(semester).strip(),
        str(academic_year).strip(),
    )
    entries = []
    for entry in result_history:
        entry_identity = (
            str(entry["roll_number"]).strip().upper(),
            str(entry["semester"]).strip(),
            str(entry["academic_year"]).strip(),
        )
        if entry_identity == identity:
            entries.append(copy.deepcopy(entry))
    entries.sort(key=lambda entry: entry["version"])
    return entries


def update_saved_student(saved_students, result_history, new_result, timestamp=None):
    index = find_saved_student(
        saved_students,
        new_result["roll_number"],
        new_result["semester"],
        new_result["academic_year"],
    )
    if index is None:
        return False

    active_result = copy.deepcopy(saved_students[index])
    previous_history = get_student_history(
        result_history,
        active_result["roll_number"],
        active_result["semester"],
        active_result["academic_year"],
    )

    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    historical_entry = copy.deepcopy(active_result)
    historical_entry["timestamp"] = timestamp
    historical_entry["version"] = len(previous_history) + 1
    result_history.append(historical_entry)

    saved_students[index] = copy.deepcopy(new_result)
    return True


def reset_result_form_state(session_state):
    session_state["name"] = ""
    session_state["roll_number"] = ""
    session_state["semester"] = "Semester 1"
    session_state["academic_year"] = "2026-2027"
    session_state["last_calculated_result"] = None
    session_state["save_message"] = ""
    session_state["subject_count"] = 5
    for index in range(1, 11):
        session_state[f"subject{index}_name"] = f"Subject {index}"
        session_state[f"marks{index}"] = 0
