#!/usr/bin/env python3
"""
Test script for debugging task creation API
"""

import requests
import json
import os
import sys

def test_task_creation():
    """Test the task creation API endpoint"""
    
    # Configuration
    base_url = "http://localhost:5004"
    
    # First, let's test if we can reach the agents list
    try:
        response = requests.get(f"{base_url}/agents")
        print(f"Agents page status: {response.status_code}")
        if response.status_code != 200:
            print("Cannot reach agents page. Is the server running?")
            return False
    except Exception as e:
        print(f"Error reaching server: {e}")
        return False
    
    # Get an existing agent (we'll need to know an agent ID)
    # For testing, let's assume there's an agent with a specific ID
    # You should replace this with an actual agent ID from your system
    test_agent_id = "test-agent-123"  # Replace with real agent ID
    
    # Test data for task creation
    task_data = {
        "name": "Test Task",
        "type": "ai",
        "description": "This is a test task created via API"
    }
    
    # Test the API endpoint
    api_url = f"{base_url}/agents/api/{test_agent_id}/tasks"
    
    print(f"\nTesting API URL: {api_url}")
    print(f"Task data: {json.dumps(task_data, indent=2)}")
    
    try:
        response = requests.post(
            api_url,
            json=task_data,
            headers={
                'Content-Type': 'application/json'
            }
        )
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        print(f"Content-Type: {content_type}")
        
        if 'application/json' in content_type:
            try:
                response_data = response.json()
                print(f"Response JSON: {json.dumps(response_data, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Raw response: {response.text[:500]}")
        else:
            print("Non-JSON response:")
            print(response.text[:1000])
            
    except Exception as e:
        print(f"Request error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing Task Creation API")
    print("=" * 40)
    test_task_creation()
