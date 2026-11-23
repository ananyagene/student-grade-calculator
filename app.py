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
