import csv
import io
import os
from pathlib import Path

import streamlit as st
from report_card import generate_report_card_pdf
from database import StudentDatabase
from auth import AuthenticationManager, PBKDF2_ITERATIONS
from csv_import import parse_student_csv, csv_template

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

DATABASE_PATH = Path(os.environ.get(
    "SRMS_DATABASE_PATH", str(Path(__file__).resolve().with_name("student_results.sqlite3"))
))
student_database = StudentDatabase(DATABASE_PATH)
student_database.initialize()
authentication_manager = AuthenticationManager(student_database)

st.session_state.setdefault("authenticated_account", None)

st.set_page_config(
    page_title="Student Grade Calculator",
    page_icon=":material/school:",
    layout="wide",
)

if st.session_state["authenticated_account"] is None:
    st.title("Student Grade Calculator", icon=":material/school:")
    st.caption("Secure account access")

    if authentication_manager.account_count() == 0:
        env_username = os.getenv("ADMIN_USERNAME", "").strip()
        env_password = os.getenv("ADMIN_PASSWORD", "")

        if env_username and env_password:
            try:
                created = authentication_manager.create_admin(env_username, env_password)
                if created:
                    st.success("First-run administrator account created from environment setup.")
                    st.rerun()
            except ValueError as error:
                st.error(str(error))

        st.subheader("First-run administrator setup")
        st.caption("This setup appears only until the first administrator account exists.")
        with st.form("first_admin_setup"):
            setup_username = st.text_input("Administrator username")
            setup_password = st.text_input("Administrator password", type="password")
            confirm_password = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create administrator")

        if submitted:
            if setup_password != confirm_password:
                st.error("Passwords do not match.")
            elif len(setup_password) < 8:
                st.error("Password must contain at least 8 characters.")
            else:
                try:
                    created = authentication_manager.create_admin(
                        setup_username,
                        setup_password,
                    )
                    if created:
                        st.success("Administrator account created. Please sign in.")
                        st.rerun()
                    else:
                        st.error("Could not create the administrator account.")
                except ValueError as error:
                    st.error(str(error))
        st.stop()

    st.subheader("Sign in")
    login_role = st.selectbox("Account type", ["ADMIN", "STUDENT"])
    login_username = st.text_input("Username or Student ID")
    login_password = st.text_input("Password", type="password")

    if st.button("Login", type="primary", icon=":material/login:", width="stretch"):
        account = authentication_manager.authenticate(
            login_username,
            login_password,
            login_role,
        )
        if account:
            st.session_state["authenticated_account"] = account
            st.rerun()
        else:
            st.error("Sign-in failed. Check your account type, username, and password.")
    st.stop()

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

authenticated_account = st.session_state["authenticated_account"]

