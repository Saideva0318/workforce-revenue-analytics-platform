# HR & Workforce Dashboard Specification

## Overview
| Attribute | Value |
|---|---|
| Dashboard Name | HR & Workforce Analytics |
| Owner | HR Business Partner / People Analytics |
| Refresh Frequency | Daily (overnight batch) |
| Data Sources | fact_employee_snapshot, dim_employee, dim_position, dim_department |
| Target Audience | CHRO, HR Managers, Department Heads |
| Tool | Power BI |

---

## Pages / Tabs

### Page 1: Headcount & Attrition

#### KPI Cards
| Metric | DAX Measure | Format |
|---|---|---|
| Total Active Headcount | `CALCULATE(COUNTROWS(fact_employee_snapshot), fact_employee_snapshot[is_active]=TRUE())` | Number |
| Attrition Rate (YTD) | `DIVIDE([Terminations YTD], [Avg Headcount YTD], 0)` | % |
| New Hires (MTD) | `CALCULATE(COUNTROWS(fact_employee_snapshot), fact_employee_snapshot[hire_month]=MONTH(TODAY()))` | Number |
| Avg Tenure (Years) | `AVERAGEX(fact_employee_snapshot, DATEDIFF(fact_employee_snapshot[hire_date], TODAY(), YEAR))` | Decimal |

#### Visuals
- **Line Chart**: Headcount trend by month (rolling 12 months)
- **Bar Chart**: Headcount by department
- **Donut Chart**: Employment type breakdown (Full-time, Part-time, Contractor)
- **Matrix**: Attrition by department and quarter

#### Filters/Slicers
- Department
- Employment Type
- Location
- Year/Quarter

---

### Page 2: Compensation & Grade Analysis

#### KPI Cards
| Metric | DAX Measure | Format |
|---|---|---|
| Avg Base Salary | `AVERAGE(fact_employee_snapshot[base_salary])` | Currency |
| Total Payroll Cost | `SUM(fact_employee_snapshot[base_salary])` | Currency |
| Salary to Revenue Ratio | `DIVIDE([Total Payroll Cost], [Total Revenue])` | % |
| Gender Pay Gap | `DIVIDE([Avg Male Salary] - [Avg Female Salary], [Avg Male Salary])` | % |

#### Visuals
- **Box Plot**: Salary distribution by grade band
- **Bar Chart**: Avg salary by department
- **Scatter Plot**: Salary vs. tenure by grade
- **Table**: Top 10 highest compensated roles

#### Filters/Slicers
- Grade Band
- Department
- Gender
- Employment Type

---

### Page 3: Diversity & Inclusion

#### KPI Cards
| Metric | Formula | Format |
|---|---|---|
| Female Representation % | Females / Total Headcount | % |
| Minority Representation % | Minority employees / Total | % |
| Leadership Diversity % | Diverse leaders / Total leaders | % |

#### Visuals
- **Stacked Bar**: Gender breakdown by department
- **Treemap**: Ethnicity distribution
- **Line Chart**: Diversity trend over 3 years
- **Gauge**: Overall D&I score vs target

---

## Data Model (Power BI Relationships)
```
fact_employee_snapshot
  --> dim_employee (employee_key)
  --> dim_position (position_key)
  --> dim_date (date_key)
  --> dim_department (department_key)
```

## Access Control
| Role | Access |
|---|---|
| CHRO | Full access all pages |
| HR Manager | All pages, no salary details |
| Department Head | Own department data only |
| Employee | Self-service page only |

## Row-Level Security
```dax
-- Department Head RLS
[department_id] = LOOKUPVALUE(dim_user[department_id], dim_user[email], USERPRINCIPALNAME())
```

## Refresh Schedule
- Full refresh: Sunday 2:00 AM UTC
- Incremental refresh: Daily 6:00 AM UTC
- Alert threshold: If refresh fails 2x consecutively → PagerDuty alert
