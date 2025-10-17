#!/bin/bash

# GupShup Cafe - AWS ECR and Fargate Deployment Script
# This script builds, tags, pushes Docker image to ECR and deploys to Fargate

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration variables
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID}"
ECR_REPOSITORY="${ECR_REPOSITORY:-gupshup-cafe}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
CLUSTER_NAME="${CLUSTER_NAME:-gupshup-cafe-cluster}"
SERVICE_NAME="${SERVICE_NAME:-gupshup-cafe-service}"
TASK_FAMILY="${TASK_FAMILY:-gupshup-cafe-task}"

# Validate required environment variables
if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo -e "${RED}Error: AWS_ACCOUNT_ID environment variable is not set${NC}"
    echo "Usage: AWS_ACCOUNT_ID=123456789012 ./deploy-aws.sh"
    exit 1
fi

echo -e "${GREEN}Starting deployment process...${NC}"
echo "AWS Region: $AWS_REGION"
echo "ECR Repository: $ECR_REPOSITORY"
echo "Image Tag: $IMAGE_TAG"

# Step 1: Authenticate Docker to ECR
echo -e "\n${YELLOW}Step 1: Authenticating Docker to ECR...${NC}"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Step 2: Create ECR repository if it doesn't exist
echo -e "\n${YELLOW}Step 2: Checking ECR repository...${NC}"
aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION 2>/dev/null || \
    aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION --image-scanning-configuration scanOnPush=true

# Step 3: Build Docker image
echo -e "\n${YELLOW}Step 3: Building Docker image...${NC}"
docker build -t $ECR_REPOSITORY:$IMAGE_TAG .

# Step 4: Tag the image for ECR
echo -e "\n${YELLOW}Step 4: Tagging image...${NC}"
ECR_IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG"
docker tag $ECR_REPOSITORY:$IMAGE_TAG $ECR_IMAGE_URI

# Also tag as latest
docker tag $ECR_REPOSITORY:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest

# Step 5: Push image to ECR
echo -e "\n${YELLOW}Step 5: Pushing image to ECR...${NC}"
docker push $ECR_IMAGE_URI
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest

echo -e "\n${GREEN}Image successfully pushed to ECR!${NC}"
echo "Image URI: $ECR_IMAGE_URI"

# Step 6: Update ECS task definition (if service exists)
echo -e "\n${YELLOW}Step 6: Updating ECS task definition...${NC}"

# Check if task definition exists
if aws ecs describe-task-definition --task-definition $TASK_FAMILY --region $AWS_REGION 2>/dev/null; then
    # Get the current task definition
    TASK_DEFINITION=$(aws ecs describe-task-definition --task-definition $TASK_FAMILY --region $AWS_REGION)
    
    # Register new task definition with updated image
    NEW_TASK_DEF=$(echo $TASK_DEFINITION | jq --arg IMAGE "$ECR_IMAGE_URI" '.taskDefinition | .containerDefinitions[0].image = $IMAGE | del(.taskDefinitionArn) | del(.revision) | del(.status) | del(.requiresAttributes) | del(.compatibilities) | del(.registeredAt) | del(.registeredBy)')
    
    aws ecs register-task-definition --region $AWS_REGION --cli-input-json "$NEW_TASK_DEF" > /dev/null
    
    echo -e "${GREEN}Task definition updated${NC}"
    
    # Step 7: Update ECS service
    echo -e "\n${YELLOW}Step 7: Updating ECS service...${NC}"
    if aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $AWS_REGION | jq -e '.services[0]' > /dev/null 2>&1; then
        aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --task-definition $TASK_FAMILY --force-new-deployment --region $AWS_REGION > /dev/null
        echo -e "${GREEN}Service update initiated${NC}"
        
        echo -e "\n${YELLOW}Waiting for service to stabilize...${NC}"
        aws ecs wait services-stable --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $AWS_REGION
        echo -e "${GREEN}Service deployment complete!${NC}"
    else
        echo -e "${YELLOW}Service does not exist. Please create it manually or use the setup script.${NC}"
    fi
else
    echo -e "${YELLOW}Task definition does not exist. Please run the initial setup script first.${NC}"
fi

echo -e "\n${GREEN}=== Deployment Complete ===${NC}"
echo -e "Image: ${ECR_IMAGE_URI}"
echo -e "To check service status: aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $AWS_REGION"
