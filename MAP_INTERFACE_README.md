# Math (MAP) interface — v12 extension

- Subjects: Math (M-TEST) / Math (MAP) / English (M-TEST). Existing `math` and `english` records are preserved.
- New question type: MAP Image Choice (A–E), with editable directions, description, prompt, correct letter and five optional images.
- An example question is created by migration `0012_map_question.py`: Manuel paid 34¢ for gum. He gave the clerk $1. Correct answer: B (66¢). All five images are intentionally blank.
- Teacher: Question Bank → Math (MAP) → Edit. Upload images A–E (JPEG/PNG/WebP/GIF, up to 5 MB each) to private S3. Existing image keys are retained when no replacement file is selected.
- Student: five selectable answer rows, zoom controls (70–150%), five reserved blank tool buttons, reset, next, assessment title, white center and gray sides.
- Before deploying: `pip install -r requirements.txt`, `python manage.py migrate`, and configure AWS credentials, bucket and region on Render. The S3 policy must allow `questions/map/*` in addition to the earlier `questions/*` prefix.
- This version does not include the five toolbar SVGs or tool implementations, as requested.
- Existing Render databases may have a migration numbered 0012 from a different branch. Inspect `python manage.py showmigrations assessments` and reconcile the migration history before running `migrate` if necessary.
- Static syntax checks were performed; Django integration tests could not be run in the artifact environment because Django was not installed.
