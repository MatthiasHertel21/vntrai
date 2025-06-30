#!/usr/bin/env python3
"""
Sprint 17 Test Tool Creation Script
Creates a test tool based on OpenAI Assistant API Integration for testing Sprint 17 features
"""

import json
import uuid
from datetime import datetime

def create_assistant_test_tool():
    """Create a test tool with OpenAI Assistant API Integration"""
    
    tool_id = str(uuid.uuid4())
    current_time = datetime.now().isoformat()
    
    tool_data = {
        "id": tool_id,
        "name": "AI Assistant Test Tool",
        "description": "Test tool for Sprint 17 - AI Assistant Integration with OpenAI Assistant API",
        "category": "AI Assistant",
        "type": "api",
        "status": "connected",  # Valid status!
        "integration_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",  # OpenAI Assistant API Integration
        "implementation": "openai_assistant_api",
        "version": "1.0.0",
        "created_at": current_time,
        "updated_at": current_time,
        "last_used": None,
        "usage_count": 0,
        "config_params": [
            {
                "name": "assistant_name",
                "label": "Assistant Name",
                "type": "text",
                "required": True,
                "description": "Name for the OpenAI Assistant",
                "default": "Test Assistant"
            },
            {
                "name": "assistant_description",
                "label": "Assistant Description", 
                "type": "textarea",
                "required": False,
                "description": "Description of what the assistant does"
            },
            {
                "name": "model",
                "label": "AI Model",
                "type": "select",
                "required": True,
                "options": [
                    {"label": "GPT-4 Turbo", "value": "gpt-4-turbo-preview"},
                    {"label": "GPT-4", "value": "gpt-4"},
                    {"label": "GPT-3.5 Turbo", "value": "gpt-3.5-turbo"}
                ],
                "default": "gpt-4-turbo-preview",
                "description": "OpenAI model to use for the assistant"
            }
        ],
        "input_params": [
            {
                "name": "message",
                "label": "Message",
                "type": "textarea",
                "required": True,
                "description": "Message to send to the assistant"
            },
            {
                "name": "instructions",
                "label": "Additional Instructions",
                "type": "textarea", 
                "required": False,
                "description": "Additional instructions for this specific request"
            }
        ],
        "output_params": [
            {
                "name": "response",
                "label": "Assistant Response",
                "type": "text",
                "description": "Response from the OpenAI Assistant"
            },
            {
                "name": "assistant_id", 
                "label": "Assistant ID",
                "type": "text",
                "description": "ID of the OpenAI Assistant used"
            },
            {
                "name": "thread_id",
                "label": "Thread ID", 
                "type": "text",
                "description": "ID of the conversation thread"
            },
            {
                "name": "run_id",
                "label": "Run ID",
                "type": "text", 
                "description": "ID of the assistant run"
            }
        ],
        "options": {
            "assistant": {
                "enabled": True,
                "description": "This tool provides AI Assistant functionality",
                "capabilities": ["chat", "function_calling", "file_handling"],
                "assistant_id": None,  # Will be set when assistant is created
                "thread_id": None,    # Will be set when thread is created
                "settings": {
                    "model": "gpt-4-turbo-preview",
                    "instructions": "You are a helpful AI assistant for testing Sprint 17 features.",
                    "tools": ["code_interpreter", "retrieval"],
                    "file_ids": []
                }
            },
            "streaming": {
                "enabled": True,
                "description": "Support for streaming responses"
            },
            "file_upload": {
                "enabled": True,
                "description": "Support for file uploads to assistant"
            }
        },
        "metadata": {
            "sprint": "Sprint 17",
            "purpose": "AI Assistant Integration Testing",
            "openai_assistant_version": "v2",
            "test_scenarios": [
                "Basic chat functionality",
                "File upload and processing", 
                "Function calling",
                "Streaming responses",
                "Agent-Tool connection"
            ]
        }
    }
    
    # Save tool to file
    filename = f"/home/ga/fb1/age/data/tools/{tool_id}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(tool_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Test Tool created successfully!")
    print(f"   Tool ID: {tool_id}")
    print(f"   Name: {tool_data['name']}")
    print(f"   Status: {tool_data['status']}")
    print(f"   Integration: {tool_data['integration_id']}")
    print(f"   Assistant enabled: {tool_data['options']['assistant']['enabled']}")
    print(f"   File: {filename}")
    
    return tool_id

if __name__ == "__main__":
    create_assistant_test_tool()
