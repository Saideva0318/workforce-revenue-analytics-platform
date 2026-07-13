-- mart_recruitment.sql
-- Mart model: Recruitment pipeline analytics for TA dashboard
-- Materialization: table (full refresh weekly, incremental daily)

{{ config(
    materialized = 'incremental',
    unique_key = 'pipeline_key',
    incremental_strategy = 'merge',
    cluster_by = ['fiscal_year', 'department_key']
) }}

WITH candidates AS (
    SELECT * FROM {{ ref('stg_candidates') }}
),

positions AS (
    SELECT * FROM {{ ref('dim_position') }}
),

stages AS (
    SELECT * FROM {{ ref('dim_recruitment_stage') }}
),

dates AS (
    SELECT * FROM {{ ref('dim_date') }}
),

recruitment_base AS (
    SELECT
        frp.pipeline_key,
        frp.candidate_key,
        frp.position_key,
        frp.stage_key,
        frp.snapshot_date_key,

        -- Candidate Info
        c.candidate_name,
        c.candidate_email,
        c.source_channel,
        c.is_diverse_candidate,

        -- Position Info
        p.position_title,
        p.department_key,
        p.department_name,
        p.employment_type,
        p.req_open_date,
        p.req_close_date,
        p.target_start_date,

        -- Stage Info
        s.stage_name,
        s.stage_order,
        s.is_active_stage,

        -- Date Dimensions
        d.fiscal_year,
        d.fiscal_quarter,
        d.fiscal_month,
        d.month_name,

        -- Time Metrics
        frp.days_in_stage,
        frp.days_to_fill,
        frp.days_to_screen,
        frp.days_to_interview,
        frp.days_to_offer,

        -- Outcome Flags
        frp.is_hired,
        frp.is_offer_accepted,
        frp.is_offer_declined,
        frp.is_withdrawn,
        frp.withdrawal_reason,

        -- Cost Metrics
        frp.agency_fee,
        frp.job_board_cost,
        frp.total_recruiting_cost,

        -- SLA Monitoring
        CASE
            WHEN frp.days_to_fill > 45 THEN TRUE
            ELSE FALSE
        END                             AS is_sla_breach,

        CASE
            WHEN frp.days_to_fill <= 30 THEN 'Fast (<30d)'
            WHEN frp.days_to_fill <= 45 THEN 'Normal (30-45d)'
            WHEN frp.days_to_fill <= 60 THEN 'Slow (45-60d)'
            ELSE 'Critical (>60d)'
        END                             AS fill_speed_category,

        -- Snapshot
        frp.snapshot_date,
        CURRENT_TIMESTAMP()             AS dbt_loaded_at

    FROM {{ ref('fact_recruitment_pipeline') }} frp
    LEFT JOIN candidates c      ON frp.candidate_key = c.candidate_key
    LEFT JOIN positions p       ON frp.position_key = p.position_key
    LEFT JOIN stages s          ON frp.stage_key = s.stage_key
    LEFT JOIN dates d           ON frp.snapshot_date_key = d.date_key

    {% if is_incremental() %}
        WHERE frp.snapshot_date > (SELECT MAX(snapshot_date) FROM {{ this }})
    {% endif %}
)

SELECT * FROM recruitment_base
