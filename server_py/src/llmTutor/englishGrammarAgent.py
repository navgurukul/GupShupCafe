"""
English Grammar Agent

Specialized agent for providing instant feedback on English language usage:
- Grammar corrections (tenses, subject-verb agreement, articles, prepositions)
- Sentence structure and framing
- Vocabulary usage and word choice
- Clarity and coherence of expression
"""

import os
from strands import Agent
from strands_agents.src.strands.models.gemini import GeminiModel
from dotenv import load_dotenv
from typing import Dict, List, Optional


class EnglishGrammarAgent(Agent):
    """
    Specialized agent for English language feedback and correction.
    
    This agent focuses exclusively on:
    - Analyzing English language usage
    - Providing constructive grammar corrections
    - Suggesting improvements for clarity and fluency
    - Offering vocabulary enhancements
    """
    
    def __init__(self, tools=None):
        """
        Initialize the English Grammar Agent.
        
        Args:
            tools: Optional list of tools for the agent to use
        """
        load_dotenv()
        _api_key = os.getenv("GEMINI_API_KEY")
        
        if not _api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        
        # Initialize Gemini Model with parameters optimized for language feedback
        self.gemini_model = GeminiModel(
            model_id="gemini-2.5-flash",
            params={
                "temperature": 0.3,  # Lower temperature for more consistent corrections
            }
        )
        
        # Define the system prompt for English grammar expertise
        system_prompt = """
You are an expert English language instructor specializing in real-time feedback for English learners.

Your expertise includes:
1. **Grammar Correction**: Identifying and correcting errors in:
   - Verb tenses (present, past, future, perfect, continuous)
   - Subject-verb agreement
   - Articles (a, an, the)
   - Prepositions (in, on, at, for, to, etc.)
   - Pronouns and pronoun reference
   - Singular/plural forms

2. **Sentence Structure**: Analyzing and improving:
   - Sentence construction and word order
   - Run-on sentences and fragments
   - Complex sentence formation
   - Transitions between ideas

3. **Vocabulary Enhancement**: Suggesting:
   - More precise word choices
   - Context-appropriate vocabulary
   - Synonyms for variety
   - Idiomatic expressions

4. **Clarity & Fluency**: Evaluating:
   - Overall coherence of expression
   - Natural flow of language
   - Clarity of intended meaning

**Your Feedback Style:**
- Be constructive and encouraging
- Explain WHY a correction is needed (not just WHAT is wrong)
- Provide examples of correct usage
- Acknowledge what the speaker did well
- Keep feedback concise and actionable
- Use simple language to explain corrections

**Feedback Format:**
For each speaker, structure your feedback as:

**[Speaker Name]:**
✓ **Strengths**: [What they did well]
✗ **Grammar**: [Specific grammar issues with corrections]
📝 **Sentence Structure**: [Improvements for clarity]
💡 **Vocabulary**: [Better word choices]
✨ **Suggestion**: [How to say it better]

Always be kind, patient, and encouraging. Remember: the goal is to help learners improve, not to discourage them.
"""
        
        # Initialize the agent with the specialized prompt
        super().__init__(
            model=self.gemini_model,
            tools=tools,
            system_prompt=system_prompt
        )
    
    def analyze_statement(self, speaker_name: str, statement: str) -> str:
        """
        Analyze a single statement for English language feedback.
        
        Args:
            speaker_name: Name of the speaker
            statement: The statement to analyze
            
        Returns:
            Detailed English language feedback
        """
        prompt = f"""
Analyze the following statement from {speaker_name} and provide specific English language feedback:

**Statement:** "{statement}"

Provide constructive feedback on:
1. Grammar accuracy
2. Sentence structure
3. Vocabulary usage
4. Overall clarity

Remember to be encouraging and explain corrections clearly.
"""
        return self(prompt)
    
    def analyze_multiple_statements(self, statements: List[Dict[str, str]]) -> str:
        """
        Analyze multiple statements from different speakers.
        
        Args:
            statements: List of dicts with 'speaker' and 'content' keys
            
        Returns:
            Consolidated English language feedback for all speakers
        """
        if not statements:
            return "No statements to analyze."
        
        # Build prompt with all statements
        prompt = "Analyze the following statements and provide English language feedback for each speaker:\n\n"
        
        for i, stmt in enumerate(statements, 1):
            prompt += f"{i}. **{stmt['speaker']}**: \"{stmt['content']}\"\n"
        
        prompt += """
\nFor EACH speaker, provide:
- Grammar corrections with explanations
- Sentence structure improvements
- Vocabulary suggestions
- An encouraging rewrite of their statement

Use the feedback format specified in your system prompt.
"""
        
        return self(prompt)
    
    def generate_summary_feedback(self, participant_statements: Dict[str, List[str]]) -> str:
        """
        Generate comprehensive English learning summary for each participant.
        
        Args:
            participant_statements: Dict mapping participant names to their statements
            
        Returns:
            Comprehensive English learning summary
        """
        if not participant_statements:
            return "No statements available for summary."
        
        prompt = "Generate a comprehensive English learning summary for each participant based on their contributions:\n\n"
        
        for participant, statements in participant_statements.items():
            prompt += f"**{participant}'s statements:**\n"
            for i, stmt in enumerate(statements, 1):
                prompt += f"  {i}. {stmt}\n"
            prompt += "\n"
        
        prompt += """
For each participant, provide:

1. **Overall English Proficiency**: Brief assessment of their current level
2. **Strengths**: What they consistently do well
3. **Common Patterns**: Recurring errors or issues
4. **Key Improvements Needed**: Top 2-3 areas to focus on
5. **Progress Observed**: Any improvements during the discussion
6. **Actionable Tips**: Specific practice suggestions

Be thorough, encouraging, and provide concrete examples from their statements.
"""
        
        return self(prompt)


if __name__ == "__main__":
    # Example usage
    agent = EnglishGrammarAgent()
    
    # Test with a single statement
    print("=== Single Statement Analysis ===\n")
    feedback = agent.analyze_statement(
        "Alice",
        "I am going to store yesterday and I buyed some books about grammer."
    )
    print(feedback)
    
    # Test with multiple statements
    print("\n\n=== Multiple Statements Analysis ===\n")
    statements = [
        {"speaker": "Bob", "content": "He don't like to reading books, but I likes them very much."},
        {"speaker": "Charlie", "content": "If I would have more time, I will study English everyday."}
    ]
    feedback = agent.analyze_multiple_statements(statements)
    print(feedback)
