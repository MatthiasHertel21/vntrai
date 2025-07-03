"""
Test the OpenAI Assistant API connection
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to sys.path to allow importing from app
parent_dir = str(Path(__file__).resolve().parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.utils.openai_assistant_wrapper import OpenAIAssistantAPI
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_openai_assistant_api():
    """Test OpenAI Assistant API connection"""
    # Try to get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        logging.info("Using API key from environment variable")
    else:
        logging.warning("No API key found in environment variable")
    
    # Initialize API wrapper
    try:
        api = OpenAIAssistantAPI(api_key=api_key)
        logging.info("OpenAI Assistant API wrapper initialized")
        
        # Try to list assistants
        assistants = api.list_assistants()
        if isinstance(assistants, list):
            logging.info(f"Successfully retrieved {len(assistants)} assistants")
            for assistant in assistants:
                if isinstance(assistant, dict):
                    logging.info(f"Assistant: {assistant.get('name', 'Unnamed')} (ID: {assistant.get('id', 'Unknown')})")
                else:
                    logging.warning(f"Assistant is not a dict but {type(assistant)}: {assistant}")
            return True
        else:
            logging.error(f"Failed to list assistants, received: {assistants}")
            return False
    except Exception as e:
        logging.error(f"Error testing OpenAI Assistant API: {e}")
        return False

if __name__ == "__main__":
    success = test_openai_assistant_api()
    print(f"Test {'successful' if success else 'failed'}")
    sys.exit(0 if success else 1)
