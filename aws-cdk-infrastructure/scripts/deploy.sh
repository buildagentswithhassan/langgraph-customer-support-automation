#!/bin/bash
set -e

# Get ECR repository URI from CDK output
ECR_URI=$(aws cloudformation describe-stacks --stack-name AgenticAssistantInfraStack --query "Stacks[0].Outputs[?OutputKey=='ECRRepositoryURI'].OutputValue" --output text)

if [ -z "$ECR_URI" ]; then
    echo "ECR URI not found. Make sure the stack is deployed first."
    exit 1
fi

# Get AWS account ID and region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region)

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build and push Docker image
cd ../../mcp-server
docker build -t mcp-server .
docker tag mcp-server:latest $ECR_URI:latest
docker push $ECR_URI:latest

# Update ECS service to use new image
aws ecs update-service --cluster mcp-server-cluster --service McpServerService --force-new-deployment

echo "Deployment complete!"
