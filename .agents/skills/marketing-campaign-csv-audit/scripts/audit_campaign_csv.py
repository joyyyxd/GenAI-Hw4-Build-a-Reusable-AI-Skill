import csv
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


REQUIRED_COLUMNS = ["campaign_name", "platform", "date", "impressions", "clicks", "conversions", "spend"]
KEY_FIELDS = ["campaign_name", "platform", "date"]
NUMERIC_FIELDS = ["impressions", "clicks", "conversions", "spend"]
DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"]


def normalize_column_name(name: str) -> str:
    return name.strip().lower()


def parse_float(value: str):
    if value is None:
        return None
    text = str(value).strip().replace(",", "").replace("$", "")
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_date(value: str):
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def read_csv_file(file_path: Path):
    with file_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV file has no header row.")
        original_headers = reader.fieldnames
        normalized_headers = [normalize_column_name(h) for h in original_headers]

        rows = []
        for raw_row in reader:
            normalized_row = {}
            for original_key, normalized_key in zip(original_headers, normalized_headers):
                normalized_row[normalized_key] = raw_row.get(original_key, "")
            rows.append(normalized_row)

    return original_headers, normalized_headers, rows


def check_missing_required_columns(headers):
    missing = [col for col in REQUIRED_COLUMNS if col not in headers]
    return missing


def check_blank_key_fields(rows):
    blank_counts = Counter()
    for row in rows:
        for field in KEY_FIELDS:
            if field in row and str(row[field]).strip() == "":
                blank_counts[field] += 1
    return dict(blank_counts)


def check_duplicate_rows(rows, headers):
    seen = Counter()
    for row in rows:
        row_tuple = tuple((h, str(row.get(h, "")).strip()) for h in headers)
        seen[row_tuple] += 1

    duplicate_count = 0
    for count in seen.values():
        if count > 1:
            duplicate_count += count - 1
    return duplicate_count


def check_date_issues(rows):
    invalid_dates = 0
    valid_dates = 0

    for row in rows:
        if "date" not in row:
            continue
        raw_value = row["date"]
        if str(raw_value).strip() == "":
            continue
        parsed = parse_date(raw_value)
        if parsed is None:
            invalid_dates += 1
        else:
            valid_dates += 1

    return {
        "valid_dates": valid_dates,
        "invalid_dates": invalid_dates
    }


def check_numeric_issues(rows):
    non_numeric_counts = Counter()
    negative_value_counts = Counter()
    clicks_gt_impressions = 0
    conversions_gt_clicks = 0
    missing_numeric_counts = Counter()

    for row in rows:
        parsed_values = {}

        for field in NUMERIC_FIELDS:
            if field not in row:
                continue

            raw_value = str(row[field]).strip()
            if raw_value == "":
                missing_numeric_counts[field] += 1
                parsed_values[field] = None
                continue

            parsed = parse_float(raw_value)
            if parsed is None:
                non_numeric_counts[field] += 1
                parsed_values[field] = None
            else:
                parsed_values[field] = parsed
                if parsed < 0:
                    negative_value_counts[field] += 1

        impressions = parsed_values.get("impressions")
        clicks = parsed_values.get("clicks")
        conversions = parsed_values.get("conversions")

        if impressions is not None and clicks is not None and clicks > impressions:
            clicks_gt_impressions += 1

        if clicks is not None and conversions is not None and conversions > clicks:
            conversions_gt_clicks += 1

    return {
        "non_numeric_counts": dict(non_numeric_counts),
        "negative_value_counts": dict(negative_value_counts),
        "missing_numeric_counts": dict(missing_numeric_counts),
        "clicks_greater_than_impressions": clicks_gt_impressions,
        "conversions_greater_than_clicks": conversions_gt_clicks
    }


def compute_summary_stats(rows):
    totals = {
        "impressions": 0.0,
        "clicks": 0.0,
        "conversions": 0.0,
        "spend": 0.0
    }

    for row in rows:
        for field in totals:
            if field in row:
                parsed = parse_float(row[field])
                if parsed is not None:
                    totals[field] += parsed

    return totals


