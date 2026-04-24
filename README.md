# Homework 5: Build a Reusable AI Skill
## Marketing Campaign CSV Audit Skill

## What this skill does
This skill audits exported marketing campaign CSV files before they are used for reporting or dashboards. It checks for data quality issues such as missing values, duplicate rows, invalid date formats, and suspicious metric relationships (e.g., clicks greater than impressions).

## Why I chose this skill
I chose this workflow because auditing campaign data is a common and practical task for marketing analysts. It is also a task where deterministic code is more reliable than a language model alone, especially for validating structure and detecting numeric inconsistencies.

## How to use it
Place a CSV file in the repository and ask the agent to audit it. For example:

"Use the marketing-campaign-csv-audit skill to audit sample_campaign.csv and summarize the results."

The agent will identify the relevant skill and run the Python script to analyze the file.

## Repository structure
- `.agents/skills/marketing-campaign-csv-audit/SKILL.md`: skill instructions and metadata
- `.agents/skills/marketing-campaign-csv-audit/scripts/audit_campaign_csv.py`: Python audit script
- `sample_campaign.csv`: sample file used for testing
- `test_prompts.md`: prompts used for the Step 5 agent test

## What the script does
The script:
- parses the CSV file
- checks for required columns
- detects duplicate rows
- validates date formats
- checks numeric fields (missing, non-numeric, negative values)
- identifies impossible relationships (e.g., clicks > impressions)
- generates a structured audit report

## What worked well
The skill successfully integrates structured instructions with deterministic code. The agent is able to:
- discover the skill based on the request
- invoke the correct script
- return a clear, business-friendly summary

## Limitations
- The skill only works with CSV or CSV-like tabular data
- It does not support PDF, images, or Excel files directly
- It does not fix data automatically, only reports issues
- It assumes a relatively standard campaign data structure

## Video Link
[Presentation Video](https://youtu.be/StQqyTnmD30)