# Databricks notebook source
# MAGIC %md
# MAGIC ## PHASE 1: Setup Environment

# COMMAND ----------

# MAGIC %md
# MAGIC In this phase, we initialize:
# MAGIC - Spark session for distributed data processing
# MAGIC - Logging to track execution flow and errors

# COMMAND ----------

# MAGIC %md
# MAGIC #### Import necessary Libraries

# COMMAND ----------

from pyspark.sql import SparkSession
import logging
import re
from functools import reduce
from pyspark.sql.functions import (
    col,
    lit,
    trim,
    when,
    count,
    expr
)
from pyspark.sql.utils import AnalysisException

# COMMAND ----------

# MAGIC %md
# MAGIC #### Create Spark session and logging 

# COMMAND ----------

try:
    # Create Spark session
    spark = SparkSession.builder.appName("Ecommerce_ETL").getOrCreate()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    logger = logging.getLogger("ETL")

    logger.info("Spark session initialized successfully")

except Exception as e:
    print(f"Error during setup: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC #### load the config file 

# COMMAND ----------

import json

config_path = "/Volumes/data_engineering/task_schema/training_dataset/config.json"

with open(config_path, "r") as f:
    config = json.load(f)

print("Config Loaded Successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC #### Store the input and output path
# MAGIC

# COMMAND ----------

input_path = config["paths"]["input_path"]
output_path = config["paths"]["output_path"]

file_format = config["output"]["format"]
write_mode = config["output"]["mode"]

# COMMAND ----------

# MAGIC %md
# MAGIC ## PHASE 2: DATA INGESTION

# COMMAND ----------

# MAGIC %md
# MAGIC In this phase we:
# MAGIC
# MAGIC - Fetch all dataset files dynamically
# MAGIC - Filter only CSV files
# MAGIC - Read each file into a DataFrame
# MAGIC - Add a category_name column
# MAGIC - Handle errors properly (file issues, read issues, etc.)

# COMMAND ----------

# MAGIC %md
# MAGIC ### File Handling: Listing and Filtering CSV Files

# COMMAND ----------


try:
    # List all files in the directory
    files = dbutils.fs.ls(input_path)

    logger.info(f"Total files found: {len(files)}")

    # Filter only CSV files (case insensitive)
    csv_files = [f.path for f in files if f.path.lower().endswith(".csv")]

    # Validate CSV presence
    if not csv_files:
        logger.error(f"No CSV files found in directory: {input_path}")
        raise Exception("Data ingestion failed - No CSV files found")

    logger.info(f"Total CSV files detected: {len(csv_files)}")

except AnalysisException as e:
    logger.error(f"Invalid path or access issue: {input_path} | {e}")
    raise

except Exception as e:
    logger.error(f"Unexpected error during file listing: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ### Load Files into DataFrames

# COMMAND ----------

df_list = []

for file_path in csv_files:
    try:
        df = spark.read \
            .option("header", config["processing"]["header"]) \
            .option("inferSchema", config["processing"]["infer_schema"]) \
            .csv(file_path)

        df_list.append(df)

    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")

# COMMAND ----------

# DBTITLE 1,Complete Pipeline Analysis
# MAGIC %md
# MAGIC # Complete ETL Pipeline Analysis
# MAGIC
# MAGIC Detailed breakdown of data transformations through each phase

# COMMAND ----------

# MAGIC %md
# MAGIC ### Validation
# MAGIC

# COMMAND ----------

try:
    # Ensure data is loaded
    if not df_list:
        raise ValueError("No datasets loaded")

    # Take one sample DataFrame
    sample_df = df_list[0]

    # Check if it has at least one row
    if sample_df.limit(1).count() == 0:
        raise ValueError("Loaded dataset is empty")

    # Preview data
    display(sample_df)
    sample_df.printSchema()

    logger.info("Data loading successful")

except ValueError as ve:
    logger.error(ve)
    raise

except Exception as e:
    logger.error(f"Error during validation: {e}")
    raise

# COMMAND ----------

# DBTITLE 1,Analysis Metric 1
# MAGIC %md
# MAGIC ### 📊 Analysis Metric 1: Row and Column Count Per Ingested File

# COMMAND ----------

# DBTITLE 1,Metric 1: File-Level Statistics
print("=" * 80)
print("METRIC 1: ROW AND COLUMN COUNT PER INGESTED FILE")
print("=" * 80)
print()

file_stats = []
for i, df in enumerate(df_list):
    row_count = df.count()
    col_count = len(df.columns)
    file_name = csv_files[i].split("/")[-1]
    file_stats.append({"file": file_name, "rows": row_count, "cols": col_count})
    print(f"File {i+1:2d}: {file_name}")
    print(f"          Rows: {row_count:,} | Columns: {col_count}")
    print()

total_initial_rows = sum([stat["rows"] for stat in file_stats])
print(f"\nTotal rows across all {len(csv_files)} files: {total_initial_rows:,}")
print("=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## PHASE 3: DATA CLEANING
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC In this phase:
# MAGIC - Column names are standardized
# MAGIC - Missing/null values are handled
# MAGIC - Schema inconsistencies across datasets are resolved
# MAGIC - Unnecessary columns are removed (if identified)
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step: Column Standardization

# COMMAND ----------

def clean_columns(df):
    try:
        original_cols = df.columns

        for col_name in original_cols:
            new_col = re.sub(r'[^a-zA-Z0-9]', '_', col_name.strip().lower())
            new_col = re.sub(r'_+', '_', new_col)  # fix multiple underscores

            if col_name != new_col:
                df = df.withColumnRenamed(col_name, new_col)

        logger.info("Column standardization applied")

        return df

    except Exception as e:
        logger.error(f"Error during column standardization: {e}")
        return df

# COMMAND ----------

try:
    df_list = [clean_columns(df) for df in df_list]
    logger.info("Column standardization completed for all datasets")

except Exception as e:
    logger.error(f"Error during column standardization across datasets: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step: Handle Missing / Null Values
# MAGIC
# MAGIC We clean data by:
# MAGIC - Removing extra spaces
# MAGIC - Converting empty strings to null
# MAGIC

# COMMAND ----------

def handle_nulls(df):
    try:
        for c, dtype in df.dtypes:
            if dtype == "string":   # only string columns
                df = df.withColumn(
                    c,
                    when(trim(col(c)) == "", None)
                    .otherwise(trim(col(c)))
                )

        return df

    except Exception as e:
        logger.error(f"Error handling nulls: {e}")
        return df

# COMMAND ----------

try:
    df_list = [handle_nulls(df) for df in df_list]
    logger.info("Null values handled successfully")

except Exception as e:
    logger.error(f"Error applying null handling: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step: Handle Schema Inconsistency
# MAGIC
# MAGIC Different datasets may have different columns.
# MAGIC We ensure consistency by:
# MAGIC - Identifying all unique columns across datasets
# MAGIC - Adding missing columns as null
# MAGIC - Aligning all DataFrames to the same schema

# COMMAND ----------

try:
    # Collect all unique column names and sort them
    all_columns = sorted(set().union(*[set(df.columns) for df in df_list]))

    logger.info(f"Total unified columns: {len(all_columns)}")

except Exception as e:
    logger.error(f"Error collecting columns: {e}")
    raise

# COMMAND ----------

aligned_dfs = []

for i, df in enumerate(df_list):
    try:
        # Add missing columns
        for c in all_columns:
            if c not in df.columns:
                df = df.withColumn(c, lit(None))

        # Reorder columns consistently
        df = df.select(*all_columns)

        aligned_dfs.append(df)

    except Exception as e:
        logger.error(f"Error aligning schema for dataset {i}: {e}")
        raise

# COMMAND ----------

df_list = aligned_dfs
logger.info("Schema alignment completed successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step: Remove Unnecessary Columns
# MAGIC
# MAGIC We remove columns that contain only null values.
# MAGIC This helps reduce noise and improves data quality.

# COMMAND ----------

def drop_empty_columns(df):
    try:
        # Get non-null count for all columns in one pass
        counts = df.select([
            count(col(c)).alias(c) for c in df.columns
        ]).collect()[0].asDict()

        # Keep only columns with non-null values
        valid_columns = [c for c, cnt in counts.items() if cnt > 0]

        return df.select(*valid_columns)

    except Exception as e:
        logger.error(f"Error removing empty columns: {e}")
        return df

# COMMAND ----------

try:
    df_list = [drop_empty_columns(df) for df in df_list]
    logger.info("Unnecessary (empty) columns removed")

except Exception as e:
    logger.error(f"Error applying column removal: {e}")
    raise

# COMMAND ----------

# After cleaning
print("Columns after cleaning:")
print(df_list[0].columns)

# COMMAND ----------

# MAGIC %md
# MAGIC ## PHASE 4: DATA TRANSFORMATION

# COMMAND ----------

# MAGIC %md
# MAGIC - Convert currency values ($, ₹, €) to numeric
# MAGIC - Convert percentage values (%)
# MAGIC - Convert 'k' values to thousands
# MAGIC - Extract numeric values from **rank**

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 1: Convert Currency Values
# MAGIC
# MAGIC We remove currency symbols and convert values to numeric

# COMMAND ----------

# DBTITLE 1,Cell 33
def transform_price(df):
    try:
        if "price" in df.columns:
            df = df.withColumn(
                "price_usd",
                expr("try_cast(regexp_replace(price, '[^0-9.]', '') as double)")
            )
        return df

    except Exception as e:
        logger.error(f"Price transformation error: {e}")
        return df

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 2: Convert Percentage Values
# MAGIC
# MAGIC Remove '%' symbol and convert to numeric

# COMMAND ----------

# DBTITLE 1,Cell 36
def transform_discount(df):
    try:
        if "discount" in df.columns:
            df = df.withColumn(
                "pct_discount",
                expr("try_cast(regexp_replace(discount, '[^0-9.]', '') as double)")
            )
        return df

    except Exception as e:
        logger.error(f"Discount transformation error: {e}")
        return df

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 3: Convert 'k' Values
# MAGIC
# MAGIC Convert values like 5k → 5000

# COMMAND ----------

# DBTITLE 1,Cell 39
def transform_k_values(df):
    try:
        if "qty_sold" in df.columns:
            df = df.withColumn(
                "qty_sold",
                expr("""
                    CASE 
                        WHEN lower(qty_sold) LIKE '%k'
                        THEN try_cast(regexp_replace(lower(qty_sold), '[^0-9.]', '') as double) * 1000
                        ELSE try_cast(qty_sold as double)
                    END
                """)
            )
        return df

    except Exception as e:
        logger.error(f"K-value transformation error: {e}")
        return df

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 4: Extract Rank Values
# MAGIC
# MAGIC Convert values like #1 → 1

# COMMAND ----------

# DBTITLE 1,Cell 42
def transform_rank(df):
    try:
        if "rank_title" in df.columns:
            df = df.withColumn(
                "rank_title_num",
                expr("try_cast(regexp_replace(rank_title, '[^0-9]', '') as int)")
            )

        if "rank_sub" in df.columns:
            df = df.withColumn(
                "rank_sub_num",
                expr("try_cast(regexp_replace(rank_sub, '[^0-9]', '') as int)")
            )

        return df

    except Exception as e:
        logger.error(f"Rank transformation error: {e}")
        return df

# COMMAND ----------

# MAGIC %md
# MAGIC ### Handle Null Values in Numeric Columns

# COMMAND ----------

def fill_null_numeric(df):
    try:
        # Read fill value from config.json
        fill_value = config["fillna"]["numeric"]

        for c, dtype in df.dtypes:
            if dtype in ["int", "bigint", "double", "float", "decimal"]:
                df = df.fillna({c: fill_value})

        return df

    except Exception as e:
        logger.error(f"Error handling numeric null values: {e}")
        return df

# COMMAND ----------

try:
    df_list = [transform_price(df) for df in df_list]
    df_list = [transform_discount(df) for df in df_list]
    df_list = [transform_k_values(df) for df in df_list]
    df_list = [transform_rank(df) for df in df_list]
    df_list = [fill_null_numeric(df) for df in df_list]

    logger.info("All required transformations completed")

except Exception as e:
    logger.error(f"Error during transformations: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 5: Verify Transformation Output
# MAGIC
# MAGIC Preview dataset and schema after transformation

# COMMAND ----------

# DBTITLE 1,Step 5: Verify Transformation Output
# Display first dataset after transformation
print("Schema after transformations:")
df_list[0].printSchema()

print("\nSample data:")
display(df_list[0].limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Remove Unwanted Column

# COMMAND ----------

def drop_unwanted_columns(df):
    try:
        # Read columns to drop from config.json
        unwanted_cols = config["cleanup"]["drop_columns"]

        # Keep only columns that exist in dataset
        existing_cols = [c for c in unwanted_cols if c in df.columns]

        # Drop columns
        df = df.drop(*existing_cols)

        return df

    except Exception as e:
        logger.error(f"Error dropping unwanted columns: {e}")
        return df

# COMMAND ----------

try:
    df_list = [drop_unwanted_columns(df) for df in df_list]

    logger.info("Configured unwanted columns removed successfully")

except Exception as e:
    logger.error(f"Error applying unwanted column removal: {e}")
    raise

# COMMAND ----------

print(df_list[0].columns)

# COMMAND ----------

# DBTITLE 1,Analysis Metrics 2-4
# MAGIC %md
# MAGIC ### 📋 Analysis Metrics 2-4: Column Transformations

# COMMAND ----------

# DBTITLE 1,Metric 2: Columns Dropped
print("=" * 80)
print("METRIC 2: COLUMNS DROPPED")
print("=" * 80)
print()

# Get unwanted columns from config
drop_columns_config = config["cleanup"]["drop_columns"]
print(f"Number of columns dropped (from config): {len(drop_columns_config)}")
print(f"\nDropped column names:")
for col in drop_columns_config:
    print(f"  - {col}")
print()
print("Note: Additional columns may have been dropped earlier if they contained only NULL values.")
print("=" * 80)
print()

# COMMAND ----------

# DBTITLE 1,Metric 3: Final Output Columns
print("=" * 80)
print("METRIC 3: COLUMNS IN FINAL OUTPUT (After Transformation)")
print("=" * 80)
print()

final_columns = df_list[0].columns
print(f"Total columns after transformation: {len(final_columns)}")
print(f"\nColumn names:")
for i, col in enumerate(final_columns, 1):
    print(f"  {i:2d}. {col}")
    
print("\n" + "=" * 80)
print()

# COMMAND ----------

# DBTITLE 1,Metric 4: Row and Column Changes During Transformation
print("=" * 80)
print("METRIC 4: ROW AND COLUMN CHANGES DURING TRANSFORMATION")
print("=" * 80)
print()

# Row count remains same during transformation
total_rows_after_transform = sum([df.count() for df in df_list])
print(f"Total rows BEFORE transformation: {total_initial_rows:,}")
print(f"Total rows AFTER transformation:  {total_rows_after_transform:,}")
print(f"Row change: {total_rows_after_transform - total_initial_rows:,}")
print()
print("Column changes:")
print("  Columns added during transformation:")
print("    - price_usd (extracted numeric from price)")
print("    - pct_discount (extracted numeric from discount)")
print("    - rank_title_num (extracted numeric from rank_title)")
print("    - rank_sub_num (extracted numeric from rank_sub)")
print(f"\n  Total columns after transformation: {len(df_list[0].columns)}")
print("\n" + "=" * 80)
print()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Phase 5: Data Merging 

# COMMAND ----------

# MAGIC %md
# MAGIC #### STEP 1: Convert all DataFrames to string

# COMMAND ----------


try:
    string_dfs = []

    for i, df in enumerate(df_list):
        temp_df = df.select(
            [col(c).cast("string").alias(c) for c in df.columns]
        )

        string_dfs.append(temp_df)

    logger.info("All datasets converted to string")

except Exception as e:
    logger.error(f"Error converting datasets to string: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ### STEP 2: Collect all unique columns

# COMMAND ----------


try:
    all_columns = sorted(
        set().union(*[set(df.columns) for df in string_dfs])
    )

    logger.info(f"Unified schema columns count: {len(all_columns)}")

except Exception as e:
    logger.error(f"Error collecting schema columns: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC #### Step 2: Align Schemas

# COMMAND ----------


try:
    aligned_dfs = []

    for df in string_dfs:

        for c in all_columns:
            if c not in df.columns:
                df = df.withColumn(c, lit(None))

        df = df.select(*all_columns)

        aligned_dfs.append(df)

    logger.info("All schemas aligned successfully")

except Exception as e:
    logger.error(f"Error aligning schemas: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC #### Step 3: Merge All DataFrames

# COMMAND ----------

try:
    final_df = reduce(
        lambda x, y: x.unionByName(y),
        aligned_dfs
    )

    logger.info("All category DataFrames merged successfully")


except Exception as e:
    logger.error(f"Error during data merging: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC #### Step 4: Validate Final Dataset

# COMMAND ----------


print("Final Row Count:", final_df.count())

print("Final Schema:")
final_df.printSchema()

display(final_df.limit(10))

# COMMAND ----------

# DBTITLE 1,Analysis Metric 5
# MAGIC %md
# MAGIC ### 🔗 Analysis Metric 5: After Merging Statistics

# COMMAND ----------

# DBTITLE 1,Metric 5: Post-Merge Counts
print("=" * 80)
print("METRIC 5: ROW AND COLUMN COUNT AFTER MERGING")
print("=" * 80)
print()

merged_row_count = final_df.count()
merged_col_count = len(final_df.columns)

print(f"Total rows after merging all {len(csv_files)} CSV files: {merged_row_count:,}")
print(f"Total columns after merging: {merged_col_count}")
print()
print(f"Column names ({merged_col_count} total):")
for i, col in enumerate(final_df.columns, 1):
    print(f"  {i:2d}. {col}")

print("\n" + "=" * 80)
print()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Phase 6: Data Quality Checks

# COMMAND ----------

# MAGIC %md
# MAGIC #### STEP 1: Recast numeric columns

# COMMAND ----------

try:
    numeric_columns = config["quality"]["numeric_columns"]

    for c in numeric_columns:
        if c in final_df.columns:

            if c in ["price_usd", "pct_discount", "qty_sold"]:
                dtype = "double"
            else:
                dtype = "int"

            final_df = final_df.withColumn(
                c,
                expr(f"try_cast({c} as {dtype})")
            )

    logger.info("Numeric columns recast successfully")

except Exception as e:
    logger.error(f"Error recasting numeric columns: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC #### STEP 2: Identify duplicate records

# COMMAND ----------


try:
    duplicate_key = config["quality"]["duplicate_key"]

    duplicate_count = final_df.groupBy(duplicate_key) \
        .count() \
        .filter("count > 1") \
        .count()

    print("Duplicate Records:", duplicate_count)

    logger.info(f"Duplicate records found: {duplicate_count}")

except Exception as e:
    logger.error(f"Error identifying duplicates: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC #### STEP 3: Remove duplicate records

# COMMAND ----------



try:
    final_df = final_df.dropDuplicates(
        [duplicate_key]
    )

    logger.info("Duplicate records removed successfully")

except Exception as e:
    logger.error(f"Error removing duplicates: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC #### STEP 4: Validate null values in key columns

# COMMAND ----------

try:
    key_columns = config["quality"]["key_columns"]

    for c in key_columns:
        if c in final_df.columns:

            null_count = final_df.filter(
                col(c).isNull()
            ).count()

            print(f"{c}: Null Count = {null_count}")

    logger.info("Null validation completed")

except Exception as e:
    logger.error(f"Error validating null values: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC #### STEP 5: Validate data types

# COMMAND ----------

try:
    print("Final Schema:")
    final_df.printSchema()

    logger.info("Schema validation completed")

except Exception as e:
    logger.error(f"Error validating schema: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC #### STEP 6: Preview final dataset

# COMMAND ----------


display(final_df.limit(10))

print("Final Row Count:", final_df.count())

# COMMAND ----------

# DBTITLE 1,Analysis Metric 6
# MAGIC %md
# MAGIC ### ✅ Analysis Metric 6: Final Quality Check Statistics

# COMMAND ----------

# DBTITLE 1,Metric 6: Final Counts After Quality Checks
print("=" * 80)
print("METRIC 6: FINAL COUNT AFTER DUPLICATE REMOVAL AND QUALITY CHECKS")
print("=" * 80)
print()

final_row_count = final_df.count()
final_col_count = len(final_df.columns)

print(f"Final row count (after duplicate removal): {final_row_count:,}")
print(f"Final column count: {final_col_count}")
print()
print(f"Rows removed due to duplicates: {merged_row_count - final_row_count:,}")
print(f"Duplicate removal rate: {((merged_row_count - final_row_count) / merged_row_count * 100):.2f}%")
print()
print("Final Schema (column names and data types):")
for i, field in enumerate(final_df.schema.fields, 1):
    print(f"  {i:2d}. {field.name:25s} : {str(field.dataType)}")

print("\n" + "=" * 80)
print()

# COMMAND ----------

# DBTITLE 1,Pipeline Summary
# MAGIC %md
# MAGIC ---
# MAGIC ## 📋 ETL PIPELINE COMPLETE SUMMARY
# MAGIC
# MAGIC All analysis metrics have been calculated and displayed throughout the pipeline.

# COMMAND ----------

# DBTITLE 1,Complete Pipeline Summary
print("\n" + "*" * 80)
print(" " * 25 + "ETL PIPELINE SUMMARY")
print("*" * 80)
print()

print("📊 PHASE 1: SETUP")
print("   ✅ Spark session initialized")
print("   ✅ Configuration loaded")
print()

print("📊 PHASE 2: DATA INGESTION")
print(f"   Files ingested: {len(csv_files)} CSV files")
print(f"   Total initial rows: {total_initial_rows:,}")
print()

print("🧹 PHASE 3: DATA CLEANING")
print("   ✅ Columns standardized (special chars → underscores)")
print("   ✅ NULL handling (empty strings → NULL)")
print("   ✅ Schema alignment across all datasets")
print("   ✅ Empty columns removed")
print()

print("🔄 PHASE 4: DATA TRANSFORMATION")
print("   ✅ Price values converted to USD (numeric)")
print("   ✅ Discount percentages extracted (numeric)")
print("   ✅ Quantity 'k' values converted (5k → 5000)")
print("   ✅ Rank values extracted (numeric)")
print(f"   Columns after transformation: {len(df_list[0].columns)}")
print(f"   Unwanted columns dropped: {len(config['cleanup']['drop_columns'])}")
print()

print("🔗 PHASE 5: DATA MERGING")
print(f"   Rows after merge: {merged_row_count:,}")
print(f"   Columns after merge: {merged_col_count}")
print()

print("✅ PHASE 6: QUALITY CHECKS")
print("   ✅ Numeric columns recast to proper types")
print("   ✅ Duplicates identified and removed")
print(f"   Final row count: {final_row_count:,}")
print(f"   Final column count: {final_col_count}")
print(f"   Duplicates removed: {merged_row_count - final_row_count:,}")
print()

print("*" * 80)
print(f" " * 25 + "✅ PIPELINE COMPLETE")
print("*" * 80)
print()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Phase 7: Save Final Output
# MAGIC

# COMMAND ----------

try:
    final_df.write \
        .mode(write_mode) \
        .format(file_format) \
        .save(output_path)

    logger.info(f"Final dataset saved successfully to {output_path}")

except Exception as e:
    logger.error(f"Error saving output: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC #### Validate saved output

# COMMAND ----------

try:
    validate_df = spark.read.format(file_format).load(output_path)

    print("Saved Row Count:", validate_df.count())

    print("Saved Schema:")
    validate_df.printSchema()

    display(validate_df.limit(10))

    logger.info("Output validation successful")

except Exception as e:
    logger.error(f"Error validating output: {e}")
    raise

# COMMAND ----------

#Completion
print("Pipeline executed successfully.")
print("Final processed dataset stored at:")
print(output_path)

# COMMAND ----------

# MAGIC %md
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC