# AWS Deployment Notes

This project is designed to run locally first and then be deployed to AWS using serverless patterns.

## Target architecture

- React frontend hosted on S3 or AWS Amplify
- API Gateway for public API routing
- AWS Lambda for the TrustLens analysis layer
- Amazon Bedrock for AI-assisted analysis
- DynamoDB for optional analysis history storage
- CloudWatch for monitoring and logs

## Local development

For local development, FastAPI replaces the Lambda/API Gateway layer so the app can run without cloud deployment.
