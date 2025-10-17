"""
Tests for Agents module
Tests for english_feedback_agent, debate_facilitator_agent, and aws_strands_orchestrator
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.agents.english_feedback_agent import EnglishFeedbackAgent
from src.agents.debate_facilitator_agent import DebateFacilitatorAgent
from src.agents.aws_strands_orchestrator import AWSStrandsOrchestrator
from src.llm.gemini_llm import GeminiLLM
from src.llm.ai_service_manager import AIServiceManager


@pytest.fixture
def mock_llm():
    """Create a mock LLM provider for testing"""
    llm = Mock()
    llm.chat = AsyncMock(return_value={
        "content": "Mock response",
        "model": "mock-model",
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
    })
    llm.analyze_english = AsyncMock(return_value={
        "grammar_score": 0.8,
        "vocabulary_score": 0.75,
        "fluency_score": 0.85,
        "cefr_level": "B1",
        "suggestions": ["Suggestion 1", "Suggestion 2"],
        "analyzed_text": "Sample text"
    })
    return llm


@pytest.fixture
def ai_service_manager():
    """Create an AI service manager for testing"""
    return AIServiceManager(config={"default_provider": "gemini"})


class TestEnglishFeedbackAgent:
    """Test English Feedback Agent"""
    
    def test_initialization(self, mock_llm):
        """Test agent initialization"""
        agent = EnglishFeedbackAgent(mock_llm)
        
        assert agent.llm_provider is not None
        assert agent.llm_provider == mock_llm
    
    @pytest.mark.asyncio
    async def test_analyze_basic(self, mock_llm):
        """Test basic analysis functionality"""
        agent = EnglishFeedbackAgent(mock_llm)
        data = {
            "text": "This is a test sentence.",
            "context": {}
        }
        
        result = await agent.analyze(data)
        
        assert result is not None
        assert "cefr_level" in result
        assert "detailed_analysis" in result
        assert "grammar" in result["detailed_analysis"]
        assert "vocabulary" in result["detailed_analysis"]
        assert "fluency" in result["detailed_analysis"]
    
    @pytest.mark.asyncio
    async def test_analyze_with_context(self, mock_llm):
        """Test analysis with additional context"""
        agent = EnglishFeedbackAgent(mock_llm)
        data = {
            "text": "Sample text for analysis.",
            "context": {
                "speaker": "test-user",
                "topic": "technology"
            }
        }
        
        result = await agent.analyze(data)
        
        assert result is not None
        mock_llm.analyze_english.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_grammar(self, mock_llm):
        """Test grammar analysis"""
        agent = EnglishFeedbackAgent(mock_llm)
        text = "This is test text."
        
        result = await agent.analyze_grammar(text)
        
        assert "score" in result
        assert "errors" in result
        assert "suggestions" in result
        assert isinstance(result["suggestions"], list)
    
    @pytest.mark.asyncio
    async def test_analyze_vocabulary(self, mock_llm):
        """Test vocabulary analysis"""
        agent = EnglishFeedbackAgent(mock_llm)
        text = "The quick brown fox jumps over the lazy dog."
        
        result = await agent.analyze_vocabulary(text)
        
        assert "score" in result
        assert "word_count" in result
        assert "unique_words" in result
        assert "suggestions" in result
        assert result["word_count"] > 0
    
    @pytest.mark.asyncio
    async def test_analyze_vocabulary_empty_text(self, mock_llm):
        """Test vocabulary analysis with empty text"""
        agent = EnglishFeedbackAgent(mock_llm)
        text = ""
        
        result = await agent.analyze_vocabulary(text)
        
        assert result["word_count"] == 0
        assert result["unique_words"] == 0
    
    @pytest.mark.asyncio
    async def test_analyze_fluency(self, mock_llm):
        """Test fluency analysis"""
        agent = EnglishFeedbackAgent(mock_llm)
        text = "This is a test. It has multiple sentences."
        
        result = await agent.analyze_fluency(text)
        
        assert "score" in result
        assert "sentence_count" in result
        assert "suggestions" in result
    
    def test_determine_cefr_level_c2(self, mock_llm):
        """Test CEFR level determination for C2"""
        agent = EnglishFeedbackAgent(mock_llm)
        scores = {"grammar": 0.95, "vocabulary": 0.92, "fluency": 0.93}
        
        level = agent.determine_cefr_level(scores)
        
        assert level == "C2"
    
    def test_determine_cefr_level_c1(self, mock_llm):
        """Test CEFR level determination for C1"""
        agent = EnglishFeedbackAgent(mock_llm)
        scores = {"grammar": 0.85, "vocabulary": 0.80, "fluency": 0.82}
        
        level = agent.determine_cefr_level(scores)
        
        assert level == "C1"
    
    def test_determine_cefr_level_b2(self, mock_llm):
        """Test CEFR level determination for B2"""
        agent = EnglishFeedbackAgent(mock_llm)
        scores = {"grammar": 0.75, "vocabulary": 0.70, "fluency": 0.72}
        
        level = agent.determine_cefr_level(scores)
        
        assert level == "B2"
    
    def test_determine_cefr_level_b1(self, mock_llm):
        """Test CEFR level determination for B1"""
        agent = EnglishFeedbackAgent(mock_llm)
        scores = {"grammar": 0.65, "vocabulary": 0.60, "fluency": 0.62}
        
        level = agent.determine_cefr_level(scores)
        
        assert level == "B1"
    
    def test_determine_cefr_level_a2(self, mock_llm):
        """Test CEFR level determination for A2"""
        agent = EnglishFeedbackAgent(mock_llm)
        scores = {"grammar": 0.55, "vocabulary": 0.50, "fluency": 0.52}
        
        level = agent.determine_cefr_level(scores)
        
        assert level == "A2"
    
    def test_determine_cefr_level_a1(self, mock_llm):
        """Test CEFR level determination for A1"""
        agent = EnglishFeedbackAgent(mock_llm)
        scores = {"grammar": 0.45, "vocabulary": 0.40, "fluency": 0.42}
        
        level = agent.determine_cefr_level(scores)
        
        assert level == "A1"


class TestDebateFacilitatorAgent:
    """Test Debate Facilitator Agent"""
    
    def test_initialization(self, mock_llm):
        """Test agent initialization"""
        facilitator_agent = DebateFacilitatorAgent(mock_llm)
        
        assert facilitator_agent.model is not None
        assert facilitator_agent.model == mock_llm
        assert facilitator_agent.agent is not None
    
    @pytest.mark.asyncio
    async def test_facilitate_turn_basic(self, mock_llm):
        """Test basic turn facilitation"""
        agent = DebateFacilitatorAgent(mock_llm)
        context = {
            "topic": "Climate Change",
            "current_speaker": {"name": "Alice"},
            "turn_number": 1
        }
        
        result = await agent.facilitate_turn(context)
        
        assert result is not None
        assert isinstance(result, str)
        mock_llm.chat.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_facilitate_turn_without_speaker_name(self, mock_llm):
        """Test turn facilitation without speaker name"""
        agent = DebateFacilitatorAgent(mock_llm)
        context = {
            "topic": "Education",
            "current_speaker": {},
            "turn_number": 2
        }
        
        result = await agent.facilitate_turn(context)
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_facilitate_turn_default_topic(self, mock_llm):
        """Test turn facilitation with default topic"""
        agent = DebateFacilitatorAgent(mock_llm)
        context = {
            "current_speaker": {"name": "Bob"},
            "turn_number": 3
        }
        
        result = await agent.facilitate_turn(context)
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_suggest_topic_direction_empty_statements(self, mock_llm):
        """Test topic direction suggestion with empty statements"""
        agent = DebateFacilitatorAgent(mock_llm)
        statements = []
        
        result = await agent.suggest_topic_direction(statements)
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_suggest_topic_direction_with_statements(self, mock_llm):
        """Test topic direction suggestion with statements"""
        agent = DebateFacilitatorAgent(mock_llm)
        statements = [
            "I think climate change is serious.",
            "We need immediate action."
        ]
        
        result = await agent.suggest_topic_direction(statements)
        
        assert result is not None
        assert isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_moderate_discussion(self, mock_llm):
        """Test discussion moderation"""
        agent = DebateFacilitatorAgent(mock_llm)
        context = {
            "topic": "Test Topic",
            "participants": [{"name": "Alice"}, {"name": "Bob"}]
        }
        
        result = await agent.moderate_discussion(context)
        
        assert result is not None
        assert "needs_intervention" in result
        assert "message" in result
        assert "reason" in result
        assert isinstance(result["needs_intervention"], bool)
    
    @pytest.mark.asyncio
    async def test_generate_speaking_prompt(self, mock_llm):
        """Test speaking prompt generation"""
        agent = DebateFacilitatorAgent(mock_llm)
        topic = "Artificial Intelligence in Education"
        
        result = await agent.generate_speaking_prompt(topic)
        
        assert result is not None
        assert isinstance(result, str)
        mock_llm.chat.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_speaking_prompt_with_custom_parameters(self, mock_llm):
        """Test speaking prompt generation uses correct parameters"""
        agent = DebateFacilitatorAgent(mock_llm)
        topic = "Technology and Privacy"
        
        await agent.generate_speaking_prompt(topic)
        
        # Check that chat was called with correct parameters
        call_args = mock_llm.chat.call_args
        assert call_args[1]["temperature"] == 0.9
        assert call_args[1]["max_tokens"] == 100


class TestAWSStrandsOrchestrator:
    """Test AWS Strands Orchestrator"""
    
    def test_initialization(self, ai_service_manager):
        """Test orchestrator initialization"""
        orchestrator = AWSStrandsOrchestrator(ai_service_manager)
        
        assert orchestrator.ai_service_manager is not None
        assert orchestrator.english_agent is not None
        assert orchestrator.facilitator_agent is not None
        assert isinstance(orchestrator.english_agent, EnglishFeedbackAgent)
        assert isinstance(orchestrator.facilitator_agent, DebateFacilitatorAgent)
    
    @pytest.mark.asyncio
    async def test_get_english_feedback_instant(self, ai_service_manager):
        """Test getting instant English feedback"""
        orchestrator = AWSStrandsOrchestrator(ai_service_manager)
        statements = ["This is a test statement."]
        
        result = await orchestrator.get_english_feedback(
            statements=statements,
            instant=True,
            context={}
        )
        
        assert result is not None
        assert result["type"] == "instant"
        assert "message" in result
        assert "cefr_level" in result
        assert "scores" in result
        assert "grammar" in result["scores"]
        assert "vocabulary" in result["scores"]
        assert "fluency" in result["scores"]
    
    @pytest.mark.asyncio
    async def test_get_english_feedback_comprehensive(self, ai_service_manager):
        """Test getting comprehensive English feedback"""
        orchestrator = AWSStrandsOrchestrator(ai_service_manager)
        statements = ["This is a test.", "Another statement."]
        
        result = await orchestrator.get_english_feedback(
            statements=statements,
            instant=False,
            context={"speaker": "test-user"}
        )
        
        assert result is not None
        assert result["type"] == "comprehensive"
        assert "analysis" in result
        assert "facilitation_suggestion" in result
        assert "message" in result
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_get_english_feedback_empty_statements(self, ai_service_manager):
        """Test feedback with empty statements list"""
        orchestrator = AWSStrandsOrchestrator(ai_service_manager)
        statements = []
        
        result = await orchestrator.get_english_feedback(
            statements=statements,
            instant=True
        )
        
        assert result is not None
        assert "type" in result
    
    @pytest.mark.asyncio
    async def test_instant_feedback_combines_statements(self, ai_service_manager):
        """Test that instant feedback combines multiple statements"""
        orchestrator = AWSStrandsOrchestrator(ai_service_manager)
        statements = ["First statement.", "Second statement.", "Third statement."]
        
        result = await orchestrator.get_english_feedback(
            statements=statements,
            instant=True
        )
        
        assert result is not None
        assert result["type"] == "instant"
    
    @pytest.mark.asyncio
    async def test_comprehensive_feedback_includes_facilitation(self, ai_service_manager):
        """Test that comprehensive feedback includes facilitation suggestion"""
        orchestrator = AWSStrandsOrchestrator(ai_service_manager)
        statements = ["Test statement one.", "Test statement two."]
        
        result = await orchestrator.get_english_feedback(
            statements=statements,
            instant=False,
            context={}
        )
        
        assert "facilitation_suggestion" in result
        assert isinstance(result["facilitation_suggestion"], str)
    
    def test_format_feedback_message(self, ai_service_manager):
        """Test feedback message formatting"""
        orchestrator = AWSStrandsOrchestrator(ai_service_manager)
        result = {
            "cefr_level": "B2",
            "suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3", "Suggestion 4"]
        }
        
        message = orchestrator._format_feedback_message(result)
        
        assert "B2" in message
        assert "Suggestion 1" in message
        assert "Suggestion 2" in message
        assert "Suggestion 3" in message
        # Only top 3 suggestions should be included
        assert "Suggestion 4" not in message
    
    def test_format_feedback_message_no_suggestions(self, ai_service_manager):
        """Test feedback message formatting without suggestions"""
        orchestrator = AWSStrandsOrchestrator(ai_service_manager)
        result = {
            "cefr_level": "C1",
            "suggestions": []
        }
        
        message = orchestrator._format_feedback_message(result)
        
        assert "C1" in message
        assert isinstance(message, str)
    
    def test_format_gentle_mention(self, ai_service_manager):
        """Test gentle mention formatting"""
        orchestrator = AWSStrandsOrchestrator(ai_service_manager)
        speaker = "Alice"
        result = {"cefr_level": "B1"}
        
        mention = orchestrator._format_gentle_mention(speaker, result)
        
        assert speaker in mention
        assert "B1" in mention
        assert isinstance(mention, str)
    
    @pytest.mark.asyncio
    async def test_orchestrator_uses_both_agents(self, ai_service_manager):
        """Test that orchestrator properly uses both English and Facilitator agents"""
        orchestrator = AWSStrandsOrchestrator(ai_service_manager)
        statements = ["Test statement."]
        
        # Get comprehensive feedback which should use both agents
        result = await orchestrator.get_english_feedback(
            statements=statements,
            instant=False
        )
        
        assert "analysis" in result
        assert "facilitation_suggestion" in result


class TestAgentsIntegration:
    """Integration tests for agents module"""
    
    @pytest.mark.asyncio
    async def test_english_agent_with_real_llm(self):
        """Test English agent with actual LLM implementation"""
        llm = GeminiLLM(api_key="test-key")
        agent = EnglishFeedbackAgent(llm)
        
        data = {
            "text": "This is a comprehensive test of the English feedback agent.",
            "context": {}
        }
        
        result = await agent.analyze(data)
        
        assert result is not None
        assert "cefr_level" in result
        assert "detailed_analysis" in result
    
    @pytest.mark.asyncio
    async def test_facilitator_agent_with_real_llm(self):
        """Test Facilitator agent with actual LLM implementation"""
        llm = GeminiLLM(api_key="test-key")
        agent = DebateFacilitatorAgent(llm)
        
        context = {
            "topic": "The Future of Work",
            "current_speaker": {"name": "TestUser"},
            "turn_number": 1
        }
        
        result = await agent.facilitate_turn(context)
        
        assert result is not None
        assert isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_orchestrator_full_workflow(self):
        """Test orchestrator complete workflow"""
        manager = AIServiceManager(config={"default_provider": "gemini"})
        orchestrator = AWSStrandsOrchestrator(manager)
        
        # Test instant feedback
        instant_result = await orchestrator.get_english_feedback(
            statements=["Hello, this is a test."],
            instant=True
        )
        assert instant_result["type"] == "instant"
        
        # Test comprehensive feedback
        comprehensive_result = await orchestrator.get_english_feedback(
            statements=["Hello, this is a test.", "Another sentence here."],
            instant=False
        )
        assert comprehensive_result["type"] == "comprehensive"
    
    @pytest.mark.asyncio
    async def test_agent_error_handling(self, mock_llm):
        """Test agent behavior when LLM calls fail"""
        # Make the mock raise an exception
        mock_llm.analyze_english.side_effect = Exception("API Error")
        
        agent = EnglishFeedbackAgent(mock_llm)
        
        with pytest.raises(Exception):
            await agent.analyze({"text": "test", "context": {}})
