# Deployment Guide - AI Roundtable Discussion Platform

This guide covers deploying the AI Roundtable Discussion Platform using AWS services.

## Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  AWS Amplify    │    │    AWS EC2      │    │  AI Services    │
│   (Frontend)    │    │   (Backend)     │    │ Strands/Gemini/ │
│                 │    │                 │    │    Bedrock      │
│  - React App    │───►│  - FastAPI      │───►│  - Feedback     │
│  - Static Files │    │  - Socket.io    │    │  - CEFR         │
│  - CDN          │    │  - Database     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

- AWS account
- AWS CLI configured
- Git repository
- Domain name (optional)

## Backend Deployment (AWS EC2 + AgentCore)

For detailed instructions on deploying the Python backend to AWS EC2, see [server_py/DEPLOYMENT.md](../server_py/DEPLOYMENT.md).

### Quick Overview

1. **Prepare Backend for Deployment**:
   - Configure environment variables
   - Set up database
   - Configure AI service credentials

2. **Deploy to AWS EC2**:
   - Launch EC2 instance
   - Install dependencies
   - Configure security groups
   - Set up systemd service

3. **Verify Backend Deployment**:
   - Check health endpoint
   - Verify API functionality
   - Test WebSocket connections

## Frontend Deployment (AWS Amplify)

### Step 1: Prepare Frontend for Deployment

1. **Create production environment file**:
   ```bash
   # In client/.env.production
   VITE_API_URL=https://your-backend-domain.com
   VITE_SOCKET_URL=https://your-backend-domain.com
   ```

2. **Build configuration is already set up in vite.config.js**

### Step 2: Deploy to AWS Amplify

1. **Connect Repository**:
   - Go to AWS Amplify Console
   - Click "New app" → "Host web app"
   - Connect your Git repository
   - Select the repository and branch

