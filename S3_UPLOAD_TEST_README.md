# S3 upload test (v12)

1. Install dependencies: `pip install -r requirements.txt`.
2. Configure server/Render environment variables:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_STORAGE_BUCKET_NAME` (your bucket name)
   - `AWS_S3_REGION_NAME` (bucket region, e.g. us-east-1)
3. Run `python manage.py migrate` and create a staff account if needed: `python manage.py createsuperuser`.
4. Start Django, log in at `/admin/`, then open `/teacher/s3-upload-test/`.
5. Upload a JPEG/PNG/GIF/WebP under 5 MB. A temporary signed image link should appear.

IAM permission: `s3:PutObject` and `s3:GetObject` for `arn:aws:s3:::YOUR_BUCKET_NAME/questions/*`. The existing bucket policy allowing this prefix should work if attached to the correct IAM principal. Bucket ListBucket is optional for this test. No public access or bucket ACL is needed.

This is a diagnostic page only, not an integration into the question authoring UI. It does not change the existing question-image storage. Delete test objects under `questions/s3-test/` manually if desired. Errors are logged server-side; no secrets are shown to visitors. Staff login is required.

## Local .env setup (Windows / macOS / Linux)

1. Copy `.env.example` to `.env` in the same directory as `manage.py`.
   Windows PowerShell: `Copy-Item .env.example .env`
2. Replace the placeholders with your real bucket, region, and IAM access keys.
3. Run `pip install -r requirements.txt` and `python manage.py runserver`.
4. Sign in at `/admin/`, then visit `/teacher/s3-upload-test/`.

`config/settings.py` loads `.env` automatically. Existing environment variables take priority, so Render configuration remains unchanged. Do not commit or upload `.env`; `.gitignore` already excludes it.


## Signature V4 fix (2026-11-03)
The test view explicitly uses botocore Config(signature_version="s3v4", s3={"addressing_style": "virtual"}) for both upload and 10-minute presigned GET URLs. Set AWS_S3_REGION_NAME to the actual S3 bucket region in local .env or Render Environment. A presigned URL expires after 10 minutes. The bucket can remain private; IAM must allow s3:PutObject and s3:GetObject under questions/.
