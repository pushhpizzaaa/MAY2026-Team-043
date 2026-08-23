"""Merge JMeter API_Manual_TestCases_Results.csv into API_Manual_TestCases_Updated.csv."""
import csv
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_CSV = os.path.join(BASE_DIR, "TestCases", "API_Manual_TestCases.csv")
RESULTS_CSV = os.path.join(BASE_DIR, "TestCases", "API_Manual_TestCases_Results.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "TestCases", "API_Manual_TestCases_Updated.csv")

FIELDNAMES = [
    "TestCaseId", "Scenario", "Steps", "Expected", "Input",
    "Actual", "Status", "Comments", "RunTime",
]


def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)


def main():
    from generate_testcase_jmx import build_test_definitions, defs_by_id, enrich_from_csv, status_for_row

    defs_map = defs_by_id(enrich_from_csv(build_test_definitions()))
    results_rows = read_csv(RESULTS_CSV)
    source_rows = read_csv(SOURCE_CSV)
    if not source_rows:
        print(f"Source not found or empty: {SOURCE_CSV}", file=sys.stderr)
        sys.exit(1)

    results_by_id = {}
    for row in results_rows:
        tc_id = (row.get("TestCaseId") or "").strip()
        if tc_id:
            row["Status"] = status_for_row(row, defs_map)
            results_by_id[tc_id] = row

    write_csv(RESULTS_CSV, list(results_by_id.values()))

    merged = []
    for row in source_rows:
        tc_id = row["TestCaseId"]
        if tc_id in results_by_id:
            r = results_by_id[tc_id]
            merged.append({
                "TestCaseId": tc_id,
                "Scenario": r.get("Scenario") or row.get("Scenario", ""),
                "Steps": r.get("Steps") or row.get("Steps", ""),
                "Expected": r.get("Expected") or row.get("Expected", ""),
                "Input": r.get("Input") or row.get("Input", ""),
                "Actual": r.get("Actual", ""),
                "Status": r.get("Status", ""),
                "Comments": r.get("Comments") or row.get("Comments", ""),
                "RunTime": r.get("RunTime", ""),
            })
        else:
            merged.append({k: row.get(k, "") for k in FIELDNAMES})

    write_csv(OUTPUT_CSV, merged)
    print(f"Merged {len(results_by_id)} test results into {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
