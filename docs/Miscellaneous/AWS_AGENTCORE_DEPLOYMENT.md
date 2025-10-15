# AWS AgentCore Deployment Guide

## Overview

This guide covers deploying the GupShup Cafe multi-agent system to AWS using Bedrock AgentCore SDK.

## Prerequisites

### 1. AWS Account Setup

- Active AWS account with billing enabled
- IAM user with appropriate permissions
- AWS CLI installed and configured

### 2. Required AWS Services

- **AWS Bedrock**: For AI agent runtime
- **AWS IAM**: For permissions management
- **AWS CloudWatch**: For logging and monitoring
- **AWS S3** (optional): For agent artifacts storage

### 3. Software Requirements

```bash
# Python 3.12 or higher
python --version

# AWS CLI v2
aws --version

# pip packages
pip install -r requirements.txt
```

## Step 1: Configure AWS Credentials

### Option A: AWS CLI Configuration

```bash
aws configure
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region name: us-east-1
# Default output format: json
```

### Option B: Environment Variables

```bash
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_DEFAULT_REGION="us-east-1"
```

### Option C: IAM Role (Recommended for EC2)

If deploying on EC2, attach an IAM role with required permissions instead of using credentials.

## Step 2: Set Up IAM Permissions

### Required IAM Policy

