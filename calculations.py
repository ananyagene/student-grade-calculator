import math
import re
import copy


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
