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
    find_saved_student,
    get_student_history,
    update_saved_student,
    reset_result_form_state,
    get_saved_student_table,
    search_saved_students,
    get_class_leaderboard,
    get_class_analytics,
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

    def test_class_analytics_empty(self):
        analytics = get_class_analytics([])
        self.assertEqual(analytics["total_students"], 0)
        self.assertEqual(analytics["class_average"], 0.0)
        self.assertEqual(analytics["highest_percentage"], 0.0)
        self.assertEqual(analytics["lowest_percentage"], 0.0)
        self.assertEqual(analytics["passed_students"], 0)
        self.assertEqual(analytics["failed_students"], 0)
        self.assertEqual(analytics["pass_rate"], 0.0)

    def test_class_analytics_one_student(self):
        students = [{"percentage": 80, "overall_result": "Pass"}]
        analytics = get_class_analytics(students)
        self.assertEqual(analytics["total_students"], 1)
        self.assertEqual(analytics["class_average"], 80.0)
        self.assertEqual(analytics["highest_percentage"], 80.0)
        self.assertEqual(analytics["lowest_percentage"], 80.0)
        self.assertEqual(analytics["passed_students"], 1)
        self.assertEqual(analytics["failed_students"], 0)
        self.assertEqual(analytics["pass_rate"], 100.0)

    def test_class_analytics_multiple_students(self):
        students = [
            {"percentage": 90, "overall_result": "Pass"},
            {"percentage": 70, "overall_result": "Pass"},
            {"percentage": 35, "overall_result": "Fail"},
        ]
        analytics = get_class_analytics(students)
        self.assertEqual(analytics["total_students"], 3)
        self.assertEqual(analytics["class_average"], 65.0)
        self.assertEqual(analytics["highest_percentage"], 90.0)
        self.assertEqual(analytics["lowest_percentage"], 35.0)
        self.assertEqual(analytics["passed_students"], 2)
        self.assertEqual(analytics["failed_students"], 1)
        self.assertEqual(analytics["pass_rate"], 66.67)

    def test_class_analytics_supports_different_subject_counts(self):
        students = [
            {"percentage": 63.33, "overall_result": "Pass", "subject_count": 3},
            {"percentage": 55, "overall_result": "Pass", "subject_count": 10},
            {"percentage": 30, "overall_result": "Fail", "subject_count": 5},
        ]
        analytics = get_class_analytics(students)
        self.assertEqual(analytics["class_average"], 49.44)
        self.assertEqual(analytics["highest_percentage"], 63.33)
        self.assertEqual(analytics["lowest_percentage"], 30.0)
        self.assertEqual(analytics["pass_rate"], 66.67)

    def test_class_analytics_does_not_mutate_saved_records(self):
        students = [
            {"percentage": 90, "overall_result": "Pass"},
            {"percentage": 70, "overall_result": "Pass"},
        ]
        original = [dict(student) for student in students]
        get_class_analytics(students)
        self.assertEqual(students, original)

    def test_search_empty_student_list(self):
        self.assertEqual(search_saved_students([]), [])

    def test_search_empty_query_returns_all_students(self):
        students = [
            {"student_name": "Ananya", "roll_number": "001"},
            {"student_name": "Rohan", "roll_number": "002"},
        ]
        results = search_saved_students(students, "   ")
        self.assertEqual(len(results), 2)

    def test_search_exact_and_partial_name(self):
        students = [
            {"student_name": "Ananya Singh", "roll_number": "001"},
            {"student_name": "Rohan Kumar", "roll_number": "002"},
        ]
        self.assertEqual(
            [student["student_name"] for student in search_saved_students(students, "Ananya Singh")],
            ["Ananya Singh"],
        )
        self.assertEqual(
            [student["student_name"] for student in search_saved_students(students, "Rohan")],
            ["Rohan Kumar"],
        )

    def test_search_exact_and_partial_roll_number(self):
        students = [
            {"student_name": "Ananya", "roll_number": "ROLL001"},
            {"student_name": "Rohan", "roll_number": "ROLL002"},
        ]
        self.assertEqual(len(search_saved_students(students, "ROLL001")), 1)
        self.assertEqual(len(search_saved_students(students, "L00")), 2)

    def test_search_is_case_insensitive(self):
        students = [{"student_name": "Ananya Singh", "roll_number": "ROLL001"}]
        self.assertEqual(len(search_saved_students(students, "ananya")), 1)
        self.assertEqual(len(search_saved_students(students, "roll001")), 1)

    def test_search_trims_query_spaces(self):
        students = [{"student_name": "Ananya Singh", "roll_number": "ROLL001"}]
        self.assertEqual(len(search_saved_students(students, "  Ananya  ")), 1)

    def test_search_no_matches(self):
        students = [{"student_name": "Ananya", "roll_number": "ROLL001"}]
        self.assertEqual(search_saved_students(students, "Meera"), [])

    def test_search_does_not_mutate_saved_records(self):
        students = [{"student_name": "Ananya", "roll_number": "ROLL001"}]
        original = [dict(student) for student in students]
        search_saved_students(students, "Ananya")
        self.assertEqual(students, original)

    def test_empty_result_history(self):
        history = []
        self.assertEqual(
            get_student_history(history, "ROLL001", "Semester 1", "2026-2027"),
            [],
        )

    def test_first_save_does_not_create_history(self):
        saved = []
        history = []
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
        self.assertEqual(history, [])
        self.assertEqual(len(saved), 1)

    def test_update_existing_result_preserves_previous_snapshot(self):
        saved = [{
            "student_name": "Ananya",
            "roll_number": "ROLL001",
            "semester": "Semester 1",
            "academic_year": "2026-2027",
            "total_marks": 400,
            "percentage": 80,
            "overall_grade": "B",
            "overall_result": "Pass",
        }]
        history = []
        updated = dict(saved[0])
        updated["total_marks"] = 450
        updated["percentage"] = 90
        updated["overall_grade"] = "A"

        self.assertTrue(update_saved_student(saved, history, updated, "2026-11-24 10:00:00"))
        self.assertEqual(saved[0]["percentage"], 90)
        self.assertEqual(history[0]["percentage"], 80)
        self.assertEqual(history[0]["version"], 1)
        self.assertEqual(history[0]["timestamp"], "2026-11-24 10:00:00")

    def test_multiple_updates_increase_versions(self):
        saved = [{
            "student_name": "Ananya",
            "roll_number": "ROLL001",
            "semester": "Semester 1",
            "academic_year": "2026-2027",
            "total_marks": 400,
            "percentage": 80,
            "overall_grade": "B",
            "overall_result": "Pass",
        }]
        history = []

        second = dict(saved[0])
        second["total_marks"] = 450
        second["percentage"] = 90
        second["overall_grade"] = "A"
        update_saved_student(saved, history, second, "2026-11-24 10:00:00")

        third = dict(saved[0])
        third["total_marks"] = 475
        third["percentage"] = 95
        update_saved_student(saved, history, third, "2026-11-24 11:00:00")

        self.assertEqual(
            [entry["version"] for entry in history],
            [1, 2],
        )
        self.assertEqual(saved[0]["percentage"], 95)

    def test_history_is_independent_for_different_students(self):
        saved = [
            {
                "student_name": "Ananya",
                "roll_number": "ROLL001",
                "semester": "Semester 1",
                "academic_year": "2026-2027",
                "total_marks": 400,
                "percentage": 80,
                "overall_grade": "B",
                "overall_result": "Pass",
            },
            {
                "student_name": "Rohan",
                "roll_number": "ROLL002",
                "semester": "Semester 1",
                "academic_year": "2026-2027",
                "total_marks": 300,
                "percentage": 60,
                "overall_grade": "D",
                "overall_result": "Pass",
            },
        ]
        history = []

        ananya_update = dict(saved[0])
        ananya_update["percentage"] = 90
        rohan_update = dict(saved[1])
        rohan_update["percentage"] = 70
        update_saved_student(saved, history, ananya_update, "2026-11-24 10:00:00")
        update_saved_student(saved, history, rohan_update, "2026-11-24 10:05:00")

        ananya_history = get_student_history(
            history, "ROLL001", "Semester 1", "2026-2027"
        )
        rohan_history = get_student_history(
            history, "ROLL002", "Semester 1", "2026-2027"
        )
        self.assertEqual(len(ananya_history), 1)
        self.assertEqual(len(rohan_history), 1)
        self.assertEqual(ananya_history[0]["percentage"], 80)
        self.assertEqual(rohan_history[0]["percentage"], 60)

    def test_update_missing_student_returns_false(self):
        saved = []
        history = []
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
        self.assertFalse(update_saved_student(saved, history, result))
        self.assertEqual(saved, [])
        self.assertEqual(history, [])

    def test_history_snapshot_is_immutable_and_active_is_separate(self):
        saved = [{
            "student_name": "Ananya",
            "roll_number": "ROLL001",
            "semester": "Semester 1",
            "academic_year": "2026-2027",
            "total_marks": 400,
            "percentage": 80,
            "overall_grade": "B",
            "overall_result": "Pass",
        }]
        history = []
        updated = dict(saved[0])
        updated["percentage"] = 95
        update_saved_student(saved, history, updated, "2026-11-24 10:00:00")

        updated["percentage"] = 10
        self.assertEqual(saved[0]["percentage"], 95)
        self.assertEqual(history[0]["percentage"], 80)

    def test_active_records_remain_separate_from_history(self):
        saved = [{
            "student_name": "Ananya",
            "roll_number": "ROLL001",
            "semester": "Semester 1",
            "academic_year": "2026-2027",
            "total_marks": 400,
            "percentage": 80,
            "overall_grade": "B",
            "overall_result": "Pass",
        }]
        history = []
        updated = dict(saved[0])
        updated["percentage"] = 95
        updated["total_marks"] = 475
        update_saved_student(saved, history, updated, "2026-11-24 10:00:00")

        leaderboard = get_class_leaderboard(saved)
        analytics = get_class_analytics(saved)
        self.assertEqual(leaderboard[0]["Percentage"], 95)
        self.assertEqual(analytics["highest_percentage"], 95)
        self.assertEqual(history[0]["percentage"], 80)

    def test_reset_preserves_saved_students_and_history(self):
        session_state = {
            "name": "Ananya",
            "roll_number": "ROLL001",
            "semester": "Semester 5",
            "academic_year": "2025-2026",
            "last_calculated_result": {"percentage": 90},
            "save_message": "Saved",
            "subject_count": 8,
            "saved_students": [{"roll_number": "ROLL001"}],
            "result_history": [{"version": 1}],
        }

        reset_result_form_state(session_state)

        self.assertEqual(session_state["name"], "")
        self.assertEqual(session_state["roll_number"], "")
        self.assertEqual(session_state["semester"], "Semester 1")
        self.assertEqual(session_state["academic_year"], "2026-2027")
        self.assertEqual(session_state["subject_count"], 5)
        self.assertIsNone(session_state["last_calculated_result"])
        self.assertEqual(session_state["saved_students"], [{"roll_number": "ROLL001"}])
        self.assertEqual(session_state["result_history"], [{"version": 1}])

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
