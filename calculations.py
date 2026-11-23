def get_total_marks(subject_marks):
    return sum(subject_marks)


def get_percentage(total_marks):
    return (total_marks / 500) * 100


def get_average_marks(total_marks):
    return round(total_marks / 5, 2)


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
