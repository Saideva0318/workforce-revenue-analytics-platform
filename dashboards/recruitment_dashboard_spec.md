# Recruitment Pipeline Dashboard Specification

## Overview
| Attribute | Value |
|---|---|
| Dashboard Name | Recruitment Pipeline Analytics |
| Owner | Talent Acquisition Team |
| Refresh Frequency | Daily at 7:00 AM UTC |
| Data Sources | fact_recruitment_pipeline, dim_candidate, dim_position, dim_date |
| Target Audience | TA Directors, Hiring Managers, Executive Leadership |
| Tool | Power BI |

---

## Pages / Tabs

### Page 1: Pipeline Overview

#### KPI Cards
| Metric | DAX Measure | Format |
|---|---|---|
| Open Requisitions | `CALCULATE(COUNTROWS(dim_position), dim_position[status]="Open")` | Number |
| Total Candidates in Pipeline | `COUNTROWS(fact_recruitment_pipeline)` | Number |
| Avg Time-to-Fill (Days) | `AVERAGEX(fact_recruitment_pipeline, fact_recruitment_pipeline[days_to_fill])` | Days |
| Offer Acceptance Rate | `DIVIDE([Accepted Offers], [Total Offers], 0)` | % |
| Cost per Hire | `DIVIDE([Total Recruiting Cost], [Total Hires], 0)` | Currency |

#### Visuals
- **Funnel Chart**: Candidate pipeline stages (Applied → Screened → Interview → Offer → Hired)
- **Bar Chart**: Open requisitions by department
- **Line Chart**: Applications received per week (rolling 12 weeks)
- **Map Visual**: Candidate location distribution

#### Filters/Slicers
- Department
- Requisition Status
- Date Range
- Hiring Manager

---

### Page 2: Time-to-Fill Analysis

#### KPI Cards
| Metric | DAX Measure | Format |
|---|---|---|
| Avg Time-to-Screen | `AVERAGE(fact_recruitment_pipeline[days_to_screen])` | Days |
| Avg Time-to-Interview | `AVERAGE(fact_recruitment_pipeline[days_to_interview])` | Days |
| Avg Time-to-Offer | `AVERAGE(fact_recruitment_pipeline[days_to_offer])` | Days |
| SLA Breach Rate | `DIVIDE([Positions Exceeding SLA], [Total Positions], 0)` | % |

#### Visuals
- **Waterfall Chart**: Stage-by-stage time breakdown
- **Scatter Plot**: Time-to-fill vs. offer acceptance rate by department
- **Heat Map**: Time-to-fill by month and department
- **Table**: Top 10 longest open requisitions

---

### Page 3: Source Effectiveness

#### KPI Cards
| Metric | Formula | Format |
|---|---|---|
| Top Hiring Source | MAX(source) by hire count | Text |
| Agency vs Direct Hire % | Agency hires / Total hires | % |
| Referral Hire Rate | Referral hires / Total hires | % |

#### Visuals
- **Donut Chart**: Candidate source breakdown (LinkedIn, Referral, Agency, Job Board, Direct)
- **Bar Chart**: Hire rate by source channel
- **Line Chart**: Source effectiveness trend over 6 months
- **Table**: Source channel cost comparison

---

### Page 4: Diversity Pipeline

#### KPI Cards
| Metric | Formula | Format |
|---|---|---|
| Diverse Candidate Rate | Diverse applicants / Total applicants | % |
| Diverse Interview Rate | Diverse interviewed / Total interviewed | % |
| Diverse Hire Rate | Diverse hires / Total hires | % |

#### Visuals
- **Funnel**: Diversity drop-off at each stage
- **Bar Chart**: Diversity hiring by department
- **Trend Line**: Diversity hire rate over time

---

## Underlying SQL Queries

### Pipeline Funnel Query
```sql
SELECT
  stage_name,
  COUNT(candidate_key) AS candidate_count,
  ROUND(COUNT(candidate_key) * 100.0 / SUM(COUNT(candidate_key)) OVER (), 1) AS pct_of_total
FROM analytics.fact_recruitment_pipeline frp
JOIN analytics.dim_recruitment_stage drs ON frp.stage_key = drs.stage_key
WHERE frp.snapshot_date = CURRENT_DATE()
GROUP BY stage_name
ORDER BY stage_order;
```

### Time-to-Fill by Department
```sql
SELECT
  dd.department_name,
  AVG(frp.days_to_fill) AS avg_days_to_fill,
  COUNT(CASE WHEN frp.days_to_fill > 45 THEN 1 END) AS sla_breaches
FROM analytics.fact_recruitment_pipeline frp
JOIN analytics.dim_position dp ON frp.position_key = dp.position_key
JOIN analytics.dim_department dd ON dp.department_key = dd.department_key
WHERE frp.hire_date >= DATEADD(month, -12, CURRENT_DATE())
GROUP BY dd.department_name
ORDER BY avg_days_to_fill DESC;
```

---

## Access Control
| Role | Access |
|---|---|
| TA Director | Full access all pages including diversity |
| Hiring Manager | Own department pipeline only |
| Executive | Summary KPIs page only |
| Recruiter | Own assigned requisitions only |

## Refresh Schedule
- Incremental refresh: Daily 7:00 AM UTC
- Full refresh: Every Sunday 1:00 AM UTC
- Data retention: 36 months rolling
