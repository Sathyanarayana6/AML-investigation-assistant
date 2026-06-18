# 🛡️ AML Investigation Assistant

> **AI-powered multi-agent system that automatically investigates suspicious financial transactions**

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![AWS](https://img.shields.io/badge/AWS-Lambda-orange?style=flat-square&logo=amazonaws)
![Bedrock](https://img.shields.io/badge/Amazon-Bedrock-orange?style=flat-square&logo=amazonaws)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-green?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=flat-square&logo=streamlit)
![Tests](https://img.shields.io/badge/Tests-8%2F8%20Passing-brightgreen?style=flat-square)

---

## 🚨 The Problem

Financial institutions generate **10,000+ AML alerts daily**.
**95%+ are false positives.**
Analysts waste hours manually investigating each one before making a decision.

**Real criminals slip through while analysts are buried in paperwork.**

---

## 💡 The Solution

A **multi-agent AI system** that automatically investigates suspicious transactions in under **3 seconds** — so analysts only review what truly matters.

```
Transaction Alert Comes In
         ↓
Agent 1: Transaction Analyzer    → Detects AML patterns
         ↓
Agent 2: Customer Profile        → Evaluates customer risk
         ↓
Agent 3: Risk Calculator         → Final risk score (0-100)
         ↓
LangGraph Orchestrator           → Coordinates all agents
         ↓
DynamoDB Audit Log               → Compliance trail
         ↓
Streamlit Dashboard              → Analyst reviews result
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                   │
│              (Corporate Analyst Interface)               │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                   AWS Lambda Function                    │
│              (Serverless Entry Point)                    │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              LangGraph Orchestrator                      │
│         (Coordinates all 3 agents)                       │
├──────────────┬──────────────┬───────────────────────────┤
│   Agent 1    │   Agent 2    │        Agent 3             │
│ Transaction  │  Customer    │    Risk Calculator         │
│  Analyzer   │  Profiler    │   (Final Decision)         │
└──────┬───────┴──────┬───────┴────────────┬──────────────┘
       │              │                    │
┌──────▼──────────────▼────────────────────▼──────────────┐
│              Amazon Bedrock (Claude Sonnet)               │
│                    (AI Reasoning)                        │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                    DynamoDB                              │
│              (Full Audit Trail)                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 AML Patterns Detected

| Pattern | Description | Risk |
|---------|-------------|------|
| **STRUCTURING** | Multiple deposits just under $10K reporting threshold | 🔴 HIGH |
| **SMURFING** | Multiple people depositing to same destination account | 🔴 HIGH |
| **LAYERING** | Money moving through multiple accounts quickly | 🔴 HIGH |
| **CIRCULAR_TRANSFERS** | Money loops back to original account with fees | 🔴 HIGH |
| **RAPID_MOVEMENT** | Large cash deposit immediately followed by withdrawal | 🟠 MEDIUM-HIGH |

---

## 🤖 Multi-Agent Pipeline

### Agent 1: Transaction Analyzer
- Analyzes every transaction for suspicious patterns
- Calls Claude via AWS Bedrock
- Returns: `patterns_found`, `risk_score`, `confidence`, `reasoning`

### Agent 2: Customer Profile Analyzer
- Evaluates customer account age, income, previous flags
- Checks PEP (Politically Exposed Person) status
- Returns: `customer_risk_level`, `risk_factors`, `reasoning`

### Agent 3: Risk Calculator
- Combines transaction + customer signals
- Applies weighted scoring (60% transaction, 40% customer)
- Returns: `final_risk_score` (0-100), `recommended_action`

### LangGraph Orchestrator
- Coordinates all 3 agents automatically
- Manages state between agents
- Logs every step to DynamoDB

---

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Amazon Bedrock** | Claude Sonnet AI model |
| **AWS Lambda** | Serverless deployment |
| **LangGraph** | Multi-agent orchestration |
| **LangChain** | AI utilities |
| **DynamoDB** | Audit trail & compliance logging |
| **S3** | Code deployment storage |
| **Streamlit** | Corporate analyst dashboard |
| **Python 3.12** | Core language |
| **Pytest** | Automated testing |
| **Docker** | Linux package building |

---

## 📊 Results

```
✅ 8/8 automated tests passing
✅ Detects all 5 AML patterns with 90%+ confidence  
✅ Full investigation in under 3 seconds
✅ Every AI decision logged for regulatory compliance
✅ Deployed live on AWS Lambda
✅ 240+ synthetic test transactions generated
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- AWS Account with Bedrock access
- AWS CLI configured
- Docker (for Lambda deployment)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/aml-investigation-assistant.git
cd aml-investigation-assistant

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your AWS credentials
```

### Run Tests
```bash
pytest tests/ -v
```

Expected output:
```
tests/test_transaction_analyzer.py::TestTransactionAnalyzer::test_structuring_detection PASSED
tests/test_transaction_analyzer.py::TestTransactionAnalyzer::test_smurfing_detection PASSED
tests/test_transaction_analyzer.py::TestTransactionAnalyzer::test_layering_detection PASSED
tests/test_transaction_analyzer.py::TestTransactionAnalyzer::test_rapid_movement_detection PASSED
tests/test_transaction_analyzer.py::TestTransactionAnalyzer::test_circular_transfers_detection PASSED
tests/test_transaction_analyzer.py::TestTransactionAnalyzer::test_legitimate_transactions PASSED
tests/test_transaction_analyzer.py::TestTransactionAnalyzer::test_output_format PASSED
tests/test_transaction_analyzer.py::TestTransactionAnalyzer::test_empty_transactions PASSED

8 passed in 45.23s
```

### Generate Test Data
```bash
python data/generate_synthetic_data.py
```

### Run Dashboard
```bash
streamlit run dashboard/app.py
```

### Test Full Pipeline
```bash
python -m src.agents.orchestrator
```

---

## 📁 Project Structure

```
aml-investigation-assistant/
├── src/
│   ├── agents/
│   │   ├── transaction_analyzer.py          # Agent 1
│   │   ├── transaction_analyzer_prompt.py   # Claude prompt
│   │   ├── customer_profile_analyzer.py     # Agent 2
│   │   ├── risk_calculator.py               # Agent 3
│   │   └── orchestrator.py                  # LangGraph pipeline
│   └── utils/
│       ├── bedrock_client.py                # AWS Bedrock connection
│       └── dynamodb_logger.py               # Audit logging
│
├── data/
│   ├── generate_synthetic_data.py           # Test data generator
│   └── sample_transactions.json            # 240 test transactions
│
├── tests/
│   └── test_transaction_analyzer.py         # 8 automated tests
│
├── infrastructure/
│   └── lambda_handler.py                    # AWS Lambda entry point
│
├── dashboard/
│   └── app.py                               # Streamlit dashboard
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔐 Environment Variables

```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_ACCOUNT_ID=your_account_id
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-6
DYNAMODB_TABLE_NAME=aml-investigation-logs
LAMBDA_ROLE_ARN=arn:aws:iam::YOUR_ACCOUNT_ID:role/aml-agent-lambda-role
S3_BUCKET_NAME=your-bucket-name
ENVIRONMENT=development
```

---

## 💰 AWS Cost Estimate

| Service | Usage | Monthly Cost |
|---------|-------|-------------|
| Lambda | 100 invocations/day | ~$0.20 |
| Bedrock (Claude) | 100 analyses/day | ~$9.00 |
| DynamoDB | On-demand | ~$1.00 |
| S3 | Storage only | ~$0.50 |
| **Total** | | **~$11/month** |

---

## 🗺️ Roadmap

- [x] Phase 1: Transaction Analyzer Agent
- [x] Phase 2: Multi-Agent Pipeline with LangGraph
- [x] Phase 3: AWS Lambda Deployment + Dashboard
- [ ] Phase 4: API Gateway integration
- [ ] Phase 5: Real-time alert notifications
- [ ] Phase 6: Historical analytics & reporting

---

## 👨‍💻 Author

Built by **Sathya** as a production-grade AI engineering project demonstrating multi-agent systems for financial compliance.

---

## 📄 License

MIT License - feel free to use this project as a reference for your own AI engineering work.

---

*Built with ❤️ using AWS Bedrock, LangGraph, and Claude AI*