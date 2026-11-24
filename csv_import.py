"""Validate academic CSV rows before saving them."""
import csv
import io
from calculations import get_grade, get_percentage, get_average_marks, is_valid_academic_year
from seed_demo_data import get_performance_category, get_remarks


def parse_student_csv(content):
    if len(content) > 2_000_000:
        raise ValueError("CSV exceeds the 2 MB upload limit")
    try:
        decoded = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must use UTF-8 encoding") from exc
    reader = csv.DictReader(io.StringIO(decoded))
    if reader.fieldnames is None:
        raise ValueError("CSV must include a header row")
    fields = ["student_name", "roll_number", "semester", "academic_year"]
    if any(name not in reader.fieldnames for name in fields):
        raise ValueError("Missing required student identity columns")
    count = sum(f"subject_{i}" in reader.fieldnames and f"marks_{i}" in reader.fieldnames for i in range(1, 11))
    if not 3 <= count <= 10 or any(f"subject_{i}" not in reader.fieldnames or f"marks_{i}" not in reader.fieldnames for i in range(1, count + 1)):
        raise ValueError("Provide 3–10 consecutive subject_N and marks_N column pairs")
    valid, errors, identities = [], [], set()
    for index, row in enumerate(reader, 2):
        if index > 501:
            raise ValueError("CSV can contain at most 500 students")
        try:
            name = (row["student_name"] or "").strip()
            roll = (row["roll_number"] or "").strip().upper()
            semester = (row["semester"] or "").strip()
            year = (row["academic_year"] or "").strip()
            if not name or not roll or semester not in [f"Semester {n}" for n in range(1, 9)] or not is_valid_academic_year(year):
                raise ValueError("Invalid student name, roll number, semester, or academic year")
            identity = (roll, semester, year)
            if identity in identities:
                raise ValueError("Duplicate identity within uploaded CSV")
            names = [(row[f"subject_{i}"] or "").strip() for i in range(1, count + 1)]
            if not all(names) or len({n.casefold() for n in names}) != count:
                raise ValueError("Subject names must be unique and nonempty")
            marks = []
            for i in range(1, count + 1):
                value = (row[f"marks_{i}"] or "").strip()
                if not value.isdigit() or not 0 <= int(value) <= 100:
                    raise ValueError("Marks must be whole numbers from 0 to 100")
                marks.append(int(value))
            total = sum(marks)
            percentage = get_percentage(total, count)
            valid.append({
                "student_name": name, "roll_number": roll, "semester": semester,
                "academic_year": year, "subject_count": count,
                "subject_names": names, "subject_marks": marks,
                "total_marks": total, "percentage": percentage,
                "average_marks": get_average_marks(total, count),
                "overall_grade": get_grade(percentage),
                "overall_result": "Pass" if all(m >= 40 for m in marks) else "Fail",
                "performance_category": get_performance_category(percentage),
                "remarks": get_remarks(percentage),
            })
            identities.add(identity)
        except (ValueError, TypeError, KeyError) as exc:
            errors.append({"Row": index, "Error": str(exc)})
    return valid, errors


def csv_template():
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["student_name", "roll_number", "semester", "academic_year"] +
                    [field for i in range(1, 6) for field in (f"subject_{i}", f"marks_{i}")])
    writer.writerow(["Example Student", "EXAMPLE001", "Semester 1", "2026-2027",
                     "Python", 85, "Mathematics", 82, "Data Science", 88, "DSA", 80, "Git & GitHub", 90])
    return buffer.getvalue()


def safe_csv_cell(value):
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def result_csv(result):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Field", "Value", "Grade", "Status"])
    for key in ("student_name", "roll_number", "semester", "academic_year", "total_marks", "percentage", "overall_grade", "overall_result"):
        writer.writerow([key, safe_csv_cell(result[key]), "", ""])
    for name, marks in zip(result["subject_names"], result["subject_marks"]):
        writer.writerow([safe_csv_cell(name), marks, get_grade(marks), "Pass" if marks >= 40 else "Fail"])
    return "\ufeff" + buffer.getvalue()
