"""
Create OpenAI integration if it doesn't exist
"""

import os
import json
from pathlib import Path
import uuid

def create_openai_assistant_integration():
    """
    Create OpenAI Assistant API integration if it doesn't exist
    """
    data_dir = Path(__file__).parent / "data" / "integrations"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if we already have an OpenAI Assistant API integration
    found = False
    for file_path in data_dir.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                integration = json.load(f)
                if (integration.get('implementation') == 'openai_assistant_api' or 
                    'OpenAI Assistant' in integration.get('name', '') or
                    'OpenAI Assistant' in integration.get('description', '')):
                    print(f"OpenAI Assistant API integration already exists: {file_path}")
                    found = True
                    break
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {file_path}: {e}")
            continue
    
    if found:
        return
    
    # Create new integration
    integration_id = str(uuid.uuid4())
    integration = {
        "id": integration_id,
        "name": "OpenAI Assistant API",
        "vendor": "OpenAI",
        "type": "api",
        "description": "Integration with OpenAI Assistant API v2",
        "status": "active",
        "implementation": "openai_assistant_api",
        "config_params": {
            "api_key": os.environ.get("OPENAI_API_KEY", ""),
            "base_url": "https://api.openai.com/v1",
            "timeout": 60.0
        },
        "version": "1.0.0",
        "created_at": "2025-07-01T00:00:00.000000",
        "updated_at": "2025-07-01T00:00:00.000000",
        "api_documentation_link": "https://platform.openai.com/docs/api-reference/assistants",
        "vendor_icon": ""
    }
    
    file_path = data_dir / f"{integration_id}.json"
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(integration, f, indent=2, ensure_ascii=False)
        print(f"Created OpenAI Assistant API integration: {file_path}")
        return integration_id
    except IOError as e:
        print(f"Error creating OpenAI integration: {e}")
        return None

if __name__ == "__main__":
    create_openai_assistant_integration()
