# Data-Engineering-Tasks

A collection of data engineering projects focused on data ingestion, validation, transformation, and revenue analysis.

## Project Overview

### 1. Revenue Tracker
Analysis of organizational revenue and salary allocation data from Excel sources.

**Location**: `Revenue Tracker/`

**Task 1** - `task 1/task1.py`
- Extracts revenue metrics and salary allocation from Excel sheets (Delta3_Apr.xlsx)
- Analyzes:
  - Revenue and revenue percentage
  - Total workforce costs (core employees, TL/managers, consultants, incentives)
  - Tech salary as percentage of revenue
  - Total salary allocation and percentages
- Output: Structured data dictionary with financial metrics

**Task 2** - `task2/task2.py`
- Maps revenue across multiple monthly reports (April, May, June)
- Processes multiple Excel files:
  - MIS_Final_April.xlsx
  - MIS_Final_May.xlsx
  - MIS_Final_June.xlsx
- Extracts project-level revenue mapping
- Consolidates data into `Delta3_Output.xlsx`

---

### 2. CLI - Data Engineering Tool
A command-line interface tool for data pipeline operations with support for CSV and JSON files.

**Location**: `CLI/`

**Features**:
- **Ingest** (`ingest.py`): Load and display summaries of CSV/JSON files
- **Validate** (`validate.py`): Check data quality (nulls, duplicates, type inconsistencies)
- **Transform** (`transform.py`): Clean column names, remove duplicates, handle missing values
- **Main Tool** (`datatool.py`): Interactive REPL interface for running operations

**Key Capabilities**:
- Multi-format support (CSV & JSON)
- Automatic column name standardization (to snake_case)
- Comprehensive data quality reporting
- Logging to `datatool.log` for audit trails
- Cleaned output files in both CSV and JSON formats

**Dependencies**:
- pandas >= 2.0.0

**Usage**:
```bash
python datatool.py
# Commands: ingest, validate, transform, help, exit
```

**Sample Files**: `sample_data.csv`, `sample_data.json`

---

### 3. Ingest Books Data
A complete data pipeline for ingesting, transforming, and visualizing book catalog data scraped from an online bookstore.

**Location**: `Ingest Books Data/`

**Pipeline Stages**:

**Stage 1 - Ingestion** (`ingestion.py`)
- Aggregates 50 individual JSON files (data_page_1.json through data_page_50.json) into a single consolidated JSON file
- Extracts page metadata from filenames and attaches to each record
- Implements graceful error handling for corrupted files
- Output: `Ingest/data/transformed/books/ingest.json`

**Stage 2 - Transformation** (`transformation.py`)
- **Price Normalization**: Converts "£51.77" format to float (51.77)
- **Rating Conversion**: Maps text ratings (One, Two, Three, Four, Five) to numeric values (1-5)
- **Availability Processing**: Converts "In stock" status to binary (1 for in stock, 0 for not in stock)
- **Book ID Extraction**: Extracts unique book_id from product URLs
- **URL Standardization**: Converts relative links to full URLs (http://books.toscrape.com/catalogue/)
- **Timestamp Addition**: Adds ingestion_time metadata for data lineage
- Output: `Ingest/data/transformed/books/books_transformed.csv`

**Stage 3 - Dashboard** (`dashboard.py`)
- Interactive Streamlit dashboard for data visualization and exploration
- **Metrics Display**: Total books, average price, stock availability count
- **Visualizations**:
  - Box plot: Pricing distribution by rating
  - Histogram: Rating distribution across catalog
  - Data preview: Top 10 records
- Real-time data exploration capabilities

**Main Entry Point** (`main.py`)
- Orchestrates the entire pipeline
- Sequence: Ingestion → Transformation → Dashboard ready

**Key Features**:
- Batch processing of 50+ JSON files
- Multi-stage data cleaning and enrichment
- Interactive analytics dashboard
- Metadata tracking (page numbers, ingestion timestamps)
- Production-ready error handling

**Dependencies**:
- pandas >= 2.0.0
- streamlit >= 1.20.0
- plotly >= 5.0.0

**Usage**:
```bash
cd Ingest\ Books\ Data
python main.py
# Then run: streamlit run dashboard.py
```

**Data Flow**:
```
Raw Data (50 JSON files)
        ↓
    Ingestion (aggregation + metadata)
        ↓
    ingest.json (consolidated)
        ↓
    Transformation (cleaning + enrichment)
        ↓
    books_transformed.csv (analysis-ready)
        ↓
    Dashboard (visualization)
```

---

## Directory Structure

```
Data-Engineering-Tasks/
├── README.md                 # This file
├── Revenue Tracker/          # Revenue analysis tasks
│   ├── task 1/
│   │   ├── task1.ipynb      # Jupyter notebook for Task 1
│   │   └── task1.py         # Python script for Task 1
│   └── task2/
│       └── task2.py         # Python script for Task 2
│
├── CLI/                      # Data engineering CLI tool
│   ├── datatool.py          # Main entry point
│   ├── ingest.py            # Data ingestion module
│   ├── validate.py          # Data validation module
│   ├── transform.py         # Data transformation module
│   ├── requirements.txt      # Python dependencies
│   ├── sample_data.csv      # Sample input data
│   ├── sample_data.json     # Sample input data
│   ├── cleaned_output.csv   # Example output (CSV)
│   ├── cleaned_output.json  # Example output (JSON)
│   └── datatool.log         # Execution logs
│
└── Ingest Books Data/        # Book data pipeline
    ├── main.py              # Main pipeline orchestrator
    ├── ingestion.py         # Data ingestion module
    ├── transformation.py    # Data transformation module
    ├── dashboard.py         # Streamlit analytics dashboard
    └── Ingest/
        └── data/
            ├── raw/
            │   └── books/
            │       └── 2026-04-01/      # 50 raw JSON files
            └── transformed/
                └── books/
                    ├── ingest.json      # Consolidated data
                    └── books_transformed.csv  # Final cleaned data
```

---

## Getting Started

### Revenue Tracker
Ensure you have the required Excel files in the respective task directories and run:
```bash
cd "Revenue Tracker/task 1"
python task1.py  # For delta revenue extraction

cd "../task2"
python task2.py  # For multi-month revenue mapping
```

### CLI Tool Setup
```bash
cd CLI
pip install -r requirements.txt
python datatool.py
```

### Ingest Books Data Pipeline
```bash
cd "Ingest Books Data"
pip install pandas streamlit plotly
python main.py
# Then run the dashboard:
streamlit run dashboard.py
```
