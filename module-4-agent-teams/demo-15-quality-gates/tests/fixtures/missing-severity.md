# Findings: uploads

## Summary
Path traversal.

## Findings
- app/uploads.py:8 – os.path.join with user filename

## Recommendation
Use secure_filename.
