# 🚀 AI Gupshup Platform - Deployment Guide

## 📋 Quick Deploy Overview

This platform provides instant feedback to students participating in a gamified discussion experience with their peers on their English speaking skills for rapid growth in English. The LLM Agent provides corrective feedback to the participants for their English based on the CEFR standard.

### ✅ Prerequisites 
- AWS account configured
- Code ready for deployment
- Environment files configured
- Documentation reviewed

## 🔥 Deploy Backend to AWS EC2

For detailed backend deployment instructions, see [server_py/DEPLOYMENT.md](./server_py/DEPLOYMENT.md).

### Quick Steps:
1. Launch EC2 instance
2. Install Python and dependencies
3. Configure environment variables
4. Set up systemd service
5. Configure security groups
6. Test deployment

## 🌐 Deploy Frontend to AWS Amplify

### Step 1: Prepare Frontend
Ensure your frontend is configured with the correct backend URL:
```env
VITE_API_URL=https://your-ec2-backend.example.com
VITE_SOCKET_URL=https://your-ec2-backend.example.com
```

### Step 2: Deploy to AWS Amplify

1. **Connect Repository**:
   - Go to AWS Amplify Console
   - Click **"New app"** → **"Host web app"**
   - Connect your Git repository

2. **Configure Build Settings**:
   - Framework: Vite
   - Root Directory: client
   - Build Command: npm run build
   - Output Directory: dist

3. **Set Environment Variables**:
   - Add environment variables in Amplify Console
   - Ensure API URLs point to your EC2 backend

4. **Deploy**:
   - Amplify will automatically build and deploy
   - Wait for deployment to complete

## 🎯 Final Configuration

### Update Backend CORS
After frontend deployment, update your backend CORS settings:
```
CORS_ORIGIN=https://your-app.amplifyapp.com
```

### Test Your Deployment
1. Visit your Amplify URL
2. Create a roundtable session
3. Test real-time features
4. Verify voice controls work
5. Test LLM feedback features

## 🔧 Troubleshooting

### Common Issues:
- **CORS Errors**: Update CORS_ORIGIN in EC2 backend
- **API Connection**: Check VITE_API_URL in Amplify
- **Voice Not Working**: Ensure HTTPS is enabled
- **WebSocket Issues**: Verify security group settings on EC2

### Health Check URLs:
- Backend: `https://your-backend.example.com/health`
- Frontend: `https://your-app.amplifyapp.com`

## 📱 Your Live App Features
- ✅ Real-time roundtable discussions
- ✅ LLM-powered conversation facilitation
- ✅ CEFR-based English feedback
- ✅ STT/TTS integration
- ✅ Voice controls and audio feedback
- ✅ Mobile-responsive design
- ✅ Gamified UI with animations
- ✅ User authentication and progress tracking
- ✅ Anonymous participation

## 🎉 Success!
Your AI Gupshup Platform is now live and ready to provide instant feedback to students for rapid English growth!

**Frontend**: AWS Amplify
**Backend**: AWS EC2 + AgentCore
**AI Services**: AWS Strands/Gemini (dev) or Bedrock (prod)

Share your platform with educators and students around the world! 🌍
