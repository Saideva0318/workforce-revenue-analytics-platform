# Finance Dashboard Specification
## Workforce & Revenue Analytics Data Platform

**Dashboard Name:** Revenue & Invoice Collections Dashboard
**Owner:** Finance / Accounts Department
**Data Source:** `analytics.fact_invoice_collections`, `analytics.fact_payment_collection`
**Refresh Rate:** Daily at 5:00 AM EST
**Tool:** Power BI

---

## Dashboard Pages

### Page 1: Invoice Overview

| Visual | Type | Measure | Filters |
|---|---|---|---|
| Total Revenue YTD | KPI Card | SUM(invoice_amount) | Current Year |
| Total Outstanding AR | KPI Card | SUM(outstanding_amount) | Status != Paid |
| Collection Rate % | KPI Card | SUM(paid_amount) / SUM(invoice_amount) * 100 | Current Year |
| DSO (Days Sales Outstanding) | KPI Card | AVG(days_to_pay) | Current Year |
| Revenue by Client | Bar Chart | SUM(invoice_amount) by client_name | Top 10 Clients |
| Monthly Revenue Trend | Line Chart | SUM(invoice_amount) by Month | Rolling 12 Months |
| Invoice Status Breakdown | Donut Chart | COUNT(invoice_id) by invoice_status | All |

### Page 2: Invoice Aging Analysis

| Visual | Type | Measure | Filters |
|---|---|---|---|
| Aging Bucket Summary | Stacked Bar | SUM(outstanding_amount) by aging_bucket | Open + Overdue |
| Overdue Invoices Table | Table | invoice_id, client, amount, days_out | Status = Overdue |
| Aging Trend | Line Chart | Outstanding AR over time by bucket | Last 6 Months |
| Top Overdue Clients | Bar Chart | SUM(outstanding_amount) by client | aging_bucket = 90+ |

### Page 3: Payment Collections

| Visual | Type | Measure | Filters |
|---|---|---|---|
| Payments Received MTD | KPI Card | SUM(payment_amount) | Current Month |
| Collection Rate by Client | Table | client, invoice_amount, paid_amount, rate | All Clients |
| Payment Method Breakdown | Pie Chart | SUM(payment_amount) by payment_method | All |
| Days to Pay Distribution | Histogram | COUNT(invoices) by days_to_pay bucket | Paid Invoices |
| Monthly Collections vs Invoiced | Line Chart | paid vs invoiced amounts | Rolling 12 Months |

---

## Key DAX Measures (Power BI)

```dax
-- Total Revenue YTD
Total Revenue YTD =
CALCULATE(
    SUM(fact_invoice_collections[invoice_amount]),
    DATESYTD(dim_date[date])
)

-- Outstanding AR
Outstanding AR =
SUM(fact_invoice_collections[outstanding_amount])

-- Collection Rate
Collection Rate % =
DIVIDE(
    SUM(fact_invoice_collections[paid_amount]),
    SUM(fact_invoice_collections[invoice_amount]),
    0
) * 100

-- Days Sales Outstanding
DSO =
AVERAGEX(
    FILTER(fact_payment_collection, fact_payment_collection[days_to_pay] > 0),
    fact_payment_collection[days_to_pay]
)

-- Overdue Balance
Overdue Balance =
CALCULATE(
    SUM(fact_invoice_collections[outstanding_amount]),
    fact_invoice_collections[invoice_status] = "Overdue"
)
```

---

## Underlying SQL (Snowflake)

```sql
-- Invoice Aging Summary
SELECT
    c.client_name,
    i.aging_bucket,
    COUNT(i.invoice_id)                     AS invoice_count,
    SUM(i.invoice_amount)                   AS total_invoiced,
    SUM(i.paid_amount)                      AS total_paid,
    SUM(i.outstanding_amount)               AS total_outstanding,
    ROUND(SUM(i.paid_amount) / NULLIF(SUM(i.invoice_amount), 0) * 100, 2) AS collection_rate_pct
FROM analytics.fact_invoice_collections i
JOIN analytics.dim_client c ON i.client_key = c.client_key
WHERE i.invoice_status IN ('Open', 'Partial', 'Overdue')
GROUP BY c.client_name, i.aging_bucket
ORDER BY c.client_name, i.aging_bucket;

-- Monthly Revenue Trend
SELECT
    d.year,
    d.month,
    d.month_name,
    SUM(i.invoice_amount)       AS revenue_invoiced,
    SUM(i.paid_amount)          AS revenue_collected,
    SUM(i.outstanding_amount)   AS revenue_outstanding
FROM analytics.fact_invoice_collections i
JOIN analytics.dim_date d ON i.date_key = d.date_key
WHERE d.year >= YEAR(CURRENT_DATE()) - 1
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;
```

---

## Access Control

| Role | Access |
|---|---|
| FINANCE_ROLE | Full dashboard access |
| ADMIN_ROLE | Full dashboard access |
| HR_ROLE | No access to finance dashboard |
| ANALYST_ROLE | Read-only, no client PII |
