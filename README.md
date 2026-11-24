# Student Grade Calculator

A simple Student Grade Calculator built with Python and Streamlit. This project calculates total marks, percentage, grade, pass/fail status, and remarks for a student based on five subject marks.

This project is developed as an academic project to practice **Git and GitHub** concepts through incremental, version-based development.

## Features

- Student name input
- Five subject marks inputs (0 to 100 each)
- Total marks calculation (out of 500)
- Percentage calculation
- Grade calculation (A to F)
- Pass/Fail result
- Result remarks (Excellent, Very Good, Good, Satisfactory, Needs Improvement, Failed)
- Reset button to clear all inputs
- Subject-wise grades for all five subjects
- Highest and lowest subject marks
- Average marks rounded to 2 decimal places
- Result Summary with the number of passed and failed subjects
- Performance Category based on the overall percentage
- Subject Performance bar chart for all five subjects
- Strongest and weakest subject insights, including tied subjects
- Subject-wise Pass/Fail status for each subject
- Subject improvement suggestions for each subject
- Overall result feedback based on passed and failed subjects
- Downloadable CSV result
- Improved result presentation using Streamlit metrics and tables
- Improved input validation for names and subject marks
- Clear application error handling for invalid input
- Final application polish and edge-case testing
- Automated calculation tests using Python's built-in unittest module

## Grading System

| Percentage | Grade |
|---|---|
| 90–100 | A |
| 80–89 | B |
| 70–79 | C |
| 60–69 | D |
| 40–59 | E |
| Below 40 | F |

## Technologies Used

- **Python** — Application logic
- **Streamlit** — Frontend and user interface
- **Git** — Version control
- **GitHub** — Remote repository

## Project Structure

```
student-grade-calculator/
├── app.py               # Main application file
├── calculations.py      # Calculation and validation helpers
├── test_calculations.py # Automated unittest cases
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
└── .gitignore           # Files ignored by Git
```

## Installation

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

2. Install the required package:

```bash
pip install -r requirements.txt
```

## Run Application

```bash
streamlit run app.py
```

## Run Automated Tests

Run the calculation tests from the project directory:

```bash
python -m unittest -v
```

The tests cover grade boundaries, total and average marks, percentage,
Pass/Fail status, highest and lowest marks, tied subjects, and important
edge cases such as all-zero and all-100 marks.

## Git Concepts Practiced

- Git initialization (`git init`)
- Staging changes (`git add`)
- Creating commits (`git commit`)
- Creating branches (`git branch`)
- Switching branches (`git checkout`, `git switch`)
- Merging branches (`git merge`)
- Adding remotes (`git remote add`)
- Pushing to GitHub (`git push`)

## Author

Developed as an MCA Artificial Intelligence academic project.

## Advanced SRMS Features (feature-advanced branch)

The application also includes SQLite persistence, role-based admin/student login,
subject counts from 3 to 10, versioned result history, student-specific report
cards, an admin dashboard, academic filters, grade distribution, a leaderboard,
confirmed academic-result deletion, validated CSV import, and an admin audit log.

### Accounts and access

On first launch, create an administrator through the setup form (or set
`ADMIN_USERNAME` and `ADMIN_PASSWORD` in the local environment before first
launch). Administrators can provision student accounts linked to saved records.
Student accounts can see their own results and history, but cannot edit results.
Do not commit account passwords or private configuration files.

### Bulk CSV import

An administrator can download a template, upload a UTF-8 CSV, review valid
rows and validation errors, and confirm the import. Required columns:
`student_name`, `roll_number`, `semester`, `academic_year`, followed by 3–10
consecutive `subject_N`, `marks_N` pairs. Marks must be whole numbers from 0
to 100. The importer limits files to 2 MB and 500 data rows. Existing results
are skipped, not overwritten. Imports are processed per valid record, not as
an all-or-nothing batch transaction.

### Result deletion and audit

Administrators can delete an active academic result after confirming the action.
The associated student identity and prior result-history versions are retained;
the deleted result is excluded from active analytics. Audit events are recorded
transactionally for administrator-initiated creation, update, and deletion.
The Audit Log page is visible to admins only. Login/logout and account
provisioning are **not yet covered** by audit events.

### Local isolated demo database

To create a **new** local demo SQLite database with five synthetic student
records and six accounts (one admin, five students):

```bash
python setup_demo.py --database demo_results.sqlite3
```

The command prints newly generated passwords **once** in your terminal. Keep
them private. To run the app against the demo database, set the environment
variable `SRMS_DATABASE_PATH` to the **absolute path** of `demo_results.sqlite3`
before running `streamlit run app.py`. For PowerShell:

```powershell
$env:SRMS_DATABASE_PATH = (Resolve-Path .\demo_results.sqlite3).Path
streamlit run app.py
```

The demo setup intentionally refuses to overwrite an existing database. The
original `seed_demo_data.py` remains available for idempotent synthetic-data
seeding in an existing database; it does not provision accounts.

### Testing and current limitations

```bash
python -m unittest -v
python -m py_compile app.py database.py auth.py calculations.py csv_import.py setup_demo.py
```

The automated suite checks calculations, SQLite operations, authentication,
seeding, audit authorization, deletion, and CSV parsing. Browser-based UI
verification and deployment/security review are still required. The interface
supports editing existing marks through its Result History workflow; changing
a student's roll number, semester or academic year is not yet supported.

The `.gitignore` excludes SQLite databases, bytecode, and local environment
folders. Never upload real student data or passwords to a public repository.

### Final verification notes

Administrators can correct student identity fields from the selected result's history section. Prior versions remain linked by the stable student ID. Audit events now include administrator sign-in, failed administrator sign-in, explicit sign-out, student account provisioning and imported results. Audit search and UTC date filtering operate on the latest 200 matching events. Student accounts can download their own CSV result.

Automated verification: `python -m unittest discover -v` (96 tests passed in the development environment), and `python -m compileall -q .`. Streamlit browser interaction remains a manual release check because Streamlit was unavailable in that environment. Verify both roles, editing, deletion, import, filters and downloads against a separate demo database before release.
