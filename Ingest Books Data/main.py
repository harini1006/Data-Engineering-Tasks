import os
from ingestion import run_ingestion
from transformation import run_transformation

# Configuration of paths as per task requirements
INPUT_DIR = "Ingest/data/raw/books/2026-04-01/"
RAW_JSON = "Ingest/data/transformed/books/ingest.json"
TRANSFORMED_CSV = "Ingest/data/transformed/books/books_transformed.csv"

def main():
    print("--- Starting Book Data Pipeline ---")

    # Step 1: Ingestion
    # Aggregates 50 JSON files into one ingest.json
    print("Step 1: Ingesting raw data...")
    run_ingestion(INPUT_DIR, RAW_JSON) 

    # Step 2: Transformation
    # Cleans the data and saves it as books_transformed.csv
    print("Step 2: Transforming data and cleaning fields...")
    run_transformation(RAW_JSON, TRANSFORMED_CSV)

    print("--- Pipeline Processing Complete ---")
    print("To view your interactive insights, run: streamlit run dashboard.py")

if __name__ == "__main__":
    main()