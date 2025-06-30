#!/usr/bin/env python3
"""
Script to create a test tool based on OpenAI Assistant API Integration
for Sprint 17 testing
"""

import json
import uuid
from datetime import datetime
import os

def create_test_assistant_tool():
    """Create a test tool that uses the OpenAI Assistant API integration"""
    
    # Tool data
    tool_data = {
        "id": str(uuid.uuid4()),
        "name": "AI Assistant Chat Tool",
        "description": "A tool for chatting with an AI assistant using OpenAI Assistant API",
        "implementation": "openai_assistant_api",
        "integration_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "version": "1.0.0",
        "status": "active",
        "category": "ai",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "last_used": None,
        "usage_count": 0,
        "config_params": [
            {
                "name": "assistant_name",
                "label": "Assistant Name",
                "type": "text",
                "required": True,
                "default": "AI Chat Assistant",
                "description": "Name for the AI assistant"
            },
            {
                "name": "assistant_instructions",
                "label": "Assistant Instructions", 
                "type": "textarea",
                "required": False,
                "default": "You are a helpful AI assistant. Answer questions clearly and concisely.",
                "description": "Instructions for how the assistant should behave"
            },
            {
                "name": "model",
                "label": "AI Model",
                "type": "select",
                "required": True,
                "default": "gpt-4-turbo-preview",
                "options": [
                    {"value": "gpt-4-turbo-preview", "label": "GPT-4 Turbo Preview"},
                    {"value": "gpt-4", "label": "GPT-4"},
                    {"value": "gpt-3.5-turbo", "label": "GPT-3.5 Turbo"}
                ],
                "description": "AI model to use for the assistant"
            }
        ],
        "input_params": [
            {
                "name": "message",
                "label": "Message",
                "type": "textarea",
                "required": True,
                "description": "Message to send to the AI assistant"
            },
            {
                "name": "thread_id",
                "label": "Thread ID",
                "type": "text",
                "required": False,
                "description": "Optional thread ID to continue conversation (leave empty for new thread)"
            }
        ],
        "output_params": [
            {
                "name": "response",
                "label": "AI Response",
                "type": "text",
                "description": "Response from the AI assistant"
            },
            {
                "name": "thread_id",
                "label": "Thread ID",
                "type": "text",
                "description": "Thread ID for continuing the conversation"
            },
            {
                "name": "assistant_id",
                "label": "Assistant ID",
                "type": "text",
                "description": "ID of the assistant used"
            }
        ],
        "options": {
            "assistant": {
                "enabled": True,
                "auto_create": True,
                "use_agent_instructions": True,
                "support_files": True,
                "support_functions": False
            }
        },
        "metadata": {
            "tags": ["ai", "chat", "assistant", "openai"],
            "sprint": "17",
            "test_tool": True
        }
    }
    
    # Create data/tools directory if it doesn't exist
    tools_dir = "data/tools"
    os.makedirs(tools_dir, exist_ok=True)
    
    # Write tool data to file
    tool_file = os.path.join(tools_dir, f"{tool_data['id']}.json")
    with open(tool_file, 'w', encoding='utf-8') as f:
        json.dump(tool_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Test tool created successfully!")
    print(f"📁 Tool ID: {tool_data['id']}")
    print(f"📁 Tool Name: {tool_data['name']}")
    print(f"📁 File: {tool_file}")
    print(f"🔗 Integration: OpenAI Assistant API ({tool_data['integration_id']})")
    print(f"⚙️  Assistant Options: {tool_data['options']['assistant']}")
    
    return tool_data

if __name__ == "__main__":
    create_test_assistant_tool()