2. **Configure Build Settings**:
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - cd client
           - npm ci
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: client/dist
       files:
         - '**/*'
     cache:
       paths:
         - client/node_modules/**/*
   ```

3. **Set Environment Variables**:
   - Add variables from `.env.production`
   - Ensure API URLs point to your EC2 backend

4. **Deploy**: Amplify will automatically build and deploy

### Step 3: Configure Custom Domain (Optional)

1. **In AWS Amplify Console**:
   - Go to your app → Domain management
   - Add your custom domain
   - Follow DNS configuration instructions

2. **Update CORS on Backend**:
   - Update CORS settings to include your custom domain

## AI Services Setup

### AWS Strands / Gemini (Development)

1. **Get API Credentials**:
   - Set up AWS account
   - Configure Gemini API access
   - Generate necessary API keys

2. **Configure Environment**:
   ```env
   AI_SERVICE=gemini
   AI_API_KEY=your_api_key_here
   ```

### Bedrock Models (Production)

1. **AWS Bedrock Setup**:
   - Enable Bedrock in your AWS account
   - Configure model access
   - Set up IAM roles and permissions

2. **Configure Environment**:
   ```env
   AI_SERVICE=bedrock
   AWS_REGION=us-east-1
   ```

## Database Considerations

### Production Database

**Recommended Options**:
1. **Amazon RDS**: Managed database service
2. **Amazon DynamoDB**: NoSQL option for scalability
3. **Self-hosted on EC2**: Full control over database

**Configuration**:
- Set up database backups
- Configure security groups
- Enable encryption at rest
- Set up monitoring and alerts

## SSL/HTTPS Configuration

AWS provides SSL certificates:

- **AWS Amplify**: Automatic SSL for all domains
- **EC2 with Load Balancer**: Use AWS Certificate Manager
- **WebRTC**: Requires HTTPS in production

## Environment Variables Summary

### Frontend (AWS Amplify)
```env
VITE_API_URL=https://your-backend.example.com
VITE_SOCKET_URL=https://your-backend.example.com
```

### Backend (AWS EC2)
```env
NODE_ENV=production
PORT=3003
DATABASE_URL=your_database_connection_string
AI_SERVICE=bedrock
MIN_PARTICIPANTS=2
MAX_PARTICIPANTS=8
DEFAULT_SPEAKING_TIME=60
ALLOWED_ORIGINS=https://your-frontend.amplifyapp.com
SESSION_TIMEOUT=3600000
```

## Performance Optimization

### Frontend Optimizations

1. **Bundle Splitting**:
   ```javascript
   // Already configured in vite.config.js
   manualChunks: {
     vendor: ['react', 'react-dom'],
     router: ['react-router-dom'],
     socket: ['socket.io-client']
   }
   ```

2. **Image Optimization**:
   - Use WebP format for images
   - Implement lazy loading
   - Optimize SVG icons

3. **Caching Strategy**:
   ```javascript
   // In vite.config.js
   build: {
     rollupOptions: {
       output: {
         assetFileNames: 'assets/[name].[hash][extname]'
       }
     }
   }
   ```

### Backend Optimizations

1. **Compression**:
   ```javascript
   // Add to server.js
   import compression from 'compression'
   app.use(compression())
   ```

2. **Caching Headers**:
   ```javascript
   // For static assets
   app.use('/static', express.static('public', {
     maxAge: '1y',
     etag: true
   }))
   ```

## Monitoring and Analytics

### AWS CloudWatch

1. **EC2 Monitoring**:
   - CPU and memory utilization
   - Network traffic
   - Disk I/O

2. **Amplify Analytics**:
   - Web Vitals monitoring
   - User sessions
   - Performance metrics

### Custom Analytics

1. **Server Logging**:
   ```python
   # Add to main.py
   import logging
   
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   ```

2. **Error Tracking**:
   - Consider AWS CloudWatch Logs
   - Or third-party services like Sentry

## Scaling Considerations

### AWS Service Limits

**EC2 Instances**:
- Monitor CPU and memory usage
- Set up auto-scaling groups
- Use Elastic Load Balancer

**AWS Amplify**:
- CDN for global distribution
- Automatic scaling for traffic
- Build minute limits

### Scaling Strategies

1. **Horizontal Scaling**:
   - Multiple EC2 instances
   - Load balancing
   - Database read replicas

2. **Caching**:
   - Amazon ElastiCache (Redis)
   - CloudFront CDN
   - Application-level caching

## Troubleshooting Deployment

### Common Issues

1. **Build Failures**:
   ```bash
   # Check build logs
   # Ensure all dependencies are in package.json
   # Verify Node.js version compatibility
   ```

2. **Socket.io Connection Issues**:
   ```javascript
   // Check CORS configuration
   // Verify WebSocket support
   // Test with polling fallback
   ```

3. **Environment Variable Issues**:
   ```bash
   # Verify all required variables are set
   # Check for typos in variable names
   # Ensure proper encoding of special characters
   ```

### Debug Steps

1. **Backend Debugging**:
   ```bash
   # Check EC2 logs
   # Test API endpoints directly
   # Verify database connectivity
   # Check systemd service status
   ```

2. **Frontend Debugging**:
   ```bash
   # Check browser console
   # Test API calls in Network tab
   # Verify environment variables in build
   # Check Amplify build logs
   ```

## Security Checklist

### Backend Security
- [ ] CORS properly configured
- [ ] Helmet.js security headers
- [ ] Input validation on all endpoints
- [ ] Rate limiting implemented
- [ ] Sensitive data not logged

### Frontend Security
- [ ] No API keys in client-side code
- [ ] XSS protection enabled
- [ ] HTTPS enforced
- [ ] Content Security Policy set

## Maintenance

### Regular Tasks

1. **Updates**:
   - Monitor dependency vulnerabilities
   - Update packages regularly
   - Test after updates

2. **Monitoring**:
   - Check service health
   - Monitor error rates
   - Review performance metrics

3. **Backups**:
   - Database backups (if using persistent storage)
   - Configuration backups
   - Code repository maintenance

### Emergency Procedures

1. **Service Down**:
   - Check EC2 instance status
   - Review recent deployments
   - Check CloudWatch logs
   - Verify security group settings

2. **Performance Issues**:
   - Monitor resource usage in CloudWatch
   - Check for memory leaks
   - Review database queries
   - Scale resources if needed

## Cost Optimization

### AWS Cost Management

1. **EC2**:
   - Use appropriate instance types
   - Consider Reserved Instances for production
   - Set up auto-stop for non-production instances

2. **Amplify**:
   - Monitor build minutes
   - Optimize bundle sizes
   - Use efficient caching

### Budget Alerts

Set up AWS Budget alerts to monitor costs:
- Daily/monthly spending limits
- Service-specific budgets
- Email notifications

## Support and Resources

### Documentation
- [AWS Amplify Docs](https://docs.amplify.aws/)
- [AWS EC2 Docs](https://docs.aws.amazon.com/ec2/)
- [AWS Bedrock Docs](https://docs.aws.amazon.com/bedrock/)

### Community
- AWS Forums for technical questions
- GitHub Discussions for project-specific help
- Stack Overflow for development questions

This deployment guide provides a complete setup for hosting your AI Roundtable Discussion Platform using AWS services with proper monitoring and scaling capabilities.
