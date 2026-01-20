## Project Overview

This project is a healthcare data pipeline that ingests large-scale provider and population data, cleans and transforms it, and generates analytics for health coverage, provider density, and specialty mix.

## Key Goals:

Efficient ingestion of CSV and Excel files (3 MB–10 GB+)

Data cleaning and standardization (provider names, postal codes, missing values)

Generation of fact and dimension tables for analytics

Automated data quality testing using dbt
Architecture

## Pipeline Flow:

# Ingestion

Polars (pl.read_excel()) for Excel files

DuckDB (read_csv_auto()) for CSVs, supporting parallel execution for large files

# Storage

S3 for raw, staged, and processed data

Parquet format for downstream consumption

# Transformation

dbt Medallion Architecture (Bronze → Silver → Gold)

Deduplication, ZIP → county mapping, provider name standardization

Analytics / Marts

Provider density (providers per 10k population)

Healthcare coverage gaps

Specialty mix per region

## Architecture

Key Technical Challenges

Large file ingestion (>10GB CSVs)

Dynamic threshold, parallel threads, memory limits, temporary storage in DuckDB

Data inconsistencies

Postal codes with 9 digits → standardized using RTRIM

Missing provider first/last name or organization name → applied rules to assign provider_name

Performance optimization

Pre-filtered unnecessary columns

Stored intermediate and final data as Parquet for faster repeated queries

Data Quality & Testing

dbt tests include:

Not null: provider_name, provider_postal_code_5

Uniqueness: npi in provider directory

Non-negative metrics: provider_count, providers_per_10k_population

Failures catch missing or inconsistent data before it reaches production.

## Dependencies

Python ≥3.10

Polars

DuckDB

dbt (with dbt-duckdb adapter)

Pandas (optional, for Excel handling)

S3 (AWS CLI or boto3 for data storage)

## Setup & Usage

Clone the repository
Install dependencies
Configure S3 & DuckDB

Set S3 bucket paths for raw and processed data

Configure DuckDB temp directory and memory settings

Run the pipeline

## File Structure

```text
├── README.md
├── nppes_dbt
│   ├── models
|   |     |_________ Staging
|   |     |_________ Marts
|   |
│   ├── tests/
│   
|--- sample_data
|        |___ all sample csv for testing
|
├── ingestion/
│   |___ api_extract.py
│   |___ ingestion.py
|   |___ local_logging.py
|   |___ main.py
|   |___ upload.py
|   |
├── scripts/
│   └── load_sample_data.py
|
├── requirements.txt

```

## References
https://duckdb.org/docs/stable/guides/network_cloud_storage/s3_import
https://duckdb.org/docs/stable/clients/python/data_ingestion
https://duckdb.org/docs/stable/guides/performance/how_to_tune_workloads
https://duckdb.org/docs/stable/configuration/overview
https://duckdb.org/2024/07/09/memory-management
