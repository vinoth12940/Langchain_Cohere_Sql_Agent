# AWS Integration Guide

This document provides instructions for setting up and using AWS Bedrock with Claude 3.5 Sonnet in the SQL Query Assistant application.

## Prerequisites

- AWS account with access to Bedrock service
- Access to Anthropic Claude 3.5 Sonnet model in Bedrock
- AWS Access Key and Secret Key with appropriate permissions

## AWS Credentials Setup

1. Create an IAM user with Bedrock access in your AWS console
2. Generate access keys for this user
3. Add the following to your `.env` file:
   ```
   AWS_ACCESS_KEY_ID=your_aws_access_key_id
   AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
   AWS_REGION=us-east-2
   AWS_BEDROCK_MODEL_ID=us.anthropic.claude-3-5-sonnet-20240620-v1:0
   ```

## AWS Bedrock Configuration

The application uses the `ChatBedrock` class from `langchain_aws` to interact with the Claude 3.5 Sonnet model:

```python
llm = ChatBedrock(
    model_id="us.anthropic.claude-3-5-sonnet-20240620-v1:0",
    model_kwargs={
        "temperature": 0.1,
        "max_tokens": 1000
    },
    region_name=aws_region,
    credentials_profile_name=None,
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)
```

## Model Parameters

- **temperature**: 0.1 (low temperature for more deterministic responses)
- **max_tokens**: 1000 (maximum response length)

## Troubleshooting AWS Integration

### Common Issues

1. **Authentication Errors**:
   - Verify your AWS credentials are correct
   - Ensure the IAM user has appropriate permissions for Bedrock

2. **Model Access Issues**:
   - Confirm you have access to the Claude 3.5 Sonnet model in your region
   - Check that your AWS account has Bedrock enabled

3. **Region Issues**:
   - Ensure the model is available in your specified region
   - Default region is us-east-2; change if necessary

### Logging

AWS-related errors are logged to `app.log`. Check this file if you encounter any issues with the AWS integration. 