# Findings: config

## Summary
Insecure defaults found. Two are critical.

## Findings
- app/config.py:3 – hard-coded SECRET_KEY – leaks via git history
- app/config.py:2 – DEBUG=True – stack traces exposed

## Severity
High – secret exposure

## Recommendation
1. Load SECRET_KEY from env
