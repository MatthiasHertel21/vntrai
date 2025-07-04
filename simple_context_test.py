#!/usr/bin/env python3
"""
Simple test to verify Flask context handling
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.routes.agents.streaming_api import get_thread_lock, build_context_prompt
from app.utils.data_manager import agent_run_manager, agents_manager, tools_manager
from app.routes.agents.api_utils import log_info

def test_context_handling():
    """Test that we can work without Flask context"""
    print("Testing context handling...")
    
    # Test thread lock
    thread_id = "test_thread_123"
    lock = get_thread_lock(thread_id)
    print(f"✓ Thread lock created: {lock}")
    
    # Test context prompt building (this should work without Flask context)
    task_def = {
        'name': 'Test Task',
        'description': 'Test Description',
        'output': {'type': 'text'}
    }
    
    task_inputs = {'test_input': 'test_value'}
    agent = {'name': 'Test Agent', 'description': 'Test Agent Description'}
    
    try:
        prompt = build_context_prompt(task_def, task_inputs, agent)
        print(f"✓ Context prompt built successfully: {len(prompt)} characters")
        return True
    except Exception as e:
        print(f"✗ Context prompt failed: {e}")
        return False

if __name__ == "__main__":
    success = test_context_handling()
    if success:
        print("✅ All context handling tests passed!")
        sys.exit(0)
    else:
        print("❌ Context handling tests failed!")
        sys.exit(1)
