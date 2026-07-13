# Data Dictionary
## Workforce & Revenue Analytics Data Platform

---

## dim_employee

| Column | Data Type | Description | Source |
|---|---|---|---|
| employee_key | INTEGER | Surrogate key (PK) | Generated |
| employee_id | VARCHAR(20) | Natural key from HRIS | HRIS |
| first_name | VARCHAR(100) | Employee first name | HRIS |
| last_name | VARCHAR(100) | Employee last name | HRIS |
| email | VARCHAR(200) | Work email (masked) | HRIS |
| department | VARCHAR(100) | Department name | HRIS |
| job_title | VARCHAR(100) | Job title | HRIS |
| employment_type | VARCHAR(50) | Full-Time / Part-Time / Contract | HRIS |
| hire_date | DATE | Date of hire | HRIS |
| termination_date | DATE | Date of termination (NULL if active) | HRIS |
| employment_status | VARCHAR(20) | Active / Inactive / On Leave | HRIS |
| manager_id | VARCHAR(20) | Direct manager employee_id | HRIS |
| location | VARCHAR(100) | Work location | HRIS |
| salary | NUMBER(12,2) | Annual salary (masked) | HRIS |
| scd_start_date | DATE | SCD2 effective start date | Generated |
| scd_end_date | DATE | SCD2 effective end date | Generated |
| is_current | BOOLEAN | True if current record | Generated |
| created_at | TIMESTAMP | Record creation timestamp | ETL |
| updated_at | TIMESTAMP | Record last update timestamp | ETL |

---

## dim_position

| Column | Data Type | Description | Source |
|---|---|---|---|
| position_key | INTEGER | Surrogate key (PK) | Generated |
| position_id | VARCHAR(20) | Natural key | ATS/HRIS |
| requisition_id | VARCHAR(20) | Requisition number | ATS |
| job_title | VARCHAR(100) | Position title | ATS |
| department | VARCHAR(100) | Hiring department | ATS |
| job_level | VARCHAR(50) | Junior / Mid / Senior / Lead | ATS |
| employment_type | VARCHAR(50) | Full-Time / Contract | ATS |
| open_date | DATE | Date requisition opened | ATS |
| close_date | DATE | Date requisition closed/filled | ATS |
| status | VARCHAR(20) | Open / Filled / Cancelled | ATS |
| hiring_manager_id | VARCHAR(20) | Hiring manager employee_id | ATS |
| recruiter_id | VARCHAR(20) | Assigned recruiter employee_id | ATS |
| target_fill_days | INTEGER | Target days to fill | Business Rule |

---

## dim_candidate

| Column | Data Type | Description | Source |
|---|---|---|---|
| candidate_key | INTEGER | Surrogate key (PK) | Generated |
| candidate_id | VARCHAR(20) | Natural key from ATS | ATS |
| first_name | VARCHAR(100) | Candidate first name | ATS |
| last_name | VARCHAR(100) | Candidate last name | ATS |
| email | VARCHAR(200) | Contact email (masked) | ATS |
| phone | VARCHAR(20) | Contact phone (masked) | ATS |
| source | VARCHAR(100) | Application source channel | ATS |
| current_stage | VARCHAR(50) | Latest pipeline stage | ATS |
| applied_date | DATE | Date application submitted | ATS |
| requisition_id | VARCHAR(20) | FK to dim_position | ATS |
| recruiter_id | VARCHAR(20) | Assigned recruiter | ATS |
| disposition | VARCHAR(50) | Active / Hired / Rejected / Withdrawn | ATS |

---

## dim_client

| Column | Data Type | Description | Source |
|---|---|---|---|
| client_key | INTEGER | Surrogate key (PK) | Generated |
| client_id | VARCHAR(20) | Natural key from CRM/ERP | CRM |
| client_name | VARCHAR(200) | Legal client name | CRM |
| industry | VARCHAR(100) | Industry sector | CRM |
| contract_type | VARCHAR(50) | T&M / Fixed / Retainer | ERP |
| billing_terms | VARCHAR(50) | Net-30 / Net-45 / Net-60 | ERP |
| account_manager_id | VARCHAR(20) | Assigned account manager | CRM |
| client_status | VARCHAR(20) | Active / Inactive | CRM |
| onboard_date | DATE | Client onboarding date | CRM |

---

## dim_project

| Column | Data Type | Description | Source |
|---|---|---|---|
| project_key | INTEGER | Surrogate key (PK) | Generated |
| project_id | VARCHAR(20) | Natural key | Operations |
| project_name | VARCHAR(200) | Project name | Operations |
| client_key | INTEGER | FK to dim_client | Operations |
| start_date | DATE | Project start date | Operations |
| end_date | DATE | Project end or planned end date | Operations |
| project_status | VARCHAR(20) | Active / Completed / On Hold | Operations |
| billing_rate | NUMBER(10,2) | Hourly billing rate | Operations |
| project_manager_id | VARCHAR(20) | Project manager employee_id | Operations |

