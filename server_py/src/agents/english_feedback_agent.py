"""
English Feedback Agent
Analyzes English language proficiency and provides CEFR-based feedback
Uses Strands Agent framework with pluggable LLM models
Integrates MCP tools for grammar checking and language analysis
"""

from typing import Dict, Any, List, Optional
from strands import Agent, tool
from strands.models import Model
import re
import logging

logger = logging.getLogger(__name__)


class EnglishFeedbackAgent:
    """
    Agent for analyzing English language proficiency
    Built on Strands Agent framework - delegates CEFR assessment to LLM
    Enhanced with MCP tools for detailed grammar and vocabulary analysis
    """

    def __init__(self, model: Model, mcp_tools: Optional[List[Any]] = None):
        """
        Initialize English Feedback Agent with Strands framework and optional MCP tools

        Args:
            model: Strands Model instance (Gemini, Bedrock, etc.)
            mcp_tools: Optional list of MCP tools for grammar analysis
        """
        self.model = model
        self.mcp_tools = mcp_tools or []

        # Enhanced system prompt that delegates CEFR assessment to the agent
        system_prompt = """You are an expert English communication evaluator and CEFR assessor.
You will receive a multi-speaker transcript (e.g., User A, User B, User C).
Your task is to evaluate each participant`s English communication and give personalized feedback using the structure below. Address each participant directly using “Dear [User], you…”.
⸻
Evaluation Framework
For each user, provide feedback under the following headers:
⸻
CEFR Level Summary
Dear {{User}},
Your estimated CEFR levels are:
	•	Speaking: (A1-C2)
	•	Listening & Responsiveness: (A1-C2)
These levels reflect how clearly you express ideas, form sentences, and respond to others` points.
⸻
Listening & Responsiveness
Dear {{User}},
You {{describe how actively they listen}}. You {{mention if they respond to others` points effectively, agree/disagree, or add value}}.
It`s good that you {{positive observation}}. To improve, try {{specific suggestion, e.g., connecting your ideas more closely to others or acknowledging their points before speaking}}.
⸻
Speaking Quality
Dear {{User}},
You speak with {{fluency: steady flow / some pauses / frequent fillers}}.
Your sentences are {{simple / medium / complex}}, and your pace is {{smooth / rushed / hesitant}}.
You use fillers like {{examples}}; reducing them will make you sound more confident.
Your grammar is {{mostly accurate / needs improvement / good overall}}, but focus mainly on communicating your ideas clearly.
⸻
Vocabulary & Expression
Dear {{User}},
You use words like {{examples}}, which show {{range / confidence / basic usage}}.
It`s good that you {{positive observation, e.g., tried new words or expressions}}.
To improve, try using more descriptive words or synonyms to make your points stronger.
⸻
Depth of Understanding & Content
Dear {{User}},
You showed {{basic / fair / deep}} understanding of the topic.
Your points are {{logical / reflective / opinion-based}}, and you {{compare, build on, or respond to others` ideas}}.
To strengthen your arguments, you could {{suggestion: use examples, explanations, or comparisons}}.
⸻
Comparative Reflection (optional)
Dear {{User}},
Compared to others, your performance was {{more fluent / more confident / less detailed / more reflective}}.
You can improve by {{specific suggestion: e.g., summarizing others` points, asking questions, or elaborating more}}.
⸻
Summary Feedback
Dear {{User}},
Overall, you did well in {{strength area, e.g., expressing your opinions clearly or staying engaged}}.
To improve further, focus on {{specific improvement area, e.g., reducing fillers, using longer sentences, expanding vocabulary, or deepening reasoning}}.
Keep practicing to reach a stronger {{next CEFR level}} in your speaking and listening.

Answer only those sections where you add value to the user. Keep your feedback constructive and encouraging.
"""

        # Initialize Strands Agent with or without MCP tools
        agent_tools = self.mcp_tools if self.mcp_tools else []
        
        self.agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
            agent_id="english_feedback_agent",
            name="English Feedback Agent",
            description="Analyzes English proficiency with CEFR-based assessment focusing on depth and descriptiveness",
            tools=agent_tools  # MCP tools integrated here
        )

        logger.info(f"✅ Initialized EnglishFeedbackAgent with Strands framework "
                   f"({len(agent_tools)} MCP tools)")
    
    def add_mcp_tools(self, tools: List[Any]):
        """
        Add MCP tools to the agent dynamically
        
        Args:
            tools: List of MCP tools (from MCPClient.list_tools_sync())
        """
        self.mcp_tools.extend(tools)
        
        # Recreate agent with new tools
        self.agent = Agent(
            model=self.model,
            system_prompt=self.agent._system_prompt,  # Preserve system prompt
            agent_id=self.agent.agent_id,
            name=self.agent.name,
            description=self.agent.description,
            tools=self.mcp_tools
        )
        
        logger.info(f"✅ Added {len(tools)} MCP tools to EnglishFeedbackAgent. "
                   f"Total tools: {len(self.mcp_tools)}")

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive English analysis using Strands Agent with MCP tools
        Delegates all CEFR assessment logic to the LLM
        LLM can use MCP tools (check_grammar, analyze_vocabulary, etc.) automatically

        Args:
            data: Dict with 'text', 'speaker_info', 'context', etc.

        Returns:
            Analysis results with scores, CEFR level, and suggestions
        """
        text = data.get("text", "")
        context = data.get("context", {})
        speaker_info = context.get("speaker_info", {})
        topic = context.get("topic", "general discussion")

        # Enhanced prompt that suggests using MCP tools
        tools_hint = ""
        if self.mcp_tools:
            tool_names = [tool.tool_name for tool in self.mcp_tools]
            tools_hint = f"\n\nYou have access to these analysis tools: {', '.join(tool_names)}. Use them if helpful for detailed analysis."

        # Construct prompt for the agent
        prompt = f"""Analyze the following English text for language proficiency:

