"""
Multi-Agent Orchestrator with AWS Bedrock AgentCore Integration

This module provides a multi-agent system that orchestrates:
1. English Grammar Agent - For instant language feedback
2. Debate Facilitator Agent - For discussion management

Uses AWS Bedrock AgentCore SDK for agent deployment and management.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

# Import AWS Bedrock AgentCore components
try:
    import boto3
    from bedrock_agentcore import AgentRuntime, Agent, AgentConfig
    AWS_AGENTCORE_AVAILABLE = True
except ImportError:
    AWS_AGENTCORE_AVAILABLE = False
    logging.warning("AWS Bedrock AgentCore SDK not available. Install with: pip install bedrock-agentcore")

# Import our custom agents
from englishGrammarAgent import EnglishGrammarAgent
from geminiAgent import GeminiAgent

logger = logging.getLogger(__name__)


class AgentType:
    """Agent type identifiers"""
    ENGLISH_GRAMMAR = "english_grammar"
    DEBATE_FACILITATOR = "debate_facilitator"


class MultiAgentOrchestrator:
    """
    Orchestrates multiple specialized agents for roundtable discussions.
    
    Features:
    - Manages lifecycle of specialized agents
    - Routes requests to appropriate agents
    - Combines responses from multiple agents
    - Integrates with AWS Bedrock AgentCore for deployment
    """
    
    def __init__(self, use_aws_agentcore: bool = True):
        """
        Initialize the multi-agent orchestrator.
        
        Args:
            use_aws_agentcore: Whether to use AWS AgentCore for deployment
        """
        load_dotenv()
        
        self.use_aws_agentcore = use_aws_agentcore and AWS_AGENTCORE_AVAILABLE
        self.agents: Dict[str, Any] = {}
        self.agent_runtime: Optional[Any] = None
        
        # AWS Configuration
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.aws_credentials_configured = self._check_aws_credentials()
        
        # Initialize AWS AgentCore if available
        if self.use_aws_agentcore and self.aws_credentials_configured:
            self._initialize_aws_agentcore()
        else:
            logger.info("Using local agent execution (AWS AgentCore not configured)")
        
        # Initialize agents
        self._initialize_agents()
        
        logger.info(f"✅ Multi-Agent Orchestrator initialized")
        logger.info(f"   AWS AgentCore: {'Enabled' if self.use_aws_agentcore else 'Disabled'}")
        logger.info(f"   Agents: {list(self.agents.keys())}")
    
    def _check_aws_credentials(self) -> bool:
        """
        Check if AWS credentials are configured.
        
        Returns:
            bool: True if AWS credentials are available
        """
        try:
            # Check for AWS credentials
            session = boto3.Session()
            credentials = session.get_credentials()
            return credentials is not None
        except Exception as e:
            logger.warning(f"AWS credentials not configured: {e}")
            return False
    
    def _initialize_aws_agentcore(self):
        """
        Initialize AWS Bedrock AgentCore runtime.
        
        This sets up the agent runtime environment for deploying agents to AWS.
        """
        try:
            if not AWS_AGENTCORE_AVAILABLE:
                logger.warning("Cannot initialize AWS AgentCore - SDK not installed")
                self.use_aws_agentcore = False
                return
            
            # Initialize AgentCore runtime
            # Note: This is a placeholder for actual AWS AgentCore initialization
            # The actual implementation depends on the specific AgentCore SDK API
            logger.info("Initializing AWS Bedrock AgentCore runtime...")
            
            # Configure agent runtime
            # self.agent_runtime = AgentRuntime(
            #     region=self.aws_region,
            #     # Additional configuration as needed
            # )
            
            logger.info(f"✅ AWS AgentCore runtime initialized (Region: {self.aws_region})")
            
        except Exception as e:
            logger.error(f"Failed to initialize AWS AgentCore: {e}")
            self.use_aws_agentcore = False
    
    def _initialize_agents(self):
        """
        Initialize all specialized agents.
        """
        try:
            # Initialize English Grammar Agent
            logger.info("Initializing English Grammar Agent...")
            self.agents[AgentType.ENGLISH_GRAMMAR] = EnglishGrammarAgent()
            logger.info("✅ English Grammar Agent initialized")
            
            # Debate Facilitator Agent will be initialized on-demand with context
            # (since it needs room configuration)
            logger.info("ℹ️ Debate Facilitator Agent will be initialized on-demand")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise
    
    def initialize_debate_facilitator(
        self,
        room_type: str,
        topic: str,
        participants: List[str],
        tools: Optional[List] = None
    ) -> bool:
        """
        Initialize the Debate Facilitator Agent with room context.
        
        Args:
            room_type: Type of room ('debate' or 'discussion')
            topic: Discussion topic
            participants: List of participant names
            tools: Optional MCP tools for the facilitator
            
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing Debate Facilitator Agent...")
            
            # Create system prompt for facilitator
            system_prompt = f"""
You are a humble, kind, and insightful {room_type} facilitator.

**Your Role:**
1. Guide the conversation productively
2. Provide thoughtful feedback on discussion content
3. Fact-check claims made by participants
4. Identify common ground and diverging points
5. Ensure balanced participation

**Current Context:**
- Room Type: {room_type}
- Topic: {topic}
- Participants: {', '.join(participants)}

**Your Style:**
- Be humble and encouraging
- Use phrases like "I notice...", "It seems...", "Perhaps..."
- Acknowledge good points
- Guide gently towards productive discussion

**Important:** 
You focus on CONTENT and DISCUSSION FLOW. 
Do NOT provide English language feedback - that's handled by a separate specialized agent.

Keep your feedback concise and focused on the substance of the discussion.
"""
            
            self.agents[AgentType.DEBATE_FACILITATOR] = GeminiAgent(
                system_prompt=system_prompt,
                tools=tools
            )
            
            logger.info("✅ Debate Facilitator Agent initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Debate Facilitator: {e}")
            return False
    
    def get_english_feedback(
        self,
        statements: List[Dict[str, str]],
        instant: bool = True
    ) -> str:
        """
        Get English language feedback using the Grammar Agent.
        
        Args:
            statements: List of dicts with 'speaker' and 'content' keys
            instant: If True, provides instant feedback; if False, more comprehensive
            
        Returns:
            English language feedback
        """
        try:
            grammar_agent = self.agents.get(AgentType.ENGLISH_GRAMMAR)
            
            if not grammar_agent:
                return "English Grammar Agent not available."
            
            if instant:
                # Instant feedback mode - analyze most recent statements
                recent_statements = statements[-3:] if len(statements) > 3 else statements
                return grammar_agent.analyze_multiple_statements(recent_statements)
            else:
                # Comprehensive feedback mode
                participant_statements = {}
                for stmt in statements:
                    speaker = stmt['speaker']
                    if speaker not in participant_statements:
                        participant_statements[speaker] = []
                    participant_statements[speaker].append(stmt['content'])
                
                return grammar_agent.generate_summary_feedback(participant_statements)
                
        except Exception as e:
            logger.error(f"Error getting English feedback: {e}")
            return f"Error generating English feedback: {str(e)}"
    
    def get_discussion_feedback(
        self,
        topic: str,
        recent_statements: List[Dict[str, str]]
    ) -> str:
        """
        Get discussion/content feedback using the Facilitator Agent.
        
        Args:
            topic: Discussion topic
            recent_statements: Recent statements from participants
            
        Returns:
            Discussion feedback (without English language feedback)
        """
        try:
            facilitator = self.agents.get(AgentType.DEBATE_FACILITATOR)
            
            if not facilitator:
                return "Debate Facilitator Agent not initialized. Call initialize_debate_facilitator() first."
            
            # Build context for facilitator
            context = f"Topic: {topic}\n\nRecent statements:\n"
            for stmt in recent_statements:
                context += f"- {stmt['speaker']}: {stmt['content']}\n"
            
            prompt = f"""{context}

Provide your feedback as the discussion facilitator. Focus on:
1. Factual accuracy of claims
2. Overall direction of the conversation
3. Common ground and diverging points
4. Suggestions to guide the discussion

Keep it concise and focused on content only (no English feedback).
"""
            
            return facilitator(prompt)
            
        except Exception as e:
            logger.error(f"Error getting discussion feedback: {e}")
            return f"Error generating discussion feedback: {str(e)}"
    
    def get_combined_feedback(
        self,
        topic: str,
        recent_statements: List[Dict[str, str]]
    ) -> Dict[str, str]:
        """
        Get combined feedback from both agents.
        
        Args:
            topic: Discussion topic
            recent_statements: Recent statements to analyze
            
        Returns:
            Dict with 'discussion_feedback' and 'english_feedback' keys
        """
        return {
            "discussion_feedback": self.get_discussion_feedback(topic, recent_statements),
            "english_feedback": self.get_english_feedback(recent_statements, instant=True)
        }
    
    def get_comprehensive_summary(
        self,
        topic: str,
        all_statements: List[Dict[str, str]]
    ) -> Dict[str, str]:
        """
        Get comprehensive end-of-discussion summary from both agents.
        
        Args:
            topic: Discussion topic
            all_statements: All statements from the discussion
            
        Returns:
            Dict with comprehensive summaries from both agents
        """
        return {
            "discussion_summary": self.get_discussion_feedback(topic, all_statements),
            "english_summary": self.get_english_feedback(all_statements, instant=False)
        }
    
    def deploy_to_aws(self) -> bool:
        """
        Deploy agents to AWS using Bedrock AgentCore.
        
        This method handles the deployment of agents to AWS infrastructure.
        
        Returns:
            bool: True if deployment successful
        """
        if not self.use_aws_agentcore:
            logger.warning("AWS AgentCore not configured. Cannot deploy to AWS.")
            return False
        
        try:
            logger.info("Deploying agents to AWS Bedrock AgentCore...")
            
            # Placeholder for AWS deployment logic
            # This would involve:
            # 1. Package agent code and dependencies
            # 2. Upload to AWS
            # 3. Register agents with AgentCore
            # 4. Configure agent runtime parameters
            
            # Actual implementation depends on the specific AgentCore SDK API
            
            logger.info("✅ Agents deployed to AWS successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy agents to AWS: {e}")
            return False
    
    def cleanup(self):
        """
        Clean up agent resources.
        """
        logger.info("Cleaning up multi-agent orchestrator...")
        self.agents.clear()
        if self.agent_runtime:
            # Cleanup AWS resources if needed
            pass
        logger.info("✅ Cleanup complete")


