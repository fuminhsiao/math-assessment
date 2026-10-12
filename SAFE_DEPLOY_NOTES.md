# Safe deploy changes

- `seed_demo` now adds missing sample questions without deleting or overwriting Questions, Assessments, Submissions, Answers or existing annotations.
- Teacher Question authoring no longer offers general/choice annotations; old DB fields remain for compatibility.
- Teacher Explanation embeds the exact student assessment renderer per question, with the teacher annotation overlay retained. The preview is isolated in an iframe to prevent student response data from being saved.
- Back up your Render database before the first deploy. Existing teacher annotations are retained.
- The preview is an iframe: its scroll and student interactions are isolated from teacher annotations.
