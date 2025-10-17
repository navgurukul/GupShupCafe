"""
Agents Service Entry Point
Allows running the agents service independently for testing and demonstration
Usage: python -m src.agents
"""

import asyncio
import sys
import os
from typing import List, Dict

from .english_feedback_agent import EnglishFeedbackAgent
from .debate_facilitator_agent import DebateFacilitatorAgent
from .aws_strands_orchestrator import AWSStrandsOrchestrator
from ..llm.ai_service_manager import AIServiceManager


async def demonstrate_english_feedback_agent():
    """Demonstrate English Feedback Agent functionality"""
    print("\n" + "="*60)
    print("📝 Demonstrating English Feedback Agent")
    print("="*60)
    
    # Initialize
    manager = AIServiceManager()
    llm = manager.get_llm()
    agent = EnglishFeedbackAgent(llm)
    
    # Test basic analysis
    print("\n🔍 Test 1: Basic English analysis")
    data = {
        "text": "I am going to the store yesterday and buy some milk.",
        "context": {"speaker": "student-1", "topic": "daily activities"}
    }
    result = await agent.analyze(data)
    
    print(f"\nText: {data['text']}")
    print(f"CEFR Level: {result['cefr_level']}")
    print(f"Grammar Score: {result.get('grammar_score', 'N/A')}")
    print(f"Vocabulary Score: {result.get('vocabulary_score', 'N/A')}")
    print(f"Fluency Score: {result.get('fluency_score', 'N/A')}")
    
    if result.get('suggestions'):
        print("\nSuggestions:")
        for i, suggestion in enumerate(result['suggestions'][:3], 1):
            print(f"  {i}. {suggestion}")
    
    # Test detailed analysis
    print("\n\n🔍 Test 2: Detailed component analysis")
    text = "The quick brown fox jumps over the lazy dog. This sentence contains every letter."
    
    grammar = await agent.analyze_grammar(text)
    vocabulary = await agent.analyze_vocabulary(text)
    fluency = await agent.analyze_fluency(text)
    
    print(f"\nText: {text}")
    print("\nGrammar Analysis:")
    print(f"  Score: {grammar['score']}")
    print(f"  Suggestions: {', '.join(grammar['suggestions'])}")
    
    print("\nVocabulary Analysis:")
    print(f"  Score: {vocabulary['score']:.2f}")
    print(f"  Word count: {vocabulary['word_count']}")
    print(f"  Unique words: {vocabulary['unique_words']}")
    
    print("\nFluency Analysis:")
    print(f"  Score: {fluency['score']}")
    print(f"  Sentence count: {fluency['sentence_count']}")
    
    # Test CEFR level determination
    print("\n\n🔍 Test 3: CEFR level determination")
    test_scores = [
        {"grammar": 0.95, "vocabulary": 0.92, "fluency": 0.93},  # C2
        {"grammar": 0.85, "vocabulary": 0.82, "fluency": 0.80},  # C1
        {"grammar": 0.75, "vocabulary": 0.72, "fluency": 0.70},  # B2
        {"grammar": 0.65, "vocabulary": 0.62, "fluency": 0.60},  # B1
        {"grammar": 0.55, "vocabulary": 0.52, "fluency": 0.50},  # A2
        {"grammar": 0.45, "vocabulary": 0.42, "fluency": 0.40},  # A1
    ]
    
    print("\nScore → CEFR Level mapping:")
    for scores in test_scores:
        level = agent.determine_cefr_level(scores)
        avg = sum(scores.values()) / len(scores)
        print(f"  Avg: {avg:.2f} → {level}")


