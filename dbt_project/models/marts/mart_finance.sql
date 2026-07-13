-- mart_finance.sql
-- Mart model: Finance & Revenue analytics for CFO dashboard
-- Materialization: incremental with merge strategy

{{ config(
    materialized = 'incremental',
    unique_key = 'invoice_key',
    incremental_strategy = 'merge',
    cluster_by = ['fiscal_year', 'client_key']
) }}

WITH invoices AS (
    SELECT * FROM {{ ref('stg_invoices') }}
),

clients AS (
    SELECT * FROM {{ ref('dim_client') }}
),

dates AS (
    SELECT * FROM {{ ref('dim_date') }}
),

projects AS (
    SELECT * FROM {{ ref('dim_project') }}
),

finance_base AS (
    SELECT
        -- Keys
        fic.invoice_key,
        fic.client_key,
        fic.project_key,
        fic.invoice_date_key,

        -- Client Dimensions
        c.client_name,
        c.client_industry,
        c.client_region,
        c.client_tier,           -- STRATEGIC, ENTERPRISE, SMB
        c.account_manager,

        -- Project Dimensions
        p.project_name,
        p.project_type,
        p.contract_type,         -- T&M, FIXED, RETAINER

        -- Date Dimensions
        d.fiscal_year,
        d.fiscal_quarter,
        d.fiscal_month,
        d.month_name,
        d.week_of_year,

        -- Invoice Metrics
        fic.invoice_number,
        fic.invoice_date,
        fic.due_date,
        fic.payment_date,
        fic.invoice_status,
        fic.invoice_amount,
        fic.paid_amount,
        fic.outstanding_amount,
        fic.aging_bucket,
        fic.payment_terms_days,
        fic.actual_days_to_pay,

        -- DSO Calculation
        CASE
            WHEN fic.actual_days_to_pay IS NOT NULL
            THEN fic.actual_days_to_pay
            ELSE DATEDIFF(day, fic.invoice_date, CURRENT_DATE())
        END                                     AS effective_dso,

        -- Revenue Classification
        CASE
            WHEN fic.invoice_status = 'PAID' THEN 'Collected'
            WHEN fic.aging_bucket = 'CURRENT' THEN 'Current'
            WHEN fic.aging_bucket IN ('1-30 Days', '31-60 Days') THEN 'At Risk'
            WHEN fic.aging_bucket IN ('61-90 Days', '90+ Days') THEN 'Bad Debt Risk'
            ELSE 'Unknown'
        END                                     AS collection_status,

        -- Period-over-Period flags
        CASE
            WHEN d.fiscal_year = EXTRACT(YEAR FROM CURRENT_DATE()) THEN TRUE
            ELSE FALSE
        END                                     AS is_current_year,

        CASE
            WHEN d.fiscal_year = EXTRACT(YEAR FROM CURRENT_DATE()) - 1 THEN TRUE
            ELSE FALSE
        END                                     AS is_prior_year,

        -- Audit
        fic.created_at,
        fic.updated_at,
        CURRENT_TIMESTAMP()                     AS dbt_loaded_at

    FROM {{ ref('fact_invoice_collections') }} fic
    LEFT JOIN clients c     ON fic.client_key = c.client_key
    LEFT JOIN projects p    ON fic.project_key = p.project_key
    LEFT JOIN dates d       ON fic.invoice_date_key = d.date_key

    {% if is_incremental() %}
        WHERE fic.updated_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
)

SELECT * FROM finance_base
