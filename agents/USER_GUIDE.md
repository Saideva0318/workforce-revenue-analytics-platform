# Recruitment AI Agent — User Guide: JD-to-Call Workflow

## Overview

This guide explains exactly how to give the agent a Job Description (JD) and have it automatically screen candidates, score them, and trigger outreach calls — end to end.

---

## Step 1: Prepare Your Job Description (JD File)

Create a file named `job_description.json` in the `agents/` folder.

```json
{
  "job_id": "JD-2025-001",
  "title": "Senior Data Engineer",
  "department": "Data & Analytics",
  "location": "Metuchen, NJ / Remote",
  "required_skills": [
    "Python", "SQL", "Snowflake", "dbt", "Airflow", "ETL/ELT"
  ],
  "preferred_skills": [
    "Spark", "Kafka", "AWS", "Power BI", "Data Modeling"
  ],
  "experience_years": 5,
  "education": "Bachelor's in Computer Science or related field",
  "salary_range": "$120,000 - $150,000",
  "visa_sponsorship": true,
  "description": "We are looking for a Senior Data Engineer to design and build scalable data pipelines on Snowflake using dbt and Airflow. Must have strong Python and SQL skills."
}
```

---

## Step 2: Prepare Your Candidate List

Create `candidates.json` in the `agents/` folder:

```json
[
  {
    "candidate_id": "C001",
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "phone": "+1-732-555-0101",
    "resume_text": "5 years of data engineering experience with Python, SQL, Snowflake, dbt, and Airflow. Built ETL pipelines for Fortune 500 companies.",
    "linkedin": "https://linkedin.com/in/alicejohnson"
  },
  {
    "candidate_id": "C002",
    "name": "Bob Smith",
    "email": "bob@example.com",
    "phone": "+1-908-555-0202",
    "resume_text": "3 years experience in SQL and basic Python. Worked with MySQL and some ETL experience.",
    "linkedin": "https://linkedin.com/in/bobsmith"
  },
  {
    "candidate_id": "C003",
    "name": "Carol Lee",
    "email": "carol@example.com",
    "phone": "+1-201-555-0303",
    "resume_text": "7 years of cloud data engineering with Snowflake, dbt, Spark, AWS Glue, and Python. Led data platform migrations.",
    "linkedin": "https://linkedin.com/in/carollee"
  }
]
```

---

## Step 3: Update agent_config.yaml for Auto-Call

Edit `agent_config.yaml` to enable call scheduling:

```yaml
agent:
  name: "Recruitment AI Agent"
  version: "1.0.0"
  model: "gpt-4"

screening:
  threshold: 0.70            # Minimum match score to qualify (0.0 - 1.0)
  max_candidates: 10         # Max candidates to process per JD
  auto_schedule_interviews: true

outreach:
  mode: "call"               # Options: email | call | both
  call_provider: "twilio"    # Options: twilio | vonage
  caller_id: "+1-732-555-0000"
  call_script_template: "scripts/call_script.txt"
  call_time_window:
    start: "09:00"
    end: "18:00"
    timezone: "America/New_York"

notifications:
  email: "recruiter@company.com"
  slack_webhook: "https://hooks.slack.com/services/YOUR/WEBHOOK"

snowflake:
  enabled: true
  log_results: true
```

---

## Step 4: Configure Call Script Template

Create `agents/scripts/call_script.txt`:

```
Hello, may I speak with {{candidate_name}}?

Hi {{candidate_name}}, this is the AI Recruitment Assistant calling on behalf of 
[Company Name] regarding your application for the {{job_title}} position.

We reviewed your profile and your experience in {{matched_skills}} impressed us.

Your match score for this role is {{match_score}}%.

We would love to schedule a technical interview with you.
Are you available this week for a 30-minute call?

If yes, I will send you a calendar invite to {{candidate_email}}.

Thank you for your time, {{candidate_name}}. Have a great day!
```

---

## Step 5: Set Environment Variables

Create `agents/.env`:

```env
# OpenAI - for resume parsing and scoring
OPENAI_API_KEY=sk-your-openai-api-key

# Twilio - for automated phone calls
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+17325550000

# Snowflake - for logging results
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account.snowflakecomputing.com
SNOWFLAKE_DATABASE=WORKFORCE_DB
SNOWFLAKE_SCHEMA=RECRUITMENT

# Notifications
NOTIFICATION_EMAIL=recruiter@company.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK
```

---

## Step 6: Run the Agent

