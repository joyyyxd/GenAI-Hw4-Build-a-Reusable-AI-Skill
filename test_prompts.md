## Step 5 Test Prompts

### Normal case
Prompt:
Use the marketing-campaign-csv-audit skill in this repository to audit sample_campaign.csv. Run the Python script if needed and give me a short business-friendly summary.

Expected behavior:
The agent should discover and activate the skill, run the Python script, and return a clear audit summary.

### Edge case
Prompt:
Use the marketing-campaign-csv-audit skill on sample_campaign.csv and tell me whether the file is usable for reporting even though some rows may contain inconsistent dates or metric anomalies.

Expected behavior:
The agent should still use the skill, detect issues, and explain whether the file is ready for reporting.

### Cautious case
Prompt:
Use the marketing-campaign-csv-audit skill to audit a marketing performance PDF for dashboard readiness.

Expected behavior:
The agent should explain that the skill is intended for CSV or CSV-like data and should not be applied directly to a PDF.