# Django Math Assessment Demo

An English-language Django prototype for testing this workflow:

1. An administrator manages a question bank in Django Admin.
2. A teacher selects questions and creates a question set.
3. Django generates a unique student URL.
4. A student enters a name and answers MathLive-response and multiple-choice questions.
5. Django saves the submission and displays the score.

## Run the project

```bash
python -m venv .venv
```

Activate the virtual environment using the command for your terminal:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# Git Bash on Windows
source .venv/Scripts/activate

# macOS/Linux
source .venv/bin/activate
```

Then run:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

Open:

- Teacher page: http://127.0.0.1:8000/teacher/sets/new/
- Admin: http://127.0.0.1:8000/admin/

## MathLive input

The student page uses the MathLive `<math-field>` web component. It provides formatted math entry and a virtual math keyboard. No API key or environment variable is required.

MathLive is loaded as an ES module from `https://esm.run/mathlive`, so the browser must have internet access while using this prototype. For production, install and serve MathLive locally instead of depending on the CDN.

The prototype stores the student's answer as LaTeX. Automatic scoring currently supports plain integer and decimal answers, such as `36.8`, plus exact text matching for other answers.

## Student exam flow

The student experience now uses a formal, one-question-at-a-time layout:

1. The student enters a name and starts the assessment.
2. Only one question is displayed at a time.
3. The student must answer before selecting **Next**.
4. **Back** allows review of earlier answers.
5. The final question displays **Submit Assessment**.
6. A progress bar and question counter remain visible throughout the assessment.

## Drag-and-drop image question

This version adds a third question type: **Drag and drop on image**. Run the migrations and seed command after installing dependencies:

```bash
python manage.py migrate
python manage.py seed_demo
```

The seed command creates **Coordinate Quadrants – Drag and Drop**, matching the supplied M-Test-style example. Drag configuration is stored in the Question model's `drag_config` JSON field and can be edited in Django Admin.


## Coordinate quadrant drag-and-drop

The coordinate-plane demonstration uses the four full quadrants as drop zones. Students may drag each ordered pair anywhere within the correct quadrant. Clicking an answer and then clicking a quadrant is also supported.
