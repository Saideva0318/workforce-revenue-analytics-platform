# Workforce & Revenue Analytics Data Platform

![Status](https://img.shields.io/badge/Status-Active-brightgreen) ![Stack](https://img.shields.io/badge/Stack-Snowflake%20%7C%20dbt%20%7C%20Airflow%20%7C%20Python-blue) ![Domain](https://img.shields.io/badge/Domain-Data%20Engineering-orange)

## Overview

An enterprise-grade cloud data warehouse that consolidates structured operational data from Human Resources, Talent Acquisition, Finance/Accounts, and Operations source systems into a centralized, governed database environment. The platform serves as the single source of truth for workforce and revenue reporting, replacing fragmented spreadsheet-based reporting with standardized, auditable database structures.

**Role:** Database Engineer — Sai Puttur
**Location:** Metuchen, NJ | **Employment:** Full-Time, 40 hrs/week

---

## Architecture

```
+------------------+     +------------------+     +------------------+     +------------------+
|   SOURCE SYSTEMS |     |   RAW / LANDING  |     |  STAGING LAYER   |     | CURATED WAREHOUSE|
|                  | --> |                  | --> |                  | --> |                  |
| - HRIS (Workday) |     | - Raw CSV/JSON   |     | - stg_employees  |     | - dim_employee   |
| - ATS (Greenhouse|     | - Snowflake Stage|     | - stg_candidates |     | - dim_position   |
| - ERP (NetSuite) |     | - S3 Bucket      |     | - stg_invoices   |     | - fact_recruitment|
| - Timesheets     |     | - Audit Logs     |     | - stg_timesheets |     | - fact_utilization|
| - CRM (Salesforce|     |                  |     | - stg_payments   |     | - fact_invoice   |
+------------------+     +------------------+     +------------------+     +------------------+
                                                                                    |
                                                                                    v
                                                                         +------------------+
                                                                         |   BI / REPORTING |
                                                                         | - Power BI Dash  |
                                                                         | - Ad-hoc SQL     |
                                                                         | - Dept Reports   |
                                                                         +------------------+
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Cloud Data Warehouse | Snowflake |
| Transformation | dbt (Data Build Tool) |
| Orchestration | Apache Airflow |
| Extraction & Scripting | Python 3.11 |
| Data Quality | dbt Tests + Great Expectations |
| Dashboards | Power BI |
| Infrastructure as Code | Terraform |
| Version Control | GitHub |
| CI/CD | GitHub Actions |

---

## Repository Structure

```
workforce-revenue-analytics-platform/
|
+-- README.md
+-- .gitignore
|
+-- docs/
|   +-- architecture_overview.md
|   +-- data_dictionary.md
|   +-- source_to_target_mapping.md
|   +-- erd_description.md
|   +-- runbook.md
|
+-- sql/
|   +-- ddl/
|   |   +-- dimensions/
|   |   |   +-- dim_employee.sql
|   |   |   +-- dim_position.sql
|   |   |   +-- dim_candidate.sql
|   |   |   +-- dim_client.sql
|   |   |   +-- dim_project.sql
|   |   |   +-- dim_date.sql
|   |   |   +-- dim_recruitment_stage.sql
|   |   +-- facts/
|   |       +-- fact_recruitment_pipeline.sql
|   |       +-- fact_consultant_utilization.sql
|   |       +-- fact_invoice_collections.sql
|   |       +-- fact_payment_collection.sql
|   |       +-- fact_employee_snapshot.sql
|   +-- queries/
|       +-- recruiter_performance.sql
|       +-- utilization_report.sql
|       +-- invoice_aging.sql
|       +-- time_to_fill.sql
|
+-- dbt_project/
|   +-- dbt_project.yml
|   +-- profiles.yml
|   +-- models/
|   |   +-- staging/
|   |   |   +-- stg_employees.sql
|   |   |   +-- stg_candidates.sql
|   |   |   +-- stg_requisitions.sql
|   |   |   +-- stg_timesheets.sql
|   |   |   +-- stg_invoices.sql
|   |   |   +-- stg_payments.sql
|   |   +-- intermediate/
|   |   |   +-- int_employee_history.sql
|   |   |   +-- int_recruitment_stages.sql
|   |   |   +-- int_invoice_aging.sql
|   |   +-- marts/
|   |       +-- dim_employee.sql
|   |       +-- dim_position.sql
|   |       +-- dim_candidate.sql
|   |       +-- fact_recruitment_pipeline.sql
|   |       +-- fact_consultant_utilization.sql
|   |       +-- fact_invoice_collections.sql
|   |       +-- fact_payment_collection.sql
|   +-- tests/
|   |   +-- assert_no_duplicate_employees.sql
|   |   +-- assert_invoice_amounts_positive.sql
|   +-- macros/
|       +-- generate_surrogate_key.sql
|       +-- scd2_merge.sql
|
+-- orchestration/
|   +-- dags/
|   |   +-- workforce_analytics_dag.py
|   |   +-- finance_etl_dag.py
|   +-- config/
|       +-- connections.yaml
|
+-- scripts/
|   +-- extract/
|   |   +-- extract_hris.py
|   |   +-- extract_ats.py
|   |   +-- extract_erp.py
|   |   +-- extract_timesheets.py
|   +-- transform/
|   |   +-- data_quality_checks.py
|   |   +-- dedup_candidates.py
|   +-- load/
|       +-- load_to_snowflake.py
|
+-- sample_data/
|   +-- employees.csv
|   +-- candidates.csv
|   +-- requisitions.csv
|   +-- timesheets.csv
|   +-- invoices.csv
|   +-- payments.csv
|
+-- dashboards/
    +-- recruitment_dashboard_spec.md
    +-- utilization_dashboard_spec.md
    +-- finance_dashboard_spec.md
```

---

## Data Model

### Dimension Tables

| Table | Description | Key Fields |
|---|---|---|
| `dim_employee` | Employee master with SCD2 history | employee_id, department, status, hire_date |
| `dim_position` | Job positions and requisitions | position_id, title, department, level |
| `dim_candidate` | Candidate profiles from ATS | candidate_id, source, current_stage |
| `dim_client` | Client accounts and billing info | client_id, client_name, contract_type |
| `dim_project` | Active and historical project records | project_id, client_id, start_date, end_date |
| `dim_date` | Standard date dimension | date_key, year, quarter, month, week |
| `dim_recruitment_stage` | Hiring pipeline stage definitions | stage_id, stage_name, stage_order |

### Fact Tables

| Table | Grain | Key Metrics |
|---|---|---|
| `fact_recruitment_pipeline` | One row per candidate per stage | days_in_stage, time_to_fill, stage_conversions |
| `fact_consultant_utilization` | One row per consultant per day | billable_hours, total_hours, utilization_pct |
| `fact_invoice_collections` | One row per invoice | invoice_amount, aging_bucket, days_outstanding |
| `fact_payment_collection` | One row per payment received | payment_amount, payment_date, collection_rate |
| `fact_employee_snapshot` | Daily employee headcount snapshot | headcount, attrition_count, new_hires |

---

## Key Business Metrics

### Recruitment
- Time-to-Fill (days from requisition open to offer accepted)
- Recruiter Performance (submittals, interviews, placements per recruiter)
- Stage Conversion Rate (% of candidates advancing per stage)
- Pipeline Aging (average days per open requisition)

### Operations
- Consultant Billable Utilization (%)
- Capacity Utilization (%)
- Revenue per Consultant
- Active Assignments by Client/Project

### Finance
- Invoice Aging Buckets (0-30, 31-60, 61-90, 90+ days)
- Days Sales Outstanding (DSO)
- Collection Rate (%)
- Outstanding Balance by Client

---

## ETL Pipeline Flow

```
1. EXTRACT   --> Python scripts pull data from HRIS, ATS, ERP, Timesheets, CRM
2. LOAD RAW  --> Raw records loaded into Snowflake raw schema (append-only)
3. STAGE     --> dbt stg_* models clean, cast, and rename fields
4. TRANSFORM --> dbt int_* models apply business rules, deduplication, SCD2
5. CURATE    --> dbt dim_* and fact_* models build analytical layer
6. TEST      --> dbt tests + Great Expectations validate every model
7. SERVE     --> Power BI connects to curated marts for dashboards
```

**Incremental Strategy:** Date-range-based loads and change-data-capture for large fact tables.
**Schedule:** Airflow DAGs run daily at 2:00 AM EST for full refresh; hourly for utilization facts.

---

## Security & Governance

| Control | Implementation |
|---|---|
| Role-Based Access Control | Snowflake RBAC — HR_ROLE, FINANCE_ROLE, OPS_ROLE, ADMIN_ROLE |
| PII Data Masking | Dynamic Data Masking on salary, SSN, email, phone fields |
| Row-Level Security | Department-scoped views per role |
| Audit Logging | All DDL/DML changes logged to audit schema |
| Data Catalog | Column-level lineage documented in data_dictionary.md |

---

## Performance Optimization

- Snowflake clustering keys on `date_key` and `employee_id` for large fact tables
- Materialized views for high-frequency dashboard queries
- Separate Snowflake virtual warehouses for ETL vs BI workloads
- Query profiling via Snowflake Query History and dbt artifacts
- Benchmark log tracking refresh times, query durations, and ETL completion rates

---

## Project Phases

| Phase | Scope | Duration |
|---|---|---|
| Phase 1 | Foundation, Snowflake setup, dbt project, HR & Recruitment core | Weeks 1-4 |
| Phase 2 | Finance & Operations integration, utilization and collections facts | Weeks 5-8 |
| Phase 3 | Advanced analytics, snapshots, materialized views, performance tuning | Weeks 9-11 |
| Phase 4 | Governance, security hardening, training docs, handoff artifacts | Weeks 12-13 |

---

## Job Duties Mapped to Project Components

| Duty Area | Project Implementation |
|---|---|
| Business Requirements Analysis | `docs/source_to_target_mapping.md`, `docs/data_dictionary.md` |
| Relational DB Design & Schema | `sql/ddl/dimensions/`, `sql/ddl/facts/` |
| ETL Pipeline Development | `scripts/extract/`, `scripts/load/`, `dbt_project/models/` |
| Query Performance & Monitoring | `sql/queries/`, `docs/runbook.md` |
| Database Security Configuration | Snowflake RBAC scripts, `docs/architecture_overview.md` |
| Data Analysis & Reporting Support | `dashboards/`, `sql/queries/` |
| Database Maintenance & User Support | `docs/runbook.md`, dbt tests |

---

## Getting Started

```bash
# Clone the repository
git clone https://github.com/Saideva0318/workforce-revenue-analytics-platform.git
cd workforce-revenue-analytics-platform

# Install Python dependencies
pip install -r requirements.txt

# Configure dbt profile
cp dbt_project/profiles.yml ~/.dbt/profiles.yml
# Edit profiles.yml with your Snowflake credentials

# Run dbt models
cd dbt_project
dbt deps
dbt run
dbt test

# Start Airflow
cd ../orchestration
airflow db init
airflow scheduler &
airflow webserver
```

---

## Contact

**Database Engineer:** Sai Puttur
**Organization:** Workforce & Revenue Analytics Platform Team
**Location:** 6 Bridge Street, Bldg. C, Metuchen, NJ 08840
