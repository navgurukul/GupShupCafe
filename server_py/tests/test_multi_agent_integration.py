"""
Tests for Multi-Agent System Integration
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock


class TestMultiAgentSystemStructure:
    """Test multi-agent system structure and configuration"""
    
    def test_files_exist(self):
        """Test that multi-agent files exist"""
        llm_tutor_path = "src/llmTutor"
        
        required_files = [
            "englishGrammarAgent.py",
            "multiAgentOrchestrator.py",
        ]
        
        for filename in required_files:
            filepath = os.path.join(llm_tutor_path, filename)
            assert os.path.exists(filepath), f"{filename} should exist"
    
    def test_debate_facilitator_has_multi_agent_support(self):
        """Test that debate_room_facilitator supports multi-agent mode"""
        with open("src/llmTutor/debate_room_facilitator.py", 'r') as f:
            content = f.read()
            
            # Check for multi-agent support
            assert "use_multi_agent" in content, "Should have use_multi_agent parameter"
            assert "MultiAgentOrchestrator" in content, "Should import MultiAgentOrchestrator"
            assert "_initialize_single_agent" in content, "Should have backward compatibility"
            assert "orchestrator" in content, "Should reference orchestrator"


class TestMultiAgentConfiguration:
    """Test multi-agent configuration"""
    
    def test_env_example_has_multi_agent_config(self):
        """Test that .env.example includes multi-agent configuration"""
        with open(".env.example", 'r') as f:
            content = f.read()
            
            required_vars = [
                "USE_MULTI_AGENT",
                "GEMINI_API_KEY",
                "USE_AWS_AGENTCORE",
                "AWS_REGION",
            ]
            
            for var in required_vars:
                assert var in content, f"{var} should be in .env.example"
    
    def test_multi_agent_readme_exists(self):
        """Test that multi-agent README exists"""
        assert os.path.exists("MULTI_AGENT_README.md"), "MULTI_AGENT_README.md should exist"
    
    def test_multi_agent_documentation_exists(self):
        """Test that documentation exists"""
        docs = [
            "../docs/Miscellaneous/MULTI_AGENT_ARCHITECTURE.md",
            "../docs/Miscellaneous/AWS_AGENTCORE_DEPLOYMENT.md",
        ]
        
        for doc in docs:
            assert os.path.exists(doc), f"{doc} should exist"


class TestMultiAgentBackwardCompatibility:
    """Test backward compatibility with existing code"""
    
    def test_debate_facilitator_default_behavior(self):
        """Test that DebateRoomFacilitator can be initialized without breaking changes"""
        # This test ensures the code doesn't break existing usage
        # We're just checking structure, not running actual agents
        
        debate_facilitator_path = "src/llmTutor/debate_room_facilitator.py"
        assert os.path.exists(debate_facilitator_path)
        
        with open(debate_facilitator_path, 'r') as f:
            content = f.read()
            
            # Ensure old init signature still works (with defaults)
            assert "use_multi_agent: bool = True" in content or "use_multi_agent=True" in content, \
                "Should have use_multi_agent with default value"
    
    def test_single_agent_mode_available(self):
        """Test that single-agent mode is still available"""
        with open("src/llmTutor/debate_room_facilitator.py", 'r') as f:
            content = f.read()
            
            assert "_initialize_single_agent" in content, \
                "Single-agent initialization method should exist"
            assert "use_multi_agent" in content, \
                "Should have use_multi_agent parameter for backward compatibility"


class TestMultiAgentAgentTypes:
    """Test agent type definitions"""
    
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'})
    def test_agent_type_constants_defined(self):
        """Test that AgentType constants are defined"""
        # We need to mock imports since strands may not be available
        with patch('sys.modules', {
            'strands': Mock(),
            'strands_agents': Mock(),
            'strands_agents.src.strands.models.gemini': Mock(),
        }):
            try:
                # Try to import and check structure
                import sys
                sys.path.insert(0, 'src/llmTutor')
                
                with open('src/llmTutor/multiAgentOrchestrator.py', 'r') as f:
                    content = f.read()
                    
                    assert "class AgentType:" in content, "AgentType class should be defined"
                    assert "ENGLISH_GRAMMAR" in content, "ENGLISH_GRAMMAR agent type should exist"
                    assert "DEBATE_FACILITATOR" in content, "DEBATE_FACILITATOR agent type should exist"
            finally:
                if 'src/llmTutor' in sys.path:
                    sys.path.remove('src/llmTutor')


class TestIntegrationTest:
    """Test the integration test script"""
    
    def test_integration_test_script_exists(self):
        """Test that integration test script exists"""
        assert os.path.exists("test_multi_agent_integration.py"), \
            "Integration test script should exist"
    
    def test_integration_test_has_main_function(self):
        """Test that integration test has main function"""
        with open("test_multi_agent_integration.py", 'r') as f:
            content = f.read()
            
            assert "def main():" in content, "Should have main function"
            assert "check_dependencies" in content, "Should check dependencies"
            assert "test_multi_agent_structure" in content, "Should test structure"
            assert "test_aws_configuration" in content, "Should test AWS config"


class TestDocumentationQuality:
    """Test documentation quality and completeness"""
    
    def test_architecture_doc_has_key_sections(self):
        """Test that architecture documentation has key sections"""
        doc_path = "../docs/Miscellaneous/MULTI_AGENT_ARCHITECTURE.md"
        
        with open(doc_path, 'r') as f:
            content = f.read()
            
            required_sections = [
                "## Overview",
                "## Architecture",
                "## AWS Bedrock AgentCore Integration",
                "## Usage",
                "## Backward Compatibility",
                "## Testing",
                "## Troubleshooting",
            ]
            
            for section in required_sections:
                assert section in content, f"Documentation should have {section}"
    
    def test_deployment_doc_has_steps(self):
        """Test that deployment documentation has deployment steps"""
        doc_path = "../docs/Miscellaneous/AWS_AGENTCORE_DEPLOYMENT.md"
        
        with open(doc_path, 'r') as f:
            content = f.read()
            
            required_steps = [
                "## Step 1:",
                "## Step 2:",
                "## Step 3:",
                "## Troubleshooting",
            ]
            
            for step in required_steps:
                assert step in content, f"Deployment doc should have {step}"


# Run with: pytest server_py/tests/test_multi_agent_integration.py -v
