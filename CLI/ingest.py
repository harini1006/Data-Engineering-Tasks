"""
ingest.py - Data Ingestion Module
Reads CSV or JSON files and displays a summary.
"""

import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)


def load_file(filepath: str) -> pd.DataFrame | None:
    """Load a CSV or JSON file into a DataFrame."""
    if not os.path.exists(filepath):
        print(f"  [ERROR] File not found: '{filepath}'")
        logger.error(f"File not found: {filepath}")
        return None

    ext = os.path.splitext(filepath)[1].lower()

    try:
        if ext == ".csv":
            df = pd.read_csv(filepath)
        elif ext == ".json":
            df = pd.read_json(filepath)
        else:
            print(f"  [ERROR] Unsupported file type '{ext}'. Use .csv or .json")
            logger.error(f"Unsupported file type: {ext}")
            return None
    except Exception as e:
        print(f"  [ERROR] Could not read file: {e}")
        logger.error(f"Failed to read {filepath}: {e}")
        return None

    return df


def ingest_file(filepath: str):
    """Ingest a file and print its summary."""
    print(f"\n  [INGEST] Reading file: {filepath}")
    df = load_file(filepath)
    if df is None:
        return

    print(f"\n  {'─'*48}")
    print(f"  File        : {os.path.basename(filepath)}")
    print(f"  Rows        : {len(df)}")
    print(f"  Columns     : {len(df.columns)}")
    print(f"  {'─'*48}")
    print(f"  {'Column Name':<25} {'Data Type'}")
    print(f"  {'─'*48}")

    for col, dtype in df.dtypes.items():
        print(f"  {str(col):<25} {str(dtype)}")

    print(f"  {'─'*48}")
    print(f"\n  Preview (first 5 rows):")
    print(df.head().to_string(index=False))
    print()

    logger.info(f"Ingested {filepath}: {len(df)} rows, {len(df.columns)} columns")
