# Data-Engineering-Tasks

A collection of data engineering projects focused on data ingestion, validation, transformation, and revenue analysis.

## Project Overview

### 1. CLI - Data Engineering Tool
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

### 2. Revenue Tracker
Analysis of organizational revenue and salary allocation data from Excel sources.

**Location**: `Revenue Tracker/`

**Task 1** - `task 1/task1.ipynb` & `task1.py`
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

## Directory Structure

```
Data-Engineering-Tasks/
├── README.md                 # This file
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
└── Revenue Tracker/          # Revenue analysis tasks
    ├── task 1/
    │   ├── task1.ipynb      # Jupyter notebook for Task 1
    │   └── task1.py         # Python script for Task 1
    └── task2/
        └── task2.py         # Python script for Task 2
```

---

## Getting Started

### CLI Tool Setup
```bash
cd CLI
pip install -r requirements.txt
python datatool.py
```

### Revenue Tracker
Ensure you have the required Excel files in the respective task directories and run:
```bash
python task1.py  # For delta revenue extraction
python task2.py  # For multi-month revenue mapping
```