# TrustLens AWS Architecture

```text
User
  ↓
React frontend
  ↓
API Gateway
  ↓
AWS Lambda
  ↓
TrustLens analysis engine
  ↓
Amazon Bedrock
  ↓
DynamoDB
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
