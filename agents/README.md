# Recruitment AI Agent 🤖

## Overview
AI-powered recruitment agent for automated candidate screening, resume parsing, skills matching, and interview scheduling. Built for the Workforce & Revenue Analytics Platform.

---

## Features
- ✅ **AI Resume Parsing** using GPT-4
- ✅ **Intelligent Skills Matching** (weighted scoring algorithm)
- ✅ **Automated Candidate Screening**  
- ✅ **Interview Recommendations** with reasoning
- ✅ **Configurable Threshold** for hiring decisions
- ✅ **Snowflake Integration** (optional)
- ✅ **CI/CD Deployment** via GitHub Actions

---

## Project Structure
```
agents/
├── recruitment_agent.py        # Main agent logic
├── agent_config.yaml          # Configuration file
├── requirements.txt           # Python dependencies
└── README.md                  # This file

.github/workflows/
└── deploy_recruitment_agent.yml  # CI/CD pipeline
```

---

## Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/Saideva0318/workforce-revenue-analytics-platform.git
cd workforce-revenue-analytics-platform/agents
```

### 2. Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create `.env` file:
```bash
OPENAI_API_KEY=sk-your-openai-api-key
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account.snowflakecomputing.com
```

### 4. Configure Agent Settings
Edit `agent_config.yaml`:
```yaml
screening_threshold: 0.7  # Adjust match score threshold
notification_email: "ta-team@company.com"
```

---

## Usage

### Run Agent Locally
```bash
python recruitment_agent.py
```

### Example Output:
```
============================================================
STARTING RECRUITMENT AGENT PIPELINE FOR: Senior Data Engineer
============================================================
INFO - Screening 2 candidates for Senior Data Engineer
INFO - Calculating match for Alice Johnson vs Senior Data Engineer
INFO - Match score: 0.92
INFO - Screening complete. Top candidate: Alice Johnson (0.92)
INFO - [NOTIFICATION to ta-team@company.com]: Screening complete
INFO - Pipeline complete.

Recommendations:
  - Alice Johnson: RECOMMENDED (0.92)
  - Bob Smith: REJECTED (0.34)
```

---

## Deployment Process

### Option 1: GitHub Actions (Automated)

The agent automatically deploys when code is pushed to `main` branch:

**Trigger deployment:**
```bash
git add agents/
git commit -m "Update recruitment agent"
git push origin main
```

**Workflow steps:**
1. Checkout code from repository
2. Set up Python 3.10 environment
3. Install dependencies from `requirements.txt`
4. Run tests (validation)
5. Deploy to cloud (AWS Lambda / GCP Cloud Run / Docker)
6. Send Slack notification on success

**View deployment status:**
Navigate to **Actions** tab in GitHub repository: 
`https://github.com/Saideva0318/workforce-revenue-analytics-platform/actions`

---

### Option 2: Manual Deployment to AWS Lambda

```bash
# Package the agent
cd agents/
zip -r recruitment_agent.zip .

# Deploy to AWS Lambda
aws lambda create-function \
  --function-name recruitment-ai-agent \
  --runtime python3.10 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler recruitment_agent.handler \
  --zip-file fileb://recruitment_agent.zip

# Update function code
aws lambda update-function-code \
  --function-name recruitment-ai-agent \
  --zip-file fileb://recruitment_agent.zip
```

---

### Option 3: Deploy to Google Cloud Run

```bash
# Create Dockerfile (if not exists)
cat > Dockerfile <<EOF
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "recruitment_agent.py"]
EOF

# Deploy to Cloud Run
gcloud run deploy recruitment-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

---

### Option 4: Deploy with Docker

```bash
# Build Docker image
docker build -t recruitment-agent:latest .

# Run locally
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY recruitment-agent:latest

# Push to registry
docker tag recruitment-agent:latest your-registry/recruitment-agent:latest
docker push your-registry/recruitment-agent:latest
```

---

## Configuration Options

| Parameter | Default | Description |
|---|---|---|
| `screening_threshold` | 0.7 | Minimum match score to recommend interview |
| `auto_schedule_interviews` | true | Automatically schedule interviews |
| `ai_model` | gpt-4 | OpenAI model for resume parsing |
| `notification_email` | - | Email for TA team notifications |
| `log_level` | INFO | Logging verbosity |

---

## Testing

```bash
# Run unit tests
pytest tests/ --cov=agents --cov-report=term-missing

# Validate configuration
python -c "import yaml; yaml.safe_load(open('agent_config.yaml'))"
```

---

## Monitoring & Logs

- **Local logs**: `./logs/recruitment_agent.log`
- **Cloud logs**: Check AWS CloudWatch / GCP Logs
- **GitHub Actions**: View workflow runs in Actions tab

---

## Troubleshooting

**Issue**: `OpenAI API key not found`
- **Solution**: Set `OPENAI_API_KEY` environment variable

**Issue**: `Configuration file not found`
- **Solution**: Ensure `agent_config.yaml` exists in agents/ folder

**Issue**: GitHub Actions workflow failing
- **Solution**: Check repository secrets are configured:
  - Go to Settings → Secrets and variables → Actions
  - Add: `OPENAI_API_KEY`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`

---

## Architecture Diagram

```
┌───────────────────────────────┐
│  Candidate Applications      │
│  (LinkedIn, Email, ATS)      │
└────────────┬──────────────────┘
               │
               │ Resume PDFs/Text
               │
               │
       ┌────────┴─────────┐
       │  Recruitment Agent │
       │  (recruitment_agent.py)
       │                     │
       │  1. Parse Resume     │
       │  2. Extract Skills   │
       │  3. Calculate Match  │
       │  4. Generate Summary │
       │  5. Recommend        │
       └────────┬───────────┘
                │
         ┌──────┼──────┐
         │             │
    ┌────┴────┐    ┌──┴────────────┐
    │ Snowflake │    │  Notification   │
    │ (Store)   │    │  (Email/Slack)  │
    └──────────┘    └────────────────┘
```

---

## License
MIT License

## Author
Saideva0318 | [GitHub](https://github.com/Saideva0318/workforce-revenue-analytics-platform)
