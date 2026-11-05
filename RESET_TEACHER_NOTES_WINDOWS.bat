@echo off
cd /d "%~dp0"
echo This will reset the POSITIONS of ALL teacher notes in the connected database.
echo Note text will NOT be deleted. Previously dragged positions will be lost.
set /p CONFIRM=Type RESET to continue: 
if /I not "%CONFIRM%"=="RESET" (
  echo Cancelled.
  pause
  exit /b 0
)
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" manage.py reset_teacher_note_positions --yes
) else if exist "venv\Scripts\python.exe" (
  "venv\Scripts\python.exe" manage.py reset_teacher_note_positions --yes
) else (
  python manage.py reset_teacher_note_positions --yes
)
pause
