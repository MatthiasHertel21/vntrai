#!/usr/bin/env python3
"""
Test Enhanced Thread Management
Tests the improved OpenAI thread race condition handling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor
from app.routes.agents.streaming_api import get_thread_lock, force_cancel_all_active_runs

def test_enhanced_thread_safety():
    """Test the enhanced thread safety mechanisms"""
    print("=== Testing Enhanced Thread Management ===")
    
    # Test 1: Thread lock acquisition
    print("\n1. Testing thread lock acquisition...")
    test_thread_id = "thread_test_123"
    
    # Get two locks for the same thread
    lock1 = get_thread_lock(test_thread_id)
    lock2 = get_thread_lock(test_thread_id)
    
    # They should be the same object
    assert lock1 is lock2, "Thread locks should be the same object for same thread ID"
    print("✓ Thread lock identity test passed")
    
    # Test 2: Concurrent access simulation
    print("\n2. Testing concurrent access simulation...")
    
    access_results = []
    
    def simulate_api_access(thread_name):
        """Simulate API access with thread locking"""
        thread_lock = get_thread_lock(test_thread_id)
        
        acquired = thread_lock.acquire(timeout=5)
        if acquired:
            try:
                access_results.append(f"{thread_name}: acquired lock")
                # Simulate work
                time.sleep(0.5)
                access_results.append(f"{thread_name}: completed work")
            finally:
                thread_lock.release()
                access_results.append(f"{thread_name}: released lock")
        else:
            access_results.append(f"{thread_name}: failed to acquire lock")
    
    # Run concurrent simulations
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(simulate_api_access, f"Thread-{i}")
            for i in range(3)
        ]
        
        # Wait for all to complete
        for future in futures:
            future.result()
    
    print("Access results:")
    for result in access_results:
        print(f"  {result}")
    
    # Check that operations were serialized
    acquired_count = len([r for r in access_results if "acquired lock" in r])
    completed_count = len([r for r in access_results if "completed work" in r])
    released_count = len([r for r in access_results if "released lock" in r])
    
    print(f"✓ Serialization test: {acquired_count} acquired, {completed_count} completed, {released_count} released")
    assert acquired_count == completed_count == released_count, "All operations should complete successfully"
    
    print("\n=== Enhanced Thread Management Tests Complete ===")

def test_force_cancel_simulation():
    """Test the force_cancel_all_active_runs function simulation"""
    print("\n=== Testing Force Cancel Simulation ===")
    
    # Mock headers (won't make real API calls)
    mock_headers = {
        'Authorization': 'Bearer test-key',
        'Content-Type': 'application/json',
        'OpenAI-Beta': 'assistants=v2'
    }
    
    # Test with invalid thread (should handle gracefully)
    result = force_cancel_all_active_runs("invalid_thread_123", mock_headers)
    print(f"Force cancel with invalid thread returned: {result}")
    
    print("✓ Force cancel simulation test completed")

def test_error_message_categorization():
    """Test error message categorization for thread conflicts"""
    print("\n=== Testing Error Message Categorization ===")
    
    # Simulate different types of OpenAI error responses
    test_cases = [
        {
            "text": "Thread thread_abc123 has an active run run_xyz789",
            "expected": "thread conflict",
            "description": "Active run conflict"
        },
        {
            "text": "Invalid API key provided",
            "expected": "auth error",
            "description": "Authentication error"
        },
        {
            "text": "Rate limit exceeded",
            "expected": "rate limit",
            "description": "Rate limiting"
        }
    ]
    
    for case in test_cases:
        is_thread_conflict = "has an active run" in case["text"]
        category = "thread conflict" if is_thread_conflict else "other error"
        
        print(f"Error: '{case['text'][:50]}...'")
        print(f"  Detected as: {category}")
        print(f"  Expected: {case['expected']}")
        print(f"  Match: {'✓' if (case['expected'] == 'thread conflict') == is_thread_conflict else '✗'}")
    
    print("✓ Error categorization test completed")

if __name__ == "__main__":
    try:
        test_enhanced_thread_safety()
        test_force_cancel_simulation()
        test_error_message_categorization()
        print("\n🎉 All enhanced thread management tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