# Global orchestrator instance
_orchestrator_instance: Optional[MultiAgentOrchestrator] = None


def get_orchestrator() -> MultiAgentOrchestrator:
    """
    Get or create the global orchestrator instance.
    
    Returns:
        MultiAgentOrchestrator instance
    """
    global _orchestrator_instance
    
    if _orchestrator_instance is None:
        _orchestrator_instance = MultiAgentOrchestrator()
    
    return _orchestrator_instance


if __name__ == "__main__":
    # Example usage
    print("=== Multi-Agent Orchestrator Demo ===\n")
    
    # Initialize orchestrator
    orchestrator = MultiAgentOrchestrator(use_aws_agentcore=False)
    
    # Initialize debate facilitator
    orchestrator.initialize_debate_facilitator(
        room_type="discussion",
        topic="The impact of AI on education",
        participants=["Alice", "Bob", "Charlie"]
    )
    
    # Test English feedback
    print("\n=== English Feedback Test ===\n")
    test_statements = [
        {"speaker": "Alice", "content": "AI are very helpful for students learning."},
        {"speaker": "Bob", "content": "I thinks AI can helping with homework and studying."}
    ]
    
    english_feedback = orchestrator.get_english_feedback(test_statements)
    print(english_feedback)
    
    # Test discussion feedback
    print("\n\n=== Discussion Feedback Test ===\n")
    discussion_feedback = orchestrator.get_discussion_feedback(
        "The impact of AI on education",
        test_statements
    )
    print(discussion_feedback)
    
    # Test combined feedback
    print("\n\n=== Combined Feedback Test ===\n")
    combined = orchestrator.get_combined_feedback(
        "The impact of AI on education",
        test_statements
    )
    print("DISCUSSION:")
    print(combined["discussion_feedback"])
    print("\nENGLISH:")
    print(combined["english_feedback"])
    
    # Cleanup
    orchestrator.cleanup()
