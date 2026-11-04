Render drag-and-drop 500 fix
================================
The legacy drag-drop coordinate-plane template previously resolved a dynamic static path from Question.drag_config.image. With WhiteNoise CompressedManifestStaticFilesStorage, a stale/missing path in production PostgreSQL can raise ValueError during template rendering, crashing the entire assessment.

The coordinate quadrant question always uses the bundled static/assessments/coordinate-plane.svg, so the template now references that known static asset directly. This does not modify data or migrations.

Deploy with the existing build.sh (collectstatic included). If 500 persists, copy the Render Python traceback; the actual cause may be different.