TOPIC: {topic}
TEXT: "{text}"
SPEAKER CONTEXT: {speaker_info if speaker_info else "Not provided"}{tools_hint}
"""

        # Get agent response - the agent will automatically use MCP tools if needed
        result = self.agent(prompt)

        # Parse the agent's response
        content_list = result.message.get('content', [])
        response_text = str(content_list[0].get(
            'text', '')) if content_list else ''

        # Extract structured data from response
        parsed_result = self._parse_agent_response(response_text, text)
        
        # Add MCP tool usage information
        parsed_result['mcp_tools_used'] = len(self.mcp_tools) > 0

        return parsed_result

    def _parse_agent_response(self, response_text: str, original_text: str) -> Dict[str, Any]:
        """
        Parse the agent's JSON response
        Falls back to text parsing if JSON is not provided
        """
        import json
        import re

        # Try to extract JSON from response
        try:
            # Look for JSON block
            json_match = re.search(
                r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)

                # Ensure all required fields are present
                return {
                    "cefr_level": parsed.get("cefr_level", None),
                    "grammar_score": float(parsed.get("grammar_score", None)),
                    "vocabulary_score": float(parsed.get("vocabulary_score", None)),
                    "fluency_score": float(parsed.get("fluency_score", None)),
                    "analysis": parsed.get("analysis", response_text),
                    "suggestions": parsed.get("suggestions", []),
                    "analyzed_text": original_text
                }
        except (json.JSONDecodeError, ValueError) as e:
            print(
                f"[EnglishFeedbackAgent] JSON parsing failed: {e}, falling back to text extraction")

        # Fallback: Extract from text
        cefr_level = self._extract_cefr_level(response_text)
        suggestions = self._extract_suggestions(response_text)
        scores = self._extract_scores(response_text)

        return {
            "cefr_level": cefr_level,
            "grammar_score": scores.get("grammar", None),
            "vocabulary_score": scores.get("vocabulary", None),
            "fluency_score": scores.get("fluency", None),
            "analysis": response_text,
            "suggestions": suggestions,
            "analyzed_text": original_text
        }

    def _extract_cefr_level(self, response_text: str) -> str:
        """Extract CEFR level from agent response text"""
        import re
        # Look for CEFR level patterns (case insensitive)
        match = re.search(r'\b([ABC][12])\b', response_text.upper())
        if match:
            return match.group(1)
        return None  # Default fallback

    def _extract_suggestions(self, response_text: str) -> list:
        """Extract suggestions from agent response"""
        lines = response_text.split('\n')
        suggestions = []
        for line in lines:
            stripped = line.strip()
            # Look for list markers
            if any(stripped.startswith(prefix) for prefix in ['•', '-', '*', '1.', '2.', '3.', '4.', '5.']):
                # Clean up the suggestion
                cleaned = re.sub(r'^[•\-*\d.]+\s*', '', stripped)
                if cleaned:
                    suggestions.append(cleaned)
        return suggestions[:5] if suggestions else None

    def _extract_scores(self, response_text: str) -> Dict[str, float]:
        """Extract numerical scores from response text"""
        import re
        scores = {}

        # Look for score patterns
        for category in ['grammar', 'vocabulary', 'fluency']:
            pattern = rf'{category}[:\s]+(\d+\.?\d*)'
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                try:
                    score = float(match.group(1))
                    # Normalize to 0-1 range if needed
                    if score > 1:
                        score = score / 100
                    scores[category] = min(max(score, 0.0), 1.0)
                except ValueError:
                    pass

        # Set defaults for missing scores
        for category in ['grammar', 'vocabulary', 'fluency']:
            if category not in scores:
                scores[category] = None

        return scores

    async def analyze_grammar(self, text: str) -> Dict[str, Any]:
        """
        Analyze grammar specifically
        Delegates to main analyze method
        """
        result = await self.analyze({"text": text})
        return {
            "score": result["grammar_score"],
            "suggestions": [s for s in result["suggestions"] if "grammar" in s.lower()][:2]
        }

    async def analyze_vocabulary(self, text: str) -> Dict[str, Any]:
        """
        Analyze vocabulary specifically
        Delegates to main analyze method
        """
        result = await self.analyze({"text": text})
        return {
            "score": result["vocabulary_score"],
            "suggestions": [s for s in result["suggestions"] if "vocabulary" in s.lower() or "word" in s.lower()][:2]
        }

    async def analyze_fluency(self, text: str) -> Dict[str, Any]:
        """
        Analyze fluency specifically
        Delegates to main analyze method
        """
        result = await self.analyze({"text": text})
        return {
            "score": result["fluency_score"],
            "suggestions": [s for s in result["suggestions"] if "fluency" in s.lower() or "flow" in s.lower()][:2]
        }

    def determine_cefr_level(self, scores: Dict[str, float]) -> str:
        """
        DEPRECATED: CEFR level determination is now delegated to the agent.
        This method exists for backward compatibility only.

        Args:
            scores: Dict with grammar, vocabulary, fluency scores

        Returns:
            Default CEFR level (use analyze() method instead)
        """
        print("[WARNING] determine_cefr_level is deprecated. Use analyze() which delegates to the agent.")
        return None
