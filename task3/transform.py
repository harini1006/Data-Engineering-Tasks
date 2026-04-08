"""
transform.py - Data Transformation Module
Cleans column names, removes duplicates, handles missing values, saves output.
"""

import pandas as pd
import re
import os
import logging
from ingest import load_file

logger = logging.getLogger(__name__)


def clean_column_name(name: str) -> str:
    """
    Standardize a column name to snake_case.
    Examples:
        'User Name'     -> 'user_name'
        'Phone Number ' -> 'phone_number'
        'EmailID'       -> 'emailid'
        '  Age  '       -> 'age'
    """
    name = str(name).strip()
    name = re.sub(r"[\s\-]+", "_", name)     # spaces/hyphens -> underscore
    name = re.sub(r"[^\w]", "", name)         # remove non-word chars
    name = re.sub(r"_+", "_", name)           # collapse multiple underscores
    name = name.lower()
    return name


def transform_file(input_path: str, output_path: str):
    """Transform and clean the input file, save to output."""
    print(f"\n  [TRANSFORM] Processing: {input_path}")
    df = load_file(input_path)
    if df is None:
        return

    original_rows = len(df)
    original_cols = list(df.columns)

    # ── Step 1: Clean Column Names ────────────────────────
    print("\n  [Step 1/4] Cleaning column names...")
    new_columns = {col: clean_column_name(col) for col in df.columns}
    df.rename(columns=new_columns, inplace=True)
    renamed = [(old, new) for old, new in new_columns.items() if old != new]
    if renamed:
        for old, new in renamed:
            print(f"    '{old}'  →  '{new}'")
    else:
        print("    All column names already clean.")

    # ── Step 2: Remove Duplicate Rows ─────────────────────
    print("\n  [Step 2/4] Removing duplicate rows...")
    before = len(df)
    df.drop_duplicates(inplace=True)
    after = len(df)
    removed_dups = before - after
    print(f"    Removed {removed_dups} duplicate row(s). ({before} → {after} rows)")

    # ── Step 3: Handle Missing Values ─────────────────────
    print("\n  [Step 3/4] Handling missing values...")
    null_before = df.isnull().sum().sum()

    for col in df.columns:
        if df[col].isnull().any():
            if df[col].dtype in ["float64", "int64"]:
                median_val = df[col].median()
                df[col].fillna(median_val, inplace=True)
                print(f"    '{col}': filled {df[col].isnull().sum()} nulls with median ({median_val})")
            else:
                df[col].fillna("Unknown", inplace=True)
                print(f"    '{col}': filled nulls with 'Unknown'")

    null_after = df.isnull().sum().sum()
    if null_before == 0:
        print("    No missing values to handle.")
    else:
        print(f"    Resolved {null_before - null_after} missing value(s).")

    # ── Step 4: Save Output ───────────────────────────────
    print(f"\n  [Step 4/4] Saving cleaned data to: {output_path}")
    try:
        out_ext = os.path.splitext(output_path)[1].lower()
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

        if out_ext == ".csv":
            df.to_csv(output_path, index=False)
        elif out_ext == ".json":
            df.to_json(output_path, orient="records", indent=2)
        else:
            # Default to CSV
            output_path += ".csv"
            df.to_csv(output_path, index=False)

        print(f"    ✅ Saved successfully!")
    except Exception as e:
        print(f"    [ERROR] Failed to save: {e}")
        logger.error(f"Save failed for {output_path}: {e}")
        return

    # ── Summary ───────────────────────────────────────────
    print(f"\n  {'═'*54}")
    print(f"  TRANSFORM SUMMARY")
    print(f"  {'─'*54}")
    print(f"  Original rows     : {original_rows}")
    print(f"  Rows after clean  : {len(df)}")
    print(f"  Duplicates removed: {removed_dups}")
    print(f"  Nulls resolved    : {null_before}")
    print(f"  Output file       : {output_path}")
    print(f"  {'═'*54}\n")

    logger.info(
        f"Transformed {input_path} -> {output_path}: "
        f"{removed_dups} dups removed, {null_before} nulls handled."
    )
