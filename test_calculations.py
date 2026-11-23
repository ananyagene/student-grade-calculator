import unittest
import math

from report_card import build_report_card_text, generate_report_card_pdf

from calculations import (
    are_subject_count_valid,
    are_subject_marks_valid,
    are_subject_names_valid,
    clean_subject_names,
    clean_student_name,
    clean_roll_number,
    get_average_marks,
    get_grade,
    get_highest_marks,
    get_lowest_marks,
    get_percentage,
    get_subject_status,
    get_tied_subject_names,
    get_total_marks,
    get_semester_options,
    is_valid_academic_year,
    is_duplicate_saved_result,
    save_student_result,
    get_saved_student_table,
    get_class_leaderboard,
)


class CalculationTests(unittest.TestCase):
    def test_total_marks(self):
        self.assertEqual(get_total_marks([80, 70, 90, 60, 85]), 385)

    def test_all_zero_marks(self):
        marks = [0, 0, 0, 0, 0]
        self.assertEqual(get_total_marks(marks), 0)
        self.assertEqual(get_percentage(get_total_marks(marks)), 0)
        self.assertEqual(get_subject_status(0), "Fail")

    def test_all_hundred_marks(self):
        marks = [100, 100, 100, 100, 100]
        self.assertEqual(get_total_marks(marks), 500)
        self.assertEqual(get_percentage(get_total_marks(marks)), 100)
        self.assertEqual(get_grade(100), "A")

    def test_mixed_passing_and_failing_subjects(self):
        marks = [39, 40, 70, 100, 59]
        statuses = [get_subject_status(mark) for mark in marks]
        self.assertEqual(statuses, ["Fail", "Pass", "Pass", "Pass", "Pass"])

    def test_percentage(self):
        self.assertEqual(get_percentage(385), 77.0)

    def test_average_marks(self):
        self.assertEqual(get_average_marks(385), 77.0)
        self.assertEqual(get_average_marks(389), 77.8)

    def test_grade_boundaries(self):
        boundary_marks = {
            39: "F",
            40: "E",
            59: "E",
            60: "D",
            69: "D",
            70: "C",
            79: "C",
            80: "B",
            89: "B",
            90: "A",
            100: "A",
        }
        for marks, expected_grade in boundary_marks.items():
            self.assertEqual(get_grade(marks), expected_grade)

    def test_subject_pass_fail_boundary(self):
        self.assertEqual(get_subject_status(39), "Fail")
        self.assertEqual(get_subject_status(40), "Pass")

    def test_highest_and_lowest_marks(self):
        subject_marks = [80, 70, 90, 60, 85]
        self.assertEqual(get_highest_marks(subject_marks), 90)
        self.assertEqual(get_lowest_marks(subject_marks), 60)

    def test_clean_student_name(self):
        self.assertEqual(clean_student_name("  Ananya  "), "Ananya")
        self.assertEqual(clean_student_name("   "), "")
        self.assertEqual(clean_student_name(None), "")

    def test_clean_subject_names(self):
        names = ["  Python  ", "Mathematics", " DSA ", "Data Science", "Git"]
        self.assertEqual(
            clean_subject_names(names),
            ["Python", "Mathematics", "DSA", "Data Science", "Git"],
        )

    def test_empty_or_whitespace_subject_names(self):
        names = clean_subject_names(["Python", "", "   ", "Data Science", "Git"])
        self.assertFalse(all(names))

    def test_subject_marks_validation(self):
        self.assertTrue(are_subject_marks_valid([0, 40, 59, 100, 75]))
        self.assertFalse(are_subject_marks_valid([-1, 40, 59, 100, 75]))
        self.assertFalse(are_subject_marks_valid([0, 40, 59, 101, 75]))
        self.assertFalse(are_subject_marks_valid([0, 40, "59", 100, 75]))
        self.assertFalse(are_subject_marks_valid([0, 40, 59, 100]))
        self.assertFalse(are_subject_marks_valid([0, 40, math.nan, 100, 75]))
        self.assertFalse(are_subject_marks_valid([0, 40, math.inf, 100, 75]))

    def test_tied_subject_names(self):
        names = ["Subject 1", "Subject 2", "Subject 3", "Subject 4", "Subject 5"]
        marks = [100, 100, 80, 100, 60]
        self.assertEqual(
            get_tied_subject_names(names, marks, get_highest_marks(marks)),
            ["Subject 1", "Subject 2", "Subject 4"],
        )
        lowest_marks = [100, 60, 60, 80, 60]
        self.assertEqual(
            get_tied_subject_names(names, lowest_marks, get_lowest_marks(lowest_marks)),
            ["Subject 2", "Subject 3", "Subject 5"],
        )

    def test_variable_subject_counts(self):
        self.assertTrue(are_subject_count_valid(3))
        self.assertTrue(are_subject_count_valid(5))
        self.assertTrue(are_subject_count_valid(10))
        self.assertFalse(are_subject_count_valid(2))
        self.assertFalse(are_subject_count_valid(11))

    def test_three_subject_calculation(self):
        marks = [90, 40, 60]
        total = get_total_marks(marks)
        self.assertEqual(total, 190)
        self.assertEqual(get_percentage(total, 3), 63.33)
        self.assertEqual(get_average_marks(total, 3), 63.33)
        self.assertEqual(get_highest_marks(marks), 90)
        self.assertEqual(get_lowest_marks(marks), 40)

    def test_ten_subject_calculation(self):
        marks = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]
        total = get_total_marks(marks)
        self.assertEqual(total, 550)
        self.assertEqual(get_percentage(total, 10), 55.0)
        self.assertEqual(get_average_marks(total, 10), 55.0)
        self.assertEqual(get_highest_marks(marks), 100)
        self.assertEqual(get_lowest_marks(marks), 10)

    def test_dynamic_marks_and_names_validation(self):
        names = ["Python", "DSA", "Data Science"]
        marks = [80, 70, 90]
        self.assertTrue(are_subject_names_valid(names))
        self.assertTrue(are_subject_marks_valid(marks, 3))
        self.assertFalse(are_subject_marks_valid(marks, 5))
        self.assertFalse(are_subject_names_valid(["Python", "", "Data Science"]))
        self.assertFalse(are_subject_marks_valid([80, 70], 3))

    def test_roll_number_validation(self):
        self.assertEqual(clean_roll_number("  "), "")
        self.assertEqual(clean_roll_number("  ROLL001  "), "ROLL001")
        self.assertEqual(clean_roll_number("00123"), "00123")

    def test_academic_year_validation(self):
        self.assertTrue(is_valid_academic_year("2026-2027"))
        self.assertTrue(is_valid_academic_year(" 2025-2026 "))
        self.assertFalse(is_valid_academic_year("2026"))
        self.assertFalse(is_valid_academic_year("2026-2028"))
        self.assertFalse(is_valid_academic_year("26-27"))

    def test_semester_options(self):
        semesters = get_semester_options()
        self.assertEqual(len(semesters), 8)
        self.assertEqual(semesters[0], "Semester 1")
        self.assertEqual(semesters[-1], "Semester 8")

    def test_save_one_student_result(self):
        saved = []
        result = {
            "student_name": "Ananya",
            "roll_number": "ROLL001",
            "semester": "Semester 1",
            "academic_year": "2026-2027",
            "total_marks": 400,
            "percentage": 80,
            "overall_grade": "B",
            "overall_result": "Pass",
        }
        self.assertTrue(save_student_result(saved, result))
        self.assertEqual(len(saved), 1)

    def test_save_multiple_and_duplicate_students(self):
        saved = []
        first = {
            "student_name": "Ananya",
            "roll_number": "ROLL001",
            "semester": "Semester 1",
            "academic_year": "2026-2027",
            "total_marks": 400,
            "percentage": 80,
            "overall_grade": "B",
            "overall_result": "Pass",
        }
        second = dict(first)
        second["student_name"] = "Rohan"
        second["roll_number"] = "ROLL002"

        self.assertTrue(save_student_result(saved, first))
        self.assertTrue(save_student_result(saved, second))
        self.assertEqual(len(saved), 2)

        duplicate = dict(second)
        duplicate["roll_number"] = "  roll002  "
        duplicate["student_name"] = "Changed Name"
        self.assertFalse(save_student_result(saved, duplicate))
        self.assertEqual(len(saved), 2)

    def test_saved_result_is_independent_snapshot(self):
        saved = []
        result = {
            "student_name": "Ananya",
            "roll_number": "001",
            "semester": "Semester 1",
            "academic_year": "2026-2027",
            "total_marks": 400,
            "percentage": 80,
            "overall_grade": "B",
            "overall_result": "Pass",
        }
        self.assertTrue(save_student_result(saved, result))
        result["student_name"] = "Changed"
        result["total_marks"] = 100
        self.assertEqual(saved[0]["student_name"], "Ananya")
        self.assertEqual(saved[0]["total_marks"], 400)

    def test_duplicate_roll_allowed_in_different_semester(self):
        saved = []
        first = {
            "student_name": "Ananya",
            "roll_number": "001",
            "semester": "Semester 1",
            "academic_year": "2026-2027",
            "total_marks": 400,
            "percentage": 80,
            "overall_grade": "B",
            "overall_result": "Pass",
        }
        second = dict(first)
        second["semester"] = "Semester 2"

        self.assertTrue(save_student_result(saved, first))
        self.assertTrue(save_student_result(saved, second))
        self.assertEqual(len(saved), 2)

    def test_saved_table_contains_required_columns(self):
        result = {
            "student_name": "Ananya",
            "roll_number": "001",
            "semester": "Semester 1",
            "academic_year": "2026-2027",
            "total_marks": 400,
            "percentage": 80,
            "overall_grade": "B",
            "overall_result": "Pass",
        }
        table = get_saved_student_table([result])
        self.assertEqual(len(table), 1)
        self.assertEqual(
            set(table[0]),
            {
                "Student Name",
                "Roll Number",
                "Semester",
                "Academic Year",
                "Total Marks",
                "Percentage",
                "Overall Grade",
                "Pass/Fail",
            },
        )

    def test_empty_leaderboard(self):
        self.assertEqual(get_class_leaderboard([]), [])

    def test_one_student_leaderboard(self):
        students = [{
            "student_name": "Ananya",
            "roll_number": "001",
            "semester": "Semester 1",
            "academic_year": "2026-2027",
            "percentage": 80,
            "overall_grade": "B",
            "overall_result": "Pass",
        }]
        leaderboard = get_class_leaderboard(students)
        self.assertEqual(len(leaderboard), 1)
        self.assertEqual(leaderboard[0]["Rank"], 1)

    def test_leaderboard_sorts_different_percentages(self):
        students = [
            {"student_name": "Rohan", "roll_number": "002", "semester": "Semester 1",
             "academic_year": "2026-2027", "percentage": 70, "overall_grade": "C",
             "overall_result": "Pass"},
            {"student_name": "Ananya", "roll_number": "001", "semester": "Semester 1",
             "academic_year": "2026-2027", "percentage": 90, "overall_grade": "A",
             "overall_result": "Pass"},
            {"student_name": "Meera", "roll_number": "003", "semester": "Semester 1",
             "academic_year": "2026-2027", "percentage": 80, "overall_grade": "B",
             "overall_result": "Pass"},
        ]
        leaderboard = get_class_leaderboard(students)
        self.assertEqual(
            [row["Student Name"] for row in leaderboard],
            ["Ananya", "Meera", "Rohan"],
        )
        self.assertEqual([row["Rank"] for row in leaderboard], [1, 2, 3])

    def test_leaderboard_competition_ranking_for_ties(self):
        students = [
            {"student_name": "Rohan", "roll_number": "003", "semester": "Semester 1",
             "academic_year": "2026-2027", "percentage": 80, "overall_grade": "B",
             "overall_result": "Pass"},
            {"student_name": "Ananya", "roll_number": "001", "semester": "Semester 1",
             "academic_year": "2026-2027", "percentage": 90, "overall_grade": "A",
             "overall_result": "Pass"},
            {"student_name": "Meera", "roll_number": "002", "semester": "Semester 1",
             "academic_year": "2026-2027", "percentage": 80, "overall_grade": "B",
             "overall_result": "Pass"},
            {"student_name": "Kiran", "roll_number": "004", "semester": "Semester 1",
             "academic_year": "2026-2027", "percentage": 70, "overall_grade": "C",
             "overall_result": "Pass"},
        ]
        leaderboard = get_class_leaderboard(students)
        self.assertEqual([row["Rank"] for row in leaderboard], [1, 2, 2, 4])

    def test_leaderboard_ties_use_stable_secondary_order(self):
        students = [
            {"student_name": "Zoya", "roll_number": "002", "semester": "Semester 1",
             "academic_year": "2026-2027", "percentage": 85, "overall_grade": "B",
             "overall_result": "Pass"},
            {"student_name": "Ananya", "roll_number": "003", "semester": "Semester 1",
             "academic_year": "2026-2027", "percentage": 85, "overall_grade": "B",
             "overall_result": "Pass"},
            {"student_name": "Ananya", "roll_number": "001", "semester": "Semester 1",
             "academic_year": "2026-2027", "percentage": 85, "overall_grade": "B",
             "overall_result": "Pass"},
        ]
        leaderboard = get_class_leaderboard(students)
        self.assertEqual(
            [(row["Student Name"], row["Roll Number"]) for row in leaderboard],
            [("Ananya", "001"), ("Ananya", "003"), ("Zoya", "002")],
        )

    def test_leaderboard_does_not_modify_saved_records(self):
        students = [
            {"student_name": "Rohan", "roll_number": "002", "semester": "Semester 1",
             "academic_year": "2026-2027", "percentage": 70, "overall_grade": "C",
             "overall_result": "Pass"},
            {"student_name": "Ananya", "roll_number": "001", "semester": "Semester 1",
             "academic_year": "2026-2027", "percentage": 90, "overall_grade": "A",
             "overall_result": "Pass"},
        ]
        original_names = [student["student_name"] for student in students]
        get_class_leaderboard(students)
        self.assertEqual(
            [student["student_name"] for student in students],
            original_names,
        )

    def test_leaderboard_supports_different_subject_counts(self):
        students = [
            {"student_name": "Three Subjects", "roll_number": "003",
             "semester": "Semester 1", "academic_year": "2026-2027",
             "percentage": 63.33, "overall_grade": "C", "overall_result": "Pass",
             "subject_count": 3},
            {"student_name": "Ten Subjects", "roll_number": "010",
             "semester": "Semester 1", "academic_year": "2026-2027",
             "percentage": 55, "overall_grade": "E", "overall_result": "Pass",
             "subject_count": 10},
        ]
        leaderboard = get_class_leaderboard(students)
        self.assertEqual(
            [row["Student Name"] for row in leaderboard],
            ["Three Subjects", "Ten Subjects"],
        )

    def test_report_card_generation_for_subject_counts(self):
        for subject_count in (3, 5, 10):
            subjects = []
            marks = []
            for index in range(subject_count):
                subject_name = f"Subject {index + 1}"
                mark = 40 + index
                marks.append(mark)
                subjects.append({
                    "name": subject_name,
                    "marks": mark,
                    "grade": get_grade(mark),
                    "status": get_subject_status(mark),
                })

            total = get_total_marks(marks)
            report_data = {
                "student_name": "Ananya Singh",
                "roll_number": "ROLL001",
                "semester": "Semester 3",
                "academic_year": "2026-2027",
                "subjects": subjects,
                "total_marks": total,
                "maximum_marks": subject_count * 100,
                "percentage": get_percentage(total, subject_count),
                "average_marks": get_average_marks(total, subject_count),
                "overall_grade": get_grade(get_percentage(total, subject_count)),
                "overall_result": "Pass",
                "performance_category": "Good",
                "remarks": "Good",
            }

            pdf_bytes = generate_report_card_pdf(report_data)
            self.assertTrue(len(pdf_bytes) > 100)
            self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

            report_text = build_report_card_text(report_data)
            self.assertIn("Ananya Singh", report_text)
            self.assertIn("ROLL001", report_text)
            self.assertIn("Semester 3", report_text)
            self.assertIn("2026-2027", report_text)
            self.assertIn("Generated Student Report Card", report_text)
            self.assertIn("Subject 1", report_text)
            self.assertIn(f"Subject {subject_count}", report_text)


if __name__ == "__main__":
    unittest.main()
