import csv
import io
from pathlib import Path

import streamlit as st
from report_card import generate_report_card_pdf
from database import StudentDatabase

from calculations import (
    are_subject_marks_valid,
    are_subject_names_valid,
    clean_subject_names,
    clean_roll_number,
    clean_student_name,
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
    get_saved_student_table,
    search_saved_students,
    get_class_leaderboard,
    get_class_analytics,
    get_grade_distribution,
    save_student_result,
    find_saved_student,
    get_student_history,
    update_saved_student,
    reset_result_form_state,
    get_sample_student_data,
)

DATABASE_PATH = Path(__file__).resolve().with_name("student_results.sqlite3")
student_database = StudentDatabase(DATABASE_PATH)
student_database.initialize()

st.set_page_config(
    page_title="Student Grade Calculator",
    page_icon=":material/school:",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp { background-color: #F8FAFC; }
    h1, h2, h3 { color: #203864; }
    .stMetric { background: #FFFFFF; border: 1px solid #E2E8F0;
                border-radius: 12px; padding: 14px; }
    [data-testid="stTable"] { border: 1px solid #E2E8F0; border-radius: 10px; }
    [data-testid="stAlert"] { border-radius: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

header_left, header_right = st.columns([5, 1], vertical_alignment="bottom")
with header_left:
    st.title("Student Grade Calculator", icon=":material/school:")
    st.caption("Academic result dashboard")


def reset_fields():
    reset_result_form_state(st.session_state)


def load_demo_student():
    sample = get_sample_student_data()
    st.session_state["name"] = sample["student_name"]
    st.session_state["roll_number"] = sample["roll_number"]
    st.session_state["semester"] = sample["semester"]
    st.session_state["academic_year"] = sample["academic_year"]
    st.session_state["subject_count"] = sample["subject_count"]
    for index in range(1, 11):
        if index <= 5:
            subject_name = sample["subject_names"][index - 1]
            subject_marks = sample["subject_marks"][index - 1]
        else:
            subject_name = f"Subject {index}"
            subject_marks = 0
        st.session_state[f"subject{index}_name"] = subject_name
        st.session_state[f"marks{index}"] = subject_marks
    st.session_state["last_calculated_result"] = None
    st.session_state["save_message"] = ""


st.session_state.setdefault("last_calculated_result", None)
st.session_state.setdefault("save_message", "")
st.session_state.setdefault("result_history", [])
st.session_state.setdefault("history_message", "")
st.session_state.setdefault("_database_migration_done", False)

legacy_saved_students = st.session_state.get("saved_students", [])
legacy_result_history = st.session_state.get("result_history", [])
if (
    legacy_saved_students
    and not st.session_state["_database_migration_done"]
    and not student_database.get_active_results()
):
    st.warning(
        "Existing session-only student results were found. "
        "Import them into the local SQLite database explicitly."
    )
    if st.button(
        "Import Session Results",
        type="secondary",
        icon=":material/database:",
    ):
        imported = student_database.import_session_snapshot(
            legacy_saved_students,
            legacy_result_history,
        )
        st.session_state["_database_migration_done"] = True
        st.session_state.pop("saved_students", None)
        st.session_state.pop("result_history", None)
        st.success(
            f"Imported {imported} active student result(s) into SQLite."
        )

with header_right:
    st.button(
        "Reset",
        on_click=reset_fields,
        type="secondary",
        icon=":material/restart_alt:",
        width="stretch",
    )

with st.container(border=True, key="student-details"):
    st.subheader("Student Details", icon=":material/person:")

    demo_col, subject_count_col = st.columns([1, 3])
    with demo_col:
        st.button(
            "Load Sample Student",
            on_click=load_demo_student,
            type="secondary",
            icon=":material/science:",
            width="stretch",
        )
        st.caption("Demonstration data only")

    name_col, roll_col = st.columns(2)
    with name_col:
        name = st.text_input("Student Name", key="name")
    with roll_col:
        st.session_state.setdefault("roll_number", "")
        roll_number = st.text_input("Roll Number", key="roll_number")

    semester_col, year_col, subject_count_col = st.columns(3)
    with semester_col:
        st.session_state.setdefault("semester", "Semester 1")
        semester = st.selectbox(
            "Semester",
            get_semester_options(),
            key="semester",
        )
    with year_col:
        st.session_state.setdefault("academic_year", "2026-2027")
        academic_year = st.text_input("Academic Year", key="academic_year")
    with subject_count_col:
        subject_count = st.number_input(
            "Number of Subjects",
            min_value=3,
            max_value=10,
            value=5,
            step=1,
            key="subject_count",
        )

with st.container(border=True, key="subject-details"):
    st.subheader("Subject Details", icon=":material/menu_book:")
    subject_names_input = []
    subject_marks = []

    subject_columns = st.columns(2)
    for index in range(1, subject_count + 1):
        name_key = f"subject{index}_name"
        marks_key = f"marks{index}"
        st.session_state.setdefault(name_key, f"Subject {index}")
        st.session_state.setdefault(marks_key, 0)

        column = subject_columns[(index - 1) % 2]
        with column:
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


with st.container(horizontal=True, key="action-row"):
    calculate_result = st.button(
        "Calculate Result",
        type="primary",
        icon=":material/calculate:",
        width="stretch",
    )

if calculate_result:
    name = clean_student_name(name)
    if name == "":
        st.error("Please enter the student name.")
        st.stop()

    roll_number = clean_roll_number(roll_number)
    if roll_number == "":
        st.error("Please enter the roll number.")
        st.stop()

    academic_year = academic_year.strip()
    if not is_valid_academic_year(academic_year):
        st.error("Please enter a valid academic year in YYYY-YYYY format with consecutive years.")
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

    st.success("Result calculated successfully")

    with st.container(border=True, key="result-card"):
        st.subheader("Student Result", icon=":material/article:")

        overview_tab, subjects_tab, insights_tab = st.tabs([
            "Overview",
            "Subjects",
            "Insights",
        ])

        with overview_tab:
            info_col, summary_col = st.columns([1, 2])
            with info_col:
                st.markdown("**Student Information**")
                st.write("**Student Name:**", name)
                st.write("**Roll Number:**", roll_number)
                st.write("**Semester:**", semester)
                st.write("**Academic Year:**", academic_year)

            with summary_col:
                metric1, metric2 = st.columns(2)
                metric1.metric("Total Marks", f"{total} / {subject_count * 100}", border=True)
                metric2.metric("Percentage", f"{round(percentage, 2)}%", border=True)
                metric3, metric4 = st.columns(2)
                metric3.metric("Average Marks", f"{average_marks} / 100", border=True)
                metric4.metric("Overall Grade", grade, border=True)

            status_col, remarks_col = st.columns(2)
            with status_col:
                st.markdown("**Result Summary**")
                st.write("Overall Result:", result)
                st.write("Remarks:", remarks)
                st.write("Performance Category:", performance_category)
            with remarks_col:
                st.markdown("**Marks Range**")
                st.write("Highest:", highest_marks, "/ 100")
                st.write("Lowest:", lowest_marks, "/ 100")
                st.write("Subjects:", len(subject_marks))
                st.write("Passed:", passed_subjects)
                st.write("Failed:", failed_subjects)

        with subjects_tab:
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

            subject_chart_data = dict(zip(subject_names, subject_marks))
            st.bar_chart(
                subject_chart_data,
                x_label="Subject",
                y_label="Marks",
                alt=f"Bar chart showing marks out of 100 for {subject_count} subjects",
            )

        with insights_tab:
            insight_col1, insight_col2 = st.columns(2)
            with insight_col1:
                st.markdown("**Strongest and Weakest**")
                st.write("Strongest:", ", ".join(strongest_subjects), "-", highest_marks, "/ 100")
                st.write("Weakest:", ", ".join(weakest_subjects), "-", lowest_marks, "/ 100")
            with insight_col2:
                st.markdown("**Overall Feedback**")
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

            st.markdown("**Subject Improvement Suggestions**")
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
                st.write("**" + subject_names[index] + ":**", suggestion)

    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow(["Field", "Value", "Grade", "Status"])
    csv_writer.writerow(["Student Name", name, "", ""])
    csv_writer.writerow(["Roll Number", roll_number, "", ""])
    csv_writer.writerow(["Semester", semester, "", ""])
    csv_writer.writerow(["Academic Year", academic_year, "", ""])
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

    subject_pdf_rows = []
    for index in range(subject_count):
        subject_pdf_rows.append({
            "name": subject_names[index],
            "marks": subject_marks[index],
            "grade": get_grade(subject_marks[index]),
            "status": get_subject_status(subject_marks[index]),
        })

    report_data = {
        "student_name": name,
        "roll_number": roll_number,
        "semester": semester,
        "academic_year": academic_year,
        "subjects": subject_pdf_rows,
        "total_marks": total,
        "maximum_marks": subject_count * 100,
        "percentage": round(percentage, 2),
        "average_marks": average_marks,
        "overall_grade": grade,
        "overall_result": result,
        "performance_category": performance_category,
        "remarks": remarks,
    }
    pdf_data = generate_report_card_pdf(report_data)
    with st.container(border=True, key="download-results"):
        st.subheader("Download Results", icon=":material/download:")
        download_csv, download_pdf = st.columns(2)
        with download_csv:
            st.download_button(
                "Download Result as CSV",
                data=csv_data,
                file_name="student_result.csv",
                mime="text/csv",
                icon=":material/table_view:",
                width="stretch",
            )
        with download_pdf:
            st.download_button(
                "Download Report Card as PDF",
                data=pdf_data,
                file_name="student_report_card.pdf",
                mime="application/pdf",
                icon=":material/picture_as_pdf:",
                width="stretch",
            )

    st.session_state["last_calculated_result"] = {
        "student_name": name,
        "roll_number": roll_number,
        "semester": semester,
        "academic_year": academic_year,
        "total_marks": total,
        "percentage": round(percentage, 2),
        "average_marks": average_marks,
        "overall_grade": grade,
        "overall_result": result,
        "performance_category": performance_category,
        "remarks": remarks,
        "subject_count": subject_count,
        "subject_names": list(subject_names),
        "subject_marks": list(subject_marks),
    }
    st.session_state["save_message"] = ""

active_students = student_database.get_active_results()

st.subheader("Result History", icon=":material/history:")

if active_students:
    history_options = []
    for student in active_students:
        history_options.append(
            f"{student['student_name']} | {student['roll_number']} | "
            f"{student['semester']} | {student['academic_year']}"
        )

    selected_history = st.selectbox(
        "Select Saved Student",
        history_options,
        key="history_student",
    )
    selected_index = history_options.index(selected_history)
    selected_student = active_students[selected_index]

    st.write("**Latest Active Result**")
    st.write(
        selected_student["student_name"],
        "|",
        selected_student["roll_number"],
        "|",
        selected_student["semester"],
        "|",
        selected_student["academic_year"],
        "|",
        "Total:",
        selected_student["total_marks"],
        "|",
        selected_student["percentage"],
        "%",
        "|",
        selected_student["overall_grade"],
        "|",
        selected_student["overall_result"],
    )

    previous_history = student_database.get_result_history(
        selected_student["roll_number"],
        selected_student["semester"],
        selected_student["academic_year"],
    )
    if previous_history:
        history_table = []
        for entry in previous_history:
            history_table.append({
                "Version": entry["version"],
                "Timestamp": entry["timestamp"],
                "Student Name": entry["student_name"],
                "Roll Number": entry["roll_number"],
                "Semester": entry["semester"],
                "Academic Year": entry["academic_year"],
                "Total Marks": entry["total_marks"],
                "Percentage": entry["percentage"],
                "Overall Grade": entry["overall_grade"],
                "Pass/Fail": entry["overall_result"],
            })
        st.table(history_table)
    else:
        st.caption("No previous versions saved for this student.")

    if st.session_state["last_calculated_result"] is not None:
        if st.button(
            "Update Existing Result",
            type="secondary",
            icon=":material/update:",
            width="stretch",
        ):
            updated = student_database.update_active_result(
                st.session_state["last_calculated_result"],
            )
            if updated:
                st.session_state["history_message"] = (
                    "Existing result updated and previous result added to history."
                )
            else:
                st.session_state["history_message"] = (
                    "No matching saved student found for the current Roll Number, "
                    "Semester, and Academic Year."
                )
else:
    st.caption("No result history available.")

if st.session_state["history_message"]:
    if "updated" in st.session_state["history_message"]:
        st.success(st.session_state["history_message"])
    else:
        st.warning(st.session_state["history_message"])

st.subheader("Saved Student Results", icon=":material/groups:")

if st.session_state["last_calculated_result"] is not None:
    if st.button(
        "Save Student Result",
        type="primary",
        icon=":material/save:",
        width="stretch",
    ):
        saved = student_database.save_active_result(
            st.session_state["last_calculated_result"]
        )
        if saved:
            st.session_state["save_message"] = "Student result saved successfully."
        else:
            st.session_state["save_message"] = (
                "A result with this roll number already exists for "
                "the same semester and academic year."
            )

    if st.session_state["save_message"]:
        if "saved successfully" in st.session_state["save_message"]:
            st.success(st.session_state["save_message"])
        else:
            st.warning(st.session_state["save_message"])

saved_table = get_saved_student_table(active_students)
if saved_table:
    st.table(saved_table)
else:
    st.caption("No student results saved yet.")

st.subheader("Search Student", icon=":material/search:")
search_query = st.text_input("Search by Name or Roll Number")

if not active_students:
    st.info("No student results saved yet.")
else:
    search_results = search_saved_students(
        active_students,
        search_query,
    )
    if search_results:
        st.table(get_saved_student_table(search_results))
    else:
        st.warning("No matching students found.")

st.subheader("Class Leaderboard", icon=":material/emoji_events:")
leaderboard = get_class_leaderboard(active_students)
if leaderboard:
    st.table(leaderboard)
else:
    st.info("Save at least one student result to create the class leaderboard.")

st.subheader("Class Analytics", icon=":material/analytics:")
class_analytics = get_class_analytics(active_students)

metric_row_one = st.columns(4)
metric_row_one[0].metric("Total Students", class_analytics["total_students"], border=True)
metric_row_one[1].metric(
    "Class Average Percentage",
    f"{class_analytics['class_average']:.2f}%",
    border=True,
)
metric_row_one[2].metric(
    "Highest Percentage",
    f"{class_analytics['highest_percentage']:.2f}%",
    border=True,
)
metric_row_one[3].metric(
    "Lowest Percentage",
    f"{class_analytics['lowest_percentage']:.2f}%",
    border=True,
)

metric_row_two = st.columns(3)
metric_row_two[0].metric("Passed Students", class_analytics["passed_students"], border=True)
metric_row_two[1].metric("Failed Students", class_analytics["failed_students"], border=True)
metric_row_two[2].metric(
    "Class Pass Rate",
    f"{class_analytics['pass_rate']:.2f}%",
    border=True,
)

st.subheader("Grade Distribution", icon=":material/bar_chart:")
grade_distribution = get_grade_distribution(active_students)
if active_students:
    chart_data = {
        row["Grade"]: row["Student Count"]
        for row in grade_distribution
    }
    chart_col, table_col = st.columns([2, 1])
    with chart_col:
        st.bar_chart(
            chart_data,
            x_label="Overall Grade",
            y_label="Number of Students",
            alt="Grade distribution for active saved student results",
        )
    with table_col:
        st.table(grade_distribution)
else:
    st.info("Save at least one student result to view the grade distribution.")
