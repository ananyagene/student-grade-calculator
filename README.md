# Student Result Management System

## About the Project

This is a Student Result Management System developed using Python, Streamlit and SQLite.

The application helps in calculating, storing and managing student results. It provides separate login and dashboard options for Admin and Students.

The main purpose of this project is to learn and practice Git and GitHub through different stages of project development.

## Features

### Result Calculation

- Enter student details and subject marks
- Select 3 to 10 subjects
- Calculate total marks, percentage and grade
- Display overall and subject-wise Pass/Fail status
- Calculate average, highest and lowest marks
- Display performance remarks and improvement suggestions
- Visualize subject performance using a bar chart

### Admin Features

- Create an Admin account during first-time setup
- Add, edit and delete student results
- Edit student details
- Create Student accounts
- Search students by name or roll number
- Filter results by semester and academic year
- View class performance and grade distribution
- View student leaderboard
- Import and export results using CSV files
- Generate PDF report cards
- View result history and audit logs

### Student Features

- Login using a Student account
- View personal academic results
- View previous result versions
- Download results in CSV format

### Other Features

- SQLite database for permanent data storage
- Password hashing and role-based access
- Input validation and error handling
- Sample student data for demonstration
- Automated testing

## Grading System

| Percentage | Grade |
|---|---|
| 90–100 | A |
| 80–Below 90 | B |
| 70–Below 80 | C |
| 60–Below 70 | D |
| 40–Below 60 | E |
| Below 40 | F |

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | User interface |
| SQLite | Database |
| ReportLab | PDF generation |
| unittest | Testing |
| Git | Version control |
| GitHub | Repository management |

## Project Structure

```
student-grade-calculator/
├── app.py
├── auth.py
├── database.py
├── calculations.py
├── csv_import.py
├── report_card.py
├── seed_demo_data.py
├── setup_demo.py
├── test_app_auth.py
├── test_auth.py
├── test_calculations.py
├── test_database.py
├── test_new_features.py
├── test_seed_demo_data.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/ananyagene/student-grade-calculator.git
```

### 2. Open the project folder

```bash
cd student-grade-calculator
```

### 3. Install the required libraries

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m streamlit run app.py
```

The application will open in the browser.

## How to Use

### Admin

1. Create an Admin account during the first-time setup.
2. Login using the Admin credentials.
3. Add student details, subjects and marks.
4. Calculate and save the results.
5. Manage student records and view reports.
6. Create login accounts for students.

### Student

1. Login using the account provided by the Admin.
2. View academic results and performance.
3. Check previous results and download the result.

## Demo Data

A separate demo database can be created to test the application using sample student records.

```bash
python setup_demo.py --database demo_results.sqlite3
```

For Windows PowerShell:

```powershell
$env:SRMS_DATABASE_PATH = (Resolve-Path ".\demo_results.sqlite3").Path
```

Run the application:

```bash
python -m streamlit run app.py
```

The demo database contains five sample students, one Admin account and five Student accounts. Login credentials are generated in the terminal.

## Testing

The application is tested using Python's unittest module and Streamlit AppTest.

```bash
python -m unittest discover -v
```

**Test Results:**

- Total tests: 106
- Passed: 106
- Failed: 0

The tests cover result calculations, input validation, authentication, database operations, CSV handling and other application features.

## Git and GitHub Concepts Practiced

- Repository initialization
- Staging and committing changes
- Creating and switching branches
- Branch merging
- Non-fast-forward merge
- Remote repository management
- Fetching, pulling and pushing changes
- Git tags
- GitHub releases
- Using .gitignore
- Version-based project development

The project was developed in multiple stages. New features were added through separate commits and branches before merging them into the main branch.

## Version History

The project started as a basic Student Grade Calculator and was gradually improved by adding result analysis, student management, database storage, authentication and reporting features.

**Current Version: 8.0**

## Data Privacy

Passwords are stored in hashed form. Local databases, passwords and private configuration files are excluded from the Git repository.

## Author

Developed as part of the MCA Artificial Intelligence programme for the Git and GitHub subject.
