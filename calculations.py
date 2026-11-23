import math


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
