# AWS Deployment Notes

This project is designed to run locally first and then be deployed to AWS using serverless patterns.

## Target architecture

- React frontend hosted on S3 or AWS Amplify
- API Gateway for public API routing
- AWS Lambda for the TrustLens analysis layer
- Amazon Bedrock for AI-assisted analysis
- DynamoDB for optional analysis history storage
- CloudWatch for monitoring and logs

## Included implementation

- `template.yaml`: SAM stack for API Gateway, Lambda, DynamoDB, CORS, and Bedrock IAM access
- `../backend/lambda_handler.py`: API Gateway/Lambda adapter
- `../backend/app/agent.py`: shared risk orchestration and policy decision
- `../backend/app/strands_runtime.py`: optional Strands Agent boundary
- `../backend/app/threat_lookup.py`: optional OpenSearch lookup
- `policies/trustlens.cedar`: Cedar policy artifact for safety decisions

## Local development

For local development, FastAPI replaces the Lambda/API Gateway layer so the app can run without cloud deployment.

## Deploy

From the repository root:

```powershell
sam build --template-file aws/template.yaml
sam deploy --guided --template-file .aws-sam/build/template.yaml
```

Set `BedrockModelId` to `amazon.nova-lite-v1:0`, set `FrontendOrigin` to the deployed
frontend URL, and optionally provide an existing `OpenSearchEndpoint`. After deployment,
set the frontend `VITE_API_BASE_URL` to the stack `ApiUrl` output and rebuild.