def build_report(file_path: Path, original_headers, normalized_headers, rows):
    missing_required_columns = check_missing_required_columns(normalized_headers)
    blank_key_fields = check_blank_key_fields(rows)
    duplicate_rows = check_duplicate_rows(rows, normalized_headers)
    date_issues = check_date_issues(rows)
    numeric_issues = check_numeric_issues(rows)
    summary_stats = compute_summary_stats(rows)

    critical_issues = []
    warnings = []
    recommended_next_steps = []

    if missing_required_columns:
        critical_issues.append(
            f"Missing required columns: {', '.join(missing_required_columns)}"
        )

    if duplicate_rows > 0:
        warnings.append(f"Found {duplicate_rows} duplicate row(s).")

    if date_issues["invalid_dates"] > 0:
        warnings.append(f"Found {date_issues['invalid_dates']} row(s) with invalid date values.")

    for field, count in blank_key_fields.items():
        if count > 0:
            warnings.append(f"Found {count} blank value(s) in key field '{field}'.")

    for field, count in numeric_issues["missing_numeric_counts"].items():
        if count > 0:
            warnings.append(f"Found {count} missing value(s) in numeric field '{field}'.")

    for field, count in numeric_issues["non_numeric_counts"].items():
        if count > 0:
            warnings.append(f"Found {count} non-numeric value(s) in '{field}'.")

    for field, count in numeric_issues["negative_value_counts"].items():
        if count > 0:
            warnings.append(f"Found {count} negative value(s) in '{field}'.")

    if numeric_issues["clicks_greater_than_impressions"] > 0:
        warnings.append(
            f"Found {numeric_issues['clicks_greater_than_impressions']} row(s) where clicks exceed impressions."
        )

    if numeric_issues["conversions_greater_than_clicks"] > 0:
        warnings.append(
            f"Found {numeric_issues['conversions_greater_than_clicks']} row(s) where conversions exceed clicks."
        )

    if not critical_issues and not warnings:
        recommended_next_steps.append("No major data quality problems were detected. The file looks ready for reporting.")
    else:
        if missing_required_columns:
            recommended_next_steps.append("Add the missing required columns before using this file in reports or dashboards.")
        if duplicate_rows > 0:
            recommended_next_steps.append("Review and remove duplicate records.")
        if date_issues["invalid_dates"] > 0:
            recommended_next_steps.append("Standardize date values to a consistent format such as YYYY-MM-DD.")
        if any(count > 0 for count in numeric_issues["non_numeric_counts"].values()):
            recommended_next_steps.append("Clean non-numeric entries in metric columns.")
        if any(count > 0 for count in numeric_issues["negative_value_counts"].values()):
            recommended_next_steps.append("Review negative metric values and confirm whether they are valid.")
        if numeric_issues["clicks_greater_than_impressions"] > 0 or numeric_issues["conversions_greater_than_clicks"] > 0:
            recommended_next_steps.append("Investigate rows with impossible metric relationships.")

    report = {
        "file_summary": {
            "file_name": file_path.name,
            "total_rows": len(rows),
            "columns_detected": original_headers
        },
        "summary_statistics": {
            "total_impressions": round(summary_stats["impressions"], 2),
            "total_clicks": round(summary_stats["clicks"], 2),
            "total_conversions": round(summary_stats["conversions"], 2),
            "total_spend": round(summary_stats["spend"], 2)
        },
        "critical_issues": critical_issues,
        "warnings": warnings,
        "recommended_next_steps": recommended_next_steps
    }

    return report


def main():
    if len(sys.argv) != 2:
        print("Usage: python audit_campaign_csv.py <path_to_csv>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(json.dumps({"error": f"File not found: {file_path}"}, indent=2))
        sys.exit(1)

    if file_path.suffix.lower() != ".csv":
        print(json.dumps({"error": "Input file must be a CSV file."}, indent=2))
        sys.exit(1)

    try:
        original_headers, normalized_headers, rows = read_csv_file(file_path)
        report = build_report(file_path, original_headers, normalized_headers, rows)
        print(json.dumps(report, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()