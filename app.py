import streamlit as st

# App title
st.title("Student Grade Calculator")

# Welcome message
st.write("Welcome! Enter your details and marks to calculate your grade.")

# This function runs when the Reset button is clicked
# It clears all input fields before the page reloads
def reset_fields():
    st.session_state["name"] = ""
    st.session_state["marks1"] = 0
    st.session_state["marks2"] = 0
    st.session_state["marks3"] = 0
    st.session_state["marks4"] = 0
    st.session_state["marks5"] = 0

# Reset button — calls reset_fields before the page reruns
st.button("Reset", on_click=reset_fields)

# Student name input
name = st.text_input("Enter Student Name", key="name")

# Subject marks inputs (each out of 100)
marks1 = st.number_input("Subject 1 Marks", min_value=0, max_value=100, key="marks1")
marks2 = st.number_input("Subject 2 Marks", min_value=0, max_value=100, key="marks2")
marks3 = st.number_input("Subject 3 Marks", min_value=0, max_value=100, key="marks3")
marks4 = st.number_input("Subject 4 Marks", min_value=0, max_value=100, key="marks4")
marks5 = st.number_input("Subject 5 Marks", min_value=0, max_value=100, key="marks5")

# Calculate result when button is clicked
if st.button("Calculate Result"):

    # Validate that student name is not empty
    if name == "":
        st.error("Please enter the student name.")
    else:
        # Calculate total marks out of 500
        total = marks1 + marks2 + marks3 + marks4 + marks5

        # Calculate percentage
        percentage = (total / 500) * 100

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
        st.write("**Total Marks:**", total, "/ 500")
        st.write("**Percentage:**", round(percentage, 2), "%")
        st.write("**Grade:**", grade)
        st.write("**Result:**", result)
        st.write("**Remarks:**", remarks)
