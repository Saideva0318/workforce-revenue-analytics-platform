-- =============================================================
-- fact_recruitment_pipeline.sql
-- Fact Table: Recruitment Pipeline Activity
-- Grain: One row per candidate per recruitment stage
-- Platform: Workforce & Revenue Analytics Data Platform
-- Author: Sai Puttur | Database Engineer
-- Updated: July 2026
-- =============================================================

CREATE TABLE IF NOT EXISTS analytics.fact_recruitment_pipeline (
    pipeline_key            INTEGER AUTOINCREMENT PRIMARY KEY,
    -- Foreign Keys
    candidate_key           INTEGER         NOT NULL REFERENCES analytics.dim_candidate(candidate_key),
    position_key            INTEGER         NOT NULL REFERENCES analytics.dim_position(position_key),
    recruiter_employee_key  INTEGER         REFERENCES analytics.dim_employee(employee_key),
    stage_key               INTEGER         NOT NULL REFERENCES analytics.dim_recruitment_stage(stage_key),
    date_key                INTEGER         NOT NULL REFERENCES analytics.dim_date(date_key),
    -- Stage tracking
    stage_entry_date        DATE            NOT NULL,
    stage_exit_date         DATE,
    days_in_stage           INTEGER         GENERATED ALWAYS AS (DATEDIFF('day', stage_entry_date, COALESCE(stage_exit_date, CURRENT_DATE()))),
    -- Outcome metrics
    time_to_fill            INTEGER,          -- Total days from req open to hire
    is_converted            BOOLEAN         DEFAULT FALSE,  -- Advanced to next stage
    is_hired                BOOLEAN         DEFAULT FALSE,  -- Ultimately hired
    rejection_reason        VARCHAR(200),
    offer_amount            NUMBER(12,2),
    -- Source metadata
    source_system           VARCHAR(50)     DEFAULT 'ATS',
    created_at              TIMESTAMP_NTZ   DEFAULT CURRENT_TIMESTAMP(),
    updated_at              TIMESTAMP_NTZ   DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Recruitment pipeline fact table. Grain: one row per candidate per stage. Source: ATS (Greenhouse).';

-- Partition/cluster on date and stage for reporting
ALTER TABLE analytics.fact_recruitment_pipeline
    CLUSTER BY (date_key, stage_key, is_hired);

-- Grant access
GRANT SELECT ON analytics.fact_recruitment_pipeline TO ROLE HR_ROLE;
GRANT SELECT ON analytics.fact_recruitment_pipeline TO ROLE ANALYST_ROLE;
GRANT SELECT ON analytics.fact_recruitment_pipeline TO ROLE ADMIN_ROLE;

-- =============================================================
-- ANALYTICAL QUERIES
-- =============================================================

-- Time-to-Fill by Recruiter
-- SELECT
--     e.full_name          AS recruiter_name,
--     p.job_title          AS position,
--     p.department,
--     AVG(f.time_to_fill)  AS avg_days_to_fill,
--     COUNT(DISTINCT f.candidate_key) FILTER (WHERE f.is_hired) AS total_hires
-- FROM analytics.fact_recruitment_pipeline f
-- JOIN analytics.dim_employee e ON f.recruiter_employee_key = e.employee_key
-- JOIN analytics.dim_position p ON f.position_key = p.position_key
-- WHERE e.is_current = TRUE
-- GROUP BY 1, 2, 3
-- ORDER BY avg_days_to_fill;

-- Stage Conversion Rate
-- SELECT
--     s.stage_name,
--     COUNT(*)                        AS total_candidates,
--     SUM(CASE WHEN f.is_converted THEN 1 ELSE 0 END) AS converted,
--     ROUND(SUM(CASE WHEN f.is_converted THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS conversion_rate_pct
-- FROM analytics.fact_recruitment_pipeline f
-- JOIN analytics.dim_recruitment_stage s ON f.stage_key = s.stage_key
-- GROUP BY s.stage_name, s.stage_order
-- ORDER BY s.stage_order;
