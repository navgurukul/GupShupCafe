#!/usr/bin/env python3
"""
Simple integration example for multi-agent system.

This script demonstrates how to use the multi-agent architecture
without requiring full strands library setup.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src/llmTutor'))

def check_dependencies():
    """Check if required dependencies are installed."""
    print("="*60)
    print("Checking Dependencies")
    print("="*60)
    
    required = {
        'boto3': 'AWS SDK for Python',
        'python_dotenv': 'Environment variable management',
    }
    
    missing = []
    for module, desc in required.items():
        try:
            if module == 'python_dotenv':
                __import__('dotenv')
            else:
                __import__(module)
            print(f"✓ {module.replace('_', '-')}: {desc}")
        except ImportError:
            print(f"✗ {module.replace('_', '-')}: {desc} (MISSING)")
            missing.append(module)
    
    optional = {
        'bedrock_agentcore': 'AWS Bedrock AgentCore SDK',
        'strands': 'Strands Agents Framework',
    }
    
    print("\nOptional Dependencies:")
    for module, desc in optional.items():
        try:
            __import__(module)
            print(f"✓ {module}: {desc}")
        except ImportError:
            print(f"⚠ {module}: {desc} (Not installed - features limited)")
    
    if missing:
        print(f"\n❌ Missing required dependencies: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    print("\n✅ All required dependencies installed")
    return True


def test_multi_agent_structure():
    """Test multi-agent system structure without API calls."""
    print("\n" + "="*60)
    print("Testing Multi-Agent Structure")
    print("="*60)
    
    try:
        # Test import of new modules
        print("\n1. Testing imports...")
        
        # These will fail without strands but we can check the files exist
        import os
        files_to_check = [
            'englishGrammarAgent.py',
            'multiAgentOrchestrator.py',
        ]
        
        for filename in files_to_check:
            filepath = os.path.join(os.path.dirname(__file__), 'src/llmTutor', filename)
            if os.path.exists(filepath):
                print(f"   ✓ {filename} exists")
            else:
                print(f"   ✗ {filename} missing")
                return False
        
        # Test debate_room_facilitator has multi-agent support
        print("\n2. Checking debate_room_facilitator updates...")
        with open(os.path.join(os.path.dirname(__file__), 'src/llmTutor/debate_room_facilitator.py'), 'r') as f:
            content = f.read()
            
            checks = [
                ('use_multi_agent', 'Multi-agent flag parameter'),
                ('MultiAgentOrchestrator', 'Orchestrator import'),
                ('_initialize_single_agent', 'Backward compatibility method'),
                ('get_combined_feedback', 'Combined feedback method'),
            ]
            
            for check_str, desc in checks:
                if check_str in content:
                    print(f"   ✓ {desc}")
                else:
                    print(f"   ✗ {desc} missing")
                    return False
        
        print("\n✅ Multi-agent structure verified")
        return True
        
    except Exception as e:
        print(f"\n❌ Structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_aws_configuration():
    """Test AWS configuration and credentials."""
    print("\n" + "="*60)
    print("Testing AWS Configuration")
    print("="*60)
    
    try:
        import boto3
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Check environment variables
        print("\n1. Checking environment variables...")
        aws_region = os.getenv('AWS_REGION')
        if aws_region:
            print(f"   ✓ AWS_REGION: {aws_region}")
        else:
            print(f"   ⚠ AWS_REGION not set (will use default)")
        
        # Try to get AWS credentials
        print("\n2. Checking AWS credentials...")
        try:
            session = boto3.Session()
            credentials = session.get_credentials()
            if credentials:
                print(f"   ✓ AWS credentials configured")
                print(f"   ✓ Access Key: {credentials.access_key[:4]}...{credentials.access_key[-4:]}")
            else:
                print(f"   ⚠ AWS credentials not configured")
                print(f"   ℹ Local mode will be used (no AWS deployment)")
        except Exception as e:
            print(f"   ⚠ Could not check credentials: {e}")
            print(f"   ℹ Local mode will be used")
        
        # Check Gemini API key
        print("\n3. Checking Gemini API key...")
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            print(f"   ✓ GEMINI_API_KEY configured")
        else:
            print(f"   ✗ GEMINI_API_KEY not set")
            print(f"   ⚠ Agents will not function without API key")
        
        print("\n✅ Configuration check complete")
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_usage_example():
    """Show example usage of multi-agent system."""
    print("\n" + "="*60)
    print("Usage Example")
    print("="*60)
    
    example = """
