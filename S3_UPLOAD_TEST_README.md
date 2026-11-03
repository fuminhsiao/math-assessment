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
