"""
Tests for LLM module
Tests for llm_interface, gemini_llm, bedrock_llm, and ai_service_manager
"""

import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from src.llm.llm_interface import LLMInterface
from src.llm.gemini_llm import GeminiLLM
from src.llm.bedrock_llm import BedrockLLM
from src.llm.ai_service_manager import AIServiceManager, get_ai_service_manager


class TestLLMInterface:
    """Test LLM Interface abstract class"""
    
    def test_cannot_instantiate_abstract_class(self):
        """Test that LLMInterface cannot be instantiated directly"""
        with pytest.raises(TypeError):
            LLMInterface()
    
    def test_interface_methods_exist(self):
        """Test that interface defines required methods"""
        assert hasattr(LLMInterface, 'chat')
        assert hasattr(LLMInterface, 'analyze_english')


class TestGeminiLLM:
    """Test Gemini LLM implementation"""
    
    def test_initialization_with_api_key(self):
        """Test Gemini LLM initialization with API key"""
        api_key = "test-api-key"
        llm = GeminiLLM(api_key=api_key)
        
        assert llm.api_key == api_key
        assert llm.model_name == "gemini-pro"
    
    def test_initialization_from_env(self):
        """Test Gemini LLM initialization from environment variable"""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "env-api-key"}):
            llm = GeminiLLM()
            assert llm.api_key == "env-api-key"
    
    def test_initialization_without_api_key(self):
        """Test Gemini LLM initialization without API key"""
        with patch.dict(os.environ, {}, clear=True):
            llm = GeminiLLM()
            assert llm.api_key is None
    
    @pytest.mark.asyncio
    async def test_chat_basic(self):
        """Test basic chat functionality"""
        llm = GeminiLLM(api_key="test-key")
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        
        response = await llm.chat(messages)
        
        assert "content" in response
        assert "model" in response
        assert "usage" in response
        assert response["model"] == "gemini-pro"
    
    @pytest.mark.asyncio
    async def test_chat_with_parameters(self):
        """Test chat with custom temperature and max_tokens"""
        llm = GeminiLLM(api_key="test-key")
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Test message"}
        ]
        
        response = await llm.chat(messages, temperature=0.5, max_tokens=500)
        
        assert response is not None
        assert "content" in response
    
    @pytest.mark.asyncio
    async def test_analyze_english(self):
        """Test English analysis functionality"""
        llm = GeminiLLM(api_key="test-key")
        transcript = "This is a test sentence for English analysis."
        
        result = await llm.analyze_english(transcript)
        
        assert "grammar_score" in result
        assert "vocabulary_score" in result
        assert "fluency_score" in result
        assert "cefr_level" in result
        assert "suggestions" in result
        assert "analyzed_text" in result
        assert result["analyzed_text"] == transcript
    
    @pytest.mark.asyncio
    async def test_analyze_english_with_context(self):
        """Test English analysis with additional context"""
        llm = GeminiLLM(api_key="test-key")
        transcript = "Test text"
        context = {"speaker": "test-user", "topic": "technology"}
        
        result = await llm.analyze_english(transcript, context)
        
        assert result is not None
        assert "cefr_level" in result


class TestBedrockLLM:
    """Test Bedrock LLM implementation"""
    
    def test_initialization_with_parameters(self):
        """Test Bedrock LLM initialization with model_id and region"""
        model_id = "anthropic.claude-v2"
        region = "us-west-2"
        llm = BedrockLLM(model_id=model_id, region=region)
        
        assert llm.model_id == model_id
        assert llm.region == region
    
    def test_initialization_with_defaults(self):
        """Test Bedrock LLM initialization with default values"""
        with patch.dict(os.environ, {}, clear=True):
            llm = BedrockLLM()
            assert llm.model_id == "anthropic.claude-v2"
            assert llm.region == "us-east-1"
    
    def test_initialization_from_env(self):
        """Test Bedrock LLM initialization from environment variables"""
        with patch.dict(os.environ, {
            "BEDROCK_MODEL_ID": "test-model",
            "AWS_REGION": "eu-west-1"
        }):
            llm = BedrockLLM()
            assert llm.model_id == "test-model"
            assert llm.region == "eu-west-1"
    
    @pytest.mark.asyncio
    async def test_chat_basic(self):
        """Test basic chat functionality"""
        llm = BedrockLLM()
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        
        response = await llm.chat(messages)
        
        assert "content" in response
        assert "model" in response
        assert "usage" in response
    
    @pytest.mark.asyncio
    async def test_chat_with_parameters(self):
        """Test chat with custom parameters"""
        llm = BedrockLLM(model_id="custom-model", region="us-west-2")
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Test"}
        ]
        
        response = await llm.chat(messages, temperature=0.9, max_tokens=200)
        
        assert response is not None
        assert response["model"] == "custom-model"
    
    @pytest.mark.asyncio
    async def test_analyze_english(self):
        """Test English analysis functionality"""
        llm = BedrockLLM()
        transcript = "Sample text for analysis."
        
        result = await llm.analyze_english(transcript)
        
        assert "grammar_score" in result
        assert "vocabulary_score" in result
        assert "fluency_score" in result
        assert "cefr_level" in result
        assert "suggestions" in result
        assert result["analyzed_text"] == transcript
    
    @pytest.mark.asyncio
    async def test_analyze_english_with_context(self):
        """Test English analysis with context"""
        llm = BedrockLLM()
        transcript = "Test text"
        context = {"level": "beginner"}
        
        result = await llm.analyze_english(transcript, context)
        
        assert result is not None
        assert isinstance(result["suggestions"], list)