# Example 1: Using multi-agent mode in debate facilitator
from debate_room_facilitator import DebateRoomFacilitator

facilitator = DebateRoomFacilitator(
    room_type="discussion",
    num_rounds=3,
    use_multi_agent=True  # Enable multi-agent architecture
)

# The facilitator will automatically:
# - Initialize English Grammar Agent for language feedback
# - Initialize Debate Facilitator for content feedback
# - Combine responses from both agents

# Example 2: Direct orchestrator usage
from multiAgentOrchestrator import get_orchestrator

orchestrator = get_orchestrator()

# Initialize facilitator
orchestrator.initialize_debate_facilitator(
    room_type="discussion",
    topic="AI in Education",
    participants=["Alice", "Bob"]
)

# Get instant English feedback
statements = [
    {"speaker": "Alice", "content": "AI are very helpful for learning."},
    {"speaker": "Bob", "content": "I thinks so too."}
]
english_feedback = orchestrator.get_english_feedback(
    statements, 
    instant=True
)

# Get discussion feedback
discussion_feedback = orchestrator.get_discussion_feedback(
    topic="AI in Education",
    recent_statements=statements
)

# Get combined feedback (both discussion and English)
combined = orchestrator.get_combined_feedback(
    topic="AI in Education",
    recent_statements=statements
)

print("Discussion:", combined["discussion_feedback"])
print("English:", combined["english_feedback"])

# Example 3: Backward compatible single-agent mode
facilitator = DebateRoomFacilitator(
    room_type="discussion",
    use_multi_agent=False  # Use original single-agent mode
)
# Works exactly as before
"""
    
    print(example)
    
    print("\n" + "="*60)
    print("Configuration Options")
    print("="*60)
    
    config = """
# In your .env file:

# Enable multi-agent mode
USE_MULTI_AGENT=true

# Use AWS AgentCore for deployment (optional)
USE_AWS_AGENTCORE=false  # Set to true for AWS deployment

# AWS Configuration (required for AWS mode)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Required: Gemini API key for agents
GEMINI_API_KEY=your_gemini_key

# Enable LLM Agent in roundtable discussions
ENABLE_LLM_AGENT=true
"""
    
    print(config)


def main():
    """Main entry point."""
    print("\n" + "="*70)
    print(" "*15 + "Multi-Agent System - Integration Test")
    print("="*70)
    
    # Check dependencies
    if not check_dependencies():
        print("\n⚠️ Some dependencies missing - install them to continue")
        print("   Run: pip install -r requirements.txt")
        return 1
    
    # Test structure
    if not test_multi_agent_structure():
        print("\n❌ Structure verification failed")
        return 1
    
    # Test AWS configuration
    test_aws_configuration()
    
    # Show usage examples
    show_usage_example()
    
    print("\n" + "="*70)
    print("Next Steps:")
    print("="*70)
    print("""
1. Set up your .env file with required API keys
2. For local development:
   - Set USE_AWS_AGENTCORE=false
   - Agents will run locally

3. For AWS deployment:
   - Follow: docs/Miscellaneous/AWS_AGENTCORE_DEPLOYMENT.md
   - Set USE_AWS_AGENTCORE=true
   - Configure AWS credentials

4. Run the debate facilitator:
   python server_py/src/llmTutor/debate_room_facilitator.py

5. Test in the web application:
   - Set ENABLE_LLM_AGENT=true
   - Start server: python server_py/main.py
   - Agents will provide feedback in discussions

For full documentation, see:
- docs/Miscellaneous/MULTI_AGENT_ARCHITECTURE.md
- docs/Miscellaneous/AWS_AGENTCORE_DEPLOYMENT.md
""")
    
    print("="*70)
    print("\n✅ Integration test complete!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
