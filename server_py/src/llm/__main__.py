"""
LLM Service Entry Point
Allows running the LLM service independently for testing and demonstration
Usage: python -m src.llm
"""

import asyncio
import sys
import os
from typing import List, Dict
from dotenv import load_dotenv

from .ai_service_manager import AIServiceManager
from .gemini_llm import GeminiLLM
from .bedrock_llm import BedrockLLM

load_dotenv(".env")  # Load environment variables from .env file


async def demonstrate_gemini():
    """Demonstrate Gemini LLM functionality"""
    print("\n" + "="*60)
    print("🤖 Demonstrating Gemini LLM")
    print("="*60)
    
    llm = GeminiLLM(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Test chat
    print("\n📝 Testing chat functionality...")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"}
    ]
    response = await llm.chat(messages, temperature=0.7, max_tokens=100)
    print(f"Response: {response['content']}")
    print(f"Model: {response['model']}")
    
    # Test English analysis
    print("\n📊 Testing English analysis...")
    transcript = "I like to coding in Python because it is very easy to learn and use."
    analysis = await llm.analyze_english(transcript)
    print(f"Text: {transcript}")
    print(f"CEFR Level: {analysis['cefr_level']}")
    print(f"Grammar Score: {analysis['grammar_score']}")
    print(f"Vocabulary Score: {analysis['vocabulary_score']}")
    print(f"Fluency Score: {analysis['fluency_score']}")
    print(f"Suggestions: {', '.join(analysis['suggestions'])}")


async def demonstrate_bedrock():
    """Demonstrate Bedrock LLM functionality"""
    print("\n" + "="*60)
    print("☁️  Demonstrating AWS Bedrock LLM")
    print("="*60)
    
    llm = BedrockLLM(
        model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-v2"),
        region=os.getenv("AWS_REGION", "us-east-1")
    )
    
    # Test chat
    print("\n📝 Testing chat functionality...")
    messages = [
        {"role": "user", "content": "Explain machine learning in simple terms."}
    ]
    response = await llm.chat(messages, temperature=0.8)
    print(f"Response: {response['content']}")
    print(f"Model: {response['model']}")
    
    # Test English analysis
    print("\n📊 Testing English analysis...")
    transcript = "The artificial intelligence is revolutionizing how we work and live."
    analysis = await llm.analyze_english(transcript)
    print(f"Text: {transcript}")
    print(f"CEFR Level: {analysis['cefr_level']}")
    print(f"Grammar Score: {analysis['grammar_score']}")
    print(f"Vocabulary Score: {analysis['vocabulary_score']}")
    print(f"Fluency Score: {analysis['fluency_score']}")
    print(f"Suggestions: {', '.join(analysis['suggestions'])}")


async def demonstrate_service_manager():
    """Demonstrate AI Service Manager functionality"""
    print("\n" + "="*60)
    print("🎯 Demonstrating AI Service Manager")
    print("="*60)
    
    # Initialize with default provider
    manager = AIServiceManager()
    print(f"\n✓ Initialized with default provider: {manager.get_current_provider()}")
    
    # Use the default LLM
    llm = manager.get_llm()
    messages = [{"role": "user", "content": "Hello, what can you do?"}]
    response = await llm.chat(messages)
    print(f"\n✓ Response from {manager.get_current_provider()}: {response['content'][:100]}...")
    
    # Switch provider
    print("\n🔄 Switching to bedrock provider...")
    manager.switch_provider("bedrock")
    print(f"✓ Current provider: {manager.get_current_provider()}")
    
    # Test new provider
    llm = manager.get_llm()
    response = await llm.chat(messages)
    print(f"✓ Response from {manager.get_current_provider()}: {response['content'][:100]}...")
    
    # Test English analysis with current provider
    print("\n📊 Testing English analysis with current provider...")
    analysis = await llm.analyze_english("This is a test sentence for analysis.")
    print(f"✓ CEFR Level: {analysis['cefr_level']}")
    print(f"✓ Scores - Grammar: {analysis['grammar_score']}, Vocabulary: {analysis['vocabulary_score']}, Fluency: {analysis['fluency_score']}")


async def interactive_mode():
    """Run interactive mode for testing LLM"""
    print("\n" + "="*60)
    print("💬 Interactive LLM Testing Mode")
    print("="*60)
    print("Commands:")
    print("  'gemini' - Switch to Gemini provider")
    print("  'bedrock' - Switch to Bedrock provider")
    print("  'analyze <text>' - Analyze English text")
    print("  'quit' or 'exit' - Exit interactive mode")
    print("  Or just type a message to chat")
    print("="*60 + "\n")
    
    manager = AIServiceManager()
    print(f"Current provider: {manager.get_current_provider()}\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'gemini':
                manager.switch_provider("gemini")
                print(f"✓ Switched to Gemini\n")
                continue
            
            if user_input.lower() == 'bedrock':
                manager.switch_provider("bedrock")
                print(f"✓ Switched to Bedrock\n")
                continue
            
            if user_input.lower().startswith('analyze '):
                text = user_input[8:].strip()
                if not text:
                    print("⚠️  Please provide text to analyze\n")
                    continue
                
                llm = manager.get_llm()
                analysis = await llm.analyze_english(text)
                print(f"\n📊 Analysis Results:")
                print(f"   CEFR Level: {analysis['cefr_level']}")
                print(f"   Grammar: {analysis['grammar_score']:.2f}")
                print(f"   Vocabulary: {analysis['vocabulary_score']:.2f}")
                print(f"   Fluency: {analysis['fluency_score']:.2f}")
                print(f"   Suggestions:")
                for suggestion in analysis['suggestions']:
                    print(f"     • {suggestion}")
                print()
                continue
            
            # Regular chat
            llm = manager.get_llm()
            messages = [{"role": "user", "content": user_input}]
            response = await llm.chat(messages)
            print(f"Assistant: {response['content']}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")


async def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🚀 LLM Service - Independent Execution")
    print("="*60)
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == 'gemini':
            await demonstrate_gemini()
        elif mode == 'bedrock':
            await demonstrate_bedrock()
        elif mode == 'manager':
            await demonstrate_service_manager()
        elif mode == 'interactive':
            await interactive_mode()
        else:
            print(f"\n❌ Unknown mode: {mode}")
            print("\nAvailable modes:")
            print("  gemini      - Demonstrate Gemini LLM")
            print("  bedrock     - Demonstrate Bedrock LLM")
            print("  manager     - Demonstrate AI Service Manager")
            print("  interactive - Interactive testing mode")
            print("\nUsage: python -m src.llm [mode]")
            sys.exit(1)
    else:
        # Default: run all demonstrations
        print("\n💡 Running all demonstrations (use 'python -m src.llm interactive' for interactive mode)")
        
        await demonstrate_service_manager()
        await demonstrate_gemini()
        await demonstrate_bedrock()
        
        print("\n" + "="*60)
        print("✅ All demonstrations completed!")
        print("="*60)
        print("\nTip: Run 'python -m src.llm interactive' for interactive testing")
        print("     or 'python -m src.llm [gemini|bedrock|manager]' for specific demos")


if __name__ == "__main__":
    asyncio.run(main())
