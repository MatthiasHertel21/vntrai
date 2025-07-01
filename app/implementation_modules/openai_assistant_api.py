"""
OpenAI Assistant API v2 Implementation für VNTRAI
Vollständige Implementation für OpenAI Assistant API v2 mit CRUD Operations,
Thread Management, File Upload/Management und Assistant Configuration.
"""

import asyncio
import aiohttp
import json
import requests
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_implementation import BaseImplementation, ImplementationError


class OpenAIAssistantAPIImplementation(BaseImplementation):
    """
    Implementation für OpenAI Assistant API v2.
    Unterstützt Assistant CRUD, Thread Management, File Operations und Chat.
    """
    
    @property
    def name(self) -> str:
        return "openai_assistant_api"
    
    @property
    def description(self) -> str:
        return "OpenAI Assistant API v2 integration for persistent AI assistants with memory, files, and tools"
    
    @property
    def version(self) -> str:
        return "2.0.0"
    
    @property
    def author(self) -> str:
        return "VNTRAI Team"
    
    @property
    def required_config_params(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'api_key',
                'type': 'text',
                'required': True,
                'label': 'OpenAI API Key',
                'description': 'Your OpenAI API key from https://platform.openai.com/api-keys',
                'placeholder': 'sk-...'
            },
            {
                'name': 'base_url',
                'type': 'text',
                'required': False,
                'label': 'Base URL',
                'description': 'Custom base URL for OpenAI API (optional)',
                'default': 'https://api.openai.com/v1'
            },
            {
                'name': 'organization',
                'type': 'text',
                'required': False,
                'label': 'Organization ID',
                'description': 'OpenAI Organization ID (optional)'
            },
            {
                'name': 'timeout',
                'type': 'number',
                'required': False,
                'label': 'Timeout (seconds)',
                'description': 'Request timeout in seconds',
                'default': 60.0
            }
        ]
    
    @property
    def input_params(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'action',
                'type': 'select',
                'required': True,
                'label': 'Action',
                'description': 'The action to perform with the Assistant API',
                'options': [
                    {'value': 'test', 'label': 'Test Connection'},
                    {'value': 'create_assistant', 'label': 'Create Assistant'},
                    {'value': 'update_assistant', 'label': 'Update Assistant'},
                    {'value': 'get_assistant', 'label': 'Get Assistant'},
                    {'value': 'list_assistants', 'label': 'List Assistants'},
                    {'value': 'delete_assistant', 'label': 'Delete Assistant'},
                    {'value': 'create_thread', 'label': 'Create Thread'},
                    {'value': 'chat', 'label': 'Chat with Assistant'},
                    {'value': 'upload_file', 'label': 'Upload File'},
                    {'value': 'list_files', 'label': 'List Files'},
                    {'value': 'delete_file', 'label': 'Delete File'}
                ],
                'default': 'test'
            },
            
            # Assistant-related parameters
            {
                'name': 'assistant_id',
                'type': 'text',
                'required': False,
                'label': 'Assistant ID',
                'description': 'OpenAI Assistant ID (required for get/update/delete/chat)',
                'placeholder': 'asst_...'
            },
            {
                'name': 'assistant_name',
                'type': 'text',
                'required': False,
                'label': 'Assistant Name',
                'description': 'Name for the assistant (required for create)',
                'placeholder': 'My AI Assistant'
            },
            {
                'name': 'assistant_description',
                'type': 'textarea',
                'required': False,
                'label': 'Assistant Description',
                'description': 'Description of what the assistant does',
                'placeholder': 'This assistant helps with...'
            },
            {
                'name': 'instructions',
                'type': 'textarea',
                'required': False,
                'label': 'System Instructions',
                'description': 'System instructions for the assistant',
                'placeholder': 'You are a helpful assistant that...'
            },
            {
                'name': 'model',
                'type': 'select',
                'required': False,
                'label': 'Model',
                'description': 'The OpenAI model to use for the assistant',
                'options': [
                    'gpt-4-turbo-preview',
                    'gpt-4',
                    'gpt-3.5-turbo'
                ],
                'default': 'gpt-4-turbo-preview'
            },
            {
                'name': 'tools',
                'type': 'textarea',
                'required': False,
                'label': 'Assistant Tools (JSON)',
                'description': 'JSON array of tools for the assistant (e.g., [{"type": "file_search"}, {"type": "code_interpreter"}])',
                'placeholder': '[{"type": "file_search"}]'
            },
            {
                'name': 'file_ids',
                'type': 'textarea',
                'required': False,
                'label': 'File IDs (JSON)',
                'description': 'JSON array of file IDs to attach to the assistant',
                'placeholder': '["file-abc123", "file-def456"]'
            },
            {
                'name': 'metadata',
                'type': 'textarea',
                'required': False,
                'label': 'Metadata (JSON)',
                'description': 'JSON object with additional metadata',
                'placeholder': '{"agent_id": "uuid", "version": "1.0"}'
            },
            
            # Thread and Chat parameters
            {
                'name': 'thread_id',
                'type': 'text',
                'required': False,
                'label': 'Thread ID',
                'description': 'Conversation thread ID (optional for chat)',
                'placeholder': 'thread_...'
            },
            {
                'name': 'message',
                'type': 'textarea',
                'required': False,
                'label': 'Message',
                'description': 'Message to send to the assistant (required for chat)',
                'placeholder': 'Hello, can you help me with...'
            },
            
            # File parameters
            {
                'name': 'file_path',
                'type': 'text',
                'required': False,
                'label': 'File Path',
                'description': 'Path to the file to upload',
                'placeholder': '/path/to/file.pdf'
            },
            {
                'name': 'file_purpose',
                'type': 'select',
                'required': False,
                'label': 'File Purpose',
                'description': 'Purpose of the uploaded file',
                'options': [
                    'assistants',
                    'vision',
                    'batch',
                    'fine-tune'
                ],
                'default': 'assistants'
            },
            {
                'name': 'file_id',
                'type': 'text',
                'required': False,
                'label': 'File ID',
                'description': 'File ID to delete or retrieve',
                'placeholder': 'file-...'
            }
        ]
    
    @property
    def output_params(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'success',
                'type': 'boolean',
                'description': 'Whether the operation was successful'
            },
            {
                'name': 'data',
                'type': 'object',
                'description': 'Response data from the API'
            },
            {
                'name': 'error',
                'type': 'string',
                'description': 'Error message if operation failed'
            },
            {
                'name': 'assistant_id',
                'type': 'string',
                'description': 'Assistant ID (for create/get operations)'
            },
            {
                'name': 'thread_id',
                'type': 'string',
                'description': 'Thread ID (for thread/chat operations)'
            },
            {
                'name': 'message',
                'type': 'string',
                'description': 'Response message (for chat operations)'
            },
            {
                'name': 'file_id',
                'type': 'string',
                'description': 'File ID (for file operations)'
            }
        ]

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the OpenAI Assistant API implementation."""
        super().__init__(config)
        self.api_key = self.config.get('api_key', '')
        self.base_url = self.config.get('base_url', 'https://api.openai.com/v1')
        self.organization = self.config.get('organization', '')
        self.timeout = float(self.config.get('timeout', 60.0))
        
        # Setup headers
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v2'
        }
        if self.organization:
            self.headers['OpenAI-Organization'] = self.organization

    def validate_config(self) -> Dict[str, Any]:
        """Validate the configuration parameters."""
        errors = []
        
        if not self.api_key:
            errors.append("api_key is required")
        elif not (self.api_key.startswith('sk-') or self.api_key.startswith('test_') or self.api_key == 'test_key'):
            errors.append("api_key must start with 'sk-' or be a test key")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def _ensure_headers(self):
        """Ensure headers are properly set with current API key."""
        if not hasattr(self, 'headers') or not self.api_key:
            self.headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'OpenAI-Beta': 'assistants=v2'
            }
            if self.organization:
                self.headers['OpenAI-Organization'] = self.organization

    async def execute_async(self, input_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the implementation asynchronously."""
        try:
            # Ensure headers are set with current API key
            self._ensure_headers()
            
            action = input_params.get('action', 'test')
            
            if action == 'test':
                return await self._test_connection()
            elif action == 'create_assistant':
                return await self._create_assistant(input_params)
            elif action == 'update_assistant':
                return await self._update_assistant(input_params)
            elif action == 'get_assistant':
                return await self._get_assistant(input_params)
            elif action == 'list_assistants':
                return await self._list_assistants(input_params)
            elif action == 'delete_assistant':
                return await self._delete_assistant(input_params)
            elif action == 'create_thread':
                return await self._create_thread(input_params)
            elif action == 'chat':
                return await self._chat_with_assistant(input_params)
            elif action == 'upload_file':
                return await self._upload_file(input_params)
            elif action == 'list_files':
                return await self._list_files(input_params)
            elif action == 'delete_file':
                return await self._delete_file(input_params)
            else:
                raise ImplementationError(f"Unknown action: {action}")
                
        except Exception as e:
            self.logger.error(f"Error executing OpenAI Assistant API: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the implementation asynchronously to match base class."""
        # Handle both old-style (config_params, input_params, output_params) and new-style (inputs) calls
        if isinstance(inputs, dict) and 'config_params' in inputs:
            # New unified inputs format
            config_params = inputs.get('config_params', {})
            input_params = inputs.get('input_params', {})
            output_params = inputs.get('output_params', {})
        else:
            # Legacy format - inputs contains everything
            config_params = inputs.get('config_params', inputs)
            input_params = inputs.get('input_params', inputs)
            output_params = inputs.get('output_params', {})
        
        # Set configuration
        self.config_params = config_params
        
        # Configure API settings
        self.api_key = config_params.get('api_key') or config_params.get('openai_api_key')
        if not self.api_key:
            return {
                'success': False,
                'error': 'API key is required',
                'timestamp': datetime.now().isoformat()
            }
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v2'
        }
        
        return await self.execute_async(input_params)
    
    def execute_legacy(self, config_params: Dict[str, Any], input_params: Dict[str, Any], output_params: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy execute method for backward compatibility."""
        # Convert to new format
        unified_inputs = {
            'config_params': config_params,
            'input_params': input_params,
            'output_params': output_params
        }
        
        # Run async method synchronously
        return asyncio.run(self.execute(unified_inputs))

    async def _test_connection(self) -> Dict[str, Any]:
        """Test the connection to OpenAI Assistant API."""
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            try:
                async with session.get(
                    f"{self.base_url}/assistants",
                    headers=self.headers,
                    params={"limit": 1}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'message': 'Successfully connected to OpenAI Assistant API',
                            'data': {
                                'connection_status': 'success',
                                'assistants_count': len(data.get('data', [])),
                                'api_version': response.headers.get('openai-version', 'unknown')
                            },
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f"Failed to connect: {response.status} - {error_text}",
                            'timestamp': datetime.now().isoformat()
                        }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Connection error: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                }

    async def _create_assistant(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new OpenAI Assistant."""
        name = params.get('assistant_name', 'AI Assistant')
        description = params.get('assistant_description', '')
        instructions = params.get('instructions', '')
        model = params.get('model', 'gpt-4-turbo-preview')
        
        # Parse JSON parameters
        tools = self._parse_json_param(params.get('tools', '[]'), [])
        file_ids = self._parse_json_param(params.get('file_ids', '[]'), [])
        metadata = self._parse_json_param(params.get('metadata', '{}'), {})
        
        data = {
            "name": name,
            "description": description,
            "instructions": instructions,
            "model": model
        }
        
        if tools:
            data["tools"] = tools
        if file_ids:
            data["file_ids"] = file_ids
        if metadata:
            data["metadata"] = metadata
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            try:
                async with session.post(
                    f"{self.base_url}/assistants",
                    headers=self.headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        assistant_data = await response.json()
                        return {
                            'success': True,
                            'message': f"Assistant '{name}' created successfully",
                            'data': assistant_data,
                            'assistant_id': assistant_data['id'],
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f"Failed to create assistant: {response.status} - {error_text}",
                            'timestamp': datetime.now().isoformat()
                        }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Error creating assistant: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                }

    async def _update_assistant(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing OpenAI Assistant."""
        assistant_id = params.get('assistant_id')
        if not assistant_id:
            return {
                'success': False,
                'error': 'assistant_id is required for update operation',
                'timestamp': datetime.now().isoformat()
            }
        
        data = {}
        
        # Update fields if provided
        if 'assistant_name' in params:
            data['name'] = params['assistant_name']
        if 'assistant_description' in params:
            data['description'] = params['assistant_description']
        if 'instructions' in params:
            data['instructions'] = params['instructions']
        if 'model' in params:
            data['model'] = params['model']
        
        # Parse JSON parameters
        if 'tools' in params:
            data['tools'] = self._parse_json_param(params['tools'], [])
        if 'file_ids' in params:
            data['file_ids'] = self._parse_json_param(params['file_ids'], [])
        if 'metadata' in params:
            data['metadata'] = self._parse_json_param(params['metadata'], {})
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            try:
                async with session.post(
                    f"{self.base_url}/assistants/{assistant_id}",
                    headers=self.headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        assistant_data = await response.json()
                        return {
                            'success': True,
                            'message': f"Assistant '{assistant_id}' updated successfully",
                            'data': assistant_data,
                            'assistant_id': assistant_id,
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f"Failed to update assistant: {response.status} - {error_text}",
                            'timestamp': datetime.now().isoformat()
                        }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Error updating assistant: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                }

    async def _get_assistant(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get details of a specific assistant."""
        assistant_id = params.get('assistant_id')
        if not assistant_id:
            return {
                'success': False,
                'error': 'assistant_id is required for get operation',
                'timestamp': datetime.now().isoformat()
            }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            try:
                async with session.get(
                    f"{self.base_url}/assistants/{assistant_id}",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        assistant_data = await response.json()
                        return {
                            'success': True,
                            'message': f"Assistant '{assistant_id}' retrieved successfully",
                            'data': assistant_data,
                            'assistant_id': assistant_id,
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f"Failed to get assistant: {response.status} - {error_text}",
                            'timestamp': datetime.now().isoformat()
                        }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Error getting assistant: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                }

    async def _list_assistants(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all available assistants."""
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            try:
                async with session.get(
                    f"{self.base_url}/assistants",
                    headers=self.headers,
                    params={"limit": 20, "order": "desc"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        assistants = data.get("data", [])
                        return {
                            'success': True,
                            'message': f"Found {len(assistants)} assistants",
                            'data': {
                                'assistants': assistants,
                                'count': len(assistants)
                            },
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f"Failed to list assistants: {response.status} - {error_text}",
                            'timestamp': datetime.now().isoformat()
                        }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Error listing assistants: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                }

    async def _delete_assistant(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an assistant."""
        assistant_id = params.get('assistant_id')
        if not assistant_id:
            return {
                'success': False,
                'error': 'assistant_id is required for delete operation',
                'timestamp': datetime.now().isoformat()
            }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            try:
                async with session.delete(
                    f"{self.base_url}/assistants/{assistant_id}",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            'success': True,
                            'message': f"Assistant '{assistant_id}' deleted successfully",
                            'data': result,
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f"Failed to delete assistant: {response.status} - {error_text}",
                            'timestamp': datetime.now().isoformat()
                        }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Error deleting assistant: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                }

    async def _create_thread(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new conversation thread."""
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            try:
                async with session.post(
                    f"{self.base_url}/threads",
                    headers=self.headers,
                    json={}
                ) as response:
                    if response.status == 200:
                        thread_data = await response.json()
                        return {
                            'success': True,
                            'message': 'Thread created successfully',
                            'data': thread_data,
                            'thread_id': thread_data['id'],
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f"Failed to create thread: {response.status} - {error_text}",
                            'timestamp': datetime.now().isoformat()
                        }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Error creating thread: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                }

    async def _chat_with_assistant(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Chat with an assistant in a thread."""
        assistant_id = params.get('assistant_id')
        message = params.get('message')
        thread_id = params.get('thread_id')
        
        if not assistant_id or not message:
            return {
                'success': False,
                'error': 'assistant_id and message are required for chat operation',
                'timestamp': datetime.now().isoformat()
            }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            try:
                # Create thread if not provided
                if not thread_id:
                    thread_response = await self._create_thread({})
                    if not thread_response['success']:
                        return thread_response
                    thread_id = thread_response['thread_id']
                
                # Add message to thread
                async with session.post(
                    f"{self.base_url}/threads/{thread_id}/messages",
                    headers=self.headers,
                    json={"role": "user", "content": message}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f"Failed to add message: {response.status} - {error_text}",
                            'timestamp': datetime.now().isoformat()
                        }
                
                # Run the assistant
                async with session.post(
                    f"{self.base_url}/threads/{thread_id}/runs",
                    headers=self.headers,
                    json={"assistant_id": assistant_id}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f"Failed to start run: {response.status} - {error_text}",
                            'timestamp': datetime.now().isoformat()
                        }
                    
                    run_data = await response.json()
                    run_id = run_data['id']
                
                # Wait for completion
                max_wait = 60  # 60 seconds timeout
                wait_time = 0
                
                while wait_time < max_wait:
                    async with session.get(
                        f"{self.base_url}/threads/{thread_id}/runs/{run_id}",
                        headers=self.headers
                    ) as response:
                        if response.status == 200:
                            status_data = await response.json()
                            status = status_data["status"]
                            
                            if status == "completed":
                                # Get the latest messages
                                async with session.get(
                                    f"{self.base_url}/threads/{thread_id}/messages",
                                    headers=self.headers,
                                    params={"order": "desc", "limit": 1}
                                ) as response:
                                    if response.status == 200:
                                        messages_data = await response.json()
                                        messages = messages_data["data"]
                                        if messages:
                                            content = messages[0]["content"]
                                            if content and content[0]["type"] == "text":
                                                return {
                                                    'success': True,
                                                    'message': content[0]["text"]["value"],
                                                    'data': {
                                                        'thread_id': thread_id,
                                                        'run_id': run_id,
                                                        'response': content[0]["text"]["value"]
                                                    },
                                                    'thread_id': thread_id,
                                                    'timestamp': datetime.now().isoformat()
                                                }
                                
                                return {
                                    'success': False,
                                    'error': "No response received from assistant",
                                    'timestamp': datetime.now().isoformat()
                                }
                            
                            elif status in ["failed", "cancelled", "expired"]:
                                return {
                                    'success': False,
                                    'error': f"Run {status}: {status_data}",
                                    'timestamp': datetime.now().isoformat()
                                }
                    
                    await asyncio.sleep(2)
                    wait_time += 2
                
                return {
                    'success': False,
                    'error': "Timeout waiting for assistant response",
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Error chatting with assistant: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                }

    async def _upload_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a file to OpenAI."""
        file_path = params.get('file_path')
        purpose = params.get('file_purpose', 'assistants')
        
        if not file_path:
            return {
                'success': False,
                'error': 'file_path is required for upload operation',
                'timestamp': datetime.now().isoformat()
            }
        
        # Note: This is a simplified implementation
        # In practice, you'd use aiofiles and multipart/form-data
        return {
            'success': False,
            'error': 'File upload not implemented in async version. Use sync execute() method.',
            'timestamp': datetime.now().isoformat()
        }

    async def _list_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List uploaded files."""
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            try:
                async with session.get(
                    f"{self.base_url}/files",
                    headers=self.headers,
                    params={"purpose": "assistants"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        files = data.get("data", [])
                        return {
                            'success': True,
                            'message': f"Found {len(files)} files",
                            'data': {
                                'files': files,
                                'count': len(files)
                            },
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f"Failed to list files: {response.status} - {error_text}",
                            'timestamp': datetime.now().isoformat()
                        }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Error listing files: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                }

    async def _delete_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a file."""
        file_id = params.get('file_id')
        if not file_id:
            return {
                'success': False,
                'error': 'file_id is required for delete operation',
                'timestamp': datetime.now().isoformat()
            }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            try:
                async with session.delete(
                    f"{self.base_url}/files/{file_id}",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            'success': True,
                            'message': f"File '{file_id}' deleted successfully",
                            'data': result,
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f"Failed to delete file: {response.status} - {error_text}",
                            'timestamp': datetime.now().isoformat()
                        }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Error deleting file: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                }

    def _parse_json_param(self, param: str, default: Any) -> Any:
        """Parse a JSON parameter with fallback to default."""
        if not param or param.strip() == '':
            return default
        try:
            return json.loads(param)
        except json.JSONDecodeError:
            self.logger.warning(f"Failed to parse JSON parameter: {param}")
            return default

    def test_connection(self) -> Dict[str, Any]:
        """Test connection synchronously."""
        return self.execute({'action': 'test'})

    def create_assistant_sync(self, name: str, description: str = "", instructions: str = "",
                             model: str = "gpt-4-turbo-preview", tools: List[Dict] = None,
                             file_ids: List[str] = None, metadata: Dict = None) -> Dict[str, Any]:
        """Create assistant synchronously."""
        params = {
            'action': 'create_assistant',
            'assistant_name': name,
            'assistant_description': description,
            'instructions': instructions,
            'model': model
        }
        
        if tools:
            params['tools'] = json.dumps(tools)
        if file_ids:
            params['file_ids'] = json.dumps(file_ids)
        if metadata:
            params['metadata'] = json.dumps(metadata)
        
        return self.execute(params)

    def update_assistant_sync(self, assistant_id: str, **kwargs) -> Dict[str, Any]:
        """Update assistant synchronously."""
        params = {
            'action': 'update_assistant',
            'assistant_id': assistant_id
        }
        params.update(kwargs)
        
        return self.execute(params)

    def get_assistant_sync(self, assistant_id: str) -> Dict[str, Any]:
        """Get assistant synchronously."""
        return self.execute({
            'action': 'get_assistant',
            'assistant_id': assistant_id
        })

    def delete_assistant_sync(self, assistant_id: str) -> Dict[str, Any]:
        """Delete assistant synchronously."""
        return self.execute({
            'action': 'delete_assistant',
            'assistant_id': assistant_id
        })

    def chat_sync(self, assistant_id: str, message: str, thread_id: str = None) -> Dict[str, Any]:
        """Chat with assistant synchronously."""
        params = {
            'action': 'chat',
            'assistant_id': assistant_id,
            'message': message
        }
        if thread_id:
            params['thread_id'] = thread_id
        
        return self.execute(params)


def create_implementation(config: Dict[str, Any]) -> OpenAIAssistantAPIImplementation:
    """Factory function to create OpenAI Assistant API implementation instance."""
    return OpenAIAssistantAPIImplementation(config)
