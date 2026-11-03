# MAP Array Numeric Input + Sequential Tokens

- The two slots now accept **any two different tokens in click order**. Clicking 12 then 13 displays 12 | 13. Clicking an occupied slot returns its token to the bank. RESET clears both. Answer is submitted as JSON of the two chosen tokens, e.g. ["12", "13"].
- New Math (MAP) question type: MAP Array Numeric Input, with teacher-editable directions, optional description, prompt, correct numeric answer and S3 image upload in Edit.
- `python manage.py seed_demo` adds the sample question (answer 12) with its picture intentionally blank. It will not delete existing data. In Edit, upload your own array picture.
- Directions default to `Use the information to answer the question.` for new questions; the seeded array example uses `Use the array to answer the question.`. Existing questions retain their directions.
- The next button remains disabled until the two tokens are filled or the array input is nonempty; it turns cyan when ready.
- Run `python manage.py migrate` and then `python manage.py seed_demo`. Verify migration history before deploying: new 0014 depends on the included 0013.
- Do not commit `.env` or AWS credentials.