async def demonstrate_debate_facilitator_agent():
    """Demonstrate Debate Facilitator Agent functionality"""
    print("\n" + "="*60)
    print("🎤 Demonstrating Debate Facilitator Agent")
    print("="*60)
    
    # Initialize
    manager = AIServiceManager()
    llm = manager.get_llm()
    agent = DebateFacilitatorAgent(llm)
    
    # Test facilitate turn
    print("\n🔍 Test 1: Facilitate speaking turn")
    context = {
        "topic": "The Impact of Social Media on Society",
        "current_speaker": {"name": "Alice", "id": "speaker-1"},
        "turn_number": 1
    }
    prompt = await agent.facilitate_turn(context)
    print(f"\nTopic: {context['topic']}")
    print(f"Speaker: {context['current_speaker']['name']}")
    print(f"Turn: {context['turn_number']}")
    print(f"Prompt: {prompt}")
    
    # Test topic direction suggestion
    print("\n\n🔍 Test 2: Suggest topic direction")
    statements = [
        "Social media has changed how we communicate.",
        "It allows us to connect with people worldwide.",
        "However, it can also be addictive."
    ]
    suggestion = await agent.suggest_topic_direction(statements)
    print("\nRecent statements:")
    for i, stmt in enumerate(statements, 1):
        print(f"  {i}. {stmt}")
    print(f"\nFacilitation suggestion: {suggestion}")
    
    # Test moderation
    print("\n\n🔍 Test 3: Moderate discussion")
    context = {
        "topic": "Climate Change",
        "participants": [
            {"name": "Bob", "speaking_time": 120},
            {"name": "Carol", "speaking_time": 90}
        ]
    }
    moderation = await agent.moderate_discussion(context)
    print(f"\nNeeds intervention: {moderation['needs_intervention']}")
    print(f"Message: {moderation['message']}")
    
    # Test speaking prompt generation
    print("\n\n🔍 Test 4: Generate speaking prompt")
    topics = [
        "Artificial Intelligence in Education",
        "Renewable Energy Solutions",
        "The Future of Work"
    ]
    print("\nGenerating prompts for various topics:")
    for topic in topics:
        prompt = await agent.generate_speaking_prompt(topic)
        print(f"\n  Topic: {topic}")
        print(f"  Prompt: {prompt}")


async def demonstrate_orchestrator():
    """Demonstrate AWS Strands Orchestrator functionality"""
    print("\n" + "="*60)
    print("🎭 Demonstrating AWS Strands Orchestrator")
    print("="*60)
    
    # Initialize
    manager = AIServiceManager()
    orchestrator = AWSStrandsOrchestrator(manager)
    
    # Test instant feedback
    print("\n🔍 Test 1: Instant English feedback")
    statements = [
        "I think technology is important for education.",
        "It helps students to learn more efficiently."
    ]
    
    instant_feedback = await orchestrator.get_english_feedback(
        statements=statements,
        instant=True,
        context={"speaker": "student-1", "topic": "technology"}
    )
    
    print(f"\nStatements analyzed:")
    for i, stmt in enumerate(statements, 1):
        print(f"  {i}. {stmt}")
    
    print(f"\nFeedback Type: {instant_feedback['type']}")
    print(f"CEFR Level: {instant_feedback['cefr_level']}")
    print(f"\nScores:")
    print(f"  Grammar: {instant_feedback['scores']['grammar']:.2f}")
    print(f"  Vocabulary: {instant_feedback['scores']['vocabulary']:.2f}")
    print(f"  Fluency: {instant_feedback['scores']['fluency']:.2f}")
    print(f"\nMessage:\n{instant_feedback['message']}")
    
    # Test comprehensive feedback
    print("\n\n🔍 Test 2: Comprehensive English feedback")
    statements = [
        "Climate change is one of the biggest challenges we face.",
        "We need to reduce carbon emissions and protect the environment.",
        "Individual actions matter, but we also need systemic change."
    ]
    
    comprehensive_feedback = await orchestrator.get_english_feedback(
        statements=statements,
        instant=False,
        context={"speaker": "student-2", "topic": "environment"}
    )
    
    print(f"\nStatements analyzed:")
    for i, stmt in enumerate(statements, 1):
        print(f"  {i}. {stmt}")
    
    print(f"\nFeedback Type: {comprehensive_feedback['type']}")
    print(f"\nAnalysis:")
    analysis = comprehensive_feedback['analysis']
    print(f"  CEFR Level: {analysis.get('cefr_level', 'N/A')}")
    print(f"  Grammar Score: {analysis.get('grammar_score', 'N/A')}")
    print(f"  Vocabulary Score: {analysis.get('vocabulary_score', 'N/A')}")
    print(f"  Fluency Score: {analysis.get('fluency_score', 'N/A')}")
    
    print(f"\nFacilitation Suggestion:")
    print(f"  {comprehensive_feedback['facilitation_suggestion']}")
    
    print(f"\nTimestamp: {comprehensive_feedback['timestamp']}")
    
    # Test message formatting
    print("\n\n🔍 Test 3: Message formatting")
    test_results = [
        {"cefr_level": "C2", "suggestions": ["Excellent work!", "Keep it up!"]},
        {"cefr_level": "B1", "suggestions": ["Try more complex sentences", "Expand vocabulary"]},
        {"cefr_level": "A1", "suggestions": ["Focus on basic grammar", "Practice more"]}
    ]
    
    print("\nFormatted feedback messages:")
    for result in test_results:
        message = orchestrator._format_feedback_message(result)
        print(f"\n  Level: {result['cefr_level']}")
        print(f"  Message: {message.replace(chr(10), chr(10) + '           ')}")


