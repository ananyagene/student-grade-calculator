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
