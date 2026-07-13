-- stg_timesheets.sql
-- Staging model: clean and standardize raw timesheet data from timekeeping system

WITH source AS (
    SELECT * FROM {{ source('timekeeping_raw', 'timesheets') }}
),

renamed AS (
    SELECT
        -- Primary Key
        timesheet_id,

        -- Foreign Keys
        employee_id,
        project_id,
        client_id,
        manager_id,

        -- Time Period
        CAST(week_start_date AS DATE)                    AS week_start_date,
        CAST(week_end_date AS DATE)                      AS week_end_date,
        EXTRACT(YEAR FROM CAST(week_start_date AS DATE)) AS fiscal_year,
        EXTRACT(MONTH FROM CAST(week_start_date AS DATE)) AS fiscal_month,

        -- Hours Breakdown
        ROUND(CAST(billable_hours AS NUMERIC), 2)        AS billable_hours,
        ROUND(CAST(non_billable_hours AS NUMERIC), 2)    AS non_billable_hours,
        ROUND(CAST(overtime_hours AS NUMERIC), 2)        AS overtime_hours,
        ROUND(CAST(pto_hours AS NUMERIC), 2)             AS pto_hours,
        ROUND(CAST(holiday_hours AS NUMERIC), 2)         AS holiday_hours,

        -- Total Hours (derived)
        ROUND(
            COALESCE(CAST(billable_hours AS NUMERIC), 0) +
            COALESCE(CAST(non_billable_hours AS NUMERIC), 0) +
            COALESCE(CAST(overtime_hours AS NUMERIC), 0) +
            COALESCE(CAST(pto_hours AS NUMERIC), 0) +
            COALESCE(CAST(holiday_hours AS NUMERIC), 0), 2
        )                                                AS total_hours,

        -- Utilization Rate (derived)
        CASE
            WHEN (
                COALESCE(CAST(billable_hours AS NUMERIC), 0) +
                COALESCE(CAST(non_billable_hours AS NUMERIC), 0)
            ) > 0
            THEN ROUND(
                CAST(billable_hours AS NUMERIC) /
                (
                    COALESCE(CAST(billable_hours AS NUMERIC), 0) +
                    COALESCE(CAST(non_billable_hours AS NUMERIC), 0)
                ), 4
            )
            ELSE 0
        END                                              AS utilization_rate,

        -- Bill Rate and Cost
        ROUND(CAST(bill_rate AS NUMERIC), 2)             AS bill_rate,
        ROUND(CAST(cost_rate AS NUMERIC), 2)             AS cost_rate,
        ROUND(CAST(billable_hours AS NUMERIC) * CAST(bill_rate AS NUMERIC), 2)
                                                         AS billable_revenue,
        ROUND(CAST(total_hours AS NUMERIC) * CAST(cost_rate AS NUMERIC), 2)
                                                         AS total_cost,

        -- Approval Status
        UPPER(TRIM(approval_status))                     AS approval_status, -- PENDING, APPROVED, REJECTED
        CAST(approved_by AS VARCHAR)                     AS approved_by,
        CAST(approved_at AS TIMESTAMP)                   AS approved_at,

        -- Audit Fields
        CAST(submitted_at AS TIMESTAMP)                  AS submitted_at,
        CAST(updated_at AS TIMESTAMP)                    AS updated_at,
        CAST(_loaded_at AS TIMESTAMP)                    AS _loaded_at

    FROM source
    WHERE timesheet_id IS NOT NULL
      AND employee_id IS NOT NULL
      AND week_start_date IS NOT NULL
      AND approval_status != 'REJECTED'
),

deduped AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY timesheet_id
            ORDER BY updated_at DESC
        ) AS row_num
    FROM renamed
)

SELECT * EXCEPT (row_num)
FROM deduped
WHERE row_num = 1
