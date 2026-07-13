"""
workforce_analytics_dag.py
Airflow DAG: Workforce & Revenue Analytics Platform - Daily ETL
Author: Sai Puttur | Database Engineer
Schedule: Daily at 2:00 AM EST
Updated: July 2026
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.utils.email import send_email
import logging

# ============================================================
# DEFAULT ARGUMENTS
# ============================================================
default_args = {
    'owner': 'sai.puttur',
    'depends_on_past': False,
    'start_date': datetime(2026, 7, 1),
    'email': ['sai.puttur@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=15),
    'execution_timeout': timedelta(hours=3),
}

# ============================================================
# DAG DEFINITION
# ============================================================
dag = DAG(
    dag_id='workforce_analytics_dag',
    default_args=default_args,
    description='Daily ETL pipeline for Workforce & Revenue Analytics Data Platform',
    schedule_interval='0 2 * * *',   # 2:00 AM EST daily
    catchup=False,
    max_active_runs=1,
    tags=['analytics', 'hr', 'recruitment', 'etl', 'production'],
)

# ============================================================
# PYTHON CALLABLES
# ============================================================
def extract_hris_data(**context):
    """Extract employee and HR data from HRIS (Workday)"""
    from scripts.extract.extract_hris import HRISExtractor
    logging.info("Starting HRIS extraction...")
    extractor = HRISExtractor()
    records = extractor.run(run_date=context['ds'])
    logging.info(f"Extracted {records} records from HRIS")
    return records

def extract_ats_data(**context):
    """Extract candidate and requisition data from ATS (Greenhouse)"""
    from scripts.extract.extract_ats import ATSExtractor
    logging.info("Starting ATS extraction...")
    extractor = ATSExtractor()
    records = extractor.run(run_date=context['ds'])
    logging.info(f"Extracted {records} records from ATS")
    return records

def extract_timesheet_data(**context):
    """Extract timesheet data from operations system"""
    from scripts.extract.extract_timesheets import TimesheetExtractor
    logging.info("Starting Timesheet extraction...")
    extractor = TimesheetExtractor()
    records = extractor.run(run_date=context['ds'])
    logging.info(f"Extracted {records} timesheet records")
    return records

def run_data_quality_checks(**context):
    """Run data quality validation before loading"""
    from scripts.transform.data_quality_checks import DataQualityChecker
    logging.info("Running data quality checks...")
    checker = DataQualityChecker()
    results = checker.run_all_checks(run_date=context['ds'])
    if results['failed_checks'] > 0:
        raise ValueError(f"Data quality checks failed: {results['failed_checks']} issues found")
    logging.info(f"All data quality checks passed: {results['passed_checks']} checks OK")

def load_to_snowflake(**context):
    """Load processed data into Snowflake raw schema"""
    from scripts.load.load_to_snowflake import SnowflakeLoader
    logging.info("Loading data to Snowflake...")
    loader = SnowflakeLoader()
    results = loader.load_all(run_date=context['ds'])
    logging.info(f"Load complete: {results}")
    return results

# ============================================================
# TASK DEFINITIONS
# ============================================================

# Extraction tasks (run in parallel)
extract_hris = PythonOperator(
    task_id='extract_hris_data',
    python_callable=extract_hris_data,
    dag=dag,
)

extract_ats = PythonOperator(
    task_id='extract_ats_data',
    python_callable=extract_ats_data,
    dag=dag,
)

extract_timesheets = PythonOperator(
    task_id='extract_timesheet_data',
    python_callable=extract_timesheet_data,
    dag=dag,
)

# Data quality check
data_quality = PythonOperator(
    task_id='run_data_quality_checks',
    python_callable=run_data_quality_checks,
    dag=dag,
)

# Load to Snowflake raw schema
load_raw = PythonOperator(
    task_id='load_to_snowflake_raw',
    python_callable=load_to_snowflake,
    dag=dag,
)

# Run dbt staging models
dbt_staging = BashOperator(
    task_id='dbt_run_staging',
    bash_command='cd /opt/airflow/dbt_project && dbt run --select staging --profiles-dir /opt/airflow/dbt_project',
    dag=dag,
)

# Run dbt intermediate models
dbt_intermediate = BashOperator(
    task_id='dbt_run_intermediate',
    bash_command='cd /opt/airflow/dbt_project && dbt run --select intermediate --profiles-dir /opt/airflow/dbt_project',
    dag=dag,
)

# Run dbt marts (dimensions + facts)
dbt_marts = BashOperator(
    task_id='dbt_run_marts',
    bash_command='cd /opt/airflow/dbt_project && dbt run --select marts --profiles-dir /opt/airflow/dbt_project',
    dag=dag,
)

# Run dbt tests
dbt_tests = BashOperator(
    task_id='dbt_test_all',
    bash_command='cd /opt/airflow/dbt_project && dbt test --profiles-dir /opt/airflow/dbt_project',
    dag=dag,
)

# Validate row counts in Snowflake
validate_counts = SnowflakeOperator(
    task_id='validate_row_counts',
    sql="""
        SELECT
            'dim_employee' AS table_name, COUNT(*) AS row_count
        FROM analytics.dim_employee WHERE is_current = TRUE
        UNION ALL
        SELECT 'fact_recruitment_pipeline', COUNT(*)
        FROM analytics.fact_recruitment_pipeline
        WHERE DATE_TRUNC('day', created_at) = CURRENT_DATE();
    """,
    snowflake_conn_id='snowflake_analytics',
    dag=dag,
)

# ============================================================
# TASK DEPENDENCIES (DAG GRAPH)
# ============================================================
#
#  extract_hris ----
#                   \---> data_quality --> load_raw --> dbt_staging
#  extract_ats  ----/                                       |
#                                                      dbt_intermediate
#  extract_timesheets --> (feeds into load_raw)             |
#                                                       dbt_marts
#                                                           |
#                                                       dbt_tests
#                                                           |
#                                                     validate_counts

[extract_hris, extract_ats, extract_timesheets] >> data_quality
data_quality >> load_raw
load_raw >> dbt_staging
dbt_staging >> dbt_intermediate
dbt_intermediate >> dbt_marts
dbt_marts >> dbt_tests
dbt_tests >> validate_counts
