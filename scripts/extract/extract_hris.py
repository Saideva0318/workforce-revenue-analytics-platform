"""
extract_hris.py
HRIS Data Extractor - Workforce & Revenue Analytics Platform
Extracts employee, department, and HR data from HRIS (Workday API simulation)
Author: Sai Puttur | Database Engineer
Updated: July 2026
"""

import os
import json
import logging
import pandas as pd
from datetime import datetime, date
from typing import Optional
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HRISExtractor:
    """
    Extracts employee data from HRIS source system.
    Supports incremental loads using last_modified_date.
    Source: Workday HRIS (simulated via CSV/API in this demo)
    """

    def __init__(self):
        self.source_name = 'HRIS_WORKDAY'
        self.raw_schema = 'RAW'
        self.raw_table = 'raw_employees'
        self.snowflake_conn = self._get_snowflake_connection()

    def _get_snowflake_connection(self):
        """Initialize Snowflake connection from environment variables"""
        return snowflake.connector.connect(
            account=os.environ['SNOWFLAKE_ACCOUNT'],
            user=os.environ['SNOWFLAKE_USER'],
            password=os.environ['SNOWFLAKE_PASSWORD'],
            warehouse=os.environ.get('SNOWFLAKE_WAREHOUSE', 'ETL_WH'),
            database=os.environ.get('SNOWFLAKE_DATABASE', 'WORKFORCE_DB'),
            schema=self.raw_schema
        )

    def extract_employees(self, run_date: str) -> pd.DataFrame:
        """
        Extract employee records modified since last run.
        In production: calls Workday SOAP/REST API.
        In demo: reads from sample_data/employees.csv
        """
        logger.info(f"Extracting employee records for run_date={run_date}")

        # Load from sample data (replace with API call in production)
        sample_path = os.path.join(
            os.path.dirname(__file__), '../../sample_data/employees.csv'
        )
        df = pd.read_csv(sample_path)

        # Apply incremental filter
        df['last_modified_date'] = pd.to_datetime(df['last_modified_date'])
        df_filtered = df[df['last_modified_date'].dt.date <= pd.Timestamp(run_date).date()]

        logger.info(f"Extracted {len(df_filtered)} employee records")
        return df_filtered

    def validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply basic validation and cleansing rules"""
        logger.info("Validating employee data...")

        # Remove records with no employee_id
        before = len(df)
        df = df.dropna(subset=['employee_id'])
        logger.info(f"Dropped {before - len(df)} records missing employee_id")

        # Standardize employment_status values
        valid_statuses = ['Active', 'Inactive', 'On Leave', 'Terminated']
        df['employment_status'] = df['employment_status'].str.strip().str.title()
        df = df[df['employment_status'].isin(valid_statuses)]

        # Standardize employment_type
        df['employment_type'] = df['employment_type'].str.strip().str.title()

        # Add ETL metadata columns
        df['source_system'] = self.source_name
        df['etl_load_date'] = datetime.utcnow().isoformat()

        logger.info(f"Validation complete. {len(df)} records passed.")
        return df

    def load_to_raw(self, df: pd.DataFrame) -> int:
        """Load validated records into Snowflake raw schema"""
        logger.info(f"Loading {len(df)} records to {self.raw_schema}.{self.raw_table}...")

        # Truncate staging table before load
        cursor = self.snowflake_conn.cursor()
        cursor.execute(f"TRUNCATE TABLE IF EXISTS {self.raw_schema}.{self.raw_table}_staging")

        # Write to Snowflake using write_pandas
        success, nchunks, nrows, _ = write_pandas(
            conn=self.snowflake_conn,
            df=df,
            table_name=f"{self.raw_table}_staging",
            schema=self.raw_schema,
            auto_create_table=True,
            overwrite=True
        )

        if success:
            logger.info(f"Successfully loaded {nrows} rows in {nchunks} chunks")
            # Merge staging into raw table
            cursor.execute(f"""
                MERGE INTO {self.raw_schema}.{self.raw_table} AS target
                USING {self.raw_schema}.{self.raw_table}_staging AS source
                ON target.employee_id = source.employee_id
                WHEN MATCHED THEN UPDATE SET
                    target.employment_status = source.employment_status,
                    target.department = source.department,
                    target.job_title = source.job_title,
                    target.etl_load_date = source.etl_load_date
                WHEN NOT MATCHED THEN INSERT VALUES (
                    source.employee_id, source.first_name, source.last_name,
                    source.email, source.department, source.job_title,
                    source.employment_type, source.hire_date, source.termination_date,
                    source.employment_status, source.manager_id, source.location,
                    source.salary, source.source_system, source.etl_load_date
                )
            """)
            return nrows
        else:
            raise RuntimeError("Failed to load data to Snowflake")

    def run(self, run_date: Optional[str] = None) -> int:
        """Main entry point - extract, validate, and load"""
        if run_date is None:
            run_date = date.today().isoformat()

        logger.info(f"=== HRIS Extractor starting for run_date={run_date} ===")
        try:
            df = self.extract_employees(run_date)
            df = self.validate_data(df)
            records_loaded = self.load_to_raw(df)
            logger.info(f"=== HRIS Extractor complete: {records_loaded} records loaded ===")
            return records_loaded
        except Exception as e:
            logger.error(f"HRIS extraction failed: {str(e)}")
            raise
        finally:
            if self.snowflake_conn:
                self.snowflake_conn.close()


if __name__ == '__main__':
    extractor = HRISExtractor()
    extractor.run()
