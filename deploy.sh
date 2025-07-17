#!/bin/bash

echo "🚀 Deploying Trackman Analytics to AWS Elastic Beanstalk..."

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo "❌ EB CLI not found. Installing..."
    pip install awsebcli
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Initialize EB application (only if not already initialized)
if [ ! -d ".elasticbeanstalk" ]; then
    echo "📦 Initializing EB application..."
    eb init -p python-3.12 trackman-analytics --region us-east-1
fi

# Deploy to production
echo "🌐 Deploying to production..."
eb deploy trackman-analytics-prod

# Open the application
echo "🔗 Opening application..."
eb open

echo "✅ Deployment complete!"
echo "📋 Don't forget to set environment variables in the AWS console:"
echo "   - SECRET_KEY: Your JWT secret key"
echo "   - DATABASE_URL: Database connection string (if using external DB)" 