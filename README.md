Project 2 - Large-Scale Healthcare Pipeline with S3, dbt & DuckDB
Team Size: 3 people
Format: Scalable data processing with industry professional presentation


🎯 Project Objectives
By the end of this project, teams will have demonstrated:

Large-scale data processing handling 10GB+ datasets with memory-efficient techniques
S3 data lake integration for raw data staging and cloud-native processing
dbt medallion architecture implementing raw → staging → marts in DuckDB
Data quality engineering with dbt tests validating pipeline integrity
Problem-solving independence through documentation research and tool evaluation


⚡ Important: Learning Approach
This project emphasizes learning how to learn:

Tool evaluation — You decide when to use Pandas vs Polars based on your research
Documentation first — Read the docs, try it, break it, fix it
Architecture decisions — Partitioning strategy, schema design, and optimization are your choices to justify
Ask the right questions — Know when to research independently vs when to ask for help


📚 Business Scenario
Client: HealthAnalytics Platform

HealthAnalytics is building a national healthcare intelligence platform requiring:

Business Challenge:

Massive healthcare datasets (10GB+ provider files) requiring efficient processing
Geographic intelligence integrating provider data with demographic and census information
Data quality assurance for regulatory compliance and business intelligence accuracy
Scalable architecture supporting weekly data updates and growing dataset volumes

Technical Requirements:

Process National Plan and Provider Enumeration System (NPPES) data (10GB+ CSV)
Integrate geographic reference data and Census API information
Build medallion architecture (raw → staging → marts) using dbt and DuckDB
Stage raw data in S3 with intelligent organization
Implement comprehensive dbt tests for data quality validation
Demonstrate scalability patterns for 10x data volume growth


🏗️ Architecture
┌─────────────────────┐
│     S3 Data Lake    │
│     (Raw Staging)   │
│                     │
│ ├─ nppes/           │
│ ├─ geographic/      │
│ └─ reference/       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Ingestion Layer   │
│                     │
│ Pandas or Polars    │
│ (Your choice)       │
│ Memory-efficient    │
│ chunked processing  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│            dbt + DuckDB                     │
│                                             │
│  ┌─────────┐  ┌──────────┐  ┌────────────┐  │
│  │   raw/  │→ │ staging/ │→ │   marts/   │  │
│  │         │  │          │  │            │  │
│  │ sources │  │ cleaned  │  │ analytics  │  │
│  │ external│  │ 1:1      │  │ joined     │  │
│  └─────────┘  └──────────┘  └────────────┘  │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │            dbt tests                │    │
│  │  unique, not_null, relationships   │    │
│  │  custom singular tests              │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│   GitHub Actions    │
│   (Stretch Goal)    │
│                     │
│ Automated test runs │
│ on pull requests    │
└─────────────────────┘


📊 Data Sources
Primary Dataset: NPPES Healthcare Provider Data

Size: 10GB+ CSV file with provider information
Complexity: Nested data structures, quality issues, regulatory requirements
Update Pattern: Weekly updates requiring incremental processing
Scale Challenge: Memory-efficient processing without infrastructure limitations

Supporting Data Sources:

Geographic Crosswalk: ZIP-to-county mapping (Excel format)
Census Demographics: Population and socioeconomic data via API
Reference Data: FIPS codes, state mappings, healthcare taxonomy


📅 Project Timeline & Phases
Architecture & Foundation
Architecture Design

Research and document your processing strategy (Pandas vs Polars — justify your choice)
Design S3 organization for raw data staging
Plan dbt project structure for medallion architecture
Design DuckDB schema for analytical workloads

Foundation Implementation

Set up S3 bucket organization and upload raw data
Initialize dbt project with DuckDB adapter
Implement memory-efficient data loading (chunked processing)
Validate architecture with sample data subset


Core Pipeline Development
Ingestion & Raw Layer

Full dataset processing with memory-efficient techniques
S3 integration for raw data access
dbt sources configuration pointing to S3/external files
Error handling for data quality issues in source data

Staging Layer

1:1 cleaning models (Python or SQL — your choice per model)
Data type standardization and null handling
Geographic data integration
Census API data processing


Analytics & Testing
Marts Layer

Analytical models joining provider, geographic, and demographic data
Business intelligence aggregations
Performance optimization for complex queries

dbt Tests (Required)

Generic tests on all marts models (unique, not_null, accepted_values)
Relationship tests validating referential integrity
Custom singular tests for business logic validation
Document your test coverage and rationale


