"""
data_quality_checks.py
Data Quality Checker - Workforce & Revenue Analytics Platform
Runs validation checks on extracted data before loading to Snowflake
Author: Sai Puttur | Database Engineer
Updated: July 2026
"""

import logging
import pandas as pd
from datetime import date
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataQualityChecker:
    """
    Runs a suite of data quality checks across all source datasets.
    Checks include: null validation, duplicate detection, referential integrity,
    value range checks, and business rule validation.
    """

    def __init__(self):
        self.results = []
        self.passed_checks = 0
        self.failed_checks = 0

    def _log_check(self, check_name: str, passed: bool, details: str = ''):
        """Log the result of a single check"""
        status = 'PASS' if passed else 'FAIL'
        log_func = logger.info if passed else logger.error
        log_func(f"[{status}] {check_name}: {details}")
        self.results.append({'check': check_name, 'status': status, 'details': details})
        if passed:
            self.passed_checks += 1
        else:
            self.failed_checks += 1

    # ============================================================
    # EMPLOYEE DATA CHECKS
    # ============================================================
    def check_employee_nulls(self, df: pd.DataFrame) -> bool:
        """Ensure required employee fields are not null"""
        required_cols = ['employee_id', 'first_name', 'last_name', 'hire_date', 'employment_status']
        for col in required_cols:
            null_count = df[col].isna().sum()
            if null_count > 0:
                self._log_check(f'employee_null_check_{col}', False,
                                f'{null_count} null values in required field {col}')
                return False
            self._log_check(f'employee_null_check_{col}', True, 'No nulls')
        return True

    def check_employee_duplicates(self, df: pd.DataFrame) -> bool:
        """Detect duplicate employee_id records"""
        dupes = df.duplicated(subset=['employee_id'], keep=False).sum()
        passed = dupes == 0
        self._log_check('employee_duplicate_check', passed,
                        f'{dupes} duplicate employee_id records found')
        return passed

    def check_employee_status_values(self, df: pd.DataFrame) -> bool:
        """Validate employment_status contains only allowed values"""
        valid_statuses = {'Active', 'Inactive', 'On Leave', 'Terminated'}
        invalid = df[~df['employment_status'].isin(valid_statuses)]
        passed = len(invalid) == 0
        self._log_check('employee_status_values_check', passed,
                        f'{len(invalid)} records with invalid employment_status')
        return passed

    def check_hire_date_not_future(self, df: pd.DataFrame) -> bool:
        """Ensure hire_date is not in the future"""
        df['hire_date'] = pd.to_datetime(df['hire_date'])
        future_hires = df[df['hire_date'].dt.date > date.today()]
        passed = len(future_hires) == 0
        self._log_check('hire_date_future_check', passed,
                        f'{len(future_hires)} employees with future hire_date')
        return passed

    # ============================================================
    # CANDIDATE / ATS DATA CHECKS
    # ============================================================
    def check_candidate_duplicates(self, df: pd.DataFrame) -> bool:
        """Detect duplicate candidate profiles by email"""
        dupes = df.duplicated(subset=['email'], keep=False).sum()
        passed = dupes == 0
        self._log_check('candidate_duplicate_email_check', passed,
                        f'{dupes} duplicate candidate email records found')
        return passed

    def check_candidate_applied_date(self, df: pd.DataFrame) -> bool:
        """Validate applied_date is not null and not in the future"""
        null_count = df['applied_date'].isna().sum()
        if null_count > 0:
            self._log_check('candidate_applied_date_null_check', False,
                            f'{null_count} null applied_date values')
            return False
        df['applied_date'] = pd.to_datetime(df['applied_date'])
        future = df[df['applied_date'].dt.date > date.today()]
        passed = len(future) == 0
        self._log_check('candidate_applied_date_future_check', passed,
                        f'{len(future)} candidates with future applied_date')
        return passed

    # ============================================================
    # INVOICE DATA CHECKS
    # ============================================================
    def check_invoice_amounts(self, df: pd.DataFrame) -> bool:
        """Ensure invoice amounts are positive"""
        negative = df[df['invoice_amount'] <= 0]
        passed = len(negative) == 0
        self._log_check('invoice_amount_positive_check', passed,
                        f'{len(negative)} invoices with zero or negative amount')
        return passed

    def check_invoice_duplicate_ids(self, df: pd.DataFrame) -> bool:
        """Detect duplicate invoice_id records"""
        dupes = df.duplicated(subset=['invoice_id'], keep=False).sum()
        passed = dupes == 0
        self._log_check('invoice_duplicate_id_check', passed,
                        f'{dupes} duplicate invoice_id records')
        return passed

    def check_client_id_not_null(self, df: pd.DataFrame) -> bool:
        """Validate client_id is present on all invoice records"""
        null_count = df['client_id'].isna().sum()
        passed = null_count == 0
        self._log_check('invoice_client_id_null_check', passed,
                        f'{null_count} invoices missing client_id')
        return passed

    # ============================================================
    # TIMESHEET DATA CHECKS
    # ============================================================
    def check_timesheet_hours(self, df: pd.DataFrame) -> bool:
        """Ensure billable hours are between 0 and 24 per day"""
        invalid = df[(df['billable_hours'] < 0) | (df['billable_hours'] > 24)]
        passed = len(invalid) == 0
        self._log_check('timesheet_hours_range_check', passed,
                        f'{len(invalid)} timesheet records with hours out of 0-24 range')
        return passed

    # ============================================================
    # MAIN RUNNER
    # ============================================================
    def run_all_checks(self, run_date: str = None) -> Dict[str, Any]:
        """
        Load all source data files and run applicable checks.
        Returns summary dict with passed/failed counts.
        """
        logger.info(f"=== Data Quality Checker starting for run_date={run_date} ===")
        import os
        base_path = os.path.join(os.path.dirname(__file__), '../../sample_data')

        # Employee checks
        emp_df = pd.read_csv(f'{base_path}/employees.csv')
        self.check_employee_nulls(emp_df)
        self.check_employee_duplicates(emp_df)
        self.check_employee_status_values(emp_df)
        self.check_hire_date_not_future(emp_df)

        # Candidate checks
        cand_df = pd.read_csv(f'{base_path}/candidates.csv')
        self.check_candidate_duplicates(cand_df)
        self.check_candidate_applied_date(cand_df)

        # Invoice checks
        inv_df = pd.read_csv(f'{base_path}/invoices.csv')
        self.check_invoice_amounts(inv_df)
        self.check_invoice_duplicate_ids(inv_df)
        self.check_client_id_not_null(inv_df)

        # Timesheet checks
        ts_df = pd.read_csv(f'{base_path}/timesheets.csv')
        self.check_timesheet_hours(ts_df)

        summary = {
            'run_date': run_date,
            'total_checks': self.passed_checks + self.failed_checks,
            'passed_checks': self.passed_checks,
            'failed_checks': self.failed_checks,
            'results': self.results
        }
        logger.info(f"=== Quality checks complete: {self.passed_checks} passed, {self.failed_checks} failed ===")
        return summary


if __name__ == '__main__':
    checker = DataQualityChecker()
    results = checker.run_all_checks(run_date=date.today().isoformat())
    print(f"Total Passed: {results['passed_checks']}")
    print(f"Total Failed: {results['failed_checks']}")
