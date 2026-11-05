# Reset all teacher note positions

Windows: double-click `RESET_TEACHER_NOTES_WINDOWS.bat` from the Django project folder, enter RESET.

Cross-platform: `python manage.py reset_teacher_note_positions --yes`

This changes ONLY x/y for all FreeAnnotation rows in the configured database. It does not delete note text, questions, assessments, or submissions. It resets manually dragged positions, too. Back up your database first.

The default position is viewport top-left (8px from top and left), with three cards stacked and a 12px gap. This is independent of M-TEST, MAP, and future interface layout. Manually dragged notes continue to save their own positions.

The command operates on the database specified by the Django environment variables/settings where you run it. For a remote Render database, run it in an environment connected to that database.
