# TrustLens AWS Architecture

```text
User
  ↓
React frontend (S3 or Amplify)
  ↓
API Gateway
  ↓
AWS Lambda (backend/lambda_handler.py)
  ↓
Strands-compatible TrustLens agent
  ├── URL analysis tool
  ├── email analysis tool
  ├── job scam analysis tool
  ├── optional OpenSearch threat lookup
  └── Cedar safety policy artifact
  ↓
Amazon Bedrock
  ↓
Risk score + explanation
  ↓
DynamoDB analysis receipt
```

## Frontend hosting

- S3 static website hosting or AWS Amplify
- A production build of the React app is served from the frontend hosting platform

## Monitoring

- CloudWatch logs and metrics
- API and Lambda performance monitoring

## Local development

- FastAPI runs locally instead of Lambda + API Gateway during development and testing
- This keeps the project usable before deployment

## Deployment

The deployable baseline is [template.yaml](template.yaml). It provisions API Gateway,
Lambda, DynamoDB, IAM permissions for Bedrock, and CORS. OpenSearch is supplied as an
existing endpoint through the `OpenSearchEndpoint` parameter because production
OpenSearch Serverless requires account-specific network and encryption policies.

```powershell
sam build --template-file aws/template.yaml
sam deploy --guided --template-file .aws-sam/build/template.yaml
```