💡 Marts Layer Guidance
Your marts layer should answer business questions by joining your cleaned staging models. Here are some directions to consider:
Core Marts (Expected)
Model
Description
Likely Joins
provider_directory
Enriched provider records with location context
provider + geographic
providers_by_geography
Provider counts aggregated by state, county, or ZIP
provider + geographic
specialty_distribution
What specialties exist in which regions
provider + geographic
provider_density
Providers per capita by geographic area
provider + geographic + census

Stretch Marts (If Time Allows)
Model
Description
underserved_areas
Regions with low provider-to-population ratios
specialty_gaps
Geographic areas missing key specialties

What We're Looking For
Joins across staging models — Your marts should combine data, not just pass it through
Business logic — Aggregations, calculations, or filters that answer real questions
Tested outputs — Every mart should have dbt tests validating data quality
Questions Your Marts Should Answer
How many providers are in each state/county?
Which areas have the most/least providers per capita?
What is the specialty mix in a given region?
Where might there be gaps in healthcare coverage?

Design your marts to answer questions a healthcare analyst would actually ask.
Production Readiness
Quality Assurance

Full pipeline run with complete dataset
Test execution and failure resolution
Performance profiling and optimization
dbt docs generation

Stretch Goal: GitHub Actions

Configure workflow to run dbt test on pull requests
Add dbt build for full pipeline validation
Document CI/CD setup for team handoff


Presentation
Final Integration

End-to-end system validation
Performance metrics collection
Presentation preparation and practice




🎤 Presentation Requirements
Section 1: Architecture & Tool Decisions (5 minutes)
Why you chose Pandas vs Polars (or both) — show your research
S3 organization strategy and rationale
dbt medallion architecture design decisions
DuckDB as the analytical engine — why it fits
Section 2: Technical Challenges & Solutions (5 minutes)
Memory efficiency — how you handled 10GB+ without crashing
Data quality issues discovered and how dbt tests catch them
Geographic integration complexity and edge cases
Performance bottlenecks and how you resolved them
Section 3: Data Quality & Testing (3 minutes)
dbt test strategy — what you tested and why
Test failures you encountered and what they revealed
How tests would catch issues in production
Section 4: Live Demonstration (5 minutes)
Run dbt build showing the pipeline execute
Run dbt test showing quality validation
Show dbt docs lineage graph
Query DuckDB to show analytical results
Section 5: Stretch Goal Demo (if completed)
GitHub Actions workflow triggering on PR
Automated test results in CI


✅ Success Criteria
Technical Requirements (Must Have)
Requirement
Evidence
Process full 10GB+ dataset
Pipeline completes without memory errors
S3 raw data staging
Organized bucket with documented structure
dbt medallion architecture
raw → staging → marts layers implemented
dbt tests passing
Generic + singular tests on marts models
DuckDB analytics
Complex queries demonstrating business value
dbt docs
Generated documentation with lineage graph

Stretch Goal
Requirement
Evidence
GitHub Actions CI
Workflow runs dbt test on pull requests

Professional Development
Skill
Evidence
Tool evaluation
Documented rationale for Pandas/Polars choice
Documentation research
Can explain decisions from official docs
Problem-solving
Overcame challenges independently before asking
Architecture thinking
Justified design decisions under Q&A



🛠️ Technical Starting Points
These are starting points for your research, not complete solutions.

Memory-Efficient Processing (research chunked reading):

# How would you process a 10GB file without loading it all into memory?
# Research: pandas read_csv chunksize, polars lazy evaluation

dbt External Sources (research dbt-duckdb external sources):

# How do you point dbt at files in S3 or local filesystem?
# Research: dbt-duckdb external_location, sources.yml

dbt Tests (research generic and singular tests):

# What tests should you write? Where do they go?
# Research: schema.yml tests, tests/ folder

GitHub Actions (stretch — research dbt in CI):

# How do you run dbt commands in GitHub Actions?
# Research: dbt GitHub Actions, workflow yaml


📋 Resources
Provided:

NPPES healthcare provider dataset (10GB+ CSV)
Geographic reference data and Census API access
S3 bucket with write permissions
Prior project resources from class exercises

Your Job to Find:

Official documentation for your tool choices
dbt-duckdb adapter documentation
GitHub Actions workflow syntax
Performance optimization techniques


🎯 Remember
This project is about learning how to learn. You will encounter problems we haven't covered in class. That's intentional.

When stuck:

Read the official documentation
Search for the specific error message
Try a minimal example to isolate the problem
Ask a teammate
Then ask an instructor (with what you've already tried)

The goal is to make you job ready — able to pick up new tools, read docs, and solve problems you've never seen before.




