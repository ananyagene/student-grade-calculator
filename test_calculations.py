import unittest
import math

from calculations import (
    are_subject_marks_valid,
    clean_student_name,
    get_average_marks,
    get_grade,
    get_highest_marks,
    get_lowest_marks,
    get_percentage,
    get_subject_status,
    get_tied_subject_names,
    get_total_marks,
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


if __name__ == "__main__":
    unittest.main()
