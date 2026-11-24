# Student Result Management System

A Student Result Management System built with Python, Streamlit, and SQLite.
It calculates and stores academic results, supports Admin and Student accounts,
and provides dashboards and reporting workflows.

This project is developed as an academic project to practice **Git and GitHub** concepts through incremental, version-based development.

## Features

- Student and Admin authentication with role-based access
- Initial Admin setup for a database that has no Admin account
- Student name and identity management
- Dynamic selection of 3 to 10 subjects, with marks from 0 to 100
- Total marks calculation (up to 1,000, depending on selected subjects)
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
- Subject Performance bar chart for selected subjects
- Strongest and weakest subject insights, including tied subjects
- Subject-wise Pass/Fail status for each subject
- Subject improvement suggestions for each subject
- Overall result feedback based on passed and failed subjects
- Downloadable CSV result
- Improved result presentation using Streamlit metrics and tables
- Improved input validation for names and subject marks
- Clear application error handling for invalid input
- SQLite persistence and versioned result history
- Admin and Student dashboards, search, filters, analytics, and leaderboard
- PDF report cards and CSV import/export
- Confirmed result deletion and Admin audit log
- Automated tests using Python's built-in unittest module and Streamlit AppTest

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
- **SQLite** — Persistent student, result, account, and audit data
- **ReportLab** — PDF report card generation
- **unittest** — Automated tests
- **Git** — Version control
- **GitHub** — Remote repository

## Project Structure

```
student-grade-calculator/
├── app.py                  # Streamlit application and dashboards
├── auth.py                 # Password hashing, login, and permissions
├── database.py             # SQLite persistence and authorization
├── calculations.py         # Result calculations and analytics
├── csv_import.py           # CSV parsing and export helpers
├── report_card.py          # PDF report card generation
├── seed_demo_data.py       # Synthetic result data
├── setup_demo.py           # Creates a new isolated demo database
├── test_*.py               # Automated unit and UI regression tests
├── requirements.txt        # Python dependencies
├── README.md               # Project and release documentation
└── .gitignore              # Local data, secrets, and generated files
```

## Installation

From the project directory, create and activate a virtual environment, then
install dependencies:

```bash
python -m venv .venv
```

PowerShell:

```bash
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Application

```bash
streamlit run app.py
```

By default, the application uses `student_results.sqlite3` beside `app.py`.
It initializes a missing database without overwriting existing records. If
there is no Admin account, the app displays the first-time setup form.

## Run Automated Tests

```bash
python -m unittest discover -v
python -m py_compile app.py auth.py database.py calculations.py csv_import.py setup_demo.py
```

The suite covers calculations, validation, authentication and permissions,
SQLite persistence, result history, audit events, CSV handling, demo setup,
and first-time Admin setup UI behavior.

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

If the selected SQLite database has no administrator account, create the initial
administrator through the setup form. Use a username of up to 64 characters
and a password of at least 8 characters. The setup is disabled once an
administrator exists; existing student accounts and records are preserved.
Passwords are hashed with PBKDF2-HMAC-SHA256. First-Admin creation is serialized
by SQLite, and subsequent Admin registrations are rejected by the backend.

Admins can create, edit, search, filter, and delete academic results; edit
student identity fields; provision Student accounts linked to saved records;
review analytics and audit events; and import/export results. Student accounts
can view their own results and history and download their CSV result, but cannot
manage results. Result deletion preserves the student identity and prior
history. Do not commit account passwords or private configuration files.

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
transactionally for administrator-initiated creation, update, deletion,
account provisioning, and bulk import. Admin login, failed login, and logout
events are also recorded. The Audit Log page is visible to Admins only.

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

### Verification

```bash
python -m unittest discover -v
python -m py_compile app.py database.py auth.py calculations.py csv_import.py setup_demo.py
```

The `.gitignore` excludes SQLite databases, bytecode, and local environment
folders, local environment files, and common credential files. Never upload
real student data, generated demo passwords, or credentials to a public
repository.

### Version history

- **8.0 (candidate):** First-time Admin setup, role-specific dashboards,
  persistent/versioned results, identity editing, audit logging, CSV import and
  export, PDF report cards, and isolated demo account setup. This candidate has
  not yet been tagged or released.
- **6.0:** Previous tagged project version.
