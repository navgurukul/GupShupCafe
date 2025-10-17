# AWS ECR & Fargate Deployment Guide

This guide covers deploying GupShup Cafe to AWS using ECR (Elastic Container Registry) and Fargate (serverless container orchestration).

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured (`aws configure`)
3. **Docker** installed on your local machine
4. **jq** (JSON processor) installed: `brew install jq` (macOS) or `sudo apt-get install jq` (Linux)

## Architecture Overview

```
┌─────────────────┐
│  React Frontend │ (Built as static files)
│   (Vite Build)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│ Docker Image    │─────▶│   AWS ECR    │
│ Frontend+Backend│      │  (Registry)  │
└─────────────────┘      └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │ AWS Fargate  │
                         │  (ECS Task)  │
                         └──────────────┘
```

## Quick Start

### 1. Initial Setup (First Time Only)

Set your AWS account details and VPC configuration:

```bash
# Set required environment variables
export AWS_ACCOUNT_ID=123456789012        # Your AWS account ID
export AWS_REGION=us-east-1               # Your preferred region
export VPC_ID=vpc-xxxxxxxxx               # Your VPC ID
export SUBNET_IDS=subnet-xxx,subnet-yyy   # Your subnet IDs (comma-separated)
export SECURITY_GROUP_ID=sg-xxxxxxxxx     # (Optional) Existing security group

# Run initial setup
./setup-fargate.sh
```

This script will:
- Create an ECS cluster
- Set up IAM roles
- Create a security group (if not provided)
- Register the task definition
- Create the ECS service
- Configure CloudWatch logging

### 2. Deploy Application

After initial setup, deploy your application:

```bash
# Build, push to ECR, and deploy to Fargate
export AWS_ACCOUNT_ID=123456789012
./deploy-aws.sh
```

This script will:
- Build the Docker image
- Tag and push to ECR
- Update the ECS task definition
- Deploy new version to Fargate

## Dockerfile Explanation

The `Dockerfile` uses a multi-stage build approach:

### Stage 1: Frontend Builder
- Uses `node:18-alpine` for smaller image size
- Installs dependencies with `npm ci`
- Builds React app with Vite (`npm run build`)
- Output: Static files in `/app/client/dist`

### Stage 2: Backend Builder
- Uses `python:3.11-slim`
- Installs Python dependencies from `requirements.txt`
- Prepares Python environment

### Stage 3: Final Image
- Combines backend code with built frontend
- Frontend static files served from `server_py/static`
- Runs as non-root user for security
- Exposes port 3003
- Includes health check endpoint

## Environment Variables

Configure these in your ECS task definition or via AWS Systems Manager Parameter Store:

### Required
```bash
PYTHON_ENV=production
PORT=3003
```

### Optional (for features)
```bash
# AI Features
HUGGINGFACE_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here

# CORS
ALLOWED_ORIGINS=https://your-domain.com

# Database (if using external DB)
DATABASE_URL=your_database_url
```

### Adding Secrets to Task Definition

Update `setup-fargate.sh` to include secrets:

```json
"secrets": [
  {
    "name": "HUGGINGFACE_API_KEY",
    "valueFrom": "arn:aws:ssm:region:account-id:parameter/gupshup/huggingface-key"
  }
]
```

## Configuration Details

### Resource Allocation

Default configuration (can be customized via environment variables):

```bash
TASK_CPU=512      # 0.5 vCPU
TASK_MEMORY=1024  # 1 GB RAM
DESIRED_COUNT=1   # Number of tasks
```

To change resources:

```bash
export TASK_CPU=1024
export TASK_MEMORY=2048
./setup-fargate.sh
```

### Networking

The service requires:
- **VPC**: Your application VPC
- **Subnets**: At least 2 subnets in different AZs (recommended for HA)
- **Security Group**: Allows inbound traffic on port 3003

### Auto-Scaling (Optional)

Add auto-scaling to your service:

```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/gupshup-cafe-cluster/gupshup-cafe-service \
  --min-capacity 1 \
  --max-capacity 4

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/gupshup-cafe-cluster/gupshup-cafe-service \
  --policy-name cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

## Load Balancer Setup (Optional but Recommended)

For production, add an Application Load Balancer:

### 1. Create Target Group

```bash
aws elbv2 create-target-group \
  --name gupshup-cafe-tg \
  --protocol HTTP \
  --port 3003 \
  --vpc-id $VPC_ID \
  --target-type ip \
  --health-check-path /api/health