---

## fact_recruitment_pipeline

| Column | Data Type | Description | Business Metric |
|---|---|---|---|
| pipeline_key | INTEGER | Surrogate key (PK) | - |
| candidate_key | INTEGER | FK to dim_candidate | - |
| position_key | INTEGER | FK to dim_position | - |
| recruiter_employee_key | INTEGER | FK to dim_employee | - |
| stage_key | INTEGER | FK to dim_recruitment_stage | - |
| date_key | INTEGER | FK to dim_date (stage entry date) | - |
| stage_entry_date | DATE | Date candidate entered stage | - |
| stage_exit_date | DATE | Date candidate exited stage | - |
| days_in_stage | INTEGER | Days spent in this stage | Stage Duration |
| time_to_fill | INTEGER | Total days from open to hire | Time-to-Fill |
| is_converted | BOOLEAN | Candidate advanced to next stage | Conversion Rate |
| is_hired | BOOLEAN | Candidate ultimately hired | Hire Rate |
| offer_amount | NUMBER(12,2) | Offered salary (if at offer stage) | Offer Analytics |

---

## fact_consultant_utilization

| Column | Data Type | Description | Business Metric |
|---|---|---|---|
| utilization_key | INTEGER | Surrogate key (PK) | - |
| employee_key | INTEGER | FK to dim_employee | - |
| project_key | INTEGER | FK to dim_project | - |
| client_key | INTEGER | FK to dim_client | - |
| date_key | INTEGER | FK to dim_date | - |
| billable_hours | NUMBER(6,2) | Hours billed to client | Billable Util % |
| non_billable_hours | NUMBER(6,2) | Internal or admin hours | Capacity |
| total_hours | NUMBER(6,2) | Total hours logged | Total Capacity |
| utilization_pct | NUMBER(5,2) | billable_hours / total_hours * 100 | Utilization Rate |
| revenue_generated | NUMBER(12,2) | billable_hours x billing_rate | Revenue |

---

## fact_invoice_collections

| Column | Data Type | Description | Business Metric |
|---|---|---|---|
| invoice_key | INTEGER | Surrogate key (PK) | - |
| invoice_id | VARCHAR(20) | Natural key from ERP | - |
| client_key | INTEGER | FK to dim_client | - |
| project_key | INTEGER | FK to dim_project | - |
| date_key | INTEGER | FK to dim_date (invoice date) | - |
| invoice_date | DATE | Date invoice issued | - |
| due_date | DATE | Payment due date | - |
| invoice_amount | NUMBER(14,2) | Total invoice amount | Revenue |
| paid_amount | NUMBER(14,2) | Amount collected so far | Collection |
| outstanding_amount | NUMBER(14,2) | invoice_amount - paid_amount | AR Balance |
| days_outstanding | INTEGER | Days since invoice date | Aging |
| aging_bucket | VARCHAR(20) | 0-30 / 31-60 / 61-90 / 90+ | Aging Bucket |
| invoice_status | VARCHAR(20) | Open / Partial / Paid / Overdue | Status |

---

## fact_payment_collection

| Column | Data Type | Description | Business Metric |
|---|---|---|---|
| payment_key | INTEGER | Surrogate key (PK) | - |
| payment_id | VARCHAR(20) | Natural key from ERP | - |
| invoice_key | INTEGER | FK to fact_invoice_collections | - |
| client_key | INTEGER | FK to dim_client | - |
| date_key | INTEGER | FK to dim_date (payment date) | - |
| payment_date | DATE | Date payment received | - |
| payment_amount | NUMBER(14,2) | Amount received | Cash Collection |
| payment_method | VARCHAR(50) | ACH / Wire / Check | - |
| collection_rate | NUMBER(5,2) | % of invoice collected | Collection Rate |
| days_to_pay | INTEGER | Days from invoice to payment | DSO |

---

## Business Rules

1. **Utilization %** = (Billable Hours / Total Hours) x 100
2. **Time-to-Fill** = Close Date - Open Date (in calendar days)
3. **Days Sales Outstanding (DSO)** = (Outstanding AR / Total Revenue) x Days in Period
4. **Invoice Aging Bucket** = CASE WHEN days_outstanding <= 30 THEN '0-30' WHEN days_outstanding <= 60 THEN '31-60' WHEN days_outstanding <= 90 THEN '61-90' ELSE '90+' END
5. **Collection Rate %** = (Paid Amount / Invoice Amount) x 100
6. **Stage Conversion Rate** = Candidates advancing to next stage / Total candidates in stage

---

## PII Masking Policy

| Field | Masking Rule |
|---|---|
| email | Show domain only (e.g., ***@company.com) for non-admin roles |
| phone | Masked entirely for non-HR roles |
| salary | Masked entirely for non-HR/Finance roles |
| offer_amount | Masked for non-recruiting leadership roles |