Create an IAM policy with the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeAgent",
        "bedrock:InvokeModel",
        "bedrock:GetAgent",
        "bedrock:ListAgents",
        "bedrock:CreateAgent",
        "bedrock:UpdateAgent",
        "bedrock:DeleteAgent"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/bedrock/agents/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::your-agent-bucket/*"
    }
  ]
}
```

### Create IAM User/Role

```bash
# Create IAM policy
aws iam create-policy \
  --policy-name GupShupCafeAgentCorePolicy \
  --policy-document file://agent-policy.json

# Attach to user
aws iam attach-user-policy \
  --user-name your-username \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/GupShupCafeAgentCorePolicy
```

## Step 3: Configure Environment

### Update `.env` File

```bash
cd server_py
cp .env.example .env
```

Edit `.env`:

```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# AgentCore Settings
USE_AWS_AGENTCORE=true
AWS_AGENTCORE_LOG_LEVEL=INFO

# Agent Configuration
GEMINI_API_KEY=your_gemini_api_key
USE_MULTI_AGENT=true

# Application Settings
PORT=3003
ENABLE_LLM_AGENT=true
```

## Step 4: Install Dependencies

### Install Python Dependencies

```bash
cd server_py
pip install -r requirements.txt
```

### Install AWS Bedrock AgentCore SDK

```bash
pip install bedrock-agentcore
pip install bedrock-agentcore-starter-toolkit
pip install boto3
```

### Verify Installation

```python
python -c "import boto3; import bedrock_agentcore; print('AWS packages installed successfully')"
```

## Step 5: Deploy Agents

### Method 1: Using Python Script

```python
from server_py.src.llmTutor.multiAgentOrchestrator import get_orchestrator

# Initialize orchestrator with AWS mode
orchestrator = get_orchestrator()

# Deploy to AWS
success = orchestrator.deploy_to_aws()

if success:
    print("✅ Agents deployed successfully to AWS")
else:
    print("❌ Deployment failed, check logs")
```

### Method 2: Using CLI Script

Create `deploy_agents.py`:

```python
#!/usr/bin/env python3
"""
Deploy GupShup Cafe agents to AWS Bedrock AgentCore
"""

import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src/llmTutor'))

from multiAgentOrchestrator import MultiAgentOrchestrator

def main():
    print("="*60)
    print("GupShup Cafe - AWS Agent Deployment")
    print("="*60)
    
    # Load environment
    load_dotenv()
    
    # Check AWS configuration
    if not os.getenv('AWS_REGION'):
        print("❌ AWS_REGION not set in .env")
        return False
    
    print(f"\n📍 Region: {os.getenv('AWS_REGION')}")
    print(f"🔧 Multi-Agent: Enabled")
    
    # Initialize orchestrator
    print("\n🚀 Initializing orchestrator...")
    orchestrator = MultiAgentOrchestrator(use_aws_agentcore=True)
    
    # Deploy agents
    print("\n📦 Deploying agents to AWS Bedrock AgentCore...")
    success = orchestrator.deploy_to_aws()
    
    if success:
        print("\n✅ Deployment successful!")
        print("\nNext steps:")
        print("1. Start the application: python main.py")
        print("2. Monitor agents: aws logs tail /aws/bedrock/agents/gupshup-cafe")
        print("3. Test functionality with debate facilitator")
        return True
    else:
        print("\n❌ Deployment failed!")
        print("Check logs for details")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

Run deployment:

```bash
cd server_py
chmod +x deploy_agents.py
python deploy_agents.py
```

## Step 6: Verify Deployment

### Check Agent Status

```python
from multiAgentOrchestrator import get_orchestrator

orchestrator = get_orchestrator()

# Get agent status
print("Agents:", list(orchestrator.agents.keys()))
print("AWS Mode:", orchestrator.use_aws_agentcore)
print("Credentials:", "Configured" if orchestrator.aws_credentials_configured else "Not configured")
```

### Test Agent Functionality

```python
# Test English Grammar Agent
statements = [
    {"speaker": "Alice", "content": "I goes to school yesterday."}
]
feedback = orchestrator.get_english_feedback(statements, instant=True)
print("English Feedback:", feedback)

# Test Debate Facilitator
orchestrator.initialize_debate_facilitator(
    room_type="discussion",
    topic="Test Topic",
    participants=["Alice", "Bob"]
)
discussion = orchestrator.get_discussion_feedback("Test Topic", statements)
print("Discussion Feedback:", discussion)
```

## Step 7: Configure Monitoring

### CloudWatch Logs

Logs are automatically sent to CloudWatch when using AWS mode.

View logs:

```bash
# List log groups
aws logs describe-log-groups --log-group-name-prefix /aws/bedrock/agents

# Tail logs
aws logs tail /aws/bedrock/agents/gupshup-cafe --follow
```

### CloudWatch Metrics

Create custom metrics for agent performance:

```python
import boto3

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

# Put custom metric
cloudwatch.put_metric_data(
    Namespace='GupShupCafe/Agents',
    MetricData=[
        {
            'MetricName': 'FeedbackLatency',
            'Value': response_time_ms,
            'Unit': 'Milliseconds',
            'Dimensions': [
                {'Name': 'AgentType', 'Value': 'EnglishGrammar'}
            ]
        }
    ]
)
```

### Set Up Alarms

```bash
# Create alarm for high latency
aws cloudwatch put-metric-alarm \
  --alarm-name gupshup-cafe-high-latency \
  --alarm-description "Alert when agent latency exceeds 5 seconds" \
  --metric-name FeedbackLatency \
  --namespace GupShupCafe/Agents \
  --statistic Average \
  --period 300 \
  --threshold 5000 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

## Step 8: Application Deployment

### Deploy to EC2

See [DEPLOYMENT.md](../../server_py/DEPLOYMENT.md) for full EC2 deployment guide.

Key differences for multi-agent deployment:

1. **Install additional packages**:
   ```bash
   pip install bedrock-agentcore bedrock-agentcore-starter-toolkit
   ```

2. **Configure IAM role** with Bedrock permissions

3. **Set environment variables**:
   ```bash
   export USE_AWS_AGENTCORE=true
   export USE_MULTI_AGENT=true
   ```

4. **Deploy agents on first run**:
   ```bash
   python deploy_agents.py
   ```

### Systemd Service Configuration

Update systemd service to include AWS credentials:

```ini
[Unit]
Description=GupShup Cafe API with Multi-Agent System
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/GupShupCafe/server_py
Environment="PATH=/home/ubuntu/GupShupCafe/server_py/venv/bin"
Environment="AWS_REGION=us-east-1"
Environment="USE_AWS_AGENTCORE=true"
Environment="USE_MULTI_AGENT=true"
ExecStart=/home/ubuntu/GupShupCafe/server_py/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Cost Optimization

### Tips to Reduce Costs

1. **Use Local Mode for Development**:
   ```env
   USE_AWS_AGENTCORE=false  # Development
   ```

2. **Implement Caching**:
   - Cache common grammar patterns
   - Store frequent feedback responses

3. **Batch Requests**:
   - Collect multiple statements before requesting feedback
   - Use comprehensive mode at end of discussion only

4. **Monitor Usage**:
   ```bash
   aws ce get-cost-and-usage \
     --time-period Start=2024-01-01,End=2024-01-31 \
     --granularity MONTHLY \
     --metrics BlendedCost \
     --filter file://bedrock-filter.json
   ```

5. **Set Spending Alerts**:
   - Configure AWS Budget alerts
   - Monitor Bedrock usage dashboard

## Troubleshooting

### Issue: "No module named 'bedrock_agentcore'"

**Solution**: Install package
```bash
pip install bedrock-agentcore
```

### Issue: "Credentials not configured"

**Solution**: Check AWS credentials
```bash
aws sts get-caller-identity
# Should return your account information
```

### Issue: "Access denied to Bedrock"

**Solution**: Verify IAM permissions
```bash
aws iam get-user-policy --user-name your-username --policy-name GupShupCafeAgentCorePolicy
```

### Issue: "Region does not support Bedrock"

**Solution**: Use supported region
```bash
# Bedrock is available in:
# us-east-1, us-west-2, eu-west-1, ap-southeast-1, ap-northeast-1
export AWS_REGION=us-east-1
```

### Issue: Agents not responding

**Solution**: Check CloudWatch logs
```bash
aws logs tail /aws/bedrock/agents/gupshup-cafe --follow
```

## Security Best Practices

1. **Use IAM Roles** instead of access keys when possible
2. **Rotate credentials** regularly
3. **Enable CloudTrail** for audit logging
4. **Encrypt data** in transit and at rest
5. **Use VPC endpoints** for private connectivity
6. **Implement least privilege** IAM policies

## Maintenance

### Regular Tasks

1. **Monitor Costs**: Weekly review of AWS billing
2. **Check Logs**: Daily check for errors
3. **Update Dependencies**: Monthly package updates
4. **Performance Review**: Weekly latency analysis
5. **Security Patches**: Apply as needed

### Updating Agents

To update agent logic:

1. Update agent code locally
2. Test thoroughly
3. Deploy new version:
   ```bash
   python deploy_agents.py
   ```
4. Monitor for issues
5. Rollback if needed

## Rollback Procedure

If deployment fails or causes issues:

```python
from multiAgentOrchestrator import get_orchestrator

orchestrator = get_orchestrator()

# Switch to local mode
orchestrator.use_aws_agentcore = False

# Or fall back to single-agent mode
from debate_room_facilitator import DebateRoomFacilitator
facilitator = DebateRoomFacilitator(use_multi_agent=False)
```

## Support Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS Support](https://console.aws.amazon.com/support/)
- [GupShup Cafe Documentation](../../docs/)
- [GitHub Issues](https://github.com/navgurukul/GupShupCafe/issues)

## Next Steps

After successful deployment:

1. ✅ Test multi-agent functionality end-to-end
2. ✅ Set up monitoring and alerts
3. ✅ Configure auto-scaling if needed
4. ✅ Document any customizations
5. ✅ Train team on new system
