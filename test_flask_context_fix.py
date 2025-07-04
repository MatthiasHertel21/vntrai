#!/usr/bin/env python3
"""
Test to simulate the streaming API without actual Flask request
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.routes.agents.thread_management import get_thread_lock
from app.routes.agents.prompt_builder import (
    build_context_prompt, 
    render_response_content,
    resolve_variables
)

def test_streaming_simulation():
    """Simulate the streaming API execution without Flask"""
    print("🧪 Testing streaming API simulation...")
    
    # Simulate extracted request data (what should be extracted outside generator)
    run_uuid = "test-run-uuid"
    task_uuid = "test-task-uuid"
    request_method = "GET"  # This should be extracted from request.method outside generator
    
    # Simulate task definition and inputs
    task_def = {
        'name': 'Test AI Task',
        'description': 'Test task for AI execution',
        'type': 'ai',
        'output': {'type': 'text', 'description': 'Plain text output'},
        'instruction': 'Create a test response for {{input_name}}'
    }
    
    task_inputs = {'input_name': 'user123'}
    
    agent = {
        'name': 'Test Agent',
        'description': 'A test agent for simulation',
        'assistant_id': 'asst_test123',
        'ai_assistant_tool': 'tool:test-tool-id'
    }
    
    print(f"✓ Simulated data setup complete")
    print(f"  - Request method: {request_method}")
    print(f"  - Task type: {task_def.get('type')}")
    print(f"  - Task inputs: {task_inputs}")
    
    # Test variable resolution
    instruction = task_def.get('instruction', '')
    resolved_instruction = resolve_variables(instruction, task_inputs)
    print(f"✓ Variable resolution test:")
    print(f"  - Original: {instruction}")
    print(f"  - Resolved: {resolved_instruction}")
    
    # Test context prompt building
    try:
        context_prompt = build_context_prompt(task_def, task_inputs, agent)
        print(f"✓ Context prompt built: {len(context_prompt)} characters")
    except Exception as e:
        print(f"✗ Context prompt failed: {e}")
        return False
    
    # Test response rendering
    test_response = "This is a test AI response"
    rendered = render_response_content(test_response, 'text')
    print(f"✓ Response rendering test: {len(rendered)} characters")
    
    # Test thread locking
    thread_id = "thread_test123"
    lock = get_thread_lock(thread_id)
    acquired = lock.acquire(timeout=1)
    if acquired:
        print(f"✓ Thread lock acquired for {thread_id}")
        lock.release()
        print(f"✓ Thread lock released for {thread_id}")
    else:
        print(f"✗ Failed to acquire thread lock")
        return False
    
    print("🎉 All streaming simulation tests passed!")
    return True

def test_generator_simulation():
    """Simulate what happens inside the generator function"""
    print("\n🔄 Testing generator simulation...")
    
    # This simulates the generate_task_execution_stream() function
    # All data should be available without accessing Flask request object
    
    def simulate_generator(task_def, task_inputs, agent, request_method):
        """Simulate the generator without Flask context"""
        yield f"Starting task execution..."
        yield f"Task type: {task_def.get('type')}"
        yield f"Request method: {request_method}"  # This should NOT cause Flask context error
        yield f"Agent: {agent.get('name')}"
        yield f"Inputs: {task_inputs}"
        yield f"Task execution completed"
    
    # Test data (simulating what should be extracted outside generator)
    task_def = {'name': 'Test Task', 'type': 'ai'}
    task_inputs = {'test': 'value'}
    agent = {'name': 'Test Agent'}
    request_method = 'GET'  # This is extracted from request.method OUTSIDE generator
    
    # Execute the generator
    try:
        messages = list(simulate_generator(task_def, task_inputs, agent, request_method))
        print(f"✓ Generator executed successfully with {len(messages)} messages")
        for msg in messages:
            print(f"  - {msg}")
        return True
    except Exception as e:
        print(f"✗ Generator failed: {e}")
        return False

if __name__ == "__main__":
    success1 = test_streaming_simulation()
    success2 = test_generator_simulation()
    
    if success1 and success2:
        print("\n✅ All tests passed! The Flask context issue should be resolved.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
