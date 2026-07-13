# Security & Data Governance Framework

## Overview
This document defines the security architecture, access control policies, data masking rules, and audit procedures for the Workforce & Revenue Analytics Platform.

---

## 1. Role-Based Access Control (RBAC)

### Snowflake Database Roles

```sql
-- Create functional roles
CREATE ROLE IF NOT EXISTS ANALYST_ROLE;
CREATE ROLE IF NOT EXISTS HR_ROLE;
CREATE ROLE IF NOT EXISTS FINANCE_ROLE;
CREATE ROLE IF NOT EXISTS TA_ROLE;
CREATE ROLE IF NOT EXISTS EXECUTIVE_ROLE;
CREATE ROLE IF NOT EXISTS DATA_ENGINEER_ROLE;
CREATE ROLE IF NOT EXISTS DBA_ROLE;

-- Grant database-level privileges
GRANT USAGE ON DATABASE ANALYTICS_DB TO ROLE ANALYST_ROLE;
GRANT USAGE ON DATABASE ANALYTICS_DB TO ROLE HR_ROLE;
GRANT USAGE ON DATABASE ANALYTICS_DB TO ROLE FINANCE_ROLE;

-- Grant schema privileges by domain
GRANT USAGE ON SCHEMA ANALYTICS_DB.ANALYTICS TO ROLE ANALYST_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA ANALYTICS_DB.ANALYTICS TO ROLE ANALYST_ROLE;

GRANT USAGE ON SCHEMA ANALYTICS_DB.ANALYTICS TO ROLE HR_ROLE;
GRANT SELECT ON TABLE ANALYTICS_DB.ANALYTICS.FACT_EMPLOYEE_SNAPSHOT TO ROLE HR_ROLE;
GRANT SELECT ON TABLE ANALYTICS_DB.ANALYTICS.DIM_EMPLOYEE TO ROLE HR_ROLE;

GRANT USAGE ON SCHEMA ANALYTICS_DB.ANALYTICS TO ROLE FINANCE_ROLE;
GRANT SELECT ON TABLE ANALYTICS_DB.ANALYTICS.FACT_INVOICE_COLLECTIONS TO ROLE FINANCE_ROLE;
GRANT SELECT ON TABLE ANALYTICS_DB.ANALYTICS.FACT_PAYMENT_COLLECTION TO ROLE FINANCE_ROLE;
```

### Role Matrix

| Role | Raw Layer | Staging | Warehouse | Marts | PII Fields | Salary Data |
|---|---|---|---|---|---|---|
| DBA_ROLE | Full | Full | Full | Full | Unmasked | Unmasked |
| DATA_ENGINEER_ROLE | Full | Full | Full | Full | Masked | Masked |
| ANALYST_ROLE | None | None | Read | Read | Masked | Masked |
| HR_ROLE | None | None | HR tables | HR mart | Unmasked | Masked |
| FINANCE_ROLE | None | None | Finance tables | Finance mart | Masked | Masked |
| TA_ROLE | None | None | Recruitment tables | TA mart | Masked | None |
| EXECUTIVE_ROLE | None | None | None | Summary views | Masked | Aggregated |

---

## 2. Data Masking Policies

### PII Masking Policy
```sql
-- Create masking policy for SSN
CREATE OR REPLACE MASKING POLICY mask_ssn AS
  (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() IN ('DBA_ROLE', 'HR_ROLE') THEN val
    ELSE CONCAT('XXX-XX-', RIGHT(val, 4))
  END;

-- Create masking policy for email
CREATE OR REPLACE MASKING POLICY mask_email AS
  (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() IN ('DBA_ROLE', 'HR_ROLE', 'TA_ROLE') THEN val
    ELSE CONCAT(LEFT(val, 2), '***@***.com')
  END;

-- Create masking policy for salary
CREATE OR REPLACE MASKING POLICY mask_salary AS
  (val NUMBER) RETURNS NUMBER ->
  CASE
    WHEN CURRENT_ROLE() IN ('DBA_ROLE') THEN val
    WHEN CURRENT_ROLE() IN ('HR_ROLE') THEN ROUND(val, -3)  -- rounded to nearest 1000
    ELSE NULL
  END;

-- Apply masking policies to columns
ALTER TABLE ANALYTICS_DB.ANALYTICS.DIM_EMPLOYEE
  MODIFY COLUMN ssn SET MASKING POLICY mask_ssn;

ALTER TABLE ANALYTICS_DB.ANALYTICS.DIM_EMPLOYEE
  MODIFY COLUMN personal_email SET MASKING POLICY mask_email;

ALTER TABLE ANALYTICS_DB.ANALYTICS.FACT_EMPLOYEE_SNAPSHOT
  MODIFY COLUMN base_salary SET MASKING POLICY mask_salary;
```