if authentication_manager.is_student(authenticated_account):
    st.title("Student Dashboard", icon=":material/person:")

    student_result = student_database.get_student_result_for_account(
        authenticated_account
    )
    if not student_result:
        st.info("No academic result is currently linked to this account.")
    else:
        st.subheader("My Academic Result")
        st.write("**Student Name:**", student_result["student_name"])
        st.write("**Roll Number:**", student_result["roll_number"])
        st.write("**Semester:**", student_result["semester"])
        st.write("**Academic Year:**", student_result["academic_year"])

        metric1, metric2, metric3, metric4 = st.columns(4)
        metric1.metric(
            "Percentage",
            f"{round(student_result['percentage'], 2)}%",
            border=True,
        )
        metric2.metric(
            "Average Marks",
            f"{student_result['average_marks']} / 100",
            border=True,
        )
        metric3.metric(
            "Overall Grade",
            student_result["overall_grade"],
            border=True,
        )
        metric4.metric(
            "Result",
            student_result["overall_result"],
            border=True,
        )

        subject_table = []
        for index, subject_name in enumerate(student_result["subject_names"]):
            marks = student_result["subject_marks"][index]
            subject_table.append({
                "Subject": subject_name,
                "Marks": marks,
                "Grade": get_grade(marks),
                "Pass/Fail Status": "Pass" if marks >= 40 else "Fail",
            })
        st.table(subject_table)

        history = student_database.get_result_history(
            student_result["roll_number"],
            student_result["semester"],
            student_result["academic_year"],
        )
        st.subheader("My Result History")
        if history:
            st.table([
                {
                    "Version": entry["version"],
                    "Timestamp": entry["timestamp"],
                    "Percentage": entry["percentage"],
                    "Overall Grade": entry["overall_grade"],
                    "Pass/Fail": entry["overall_result"],
                }
                for entry in history
            ])
        else:
            st.caption("No previous result versions are available.")

        subject_pdf_rows = [
            {
                "name": student_result["subject_names"][index],
                "marks": student_result["subject_marks"][index],
                "grade": get_grade(student_result["subject_marks"][index]),
                "status": "Pass" if student_result["subject_marks"][index] >= 40 else "Fail",
            }
            for index in range(student_result["subject_count"])
        ]
        report_data = {
            "student_name": student_result["student_name"],
            "roll_number": student_result["roll_number"],
            "semester": student_result["semester"],
            "academic_year": student_result["academic_year"],
            "subjects": subject_pdf_rows,
            "total_marks": student_result["total_marks"],
            "maximum_marks": student_result["subject_count"] * 100,
            "percentage": student_result["percentage"],
            "average_marks": student_result["average_marks"],
            "overall_grade": student_result["overall_grade"],
            "overall_result": student_result["overall_result"],
            "performance_category": student_result["performance_category"],
            "remarks": student_result["remarks"],
        }
        st.download_button(
            "Download My Report Card",
            data=generate_report_card_pdf(report_data),
            file_name="my_student_report_card.pdf",
            mime="application/pdf",
            icon=":material/picture_as_pdf:",
        )

    if st.button("Logout", type="secondary", icon=":material/logout:"):
        authentication_manager.clear_authenticated_session(st.session_state)
        st.rerun()
    st.stop()

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
    if st.button(
        "Logout",
        type="secondary",
        icon=":material/logout:",
        width="stretch",
    ):
        authentication_manager.clear_authenticated_session(st.session_state)
        st.rerun()
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

    with st.form("edit_identity_" + str(selected_index)):
        edited_name = st.text_input("Edit student name", selected_student["student_name"])
        edited_roll = st.text_input("Edit roll number", selected_student["roll_number"])
        semesters = [f"Semester {n}" for n in range(1, 9)]
        if selected_student["semester"] not in semesters:
            semesters.append(selected_student["semester"])
        edited_semester = st.selectbox("Edit semester", semesters, index=semesters.index(selected_student["semester"]))
        edited_year = st.text_input("Edit academic year", selected_student["academic_year"])
        edit_submit = st.form_submit_button("Save student identity")
    if edit_submit:
        import re
        if not edited_name.strip() or not edited_roll.strip() or not re.fullmatch(r"\d{4}-\d{4}", edited_year) or int(edited_year[5:]) != int(edited_year[:4]) + 1:
            st.error("Enter a name, roll number and consecutive academic years (YYYY-YYYY).")
        else:
            edited = dict(selected_student, student_name=edited_name, roll_number=edited_roll, semester=edited_semester, academic_year=edited_year)
            if student_database.update_active_result_for_account(authenticated_account, edited, (selected_student["roll_number"], selected_student["semester"], selected_student["academic_year"])):
                st.session_state["history_message"] = "Student identity updated."
                st.rerun()
            else:
                st.error("Update failed: duplicate identity or missing record.")

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
            updated = student_database.update_active_result_for_account(
                authenticated_account,
                st.session_state["last_calculated_result"],
            )
            if updated:
                st.session_state["history_message"] = (
                    "Existing result updated and previous result added to history."
                )
                active_students = student_database.get_active_results()
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

st.subheader("Admin Dashboard", icon=":material/dashboard:")
if active_students:
    st.caption(f"Managing {len(active_students)} active academic results")
    st.markdown("**Recently Updated Results**")
    recent_results = sorted(
        active_students, key=lambda r: r.get("updated_at", ""), reverse=True
    )[:5]
    st.dataframe(get_saved_student_table(recent_results), hide_index=True)
else:
    st.info("No saved results yet. Create or import academic records to populate the dashboard.")

st.subheader("Saved Student Results", icon=":material/groups:")

if authentication_manager.is_admin(authenticated_account):
    st.subheader("Student Account Provisioning", icon=":material/person_add:")
    if active_students:
        provisioning_options = [
            f"{student['student_name']} | {student['roll_number']} | "
            f"{student['semester']} | {student['academic_year']}"
            for student in active_students
        ]
        selected_provisioning = st.selectbox(
            "Select student account",
            provisioning_options,
            key="provision_student",
        )
        provision_index = provisioning_options.index(selected_provisioning)
        provision_student = active_students[provision_index]

        with st.form("student_account_form"):
            provision_username = st.text_input("Student username")
            provision_password = st.text_input(
                "Initial password",
                type="password",
            )
            provision_confirm = st.text_input(
                "Confirm initial password",
                type="password",
            )
            provision_submitted = st.form_submit_button(
                "Create Student Account",
                icon=":material/person_add:",
            )

        if provision_submitted:
            if provision_password != provision_confirm:
                st.error("Passwords do not match.")
            elif len(provision_password) < 8:
                st.error("Password must contain at least 8 characters.")
            else:
                created = authentication_manager.provision_student(
                    provision_username,
                    provision_password,
                    provision_student["roll_number"],
                    provision_student["semester"],
                    provision_student["academic_year"],
                )
                if created:
                    st.success("Student account created successfully.")
                else:
                    st.error(
                        "Student account could not be created. "
                        "Check the username and student identity."
                    )
    else:
        st.caption("Save a student result before provisioning an account.")

