import streamlit as st
import csv
import io
from calculations import (
    are_subject_marks_valid,
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

# App title
st.title("Student Grade Calculator")

# Welcome message
st.write("Welcome! Enter your details and marks to calculate your grade.")

# This function runs when the Reset button is clicked
# It clears all input fields before the page reloads
def reset_fields():
    st.session_state["name"] = ""
    st.session_state["subject1_name"] = "Subject 1"
    st.session_state["subject2_name"] = "Subject 2"
    st.session_state["subject3_name"] = "Subject 3"
    st.session_state["subject4_name"] = "Subject 4"
    st.session_state["subject5_name"] = "Subject 5"
    st.session_state["marks1"] = 0
    st.session_state["marks2"] = 0
    st.session_state["marks3"] = 0
    st.session_state["marks4"] = 0
    st.session_state["marks5"] = 0

# Reset button — calls reset_fields before the page reruns
st.button("Reset", on_click=reset_fields)

# Student name input
name = st.text_input("Enter Student Name", key="name")

# Custom subject names
st.session_state.setdefault("subject1_name", "Subject 1")
st.session_state.setdefault("subject2_name", "Subject 2")
st.session_state.setdefault("subject3_name", "Subject 3")
st.session_state.setdefault("subject4_name", "Subject 4")
st.session_state.setdefault("subject5_name", "Subject 5")

subject1_name = st.text_input("Subject 1 Name", key="subject1_name")
subject2_name = st.text_input("Subject 2 Name", key="subject2_name")
subject3_name = st.text_input("Subject 3 Name", key="subject3_name")
subject4_name = st.text_input("Subject 4 Name", key="subject4_name")
subject5_name = st.text_input("Subject 5 Name", key="subject5_name")

subject_names_preview = clean_subject_names([
    subject1_name,
    subject2_name,
    subject3_name,
    subject4_name,
    subject5_name,
])

# Subject marks inputs (each out of 100)
marks1 = st.number_input(f"{subject_names_preview[0]} Marks", min_value=0, max_value=100, key="marks1")
marks2 = st.number_input(f"{subject_names_preview[1]} Marks", min_value=0, max_value=100, key="marks2")
marks3 = st.number_input(f"{subject_names_preview[2]} Marks", min_value=0, max_value=100, key="marks3")
marks4 = st.number_input(f"{subject_names_preview[3]} Marks", min_value=0, max_value=100, key="marks4")
marks5 = st.number_input(f"{subject_names_preview[4]} Marks", min_value=0, max_value=100, key="marks5")

# Calculate result when button is clicked
if st.button("Calculate Result"):

    # Remove extra spaces and validate the student name
    name = clean_student_name(name)
    if name == "":
        st.error("Please enter the student name.")
        st.stop()

    # Remove extra spaces and validate custom subject names
    subject_names = clean_subject_names([
        subject1_name,
        subject2_name,
        subject3_name,
        subject4_name,
        subject5_name,
    ])
    if not all(subject_names):
        st.error("Please enter a name for all five subjects.")
        st.stop()

    # Recheck all subject marks before calculating results
    subject_marks = [marks1, marks2, marks3, marks4, marks5]
    if not are_subject_marks_valid(subject_marks):
        st.error("Please enter valid numeric marks for all five subjects between 0 and 100.")
        st.stop()

    # Calculate total marks out of 500
    total = get_total_marks(subject_marks)

    # Calculate highest and lowest subject marks
    subject_marks = [marks1, marks2, marks3, marks4, marks5]
    highest_marks = get_highest_marks(subject_marks)
    lowest_marks = get_lowest_marks(subject_marks)
    average_marks = get_average_marks(total)
    strongest_subjects = get_tied_subject_names(
        subject_names, subject_marks, highest_marks
    )
    weakest_subjects = get_tied_subject_names(
        subject_names, subject_marks, lowest_marks
    )

    passed_subjects = 0
    failed_subjects = 0
    for marks in subject_marks:
        if get_subject_status(marks) == "Pass":
            passed_subjects = passed_subjects + 1
        else:
            failed_subjects = failed_subjects + 1

    # Calculate percentage
    percentage = get_percentage(total)

    # Determine performance category based on percentage
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

    # Determine grade based on percentage
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

    # Determine pass or fail
    if percentage >= 40:
        result = "Pass"
    else:
        result = "Fail"

    # Determine remarks based on percentage
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

    # Display final result
    st.success("Result Calculated Successfully!")
    st.subheader("Student Result")
    st.write("**Student Name:**", name)

    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("Total Marks", f"{total} / 500")
    metric2.metric("Percentage", f"{round(percentage, 2)}%")
    metric3.metric("Average Marks", f"{average_marks} / 100")
    metric4.metric("Overall Grade", grade)

    st.write("**Result:**", result)
    st.write("**Remarks:**", remarks)
    st.write("**Performance Category:**", performance_category)
    st.write("**Highest Subject Marks:**", highest_marks, "/ 100")
    st.write("**Lowest Subject Marks:**", lowest_marks, "/ 100")

    # Display a simple subject result summary
    st.subheader("Result Summary")
    st.write("**Number of Subjects:**", len(subject_marks))
    st.write("**Passed Subjects:**", passed_subjects)
    st.write("**Failed Subjects:**", failed_subjects)

    # Display marks and grade for each subject
    st.subheader("Subject-Wise Grades")
    subject_table = []
    for index in range(len(subject_names)):
        subject_status = get_subject_status(subject_marks[index])

        subject_table.append({
            "Subject": subject_names[index],
            "Marks": subject_marks[index],
            "Grade": get_grade(subject_marks[index]),
            "Pass/Fail Status": subject_status,
        })

    st.table(subject_table)

    # Display marks for all five subjects in a bar chart
    st.subheader("Subject Performance Chart")
    subject_chart_data = dict(zip(subject_names, subject_marks))
    st.bar_chart(
        subject_chart_data,
        x_label="Subject",
        y_label="Marks",
        alt="Bar chart showing marks out of 100 for five subjects",
    )

    # Display strongest and weakest subjects
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

    # Display improvement suggestions for each subject
    st.subheader("Subject Improvement Suggestions")
    for index in range(len(subject_names)):
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

    # Give one overall feedback message based on subject results
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

    # Generate CSV data for the calculated student result
    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow(["Field", "Value", "Grade", "Status"])
    csv_writer.writerow(["Student Name", name, "", ""])
    for index in range(len(subject_names)):
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