---

## 3. Row-Level Security (Row Access Policies)

### Department-Level Row Access
```sql
-- Create mapping table for department access
CREATE OR REPLACE TABLE SECURITY.DEPT_ACCESS_MAPPING (
  user_name     VARCHAR,
  department_id VARCHAR,
  access_level  VARCHAR   -- FULL, READ, NONE
);

-- Create row access policy
CREATE OR REPLACE ROW ACCESS POLICY dept_row_policy AS
  (department_key VARCHAR) RETURNS BOOLEAN ->
  CASE
    WHEN CURRENT_ROLE() IN ('DBA_ROLE', 'DATA_ENGINEER_ROLE', 'EXECUTIVE_ROLE') THEN TRUE
    WHEN EXISTS (
      SELECT 1 FROM SECURITY.DEPT_ACCESS_MAPPING
      WHERE user_name = CURRENT_USER()
        AND department_id = department_key
        AND access_level != 'NONE'
    ) THEN TRUE
    ELSE FALSE
  END;

-- Apply policy to fact table
ALTER TABLE ANALYTICS_DB.ANALYTICS.FACT_EMPLOYEE_SNAPSHOT
  ADD ROW ACCESS POLICY dept_row_policy ON (department_key);
```

---

## 4. Audit Logging

### Snowflake Query History Audit
```sql
-- Audit view for sensitive table access
CREATE OR REPLACE VIEW SECURITY.V_SENSITIVE_ACCESS_AUDIT AS
SELECT
    query_id,
    query_text,
    user_name,
    role_name,
    database_name,
    schema_name,
    start_time,
    end_time,
    execution_status,
    rows_produced
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE (
    UPPER(query_text) LIKE '%DIM_EMPLOYEE%'
    OR UPPER(query_text) LIKE '%BASE_SALARY%'
    OR UPPER(query_text) LIKE '%SSN%'
    OR UPPER(query_text) LIKE '%FACT_INVOICE%'
)
AND start_time >= DATEADD(day, -90, CURRENT_TIMESTAMP())
ORDER BY start_time DESC;
```

### Data Access Log Table
```sql
CREATE TABLE IF NOT EXISTS SECURITY.DATA_ACCESS_LOG (
    log_id          NUMBER AUTOINCREMENT PRIMARY KEY,
    accessed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    user_name       VARCHAR,
    role_name       VARCHAR,
    table_name      VARCHAR,
    action_type     VARCHAR,  -- SELECT, INSERT, UPDATE, DELETE
    row_count       NUMBER,
    session_id      VARCHAR,
    ip_address      VARCHAR
);
```

---

## 5. Network Security

### Snowflake Network Policy
```sql
-- Restrict access to corporate IP ranges
CREATE NETWORK POLICY corporate_access_policy
  ALLOWED_IP_LIST = (
    '10.0.0.0/8',        -- Corporate VPN
    '192.168.0.0/16',    -- Office Network
    '172.16.0.0/12'      -- Data Center
  )
  BLOCKED_IP_LIST = ();

-- Apply to account
ALTER ACCOUNT SET NETWORK_POLICY = corporate_access_policy;
```

---

## 6. Data Classification

| Classification | Examples | Handling |
|---|---|---|
| Confidential | SSN, Bank Account, Medical | Encrypted at rest + transit, Masked in UI |
| Restricted | Salary, Performance, HR notes | Role-restricted, Audit logged |
| Internal | Employee name, Dept, Title | RBAC protected |
| Public | Aggregated metrics, Org chart | Shareable externally |

---

## 7. Compliance Checklist

- [ ] SOC 2 Type II controls implemented
- [ ] GDPR data subject request process documented
- [ ] CCPA consumer rights workflow defined
- [ ] Data retention policy enforced (7 years financial, 5 years HR)
- [ ] Annual access review completed
- [ ] Quarterly masking policy audit completed
- [ ] MFA enforced for all users
- [ ] Service accounts rotated quarterly
- [ ] Sensitive query alerts configured in Snowflake
- [ ] DLP (Data Loss Prevention) scanning enabled

---

## 8. Incident Response

### Data Breach Protocol
1. **Detect**: Alert from Snowflake anomaly detection or SIEM
2. **Contain**: Revoke affected user/role immediately
3. **Assess**: Run `V_SENSITIVE_ACCESS_AUDIT` to scope exposure
4. **Notify**: Legal + Compliance within 72 hours (GDPR requirement)
5. **Remediate**: Rotate secrets, patch vulnerability, update policies
6. **Review**: Post-incident review within 5 business days

### Emergency Access Revocation
```sql
-- Emergency: revoke all access for a user
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA ANALYTICS_DB.ANALYTICS FROM ROLE USER_ROLE;
ALTER USER compromised_user DISABLE;
```
