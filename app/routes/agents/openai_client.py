"""
OpenAI Client Integration
Handles OpenAI API interactions and thread operations
"""

import requests
import time
import json
from .api_utils import log_error, log_info
from .thread_management import ensure_thread_is_clean


class OpenAIClient:
    """Client for OpenAI Assistant API operations"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v2'
        }
    
    def create_thread(self):
        """Create a new OpenAI thread"""
        try:
            response = requests.post(
                'https://api.openai.com/v1/threads',
                headers=self.headers,
                json={},
                timeout=30
            )
            
            if response.status_code == 200:
                thread_data = response.json()
                return True, thread_data['id'], None
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                return False, None, error_msg
                
        except Exception as e:
            return False, None, str(e)
    
    def add_message_to_thread(self, thread_id, content):
        """Add a message to an existing thread"""
        try:
            # Ensure thread is clean before adding message
            is_clean, error_msg = ensure_thread_is_clean(thread_id, self.headers)
            if not is_clean:
                return False, error_msg
            
            log_info(f"Adding message to thread {thread_id}")
            response = requests.post(
                f'https://api.openai.com/v1/threads/{thread_id}/messages',
                headers=self.headers,
                json={"role": "user", "content": content},
                timeout=30
            )
            
            if response.status_code == 200:
                return True, None
            else:
                error_msg = f"Failed to add message: {response.status_code} - {response.text}"
                log_error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error adding message: {str(e)}"
            log_error(error_msg)
            return False, error_msg
    
    def create_run_stream(self, thread_id, assistant_id):
        """Create a streaming run on a thread using v2 API"""
        try:
            log_info("Creating new streaming run")
            response = requests.post(
                f'https://api.openai.com/v1/threads/{thread_id}/runs',
                headers=self.headers,
                json={
                    "assistant_id": assistant_id,
                    "stream": True
                },
                stream=True,
                timeout=30
            )
            
            if response.status_code == 200:
                log_info(f"Started streaming run for thread {thread_id}")
                return True, response, None
            else:
                error_msg = f"Failed to create streaming run: {response.status_code} - {response.text}"
                log_error(error_msg)
                return False, None, error_msg
                
        except Exception as e:
            error_msg = f"Error creating streaming run: {str(e)}"
            log_error(error_msg)
            return False, None, error_msg

    def create_run(self, thread_id, assistant_id):
        """Create a new run on a thread"""
        try:
            log_info("Creating new run")
            response = requests.post(
                f'https://api.openai.com/v1/threads/{thread_id}/runs',
                headers=self.headers,
                json={"assistant_id": assistant_id},
                timeout=30
            )
            
            if response.status_code == 200:
                run_data = response.json()
                run_id = run_data['id']
                log_info(f"Created new run: {run_id}")
                return True, run_id, None
            else:
                error_msg = f"Failed to create run: {response.status_code} - {response.text}"
                log_error(error_msg)
                return False, None, error_msg
                
        except Exception as e:
            error_msg = f"Error creating run: {str(e)}"
            log_error(error_msg)
            return False, None, error_msg
    
    def poll_run_completion(self, thread_id, run_id, max_attempts=60):
        """Poll for run completion with timeout"""
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            time.sleep(1)
            
            try:
                status_response = requests.get(
                    f'https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}',
                    headers=self.headers,
                    timeout=30
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status')
                    
                    if status == 'completed':
                        return True, 'completed', None
                        
                    elif status in ['failed', 'cancelled', 'expired']:
                        error_msg = f"Run {status}: {status_data.get('last_error', {}).get('message', 'Unknown error')}"
                        return False, status, error_msg
                        
                    # Status is still in_progress, queued, or requires_action - continue polling
                    
                else:
                    error_msg = f"Failed to check run status: {status_response.status_code}"
                    return False, 'error', error_msg
                    
            except Exception as e:
                error_msg = f"Error polling run status: {str(e)}"
                return False, 'error', error_msg
        
        # Timeout reached
        return False, 'timeout', "Timeout waiting for AI response"
    
    def get_thread_messages(self, thread_id):
        """Get messages from a thread"""
        try:
            response = requests.get(
                f'https://api.openai.com/v1/threads/{thread_id}/messages',
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                messages_data = response.json()
                messages = messages_data.get('data', [])
                
                # Get the latest assistant message
                for message in messages:
                    if message.get('role') == 'assistant':
                        content_blocks = message.get('content', [])
                        if content_blocks and len(content_blocks) > 0:
                            text_content = content_blocks[0].get('text', {})
                            response_content = text_content.get('value', 'No content')
                            return True, response_content, None
                
                return True, "No response received", None
                
            else:
                error_msg = f"Failed to get messages: {response.status_code}"
                return False, None, error_msg
                
        except Exception as e:
            error_msg = f"Error getting messages: {str(e)}"
            return False, None, error_msg
    
    def create_streaming_run(self, thread_id, assistant_id):
        """Create a streaming run using OpenAI Assistants API v2"""
        import openai
        
        try:
            # Initialize OpenAI client with API key
            client = openai.OpenAI(api_key=self.api_key)
            
            log_info("Creating new streaming run")
            
            # Create streaming run
            stream = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id,
                stream=True
            )
            
            log_info(f"Started streaming run for thread {thread_id}")
            return stream
            
        except Exception as e:
            log_error(f"Error creating streaming run: {str(e)}")
            return None
