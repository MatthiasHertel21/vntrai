#!/usr/bin/env python3
"""
Test script to verify streaming API fixes for concurrent execution issues
Run with: sudo docker exec web_1 python test_streaming_fixes.py
"""

import sys
import os
import threading
import time
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the app directory to Python path
sys.path.append('/app')

def test_thread_lock_mechanism():
    """Test the thread locking mechanism"""
    print("Testing thread lock mechanism...")
    
    # Import after adding to path
    try:
        from app.routes.agents.streaming_api import get_thread_lock
        
        # Test creating locks for the same thread ID
        thread_id = "test_thread_123"
        
        lock1 = get_thread_lock(thread_id)
        lock2 = get_thread_lock(thread_id)
        
        # Should be the same lock object
        if lock1 is lock2:
            print("✓ Thread lock mechanism works correctly - same object returned")
        else:
            print("✗ Thread lock mechanism failed - different objects returned")
            return False
            
        # Test acquiring and releasing lock
        acquired = lock1.acquire(timeout=1)
        if acquired:
            print("✓ Lock acquired successfully")
            lock1.release()
            print("✓ Lock released successfully")
        else:
            print("✗ Failed to acquire lock")
            return False
            
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing thread locks: {e}")
        return False

def test_request_context_handling():
    """Test that request context issues are resolved"""
    print("\nTesting request context handling...")
    
    try:
        from app.routes.agents.streaming_api import build_context_prompt
        
        # Test building context prompt without Flask request context
        task_def = {
            'name': 'Test Task',
            'description': 'Test description',
            'output': {'type': 'text'}
        }
        
        task_inputs = {'test_input': 'test_value'}
        
        agent = {
            'name': 'Test Agent',
            'description': 'Test agent description'
        }
        
        prompt = build_context_prompt(task_def, task_inputs, agent)
        
        if prompt and len(prompt) > 0:
            print("✓ Context prompt building works without Flask context")
            print(f"  Generated prompt length: {len(prompt)} characters")
        else:
            print("✗ Context prompt building failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Error testing context handling: {e}")
        return False

def test_concurrent_access_simulation():
    """Simulate concurrent access to test race condition prevention"""
    print("\nTesting concurrent access simulation...")
    
    try:
        from app.routes.agents.streaming_api import get_thread_lock
        
        thread_id = "concurrent_test_thread"
        results = []
        
        def worker(worker_id):
            """Worker function to simulate concurrent access"""
            try:
                lock = get_thread_lock(thread_id)
                start_time = time.time()
                
                # Try to acquire lock with timeout
                acquired = lock.acquire(timeout=5)
                acquire_time = time.time()
                
                if acquired:
                    # Hold the lock for a short time
                    time.sleep(0.1)
                    lock.release()
                    release_time = time.time()
                    
                    results.append({
                        'worker_id': worker_id,
                        'success': True,
                        'acquire_duration': acquire_time - start_time,
                        'hold_duration': release_time - acquire_time
                    })
                else:
                    results.append({
                        'worker_id': worker_id,
                        'success': False,
                        'error': 'Lock acquisition timeout'
                    })
                    
            except Exception as e:
                results.append({
                    'worker_id': worker_id,
                    'success': False,
                    'error': str(e)
                })
        
        # Start multiple workers concurrently
        num_workers = 5
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker, i) for i in range(num_workers)]
            
            # Wait for all workers to complete
            for future in as_completed(futures, timeout=30):
                future.result()
        
        # Analyze results
        successful_workers = [r for r in results if r['success']]
        failed_workers = [r for r in results if not r['success']]
        
        print(f"  Successful workers: {len(successful_workers)}")
        print(f"  Failed workers: {len(failed_workers)}")
        
        if len(successful_workers) == num_workers:
            print("✓ All workers completed successfully - no race conditions detected")
            
            # Check that workers were serialized (not all acquired lock instantly)
            acquire_times = [r['acquire_duration'] for r in successful_workers]
            if max(acquire_times) > 0.05:  # At least one worker had to wait
                print("✓ Lock serialization working correctly")
            else:
                print("⚠ All workers acquired lock instantly - may indicate issue")
                
        else:
            print("✗ Some workers failed - potential concurrency issues")
            for failed in failed_workers:
                print(f"    Worker {failed['worker_id']}: {failed['error']}")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Error testing concurrent access: {e}")
        return False
    
    print("Concurrent access results:")
    for result in results:
        print(f"  {result}")
    
    # Should have exactly 1 acquire and 1 release, and 2 timeouts
    acquires = len([r for r in results if "acquired" in r])
    releases = len([r for r in results if "released" in r])
    timeouts = len([r for r in results if "timeout" in r])
    
    print(f"Acquires: {acquires}, Releases: {releases}, Timeouts: {timeouts}")
    assert acquires == 1, f"Expected 1 acquire, got {acquires}"
    assert releases == 1, f"Expected 1 release, got {releases}"
    assert timeouts == 2, f"Expected 2 timeouts, got {timeouts}"
    
    print("✓ Concurrent access test passed")
    print("All thread lock tests passed!")

def test_imports():
    """Test that all required modules can be imported"""
    print("\nTesting imports...")
    
    try:
        from app.routes.agents.streaming_api import (
            get_thread_lock,
            force_cancel_all_active_runs,
            build_context_prompt,
            resolve_variables,
            render_response_content
        )
        print("✓ All streaming API functions imported successfully")
        
        from app.utils.data_manager import agent_run_manager, agents_manager, tools_manager
        print("✓ Data managers imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing imports: {e}")
        return False

def test_variable_resolution():
    """Test variable resolution functionality"""
    print("\nTesting variable resolution...")
    
    try:
        from app.routes.agents.streaming_api import resolve_variables
        
        # Test cases
        test_cases = [
            {
                'text': 'Hello {{name}}, welcome to {{place}}!',
                'variables': {'name': 'Alice', 'place': 'Wonderland'},
                'expected': 'Hello Alice, welcome to Wonderland!'
            },
            {
                'text': 'No variables here',
                'variables': {'unused': 'value'},
                'expected': 'No variables here'
            },
            {
                'text': '{{missing}} variable',
                'variables': {'other': 'value'},
                'expected': '{{missing}} variable'
            }
        ]
        
        all_passed = True
        for i, test_case in enumerate(test_cases):
            result = resolve_variables(test_case['text'], test_case['variables'])
            if result == test_case['expected']:
                print(f"✓ Test case {i+1} passed")
            else:
                print(f"✗ Test case {i+1} failed:")
                print(f"    Expected: {test_case['expected']}")
                print(f"    Got: {result}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Error testing variable resolution: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("STREAMING API FIXES TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_thread_lock_mechanism,
        test_request_context_handling,
        test_variable_resolution,
        test_concurrent_access_simulation
    ]
    
    results = []
    
    for test_func in tests:
        try:
            result = test_func()
            results.append((test_func.__name__, result))
        except Exception as e:
            print(f"✗ Test {test_func.__name__} crashed: {e}")
            results.append((test_func.__name__, False))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The streaming API fixes should resolve the concurrent execution issues.")
        return 0
    else:
        print("❌ Some tests failed. The fixes may need additional work.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