class TestAIServiceManager:
    """Test AI Service Manager factory"""
    
    def test_initialization_default_provider(self):
        """Test manager initialization with default provider"""
        manager = AIServiceManager()
        
        assert manager.get_current_provider() == "gemini"
        assert manager.get_llm() is not None
    
    def test_initialization_with_config(self):
        """Test manager initialization with custom config"""
        config = {
            "default_provider": "bedrock",
            "bedrock_model_id": "test-model",
            "aws_region": "us-west-2"
        }
        manager = AIServiceManager(config=config)
        
        assert manager.get_current_provider() == "bedrock"
    
    def test_get_llm_returns_instance(self):
        """Test that get_llm returns an LLM instance"""
        manager = AIServiceManager()
        llm = manager.get_llm()
        
        assert llm is not None
        assert isinstance(llm, LLMInterface)
    
    def test_switch_provider_to_bedrock(self):
        """Test switching provider from Gemini to Bedrock"""
        manager = AIServiceManager()
        initial_provider = manager.get_current_provider()
        
        manager.switch_provider("bedrock")
        
        assert manager.get_current_provider() == "bedrock"
        assert manager.get_current_provider() != initial_provider
    
    def test_switch_provider_to_gemini(self):
        """Test switching provider to Gemini"""
        config = {"default_provider": "bedrock"}
        manager = AIServiceManager(config=config)
        
        manager.switch_provider("gemini")
        
        assert manager.get_current_provider() == "gemini"
        assert isinstance(manager.get_llm(), GeminiLLM)
    
    def test_unknown_provider_defaults_to_gemini(self):
        """Test that unknown provider defaults to Gemini"""
        config = {"default_provider": "unknown-provider"}
        manager = AIServiceManager(config=config)
        
        # Should default to gemini
        llm = manager.get_llm()
        assert isinstance(llm, GeminiLLM)
    
    def test_get_llm_multiple_calls(self):
        """Test that multiple calls to get_llm return the same instance"""
        manager = AIServiceManager()
        llm1 = manager.get_llm()
        llm2 = manager.get_llm()
        
        assert llm1 is llm2
    
    def test_get_current_provider(self):
        """Test getting current provider name"""
        manager = AIServiceManager()
        provider = manager.get_current_provider()
        
        assert provider in ["gemini", "bedrock"]
    
    def test_singleton_function(self):
        """Test get_ai_service_manager singleton function"""
        # Reset singleton
        import src.llm.ai_service_manager as asm
        asm._ai_service_manager = None
        
        manager1 = get_ai_service_manager()
        manager2 = get_ai_service_manager()
        
        assert manager1 is manager2
        assert isinstance(manager1, AIServiceManager)
    
    def test_initialization_with_gemini_api_key(self):
        """Test manager initialization with Gemini API key in config"""
        config = {
            "default_provider": "gemini",
            "gemini_api_key": "test-gemini-key"
        }
        manager = AIServiceManager(config=config)
        llm = manager.get_llm()
        
        assert isinstance(llm, GeminiLLM)
        assert llm.api_key == "test-gemini-key"


class TestLLMIntegration:
    """Integration tests for LLM module"""
    
    @pytest.mark.asyncio
    async def test_manager_can_use_gemini_llm(self):
        """Test that manager can properly use Gemini LLM"""
        manager = AIServiceManager(config={"default_provider": "gemini"})
        llm = manager.get_llm()
        
        messages = [{"role": "user", "content": "Test"}]
        response = await llm.chat(messages)
        
        assert response is not None
        assert "content" in response
    
    @pytest.mark.asyncio
    async def test_manager_can_use_bedrock_llm(self):
        """Test that manager can properly use Bedrock LLM"""
        manager = AIServiceManager(config={"default_provider": "bedrock"})
        llm = manager.get_llm()
        
        messages = [{"role": "user", "content": "Test"}]
        response = await llm.chat(messages)
        
        assert response is not None
        assert "content" in response
    
    @pytest.mark.asyncio
    async def test_analyze_english_across_providers(self):
        """Test English analysis works across different providers"""
        # Test with Gemini
        gemini_manager = AIServiceManager(config={"default_provider": "gemini"})
        gemini_llm = gemini_manager.get_llm()
        gemini_result = await gemini_llm.analyze_english("Test text")
        
        # Test with Bedrock
        bedrock_manager = AIServiceManager(config={"default_provider": "bedrock"})
        bedrock_llm = bedrock_manager.get_llm()
        bedrock_result = await bedrock_llm.analyze_english("Test text")
        
        # Both should have required fields
        assert "cefr_level" in gemini_result
        assert "cefr_level" in bedrock_result
        assert "grammar_score" in gemini_result
        assert "grammar_score" in bedrock_result
