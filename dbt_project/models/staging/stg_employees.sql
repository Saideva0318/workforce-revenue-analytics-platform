-- =============================================================
-- stg_employees.sql
-- Staging Model: Employee Records from HRIS
-- Materialized: view (no storage cost, always fresh)
-- Platform: Workforce & Revenue Analytics Data Platform
-- Author: Sai Puttur | Database Engineer
-- =============================================================

WITH source AS (

    -- Pull from raw employee table loaded by Python ETL
    SELECT * FROM {{ source('raw', 'raw_employees') }}

),

cleaned AS (

    SELECT
        -- Natural key
        TRIM(UPPER(employee_id))                            AS employee_id,

        -- Name fields
        INITCAP(TRIM(first_name))                           AS first_name,
        INITCAP(TRIM(last_name))                            AS last_name,
        LOWER(TRIM(email))                                  AS email,

        -- Classification
        INITCAP(TRIM(department))                           AS department,
        INITCAP(TRIM(job_title))                            AS job_title,
        INITCAP(TRIM(employment_type))                      AS employment_type,

        -- Dates
        TRY_TO_DATE(hire_date::VARCHAR, 'YYYY-MM-DD')       AS hire_date,
        TRY_TO_DATE(termination_date::VARCHAR, 'YYYY-MM-DD') AS termination_date,

        -- Status (standardize casing)
        INITCAP(TRIM(employment_status))                    AS employment_status,

        -- Relationships
        TRIM(UPPER(manager_id))                             AS manager_id,
        TRIM(location)                                      AS location,

        -- Financial (cast and validate)
        TRY_TO_NUMBER(salary, 12, 2)                        AS salary,

        -- ETL metadata
        source_system,
        TRY_TO_TIMESTAMP(etl_load_date)                     AS etl_load_timestamp

    FROM source
    WHERE employee_id IS NOT NULL
      AND first_name IS NOT NULL
      AND last_name IS NOT NULL

),

deduped AS (

    -- Remove duplicate employee_id records, keep latest load
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY employee_id
            ORDER BY etl_load_timestamp DESC
        ) AS row_num
    FROM cleaned

)

SELECT
    employee_id,
    first_name,
    last_name,
    email,
    department,
    job_title,
    employment_type,
    hire_date,
    termination_date,
    employment_status,
    manager_id,
    location,
    salary,
    source_system,
    etl_load_timestamp
FROM deduped
WHERE row_num = 1
