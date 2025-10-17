# AWS Deployment Scripts

Quick reference for deploying GupShup Cafe to AWS ECR and Fargate.

## Files

- **`Dockerfile`** - Multi-stage build for frontend + backend
- **`setup-fargate.sh`** - Initial AWS infrastructure setup
- **`deploy-aws.sh`** - Build, push, and deploy updates
- **`.dockerignore`** - Optimize Docker build context

## Quick Start

### First Time Setup

```bash
# Configure AWS credentials first
aws configure

# Set environment variables and run setup
export AWS_ACCOUNT_ID=123456789012
export AWS_REGION=us-east-1
export VPC_ID=vpc-xxxxxxxxx
export SUBNET_IDS=subnet-xxx,subnet-yyy

./setup-fargate.sh
```

### Deploy Updates

```bash
export AWS_ACCOUNT_ID=123456789012
./deploy-aws.sh
```

## What Gets Deployed

The Docker container includes:
- ✅ React frontend (built with Vite)
- ✅ Python FastAPI backend
- ✅ Socket.io for real-time communication
- ✅ SQLite database (local storage)
- ✅ Health check endpoint

## Environment Variables

Set in ECS task definition:
- `PYTHON_ENV=production`
- `PORT=3003`
- `HUGGINGFACE_API_KEY` (optional)
- `GEMINI_API_KEY` (optional)
- `ALLOWED_ORIGINS` (for CORS)

## Resources

- CPU: 0.5 vCPU (512)
- Memory: 1 GB (1024)
- Port: 3003

## Documentation

See **[docs/AWS_DEPLOYMENT.md](docs/AWS_DEPLOYMENT.md)** for:
- Detailed setup instructions
- Load balancer configuration
- Auto-scaling setup
- Monitoring and troubleshooting
- Cost optimization
- CI/CD integration

## Common Commands

```bash
# View logs
aws logs tail /ecs/gupshup-cafe-task --follow

# Get service status
aws ecs describe-services --cluster gupshup-cafe-cluster --services gupshup-cafe-service

# Force new deployment
aws ecs update-service --cluster gupshup-cafe-cluster --service gupshup-cafe-service --force-new-deployment

# Get public IP
aws ecs list-tasks --cluster gupshup-cafe-cluster --service-name gupshup-cafe-service
```

## Support

For issues or questions, see the troubleshooting section in `docs/AWS_DEPLOYMENT.md`.
