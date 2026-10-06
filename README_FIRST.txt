Setup / update
==============
1. Activate your virtual environment.
2. pip install -r requirements.txt
3. python manage.py migrate
4. python manage.py runserver

Migration 0005 intentionally resets the old demo Question Bank and creates exactly four demo questions:
- Value Input
- Multiple Choice
- Drag-and-Drop
- Multi-select

The Multi-select sample is:
Select all the expressions that are equivalent to 8(t + 4).
Correct choices: 8t + 32 and (8 × t) + (8 × 4).

Migration 0008 adds Equation Builder and the Christy plants sample item. Run: python manage.py migrate