```

### 2. Create Application Load Balancer

```bash
aws elbv2 create-load-balancer \
  --name gupshup-cafe-alb \
  --subnets $SUBNET_ID_1 $SUBNET_ID_2 \
  --security-groups $ALB_SECURITY_GROUP_ID
```

### 3. Update Service Configuration

Modify `setup-fargate.sh` to include load balancer configuration in the service definition.

## Monitoring & Logging

### CloudWatch Logs

View logs:

```bash
aws logs tail /ecs/gupshup-cafe-task --follow
```

### CloudWatch Metrics

Monitor your service:
- CPU Utilization
- Memory Utilization
- Request Count
- Error Rate

### Get Service Status

```bash
aws ecs describe-services \
  --cluster gupshup-cafe-cluster \
  --services gupshup-cafe-service
```

### Get Task Public IP

```bash
# List tasks
TASK_ARN=$(aws ecs list-tasks \
  --cluster gupshup-cafe-cluster \
  --service-name gupshup-cafe-service \
  --query 'taskArns[0]' \
  --output text)

# Get task details
aws ecs describe-tasks \
  --cluster gupshup-cafe-cluster \
  --tasks $TASK_ARN \
  --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
  --output text

# Get public IP from ENI
ENI_ID=$(aws ecs describe-tasks \
  --cluster gupshup-cafe-cluster \
  --tasks $TASK_ARN \
  --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
  --output text)

aws ec2 describe-network-interfaces \
  --network-interface-ids $ENI_ID \
  --query 'NetworkInterfaces[0].Association.PublicIp' \
  --output text
```

## Cost Optimization

### Fargate Pricing Factors
- vCPU per hour
- Memory per hour
- Data transfer

### Tips
1. **Right-size your tasks**: Start with smaller resources and scale up if needed
2. **Use Fargate Spot**: For non-critical workloads (up to 70% savings)
3. **Implement auto-scaling**: Scale down during off-peak hours
4. **Use Reserved Capacity**: For predictable workloads

### Enable Fargate Spot

Update service capacity provider:

```bash
aws ecs put-cluster-capacity-providers \
  --cluster gupshup-cafe-cluster \
  --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy \
    capacityProvider=FARGATE_SPOT,weight=1 \
    capacityProvider=FARGATE,weight=1
```

## Troubleshooting

### Container Won't Start

1. Check CloudWatch logs:
   ```bash
   aws logs tail /ecs/gupshup-cafe-task --follow
   ```

2. Verify task definition:
   ```bash
   aws ecs describe-task-definition --task-definition gupshup-cafe-task
   ```

3. Check stopped tasks:
   ```bash
   aws ecs describe-tasks --cluster gupshup-cafe-cluster --tasks <task-arn>
   ```

### Health Check Failing

- Ensure `/api/health` endpoint is accessible
- Verify container port (3003) is correctly mapped
- Check security group rules

### Cannot Pull Image from ECR

- Verify task execution role has ECR permissions
- Check ECR repository permissions
- Ensure image exists: `aws ecr describe-images --repository-name gupshup-cafe`

### Service Won't Update

- Force new deployment:
  ```bash
  aws ecs update-service \
    --cluster gupshup-cafe-cluster \
    --service gupshup-cafe-service \
    --force-new-deployment
  ```

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS Fargate

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Deploy to Fargate
        env:
          AWS_ACCOUNT_ID: ${{ secrets.AWS_ACCOUNT_ID }}
        run: ./deploy-aws.sh
```

## Cleanup

To remove all AWS resources:

```bash
# Delete service
aws ecs delete-service \
  --cluster gupshup-cafe-cluster \
  --service gupshup-cafe-service \
  --force

# Delete cluster
aws ecs delete-cluster --cluster gupshup-cafe-cluster

# Delete ECR repository
aws ecr delete-repository \
  --repository-name gupshup-cafe \
  --force

# Delete security group
aws ec2 delete-security-group --group-id $SECURITY_GROUP_ID

# Delete CloudWatch log group
aws logs delete-log-group --log-group-name /ecs/gupshup-cafe-task
```

## Support

For issues or questions:
1. Check CloudWatch logs
2. Review [AWS ECS documentation](https://docs.aws.amazon.com/ecs/)
3. Check the project's GitHub issues

## Additional Resources

- [AWS Fargate Pricing](https://aws.amazon.com/fargate/pricing/)
- [ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/intro.html)
- [Docker Multi-stage Builds](https://docs.docker.com/develop/develop-images/multistage-build/)
