---
name: marketing-campaign-csv-audit
description: Audits exported campaign performance CSV files for a marketing analyst before the data is used in reports or dashboards. It checks column structure, missing values, duplicate records, date consistency, and suspicious metric values, then returns a concise issue summary and cleanup guidance.
---

# Marketing Campaign CSV Audit

## When to use this skill
Use this skill when the user provides or refers to a marketing campaign CSV file and wants to:
- audit the file before analysis
- check data quality
- find missing values or duplicates
- validate column structure
- detect invalid date formats
- identify suspicious numeric values such as negative spend, impossible clicks, or missing impressions

This skill is designed for a narrow workflow: reviewing exported campaign data before it is used for reporting, dashboarding, or further analysis.

## When not to use this skill
Do not use this skill when:
- the user only wants a general explanation of marketing metrics
- the input is not tabular CSV data
- the user wants advanced forecasting or business strategy recommendations
- the file is an Excel workbook, PDF, image, or presentation instead of a CSV
- the user asks for final business decisions that require domain judgment beyond data validation

## Expected inputs
This skill expects:
- a CSV file containing marketing campaign data, or
- pasted CSV-formatted text

Optional context may include:
- a short description of the CSV schema
- a note about which checks the user wants

Typical columns may include:
- campaign_name
- platform
- date
- impressions
- clicks
- conversions
- spend

The exact schema may vary, but the skill should first identify which columns are present before applying checks.

## Step-by-step instructions
1. Confirm that the input is a CSV file or CSV-like tabular text.
2. Read the header and identify available columns.
3. Run the Python script in `scripts/audit_campaign_csv.py` to inspect the file.
4. Check for structural issues such as:
   - missing required columns
   - duplicate rows
   - blank cells in key fields
   - invalid or inconsistent date formats
   - non-numeric values in numeric columns
   - suspicious values such as negative spend or clicks greater than impressions
5. Summarize the findings in a short audit report.
6. If possible, separate findings into:
   - critical issues
   - warnings
   - summary statistics
7. Keep the final output concise and useful for a business user.
8. If the file is not actually CSV data, explain that this skill does not apply and suggest a more appropriate workflow.

## Expected output format
Return a short structured audit report with:
- file summary
- columns detected
- row count
- issues found
- warnings
- recommended next steps

A typical response format:

### Audit Summary
- File name:
- Total rows:
- Columns detected:

### Critical Issues
- ...

### Warnings
- ...

### Recommended Next Steps
- ...

## Important limitations and checks
- This skill audits data quality. It does not guarantee business correctness.
- It should not invent missing values or silently fix data without telling the user.
- It should clearly distinguish confirmed issues from possible anomalies.
- If the schema is very different from standard campaign exports, the skill should say which checks were applied and which were skipped.
- If the file cannot be parsed as CSV, the skill should stop and report that clearly.
- The script should handle the deterministic checks. The model should explain the results in plain language.