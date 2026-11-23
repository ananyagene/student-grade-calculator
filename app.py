import streamlit as st

# App title
st.title("Student Grade Calculator")

# Welcome message
st.write("Welcome! Enter your details and marks to calculate your grade.")

# Student name input
name = st.text_input("Enter Student Name")

# Subject marks inputs (each out of 100)
marks1 = st.number_input("Subject 1 Marks", min_value=0, max_value=100, value=0)
marks2 = st.number_input("Subject 2 Marks", min_value=0, max_value=100, value=0)
marks3 = st.number_input("Subject 3 Marks", min_value=0, max_value=100, value=0)
marks4 = st.number_input("Subject 4 Marks", min_value=0, max_value=100, value=0)
marks5 = st.number_input("Subject 5 Marks", min_value=0, max_value=100, value=0)

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

        # Display final result
        st.success("Result Calculated Successfully!")
        st.write("**Student Name:**", name)
        st.write("**Total Marks:**", total, "/ 500")
        st.write("**Percentage:**", round(percentage, 2), "%")
        st.write("**Grade:**", grade)
