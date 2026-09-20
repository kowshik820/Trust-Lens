# TrustLens

TrustLens is an AI-assisted digital trust and scam analyzer designed to help users assess suspicious messages, links, emails, and job offers before they click, pay, share, or trust them.

## Project goal

The app helps users identify common scam indicators such as urgency, payment demands, impersonation patterns, and credential requests. It provides a risk assessment, evidence-based explanations, and safe next steps.

> TrustLens provides AI-assisted risk assessment and does not guarantee that content is fraudulent.

## Structure

- frontend/ - React + Vite user interface
- backend/ - FastAPI API and analysis services
- aws/ - AWS SAM infrastructure, Cedar policy, deployment notes, and architecture documentation

The AWS deployment path includes API Gateway, Lambda, a Strands-compatible agent boundary,
Amazon Bedrock, optional OpenSearch threat lookup, Cedar safety policy, and DynamoDB analysis
receipts. FastAPI remains the local development adapter.

## Local setup

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment variables

Copy the backend example file and fill in your own values:

```bash
cd backend
copy .env.example .env
```

Set:

- AWS_REGION
- BEDROCK_MODEL_ID
- PORT (recommended: 8001 because 8000 is commonly occupied locally)
- MAX_INPUT_LENGTH (recommended: 10000)
- ALLOWED_ORIGINS (comma-separated list of frontend URLs)

For the frontend, create a `.env` file in the frontend folder when deploying elsewhere:

```bash
VITE_API_BASE_URL=http://localhost:8001
```

On production or staging, point this to your deployed backend URL instead.

## AWS serverless deployment

Install the AWS SAM CLI, then from the repository root run:

```powershell
sam build --template-file aws/template.yaml
sam deploy --guided --template-file .aws-sam/build/template.yaml
```

Use `amazon.nova-lite-v1:0` for `BedrockModelId`. Set `FrontendOrigin` to the deployed
frontend URL. The stack creates the API Gateway endpoint and DynamoDB table. Supply an
existing OpenSearch endpoint through `OpenSearchEndpoint` when threat lookup is ready.

The AWS account must have Bedrock model authorization and the deploying identity must be
allowed to use `bedrock:Converse` and `bedrock:InvokeModel`.

## Security notes

- Never commit secrets or API keys
- Do not expose AWS credentials in frontend code
- Validate input and limit message size
- Do not crawl arbitrary URLs automatically

## Disclaimer

TrustLens is a decision-support tool. It is not a legal or financial authority and it does not prove that content is malicious.