if st.session_state["last_calculated_result"] is not None:
    if st.button(
        "Save Student Result",
        type="primary",
        icon=":material/save:",
        width="stretch",
    ):
        saved = student_database.save_active_result_for_account(
            authenticated_account,
            st.session_state["last_calculated_result"]
        )
        if saved:
            st.session_state["save_message"] = "Student result saved successfully."
            active_students = student_database.get_active_results()
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

# Filters are applied to reporting views, never to database writes.
st.subheader("Academic Filters", icon=":material/filter_alt:")
filter_semester_col, filter_year_col = st.columns(2)
with filter_semester_col:
    selected_semester = st.selectbox(
        "Filter by Semester", ["All"] + [f"Semester {n}" for n in range(1, 9)],
        key="admin_semester_filter",
    )
with filter_year_col:
    available_years = sorted({str(s["academic_year"]) for s in active_students})
    selected_year = st.selectbox(
        "Filter by Academic Year", ["All"] + available_years,
        key="admin_year_filter",
    )
filtered_students = [
    student for student in active_students
    if (selected_semester == "All" or str(student["semester"]) == selected_semester)
    and (selected_year == "All" or str(student["academic_year"]) == selected_year)
]

saved_table = get_saved_student_table(filtered_students)
if saved_table:
    st.table(saved_table)
else:
    st.caption("No student results saved yet.")

st.subheader("Delete Academic Result", icon=":material/delete:")
if active_students:
    delete_labels = [
        f"{r['student_name']} | {r['roll_number']} | {r['semester']} | {r['academic_year']}"
        for r in active_students
    ]
    with st.form("delete_result_form"):
        delete_selection = st.selectbox("Select academic record", range(len(delete_labels)),
                                        format_func=lambda i: delete_labels[i])
        confirm_delete = st.checkbox("I confirm that this academic result should be deleted")
        delete_submitted = st.form_submit_button("Delete selected result")
    if delete_submitted:
        if not confirm_delete:
            st.warning("Confirm deletion before continuing.")
        else:
            selected_record = active_students[delete_selection]
            if student_database.delete_result_for_account(
                authenticated_account, selected_record["roll_number"],
                selected_record["semester"], selected_record["academic_year"]
            ):
                st.success("Academic result deleted.")
                st.rerun()
            else:
                st.error("Could not delete this result.")
else:
    st.caption("No academic results to delete.")

st.subheader("Bulk CSV Import", icon=":material/upload_file:")
st.download_button("Download CSV Template", csv_template(), "student_import_template.csv", "text/csv")
uploaded_csv = st.file_uploader("Upload student results CSV", type=["csv"], key="bulk_student_csv")
if uploaded_csv is not None:
    try:
        parsed_rows, csv_errors = parse_student_csv(uploaded_csv.getvalue())
        st.caption(f"{len(parsed_rows)} valid rows; {len(csv_errors)} rows with errors")
        if csv_errors:
            st.dataframe(csv_errors, hide_index=True)
        if parsed_rows:
            st.dataframe(get_saved_student_table(parsed_rows), hide_index=True)
            with st.form("confirm_csv_import"):
                confirmed_csv = st.checkbox("I confirm importing the valid rows shown above")
                submit_csv = st.form_submit_button("Import valid students")
            if submit_csv:
                if not confirmed_csv:
                    st.warning("Confirm the import first.")
                else:
                    imported_count, skipped_count = 0, 0
                    for record in parsed_rows:
                        if student_database.save_active_result_for_account(authenticated_account, record):
                            imported_count += 1
                        else:
                            skipped_count += 1
                    st.success(f"Imported {imported_count}; skipped {skipped_count} duplicates.")
                    st.rerun()
    except ValueError as csv_error:
        st.error(str(csv_error))

st.subheader("Search Student", icon=":material/search:")
search_query = st.text_input("Search by Name or Roll Number")

if not filtered_students:
    st.info("No student results match the selected filters.")
else:
    search_results = search_saved_students(
        filtered_students,
        search_query,
    )
    if search_results:
        st.table(get_saved_student_table(search_results))
    else:
        st.warning("No matching students found.")

st.subheader("Class Leaderboard", icon=":material/emoji_events:")
leaderboard = get_class_leaderboard(filtered_students)
if leaderboard:
    st.table(leaderboard)
else:
    st.info("Save at least one student result to create the class leaderboard.")

st.subheader("Class Analytics", icon=":material/analytics:")
class_analytics = get_class_analytics(filtered_students)

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
grade_distribution = get_grade_distribution(filtered_students)
if filtered_students:
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


st.subheader("Admin Audit Log", icon=":material/receipt_long:")
audit_action = st.selectbox("Audit event type", ["All", "CREATE_RESULT", "UPDATE_RESULT", "DELETE_RESULT"])
audit_rows = student_database.get_audit_logs_for_account(authenticated_account, audit_action)
if audit_rows:
    st.dataframe([{
        "Timestamp (UTC)": row["timestamp"],
        "Administrator": row["actor_username"],
        "Action": row["action"],
        "Record": row["target_reference"],
        "Description": row["description"],
    } for row in audit_rows], hide_index=True)
else:
    st.caption("No audit events for this selection.")
