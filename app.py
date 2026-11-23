import csv
import io

import streamlit as st

from calculations import (
    are_subject_marks_valid,
    are_subject_names_valid,
    clean_subject_names,
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


st.title("Student Grade Calculator")
st.write("Welcome! Enter your details and marks to calculate your grade.")


def reset_fields():
    st.session_state["name"] = ""
    st.session_state["subject_count"] = 5
    for index in range(1, 11):
        st.session_state[f"subject{index}_name"] = f"Subject {index}"
        st.session_state[f"marks{index}"] = 0


st.button("Reset", on_click=reset_fields)

name = st.text_input("Enter Student Name", key="name")

subject_count = st.number_input(
    "Number of Subjects",
    min_value=3,
    max_value=10,
    value=5,
    step=1,
    key="subject_count",
)

subject_names_input = []
subject_marks = []

for index in range(1, subject_count + 1):
    name_key = f"subject{index}_name"
    marks_key = f"marks{index}"
    st.session_state.setdefault(name_key, f"Subject {index}")
    st.session_state.setdefault(marks_key, 0)

    subject_name = st.text_input(
        f"Subject {index} Name",
        key=name_key,
    )
    subject_names_input.append(subject_name)
    subject_marks.append(
        st.number_input(
            f"{subject_name.strip() or f'Subject {index}'} Marks",
            min_value=0,
            max_value=100,
            key=marks_key,
        )
    )


if st.button("Calculate Result"):
    name = clean_student_name(name)
    if name == "":
        st.error("Please enter the student name.")
        st.stop()

    subject_names = clean_subject_names(subject_names_input)
    if not are_subject_names_valid(subject_names):
        st.error("Please enter a name for all selected subjects.")
        st.stop()

    if not are_subject_marks_valid(subject_marks, subject_count):
        st.error(
            f"Please enter valid numeric marks for all {subject_count} "
            "subjects between 0 and 100."
        )
        st.stop()

    total = get_total_marks(subject_marks)
    highest_marks = get_highest_marks(subject_marks)
    lowest_marks = get_lowest_marks(subject_marks)
    average_marks = get_average_marks(total, subject_count)
    strongest_subjects = get_tied_subject_names(
        subject_names,
        subject_marks,
        highest_marks,
    )
    weakest_subjects = get_tied_subject_names(
        subject_names,
        subject_marks,
        lowest_marks,
    )

    passed_subjects = 0
    failed_subjects = 0
    for marks in subject_marks:
        if get_subject_status(marks) == "Pass":
            passed_subjects += 1
        else:
            failed_subjects += 1

    percentage = get_percentage(total, subject_count)

    if percentage >= 90:
        performance_category = "Outstanding"
    elif percentage >= 75:
        performance_category = "Excellent"
    elif percentage >= 60:
        performance_category = "Good"
    elif percentage >= 40:
        performance_category = "Needs Improvement"
    else:
        performance_category = "Poor"

    if percentage >= 90:
        grade = "A"
    elif percentage >= 80:
        grade = "B"
    elif percentage >= 70:
        grade = "C"
    elif percentage >= 60:
        grade = "D"
    elif percentage >= 40:
        grade = "E"
    else:
        grade = "F"

    result = "Pass" if percentage >= 40 else "Fail"

    if percentage >= 90:
        remarks = "Excellent"
    elif percentage >= 80:
        remarks = "Very Good"
    elif percentage >= 70:
        remarks = "Good"
    elif percentage >= 60:
        remarks = "Satisfactory"
    elif percentage >= 40:
        remarks = "Needs Improvement"
    else:
        remarks = "Failed"

    st.success("Result Calculated Successfully!")
    st.subheader("Student Result")
    st.write("**Student Name:**", name)

    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("Total Marks", f"{total} / {subject_count * 100}")
    metric2.metric("Percentage", f"{round(percentage, 2)}%")
    metric3.metric("Average Marks", f"{average_marks} / 100")
    metric4.metric("Overall Grade", grade)

    st.write("**Result:**", result)
    st.write("**Remarks:**", remarks)
    st.write("**Performance Category:**", performance_category)
    st.write("**Highest Subject Marks:**", highest_marks, "/ 100")
    st.write("**Lowest Subject Marks:**", lowest_marks, "/ 100")

    st.subheader("Result Summary")
    st.write("**Number of Subjects:**", len(subject_marks))
    st.write("**Passed Subjects:**", passed_subjects)
    st.write("**Failed Subjects:**", failed_subjects)

    st.subheader("Subject-Wise Grades")
    subject_table = []
    for index in range(subject_count):
        subject_status = get_subject_status(subject_marks[index])
        subject_table.append({
            "Subject": subject_names[index],
            "Marks": subject_marks[index],
            "Grade": get_grade(subject_marks[index]),
            "Pass/Fail Status": subject_status,
        })
    st.table(subject_table)

    st.subheader("Subject Performance Chart")
    subject_chart_data = dict(zip(subject_names, subject_marks))
    st.bar_chart(
        subject_chart_data,
        x_label="Subject",
        y_label="Marks",
        alt=f"Bar chart showing marks out of 100 for {subject_count} subjects",
    )

    st.subheader("Subject Performance Insights")
    st.write(
        "**Strongest Subject(s):**",
        ", ".join(strongest_subjects),
        "-", highest_marks, "/ 100",
    )
    st.write(
        "**Weakest Subject(s):**",
        ", ".join(weakest_subjects),
        "-", lowest_marks, "/ 100",
    )

    st.subheader("Subject Improvement Suggestions")
    for index in range(subject_count):
        if subject_marks[index] >= 90:
            suggestion = "Excellent performance. Keep it up!"
        elif subject_marks[index] >= 75:
            suggestion = "Very good. Continue practicing."
        elif subject_marks[index] >= 60:
            suggestion = "Good progress. Focus on revision."
        elif subject_marks[index] >= 40:
            suggestion = "More practice and revision recommended."
        else:
            suggestion = "Focus on fundamentals and seek additional support."

        st.write(
            "**" + subject_names[index] + ":**",
            suggestion,
        )

    st.subheader("Overall Result Feedback")
    if failed_subjects > 0:
        feedback = (
            "Give extra attention to the "
            + str(failed_subjects)
            + " failed subject(s), strengthen the basics, and revise regularly."
        )
    elif performance_category == "Outstanding":
        feedback = "An exceptional overall effort. Keep challenging yourself to maintain this level."
    elif performance_category == "Excellent":
        feedback = "A strong overall performance. Regular practice can help you reach the top level."
    elif performance_category == "Good":
        feedback = "A solid overall result. Consistent revision can make the performance even better."
    elif performance_category == "Needs Improvement":
        feedback = "You have passed all subjects. A structured study plan will help you improve overall."
    else:
        feedback = "You have passed all subjects. Keep building confidence with focused practice."
    st.write(feedback)

    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow(["Field", "Value", "Grade", "Status"])
    csv_writer.writerow(["Student Name", name, "", ""])
    for index in range(subject_count):
        subject_status = get_subject_status(subject_marks[index])
        csv_writer.writerow([
            subject_names[index],
            subject_marks[index],
            get_grade(subject_marks[index]),
            subject_status,
        ])

    csv_writer.writerow(["Total Marks", total, "", ""])
    csv_writer.writerow(["Percentage", round(percentage, 2), "", ""])
    csv_writer.writerow(["Average Marks", average_marks, "", ""])
    csv_writer.writerow(["Overall Grade", grade, "", ""])
    csv_writer.writerow(["Overall Result", result, "", ""])
    csv_writer.writerow(["Performance Category", performance_category, "", ""])
    csv_writer.writerow(["Highest Marks", highest_marks, "", ""])
    csv_writer.writerow(["Lowest Marks", lowest_marks, "", ""])

    csv_data = "\ufeff" + csv_buffer.getvalue()
    st.download_button(
        "Download Result as CSV",
        data=csv_data,
        file_name="student_result.csv",
        mime="text/csv",
    )
