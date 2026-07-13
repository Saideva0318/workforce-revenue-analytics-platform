-- stg_invoices.sql
-- Staging model: clean and standardize raw invoice data from ERP source

WITH source AS (
    SELECT * FROM {{ source('erp_raw', 'invoices') }}
),

renamed AS (
    SELECT
        -- Primary Key
        invoice_id,

        -- Foreign Keys
        client_id,
        project_id,
        consultant_id,

        -- Invoice Details
        UPPER(TRIM(invoice_number))                      AS invoice_number,
        CAST(invoice_date AS DATE)                       AS invoice_date,
        CAST(due_date AS DATE)                           AS due_date,
        UPPER(TRIM(invoice_status))                      AS invoice_status,  -- PENDING, PAID, OVERDUE, CANCELLED

        -- Amounts
        ROUND(CAST(invoice_amount AS NUMERIC), 2)        AS invoice_amount,
        ROUND(CAST(paid_amount AS NUMERIC), 2)           AS paid_amount,
        ROUND(
            CAST(invoice_amount AS NUMERIC) - CAST(paid_amount AS NUMERIC), 2
        )                                                AS outstanding_amount,

        -- Payment Details
        CAST(payment_date AS DATE)                       AS payment_date,
        UPPER(TRIM(payment_method))                      AS payment_method,  -- ACH, WIRE, CHECK, CREDIT
        TRIM(payment_reference)                          AS payment_reference,

        -- Aging Bucket (derived)
        CASE
            WHEN CAST(invoice_amount AS NUMERIC) = CAST(paid_amount AS NUMERIC)
                THEN 'PAID'
            WHEN DATEDIFF(day, CAST(due_date AS DATE), CURRENT_DATE()) <= 0
                THEN 'CURRENT'
            WHEN DATEDIFF(day, CAST(due_date AS DATE), CURRENT_DATE()) BETWEEN 1 AND 30
                THEN '1-30 Days'
            WHEN DATEDIFF(day, CAST(due_date AS DATE), CURRENT_DATE()) BETWEEN 31 AND 60
                THEN '31-60 Days'
            WHEN DATEDIFF(day, CAST(due_date AS DATE), CURRENT_DATE()) BETWEEN 61 AND 90
                THEN '61-90 Days'
            ELSE '90+ Days'
        END                                              AS aging_bucket,

        -- Days Sales Outstanding (DSO) components
        DATEDIFF(day, CAST(invoice_date AS DATE), CAST(due_date AS DATE))
                                                         AS payment_terms_days,
        CASE
            WHEN payment_date IS NOT NULL
            THEN DATEDIFF(day, CAST(invoice_date AS DATE), CAST(payment_date AS DATE))
            ELSE NULL
        END                                              AS actual_days_to_pay,

        -- Audit Fields
        CAST(created_at AS TIMESTAMP)                    AS created_at,
        CAST(updated_at AS TIMESTAMP)                    AS updated_at,
        CAST(_loaded_at AS TIMESTAMP)                    AS _loaded_at

    FROM source
    WHERE invoice_id IS NOT NULL
      AND invoice_amount IS NOT NULL
      AND invoice_date IS NOT NULL
),

deduped AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY invoice_id
            ORDER BY updated_at DESC
        ) AS row_num
    FROM renamed
)

SELECT * EXCEPT (row_num)
FROM deduped
WHERE row_num = 1
