import unittest

from calculations import (
    get_average_marks,
    get_grade,
    get_highest_marks,
    get_lowest_marks,
    get_percentage,
    get_subject_status,
    get_total_marks,
)


class CalculationTests(unittest.TestCase):
    def test_total_marks(self):
        self.assertEqual(get_total_marks([80, 70, 90, 60, 85]), 385)

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


if __name__ == "__main__":
    unittest.main()
