"""
Tests for Multi-Agent System
"""

import sys
from unittest.mock import Mock, patch, MagicMock


def test_english_grammar_agent_initialization():
    """Test that English Grammar Agent can be initialized"""
    print("\n=== Testing English Grammar Agent Initialization ===")
    
    # Mock the Gemini API key
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
        try:
            from englishGrammarAgent import EnglishGrammarAgent
            
            # This will fail without actual API, but we can test structure
            print("✓ EnglishGrammarAgent class imported successfully")
            
            # Test that class has required methods
            assert hasattr(EnglishGrammarAgent, 'analyze_statement')
            assert hasattr(EnglishGrammarAgent, 'analyze_multiple_statements')
            assert hasattr(EnglishGrammarAgent, 'generate_summary_feedback')
            print("✓ EnglishGrammarAgent has required methods")
            
        except ImportError as e:
            print(f"✗ Failed to import EnglishGrammarAgent: {e}")
            raise


def test_multi_agent_orchestrator_initialization():
    """Test that Multi-Agent Orchestrator can be initialized"""
    print("\n=== Testing Multi-Agent Orchestrator Initialization ===")
    
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
        try:
            from multiAgentOrchestrator import MultiAgentOrchestrator, AgentType
            
            print("✓ MultiAgentOrchestrator class imported successfully")
            
            # Test initialization without AWS (local mode)
            # We need to mock the agent initialization to avoid API calls
            with patch('multiAgentOrchestrator.EnglishGrammarAgent') as mock_grammar:
                mock_grammar.return_value = Mock()
                
                orchestrator = MultiAgentOrchestrator(use_aws_agentcore=False)
                
                print("✓ Orchestrator initialized in local mode")
                
                # Check attributes
                assert orchestrator.use_aws_agentcore == False
                assert AgentType.ENGLISH_GRAMMAR in orchestrator.agents
                print("✓ Orchestrator has English Grammar Agent")
                
                # Test that required methods exist
                assert hasattr(orchestrator, 'get_english_feedback')
                assert hasattr(orchestrator, 'get_discussion_feedback')
                assert hasattr(orchestrator, 'get_combined_feedback')
                assert hasattr(orchestrator, 'initialize_debate_facilitator')
                print("✓ Orchestrator has required methods")
                
        except Exception as e:
            print(f"✗ Failed to initialize MultiAgentOrchestrator: {e}")
            raise


def test_multi_agent_orchestrator_agent_types():
    """Test that agent type constants are defined"""
    print("\n=== Testing Agent Types ===")
    
    from multiAgentOrchestrator import AgentType
    
    assert hasattr(AgentType, 'ENGLISH_GRAMMAR')
    assert hasattr(AgentType, 'DEBATE_FACILITATOR')
    print("✓ Agent type constants defined")
    
    assert AgentType.ENGLISH_GRAMMAR == "english_grammar"
    assert AgentType.DEBATE_FACILITATOR == "debate_facilitator"
    print("✓ Agent types have correct values")


def test_debate_facilitator_multi_agent_integration():
    """Test that DebateRoomFacilitator can use multi-agent mode"""
    print("\n=== Testing Debate Facilitator Multi-Agent Integration ===")
    
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
        try:
            # Mock the orchestrator and agents
            with patch('debate_room_facilitator.MultiAgentOrchestrator') as mock_orchestrator:
                mock_orch_instance = Mock()
                mock_orchestrator.return_value = mock_orch_instance
                
                from debate_room_facilitator import DebateRoomFacilitator
                
                # Test initialization with multi-agent enabled
                facilitator = DebateRoomFacilitator(
                    room_type="discussion",
                    num_rounds=3,
                    use_multi_agent=True
                )
                
                print("✓ Facilitator initialized with multi-agent enabled")
                
                # Check attributes
                assert facilitator.use_multi_agent == True
                assert facilitator.orchestrator is not None
                print("✓ Facilitator has orchestrator reference")
                
        except Exception as e:
            print(f"✗ Failed to test multi-agent integration: {e}")
            raise


def test_debate_facilitator_backward_compatibility():
    """Test that DebateRoomFacilitator works with single-agent mode"""
    print("\n=== Testing Backward Compatibility (Single-Agent Mode) ===")
    
    try:
        from debate_room_facilitator import DebateRoomFacilitator
        
        # Test initialization with multi-agent disabled
        facilitator = DebateRoomFacilitator(
            room_type="discussion",
            num_rounds=3,
            use_multi_agent=False
        )
        
        print("✓ Facilitator initialized in single-agent mode")
        
        # Check attributes
        assert facilitator.use_multi_agent == False
        assert facilitator.orchestrator is None
        print("✓ Facilitator works without orchestrator (backward compatible)")
        
    except Exception as e:
        print(f"✗ Failed backward compatibility test: {e}")
        raise


def test_orchestrator_feedback_methods():
    """Test that orchestrator feedback methods have correct signatures"""
    print("\n=== Testing Orchestrator Feedback Methods ===")
    
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
        with patch('multiAgentOrchestrator.EnglishGrammarAgent') as mock_grammar:
            mock_grammar.return_value = Mock()
            
            from multiAgentOrchestrator import MultiAgentOrchestrator
            
            orchestrator = MultiAgentOrchestrator(use_aws_agentcore=False)
            
            # Test method signatures
            import inspect
            
            # get_english_feedback
            sig = inspect.signature(orchestrator.get_english_feedback)
            assert 'statements' in sig.parameters
            assert 'instant' in sig.parameters
            print("✓ get_english_feedback has correct signature")
            
            # get_discussion_feedback
            sig = inspect.signature(orchestrator.get_discussion_feedback)
            assert 'topic' in sig.parameters
            assert 'recent_statements' in sig.parameters
            print("✓ get_discussion_feedback has correct signature")
            
            # get_combined_feedback
            sig = inspect.signature(orchestrator.get_combined_feedback)
            assert 'topic' in sig.parameters
            assert 'recent_statements' in sig.parameters
            print("✓ get_combined_feedback has correct signature")


def test_aws_agentcore_optional():
    """Test that AWS AgentCore is optional and gracefully handled"""
    print("\n=== Testing AWS AgentCore Optional Dependency ===")
    
    # Test without AWS credentials
    with patch.dict('os.environ', {
        'GEMINI_API_KEY': 'test_key',
        'AWS_ACCESS_KEY_ID': '',
        'AWS_SECRET_ACCESS_KEY': ''
    }, clear=True):
        with patch('multiAgentOrchestrator.EnglishGrammarAgent') as mock_grammar:
            mock_grammar.return_value = Mock()
            
            from multiAgentOrchestrator import MultiAgentOrchestrator
            
            # Should initialize without AWS
            orchestrator = MultiAgentOrchestrator(use_aws_agentcore=True)
            
            # Should fall back to local mode
            assert orchestrator.use_aws_agentcore == False
            print("✓ Orchestrator gracefully falls back to local mode without AWS credentials")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MULTI-AGENT SYSTEM - UNIT TESTS")
    print("="*60)
    
    try:
        test_english_grammar_agent_initialization()
        test_multi_agent_orchestrator_initialization()
        test_multi_agent_orchestrator_agent_types()
        test_debate_facilitator_multi_agent_integration()
        test_debate_facilitator_backward_compatibility()
        test_orchestrator_feedback_methods()
        test_aws_agentcore_optional()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED! ✅")
        print("="*60)
        
    except Exception as e:
        print(f"\n{'='*60}")
        print("TEST FAILED ❌")
        print("="*60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