async def interactive_mode():
    """Run interactive mode for testing agents"""
    print("\n" + "="*60)
    print("💬 Interactive Agents Testing Mode")
    print("="*60)
    print("Commands:")
    print("  'analyze <text>' - Get English analysis")
    print("  'feedback <text>' - Get instant feedback")
    print("  'comprehensive <text>' - Get comprehensive feedback")
    print("  'facilitate <topic>' - Get facilitation prompt")
    print("  'quit' or 'exit' - Exit interactive mode")
    print("="*60 + "\n")
    
    manager = AIServiceManager()
    orchestrator = AWSStrandsOrchestrator(manager)
    
    while True:
        try:
            user_input = input("Command: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower().startswith('analyze '):
                text = user_input[8:].strip()
                if not text:
                    print("⚠️  Please provide text to analyze\n")
                    continue
                
                agent = EnglishFeedbackAgent(manager.get_llm())
                result = await agent.analyze({"text": text, "context": {}})
                
                print(f"\n📊 Analysis:")
                print(f"   CEFR Level: {result['cefr_level']}")
                print(f"   Grammar: {result.get('grammar_score', 'N/A')}")
                print(f"   Vocabulary: {result.get('vocabulary_score', 'N/A')}")
                print(f"   Fluency: {result.get('fluency_score', 'N/A')}\n")
                continue
            
            if user_input.lower().startswith('feedback '):
                text = user_input[9:].strip()
                if not text:
                    print("⚠️  Please provide text\n")
                    continue
                
                result = await orchestrator.get_english_feedback(
                    statements=[text],
                    instant=True
                )
                
                print(f"\n💬 Instant Feedback:")
                print(f"   {result['message']}\n")
                continue
            
            if user_input.lower().startswith('comprehensive '):
                text = user_input[14:].strip()
                if not text:
                    print("⚠️  Please provide text\n")
                    continue
                
                result = await orchestrator.get_english_feedback(
                    statements=[text],
                    instant=False
                )
                
                print(f"\n📊 Comprehensive Analysis:")
                print(f"   {result['message']}")
                print(f"\n   Facilitation: {result['facilitation_suggestion']}\n")
                continue
            
            if user_input.lower().startswith('facilitate '):
                topic = user_input[11:].strip()
                if not topic:
                    print("⚠️  Please provide a topic\n")
                    continue
                
                agent = DebateFacilitatorAgent(manager.get_llm())
                prompt = await agent.generate_speaking_prompt(topic)
                
                print(f"\n🎤 Speaking Prompt:")
                print(f"   {prompt}\n")
                continue
            
            print("⚠️  Unknown command. Type 'quit' to exit or use one of the available commands.\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")


async def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🚀 Agents Service - Independent Execution")
    print("="*60)
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == 'english':
            await demonstrate_english_feedback_agent()
        elif mode == 'facilitator':
            await demonstrate_debate_facilitator_agent()
        elif mode == 'orchestrator':
            await demonstrate_orchestrator()
        elif mode == 'interactive':
            await interactive_mode()
        else:
            print(f"\n❌ Unknown mode: {mode}")
            print("\nAvailable modes:")
            print("  english      - Demonstrate English Feedback Agent")
            print("  facilitator  - Demonstrate Debate Facilitator Agent")
            print("  orchestrator - Demonstrate AWS Strands Orchestrator")
            print("  interactive  - Interactive testing mode")
            print("\nUsage: python -m src.agents [mode]")
            sys.exit(1)
    else:
        # Default: run all demonstrations
        print("\n💡 Running all demonstrations (use 'python -m src.agents interactive' for interactive mode)")
        
        await demonstrate_english_feedback_agent()
        await demonstrate_debate_facilitator_agent()
        await demonstrate_orchestrator()
        
        print("\n" + "="*60)
        print("✅ All demonstrations completed!")
        print("="*60)
        print("\nTip: Run 'python -m src.agents interactive' for interactive testing")
        print("     or 'python -m src.agents [english|facilitator|orchestrator]' for specific demos")


if __name__ == "__main__":
    asyncio.run(main())
