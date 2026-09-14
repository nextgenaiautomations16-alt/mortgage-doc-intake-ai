"""
Scores the verification engine's outcome predictions against
ground_truth.csv.

Run from repo root: python -m eval.run_eval
"""
import csv
import json
from pathlib import Path

from src.verification import run_batch

DATA_DIR = Path(__file__).parent.parent / "data"


def load_json(name):
    with open(DATA_DIR / name) as f:
        return json.load(f)


def load_ground_truth():
    rows = {}
    with open(DATA_DIR / "ground_truth.csv") as f:
        for row in csv.DictReader(f):
            rows[row["application_id"]] = row
    return rows


def main():
    applications = load_json("applications.json")
    ground_truth = load_ground_truth()

    results = run_batch(applications)

    correct = 0
    mismatches = []

    for r in results:
        expected = ground_truth[r.application_id]["expected_outcome"]
        if r.outcome == expected:
            correct += 1
        else:
            mismatches.append((r.application_id, expected, r.outcome, r.reasons))

    total = len(results)
    accuracy = correct / total if total else 0

    print("=== Mortgage Doc Intake AI — Evaluation Report ===")
    print(f"Total applications evaluated: {total}")
    print(f"Outcome accuracy: {accuracy:.1%}  ({correct}/{total})")

    if mismatches:
        print("\n--- Mismatches vs. ground truth ---")
        for app_id, expected, actual, reasons in mismatches:
            print(f"  {app_id}: expected {expected}, got {actual} {reasons if reasons else ''}")
    else:
        print("\nNo mismatches — every application landed in the expected outcome bucket.")


if __name__ == "__main__":
    main()
