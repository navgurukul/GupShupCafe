#!/usr/bin/env python3
"""
Test Runner for Agent Socket Handler Tests
Simple script to run the agent-related socket handler tests
"""

import sys
import subprocess
import os

def run_agent_tests():
    """Run the agent socket handler tests"""
    print("🤖 Running Agent Socket Handler Tests...")
    print("=" * 50)
    
    # Change to the server_py directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Run the specific test file
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_agent_socket_handlers.py", 
            "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        print(f"\nTest execution completed with return code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ All agent tests passed!")
        else:
            print("❌ Some agent tests failed!")
            
        return result.returncode
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_agent_tests()
    sys.exit(exit_code)