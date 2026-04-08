"""
validate.py - Data Validation Module
Checks for nulls, duplicates, and type inconsistencies.
"""

import pandas as pd
import logging
from ingest import load_file

logger = logging.getLogger(__name__)


def validate_file(filepath: str):
    """Validate data quality of the given file."""
    print(f"\n  [VALIDATE] Checking file: {filepath}")
    df = load_file(filepath)
    if df is None:
        return

    issues_found = 0

    print(f"\n  {'═'*54}")
    print(f"  DATA QUALITY REPORT: {filepath}")
    print(f"  {'═'*54}")

    # ── 1. Missing / Null Values ──────────────────────────
    print(f"\n  [1] Missing / Null Values")
    print(f"  {'─'*40}")
    null_counts = df.isnull().sum()
    has_nulls = null_counts[null_counts > 0]

    if has_nulls.empty:
        print("  ✅ No missing values found.")
    else:
        issues_found += len(has_nulls)
        for col, count in has_nulls.items():
            pct = (count / len(df)) * 100
            print(f"  ⚠️  '{col}': {count} missing ({pct:.1f}%)")

    # ── 2. Duplicate Rows ─────────────────────────────────
    print(f"\n  [2] Duplicate Rows")
    print(f"  {'─'*40}")
    dup_count = df.duplicated().sum()

    if dup_count == 0:
        print("  ✅ No duplicate rows found.")
    else:
        issues_found += 1
        print(f"  ⚠️  {dup_count} duplicate row(s) detected.")
        print(f"\n  Duplicate rows preview:")
        print(df[df.duplicated(keep=False)].to_string(index=True))

    # ── 3. Inconsistent Data Types ────────────────────────
    print(f"\n  [3] Inconsistent / Suspicious Data Types")
    print(f"  {'─'*40}")
    type_issues = []

    for col in df.columns:
        if df[col].dtype == object:
            # Try to detect if a string column should be numeric
            converted = pd.to_numeric(df[col], errors="coerce")
            valid_numeric = converted.notna().sum()
            total_non_null = df[col].notna().sum()

            if total_non_null > 0 and valid_numeric == total_non_null:
                type_issues.append(
                    f"  ⚠️  '{col}' is stored as text but all values appear numeric."
                )
            elif 0 < valid_numeric < total_non_null:
                mixed = total_non_null - valid_numeric
                type_issues.append(
                    f"  ⚠️  '{col}' has mixed types: {valid_numeric} numeric, {mixed} non-numeric."
                )

    if not type_issues:
        print("  ✅ No type inconsistencies detected.")
    else:
        issues_found += len(type_issues)
        for msg in type_issues:
            print(msg)

    # ── Summary ───────────────────────────────────────────
    print(f"\n  {'═'*54}")
    if issues_found == 0:
        print("  ✅ RESULT: Data looks clean! No issues found.")
    else:
        print(f"  ⚠️  RESULT: {issues_found} issue(s) found. Consider running transform.")
    print(f"  {'═'*54}\n")

    logger.info(f"Validated {filepath}: {issues_found} issue(s) found.")
