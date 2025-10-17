#!/bin/bash

# GupShup Cafe - AWS ECS Fargate Initial Setup Script
# Creates ECS cluster, task definition, and service

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID}"
ECR_REPOSITORY="${ECR_REPOSITORY:-gupshup-cafe}"
CLUSTER_NAME="${CLUSTER_NAME:-gupshup-cafe-cluster}"
SERVICE_NAME="${SERVICE_NAME:-gupshup-cafe-service}"
TASK_FAMILY="${TASK_FAMILY:-gupshup-cafe-task}"
CONTAINER_NAME="${CONTAINER_NAME:-gupshup-cafe-container}"
VPC_ID="${VPC_ID}"
SUBNET_IDS="${SUBNET_IDS}" # Comma-separated subnet IDs
SECURITY_GROUP_ID="${SECURITY_GROUP_ID}"

# Task configuration
TASK_CPU="${TASK_CPU:-512}"       # 0.5 vCPU
TASK_MEMORY="${TASK_MEMORY:-1024}" # 1 GB
DESIRED_COUNT="${DESIRED_COUNT:-1}"

# Validate required variables
if [ -z "$AWS_ACCOUNT_ID" ] || [ -z "$VPC_ID" ] || [ -z "$SUBNET_IDS" ]; then
    echo -e "${RED}Error: Required environment variables are not set${NC}"
    echo "Required: AWS_ACCOUNT_ID, VPC_ID, SUBNET_IDS"
    echo ""
    echo "Usage:"
    echo "  AWS_ACCOUNT_ID=123456789012 \\"
    echo "  VPC_ID=vpc-xxxxxx \\"
    echo "  SUBNET_IDS=subnet-xxxx,subnet-yyyy \\"
    echo "  SECURITY_GROUP_ID=sg-xxxxx \\"
    echo "  ./setup-fargate.sh"
    exit 1
fi

echo -e "${GREEN}Starting AWS Fargate setup...${NC}"

# Step 1: Create ECS Cluster
echo -e "\n${YELLOW}Step 1: Creating ECS Cluster...${NC}"
aws ecs describe-clusters --clusters $CLUSTER_NAME --region $AWS_REGION 2>/dev/null || \
    aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $AWS_REGION

echo -e "${GREEN}Cluster ready: $CLUSTER_NAME${NC}"

# Step 2: Create CloudWatch Log Group
echo -e "\n${YELLOW}Step 2: Creating CloudWatch Log Group...${NC}"
LOG_GROUP="/ecs/$TASK_FAMILY"
aws logs create-log-group --log-group-name $LOG_GROUP --region $AWS_REGION 2>/dev/null || \
    echo "Log group already exists"

# Step 3: Create IAM Role for ECS Task Execution (if not exists)
echo -e "\n${YELLOW}Step 3: Setting up IAM roles...${NC}"
EXECUTION_ROLE_NAME="ecsTaskExecutionRole"

# Check if role exists
if ! aws iam get-role --role-name $EXECUTION_ROLE_NAME 2>/dev/null; then
    echo "Creating execution role..."
    
    # Create trust policy
    cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

    aws iam create-role --role-name $EXECUTION_ROLE_NAME --assume-role-policy-document file://trust-policy.json
    aws iam attach-role-policy --role-name $EXECUTION_ROLE_NAME --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
    
    rm trust-policy.json
fi

EXECUTION_ROLE_ARN="arn:aws:iam::$AWS_ACCOUNT_ID:iam::role/$EXECUTION_ROLE_NAME"

# Step 4: Create Security Group (if not provided)
if [ -z "$SECURITY_GROUP_ID" ]; then
    echo -e "\n${YELLOW}Step 4: Creating Security Group...${NC}"
    SECURITY_GROUP_ID=$(aws ec2 create-security-group \
        --group-name gupshup-cafe-sg \
        --description "Security group for GupShup Cafe" \
        --vpc-id $VPC_ID \
        --region $AWS_REGION \
        --query 'GroupId' \
        --output text)
    
    # Allow inbound traffic on port 3003
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 3003 \
        --cidr 0.0.0.0/0 \
        --region $AWS_REGION
    
    echo -e "${GREEN}Security Group created: $SECURITY_GROUP_ID${NC}"
fi

# Step 5: Register Task Definition
echo -e "\n${YELLOW}Step 5: Registering ECS Task Definition...${NC}"

ECR_IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest"

cat > task-definition.json <<EOF
{
  "family": "$TASK_FAMILY",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "$TASK_CPU",
  "memory": "$TASK_MEMORY",
  "executionRoleArn": "$EXECUTION_ROLE_ARN",
  "containerDefinitions": [
    {
      "name": "$CONTAINER_NAME",
      "image": "$ECR_IMAGE_URI",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 3003,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "PYTHON_ENV",
          "value": "production"
        },
        {
          "name": "PORT",
          "value": "3003"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "$LOG_GROUP",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:3003/api/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
EOF

aws ecs register-task-definition --cli-input-json file://task-definition.json --region $AWS_REGION
rm task-definition.json

echo -e "${GREEN}Task definition registered${NC}"

# Step 6: Create ECS Service
echo -e "\n${YELLOW}Step 6: Creating ECS Service...${NC}"

# Convert comma-separated subnet IDs to JSON array
IFS=',' read -ra SUBNET_ARRAY <<< "$SUBNET_IDS"
SUBNET_JSON=$(printf '"%s",' "${SUBNET_ARRAY[@]}" | sed 's/,$//')

cat > service-definition.json <<EOF
{
  "cluster": "$CLUSTER_NAME",
  "serviceName": "$SERVICE_NAME",
  "taskDefinition": "$TASK_FAMILY",
  "desiredCount": $DESIRED_COUNT,
  "launchType": "FARGATE",
  "networkConfiguration": {
    "awsvpcConfiguration": {
      "subnets": [$SUBNET_JSON],
      "securityGroups": ["$SECURITY_GROUP_ID"],
      "assignPublicIp": "ENABLED"
    }
  },
  "deploymentConfiguration": {
    "maximumPercent": 200,
    "minimumHealthyPercent": 100
  }
}
EOF

aws ecs create-service --cli-input-json file://service-definition.json --region $AWS_REGION
rm service-definition.json

echo -e "${GREEN}Service created successfully!${NC}"

# Step 7: Wait for service to stabilize
echo -e "\n${YELLOW}Step 7: Waiting for service to become stable...${NC}"
aws ecs wait services-stable --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $AWS_REGION

echo -e "\n${GREEN}=== Setup Complete ===${NC}"
echo -e "Cluster: $CLUSTER_NAME"
echo -e "Service: $SERVICE_NAME"
echo -e "Task Definition: $TASK_FAMILY"
echo -e "Security Group: $SECURITY_GROUP_ID"
echo ""
echo -e "To get the public IP of your task:"
echo -e "  aws ecs list-tasks --cluster $CLUSTER_NAME --service-name $SERVICE_NAME --region $AWS_REGION"
echo -e "  aws ecs describe-tasks --cluster $CLUSTER_NAME --tasks <task-arn> --region $AWS_REGION"
echo ""
echo -e "To deploy updates, run: ./deploy-aws.sh"