### Option A — Local Run
```bash
cd agents/
pip install -r requirements.txt
python recruitment_agent.py --jd job_description.json --candidates candidates.json
```

### Option B — With Call Mode
```bash
python recruitment_agent.py \
  --jd job_description.json \
  --candidates candidates.json \
  --mode call \
  --threshold 0.70
```

### Option C — GitHub Actions (CI/CD Trigger)
Commit your `job_description.json` and push to the `main` branch:
```bash
git add agents/job_description.json agents/candidates.json
git commit -m "New JD: Senior Data Engineer"
git push origin main
# GitHub Actions auto-triggers the deployment workflow
```

---

## How the Agent Works — Full Workflow

```
[You provide JD + Candidates]
         |
         v
[Step 1] PARSE RESUME
  Agent sends each resume to GPT-4
  GPT-4 extracts: skills, experience years, education, tools
         |
         v
[Step 2] SCORE & RANK
  Weighted scoring algorithm compares resume vs JD:
  - Required Skills Match   → 40% weight
  - Experience Years        → 30% weight
  - Preferred Skills Match  → 20% weight
  - Education               → 10% weight
  Result: Match Score (0-100%)
         |
         v
[Step 3] FILTER
  Candidates with score >= threshold (e.g. 70%) → QUALIFIED
  Candidates below threshold → REJECTED (polite email sent)
         |
         v
[Step 4] CALL QUALIFIED CANDIDATES
  Twilio API places automated call to candidate phone
  Call script is personalized with:
  - Candidate name
  - Job title
  - Matched skills
  - Match score
  - Interview invite
         |
         v
[Step 5] LOG TO SNOWFLAKE
  All results stored in RECRUITMENT.CANDIDATE_SCREENING table:
  - candidate_id, job_id, match_score, call_status, timestamp
         |
         v
[Step 6] NOTIFY RECRUITER
  Slack message + Email sent to TA team:
  - List of qualified candidates
  - Their scores
  - Call status (Connected / Voicemail / Failed)
  - Interview slots requested
```

---

## Sample Output After Running

```
===============================================
 RECRUITMENT AI AGENT — SCREENING RESULTS
===============================================
 JD: Senior Data Engineer (JD-2025-001)
 Total Candidates: 3
 Qualified (>=70%): 2
 Rejected (<70%): 1
===============================================

 QUALIFIED CANDIDATES:
 +--------+---------------+-------+----------------+------------+
 | ID     | Name          | Score | Matched Skills | Call Status|
 +--------+---------------+-------+----------------+------------+
 | C001   | Alice Johnson | 88%   | Python,SQL,dbt | Connected  |
 | C003   | Carol Lee     | 95%   | Snowflake,Spark| Voicemail  |
 +--------+---------------+-------+----------------+------------+

 REJECTED CANDIDATES:
 +--------+---------------+-------+-----------------------------+
 | ID     | Name          | Score | Reason                      |
 +--------+---------------+-------+-----------------------------+
 | C002   | Bob Smith     | 45%   | Missing: Snowflake, dbt, ETL|
 +--------+---------------+-------+-----------------------------+

 Slack notification sent to: #recruitment-alerts
 Recruiter email sent to: recruiter@company.com
 Results logged to Snowflake: RECRUITMENT.CANDIDATE_SCREENING
===============================================
```

---

## Twilio Setup (for Real Phone Calls)

1. Sign up at https://www.twilio.com/try-twilio
2. Get a free phone number ($1/month)
3. Copy Account SID + Auth Token to your `.env`
4. Verify your recipient phone numbers (trial accounts only call verified numbers)
5. Upgrade to paid for unrestricted calling (~$0.013/min)

---

## Cost Estimate (Per Hiring Campaign)

| Service | Usage | Cost |
|---------|-------|------|
| OpenAI GPT-4 | 100 resumes x ~1000 tokens | ~$3.00 |
| Twilio Calls | 20 qualified calls x 2 min | ~$0.52 |
| Snowflake Compute | Logging queries | ~$0.05 |
| **Total** | **Per campaign** | **~$3.57** |

---

## Snowflake Table — Where Results Are Stored

```sql
SELECT
  candidate_id,
  candidate_name,
  job_id,
  match_score,
  matched_skills,
  call_status,
  call_timestamp,
  interview_requested
FROM WORKFORCE_DB.RECRUITMENT.CANDIDATE_SCREENING
WHERE job_id = 'JD-2025-001'
ORDER BY match_score DESC;
```

---

*Built for Workforce & Revenue Analytics Platform | Saideva0318*
