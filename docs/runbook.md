# Operations Runbook
## Workforce & Revenue Analytics Data Platform

**Version:** 1.0 | **Owner:** Database Engineer | **Last Updated:** July 2026

---

## 1. Daily Operations Checklist

### Morning Checks (8:00 AM EST)
- [ ] Verify Airflow DAG `workforce_analytics_dag` completed successfully
- [ ] Check Snowflake query history for failed queries
- [ ] Review ETL job logs in `/orchestration/logs/`
- [ ] Confirm all fact tables updated with previous day data
- [ ] Validate row counts match expected ranges

### Evening Checks (6:00 PM EST)
- [ ] Check incremental utilization fact load completed
- [ ] Verify dbt test results show 0 failures
- [ ] Review Airflow task durations against benchmarks

---

## 2. ETL Pipeline Schedule

| DAG | Schedule | Description |
|---|---|---|
| workforce_analytics_dag | Daily 2:00 AM EST | Full HR + Recruitment ETL |
| finance_etl_dag | Daily 3:00 AM EST | Invoice + Payment ETL |
| utilization_incremental | Hourly | Timesheet data incremental load |
| dbt_run_all | Daily 4:00 AM EST | Full dbt model refresh |
| dbt_test_all | Daily 4:30 AM EST | Data quality validation |

---

## 3. Incident Response Procedures

### P1 - ETL Pipeline Failure
1. Check Airflow logs: `Admin > DAG Runs > [failed DAG] > Log`
2. Identify failing task and error message
3. Check Snowflake for partial loads: `SELECT COUNT(*) FROM raw.etl_audit WHERE run_date = CURRENT_DATE AND status = 'FAILED'`
4. Rollback partial data if needed: `TRUNCATE TABLE raw.[table_name]_staging`
5. Re-trigger DAG after fix
6. Log incident in issue tracker with root cause

### P2 - Slow Query / Timeout
1. Identify query in Snowflake Query History
2. Run `EXPLAIN` on the query to review execution plan
3. Check index/clustering usage
4. Increase warehouse size temporarily if needed
5. Apply query optimization (add filters, rewrite joins)
6. Test optimized query and log performance improvement

### P3 - Data Quality Failure
1. Check dbt test output: `dbt test --select [model_name]`
2. Identify failing test and affected rows
3. Trace data back to source system
4. Apply data quality fix in `scripts/transform/data_quality_checks.py`
5. Re-run dbt for affected model
6. Validate output before promoting

### P4 - Connection Failure
1. Verify Snowflake account is accessible
2. Check ODBC/JDBC driver configurations
3. Validate credentials in Airflow connections
4. Test connection: `snowflake connector python test`
5. Escalate to infrastructure team if unresolved within 15 minutes

---

## 4. Scheduled Maintenance Tasks

| Task | Frequency | Procedure |
|---|---|---|
| Index Rebuild | Weekly (Sunday 1 AM) | Run `ALTER TABLE ... CLUSTER BY` on large fact tables |
| Statistics Update | Weekly | Run `ANALYZE TABLE` on all warehouse tables |
| Log File Cleanup | Monthly | Archive logs older than 90 days |
| Storage Capacity Check | Weekly | Review Snowflake credit usage dashboard |
| Credential Rotation | Quarterly | Rotate service account passwords per security policy |
| Performance Benchmark | Monthly | Run benchmark queries and log to performance_log.csv |

---

## 5. Performance Benchmarks

| Query Type | Target | Alert Threshold |
|---|---|---|
| Recruiter Performance Report | < 5 seconds | > 15 seconds |
| Invoice Aging Dashboard | < 3 seconds | > 10 seconds |
| Utilization Summary | < 4 seconds | > 12 seconds |
| Full ETL Pipeline | < 45 minutes | > 90 minutes |
| dbt Full Run | < 20 minutes | > 40 minutes |

---

## 6. Access Control Management

### Snowflake Roles

| Role | Access Level | Departments |
|---|---|---|
| HR_ROLE | dim_employee, fact_recruitment_pipeline | Human Resources, Talent Acquisition |
| FINANCE_ROLE | fact_invoice_collections, fact_payment_collection | Finance, Accounts |
| OPS_ROLE | fact_consultant_utilization, dim_project | Operations |
| ANALYST_ROLE | All marts, read-only | Analytics, Management |
| ADMIN_ROLE | Full access + DDL | Database Engineering |

### Adding a New User
1. Create Snowflake user: `CREATE USER username PASSWORD='...' DEFAULT_ROLE=HR_ROLE`
2. Grant role: `GRANT ROLE HR_ROLE TO USER username`
3. Log change in audit table
4. Notify user with onboarding guide

---

## 7. Deployment Checklist

### Before Deploying Schema Changes
- [ ] Schema change reviewed in design session
- [ ] DDL script tested in DEV environment
- [ ] dbt models updated for schema change
- [ ] dbt tests pass in DEV
- [ ] Downstream dashboard tested
- [ ] Rollback script prepared
- [ ] Change management ticket created

### Before Deploying ETL Changes
- [ ] Python script linted and unit tested
- [ ] Test run completed against sample data
- [ ] Performance tested (no regression)
- [ ] Peer code review completed
- [ ] Deployed to STAGING and validated
- [ ] Production deployment scheduled during low-traffic window

---

## 8. Contacts & Escalation

| Role | Responsibility |
|---|---|
| Database Engineer (Sai Puttur) | Primary: ETL, schema, performance |
| Senior Technical Lead | Escalation: Architecture decisions |
| Snowflake Support | Platform issues, credit alerts |
| HR Department | Data issues in HRIS source |
| Finance Department | Data issues in ERP source |
