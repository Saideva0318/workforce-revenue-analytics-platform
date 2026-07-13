-- =============================================================
-- dim_employee.sql
-- Dimension: Employee Master with SCD Type 2 History
-- Platform: Workforce & Revenue Analytics Data Platform
-- Author: Sai Puttur | Database Engineer
-- Updated: July 2026
-- =============================================================

CREATE TABLE IF NOT EXISTS analytics.dim_employee (
    employee_key        INTEGER AUTOINCREMENT PRIMARY KEY,
    employee_id         VARCHAR(20)     NOT NULL,
    first_name          VARCHAR(100)    NOT NULL,
    last_name           VARCHAR(100)    NOT NULL,
    full_name           VARCHAR(200)    GENERATED ALWAYS AS (first_name || ' ' || last_name),
    email               VARCHAR(200),
    department          VARCHAR(100),
    job_title           VARCHAR(100),
    employment_type     VARCHAR(50)     CHECK (employment_type IN ('Full-Time','Part-Time','Contract','Intern')),
    hire_date           DATE,
    termination_date    DATE,
    employment_status   VARCHAR(20)     CHECK (employment_status IN ('Active','Inactive','On Leave','Terminated')),
    manager_id          VARCHAR(20),
    location            VARCHAR(100),
    salary              NUMBER(12,2),
    -- SCD Type 2 tracking columns
    scd_start_date      DATE            NOT NULL DEFAULT CURRENT_DATE(),
    scd_end_date        DATE            DEFAULT '9999-12-31',
    is_current          BOOLEAN         DEFAULT TRUE,
    -- Audit columns
    source_system       VARCHAR(50)     DEFAULT 'HRIS',
    created_at          TIMESTAMP_NTZ   DEFAULT CURRENT_TIMESTAMP(),
    updated_at          TIMESTAMP_NTZ   DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Employee dimension table with SCD Type 2 history tracking. Source: HRIS (Workday).';

-- Clustering for query optimization
ALTER TABLE analytics.dim_employee
    CLUSTER BY (department, employment_status, is_current);

-- Dynamic data masking on PII fields
CREATE MASKING POLICY IF NOT EXISTS mask_email
    AS (val VARCHAR) RETURNS VARCHAR ->
    CASE
        WHEN CURRENT_ROLE() IN ('HR_ROLE', 'ADMIN_ROLE') THEN val
        ELSE REGEXP_REPLACE(val, '^[^@]+', '***')
    END;

CREATE MASKING POLICY IF NOT EXISTS mask_salary
    AS (val NUMBER) RETURNS NUMBER ->
    CASE
        WHEN CURRENT_ROLE() IN ('HR_ROLE', 'FINANCE_ROLE', 'ADMIN_ROLE') THEN val
        ELSE NULL
    END;

ALTER TABLE analytics.dim_employee
    MODIFY COLUMN email SET MASKING POLICY mask_email;

ALTER TABLE analytics.dim_employee
    MODIFY COLUMN salary SET MASKING POLICY mask_salary;

-- Grant access by role
GRANT SELECT ON analytics.dim_employee TO ROLE HR_ROLE;
GRANT SELECT ON analytics.dim_employee TO ROLE ANALYST_ROLE;
GRANT SELECT ON analytics.dim_employee TO ROLE ADMIN_ROLE;

-- =============================================================
-- INDEXES (Snowflake search optimization)
-- =============================================================
ALTER TABLE analytics.dim_employee
    ADD SEARCH OPTIMIZATION ON EQUALITY(employee_id, department, employment_status);
