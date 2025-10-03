#!/bin/bash
set -e

# Check if environment is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <environment>"
    echo "Example: $0 dev"
    exit 1
fi

ENVIRONMENT=$1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET_NAME="${ACCOUNT_ID}-${ENVIRONMENT}-lambdas"
PACKAGE_NAME="aichat-server.zip"

# Get absolute paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_ROOT/build"

# Create and clean build directory
echo "Preparing build directory..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copy project files to build directory
echo "Copying project files..."
cd "$PROJECT_ROOT"
rsync -av --progress . "$BUILD_DIR/" \
    --exclude '.git' \
    --exclude '.gitignore' \
    --exclude '__pycache__' \
    --exclude '.pytest_cache' \
    --exclude '*.pyc' \
    --exclude '.env' \
    --exclude '.venv' \
    --exclude 'venv' \
    --exclude '.idea' \
    --exclude '.vscode' \
    --exclude "$PACKAGE_NAME" \
    --exclude 'build' \
    --exclude 'scripts'

cd "$BUILD_DIR"

# Install dependencies to include in the package
echo "Installing dependencies..."
if [ -f requirements.txt ]; then
    pip install --target . -r requirements.txt
else
    echo "Error: requirements.txt not found in build directory"
    exit 1
fi

# Create deployment package
echo "Creating deployment package..."
zip -r "$PACKAGE_NAME" . -x "*.git*" "*.pyc" "__pycache__/*" "*.zip"

# Check if bucket exists, if not create it
if ! aws s3 ls "s3://${BUCKET_NAME}" 2>&1 > /dev/null; then
    echo "Creating S3 bucket: ${BUCKET_NAME}"
    aws s3 mb "s3://${BUCKET_NAME}"
fi

# Upload to S3
echo "Uploading package to S3..."
aws s3 cp "$PACKAGE_NAME" "s3://${BUCKET_NAME}/"

# Go back to original directory
cd ../scripts

echo "Build completed successfully!"
echo "Package uploaded to s3://${BUCKET_NAME}/${PACKAGE_NAME}"
echo "Build completed successfully!"
echo "Package uploaded to s3://${BUCKET_NAME}/${PACKAGE_NAME}"