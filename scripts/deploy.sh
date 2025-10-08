#!/bin/bash
set -e

# Check if environment is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <environment>"
    echo "Example: $0 dev"
    exit 1
fi

ENVIRONMENT=$1
STACK_NAME="aichat-server-${ENVIRONMENT}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Get absolute paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATE_PATH="$PROJECT_ROOT/template.yaml"
ENV_FILE="$PROJECT_ROOT/.env"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found at $ENV_FILE"
    exit 1
fi

# Set allowed origins based on environment
if [ "$ENVIRONMENT" = "dev" ]; then
    # For development, you might want to allow both localhost:3000 and localhost:3001
    ALLOWED_ORIGINS="http://localhost:3000"
else
    # For production, you can specify multiple domains without spaces
    ALLOWED_ORIGINS="https://usmanaftab.github.io,https://ai.usmanaftab.com,https://usmanaftab.com"  # Replace with your production domains
fi

# Deploy CloudFormation stack
echo "Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file "$TEMPLATE_PATH" \
    --stack-name "$STACK_NAME" \
    --parameter-overrides \
        Environment="$ENVIRONMENT" \
        AllowedOrigins="$ALLOWED_ORIGINS" \
    --capabilities CAPABILITY_IAM

# Get Lambda function name from CloudFormation
FUNCTION_NAME=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionName`].OutputValue' \
    --output text)

if [ -z "$FUNCTION_NAME" ]; then
    FUNCTION_NAME="aichat-server-${ENVIRONMENT}"
fi

# Update Lambda environment variables
echo "Updating Lambda environment variables..."

# First, get the current environment variables to preserve FLASK_ENV
CURRENT_ENV=$(aws lambda get-function-configuration \
    --function-name "$FUNCTION_NAME" \
    --query 'Environment.Variables' \
    --output json)

# Process environment variables
echo "Processing environment variables..."
ENV_VARS_JSON="{"

# Add FLASK_ENV first
ENV_VARS_JSON="$ENV_VARS_JSON\"FLASK_ENV\": \"$ENVIRONMENT\""

# Read and process environment variables from .env file
while IFS='=' read -r key value || [[ -n "$key" ]]; do
    # Skip empty lines and comments
    [[ -z "$key" || "$key" =~ ^# ]] && continue

    # Clean up key and value
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs | sed 's/^["\x27]\(.*\)["\x27]$/\1/')

    # Skip if key or value is empty
    [[ -z "$key" || -z "$value" ]] && continue

    # Add to JSON
    ENV_VARS_JSON="$ENV_VARS_JSON, \"$key\": \"$value\""
done < "$ENV_FILE"

ENV_VARS_JSON="$ENV_VARS_JSON}"

# Create the full environment update JSON
# Create and validate final JSON
FULL_ENV_JSON="{\"Variables\": $ENV_VARS_JSON}"

# Print the environment variables for verification
echo "Environment variables to be set:"
echo "$FULL_ENV_JSON" | jq '.' || {
    echo "Error: Failed to parse environment variables JSON"
    exit 1
}

# Update Lambda function code to use the latest S3 package
echo "Updating Lambda function code..."
aws lambda update-function-code \
    --function-name "$FUNCTION_NAME" \
    --s3-bucket "${ACCOUNT_ID}-${ENVIRONMENT}-lambdas" \
    --s3-key "aichat-server.zip" \
    --publish

# Wait for the update to complete
echo "Waiting for Lambda update to complete..."
aws lambda wait function-updated --function-name "$FUNCTION_NAME"

# Verify the update
LAST_MODIFIED=$(aws lambda get-function --function-name "$FUNCTION_NAME" --query 'Configuration.LastModified' --output text)
echo "Lambda function code updated. Last modified: $LAST_MODIFIED"

# Update Lambda configuration with environment variables
echo "Updating Lambda configuration..."
aws lambda update-function-configuration \
    --function-name "$FUNCTION_NAME" \
    --environment "$FULL_ENV_JSON"

# Wait for Lambda update to complete
echo "Waiting for Lambda update to complete..."
aws lambda wait function-updated \
    --function-name "$FUNCTION_NAME"

# Get API Gateway URL
API_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text)

echo "Deployment completed successfully!"
echo "API Gateway URL: ${API_URL}"
