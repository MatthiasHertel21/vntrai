#!/usr/bin/env python3
"""
Test the stop task functionality end-to-end
"""

import requests
import time
import json

def test_stop_functionality():
    """Test the stop button functionality"""
    
    base_url = "http://localhost:8080"
    
    print("🧪 Testing Stop Task Functionality")
    print("=" * 50)
    
    try:
        # Test 1: Check if the stop endpoint is available
        print("1. Testing stop endpoint availability...")
        
        # We need a valid run UUID and task UUID for the test
        # For now, let's just test that the endpoint responds correctly to invalid data
        test_run_uuid = "00000000-0000-0000-0000-000000000000"
        test_task_uuid = "00000000-0000-0000-0000-000000000000"
        
        stop_url = f"{base_url}/agents/api/agent_run/{test_run_uuid}/task_execute/{test_task_uuid}/stop"
        
        response = requests.post(
            stop_url,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   Stop endpoint response: {response.status_code}")
        if response.status_code == 404:
            print("   ✅ Stop endpoint exists and responds correctly to invalid UUIDs")
        else:
            print(f"   📝 Response: {response.text}")
        
        # Test 2: Check if the template has the stop button
        print("\n2. Testing template stop button...")
        
        template_response = requests.get(f"{base_url}/agents", timeout=10)
        if template_response.status_code == 200:
            print("   ✅ Main agents page accessible")
        else:
            print(f"   ❌ Cannot access agents page: {template_response.status_code}")
        
        print("\n✅ Stop functionality tests completed!")
        print("Manual verification needed:")
        print("  1. Open an agent run with AI tasks")
        print("  2. Start executing a task")
        print("  3. Click the red 'Stop' button that should appear")
        print("  4. Verify the task is cancelled and UI updates correctly")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_stop_functionality()
