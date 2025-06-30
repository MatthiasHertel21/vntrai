"""
OpenAI Assistant API Client Utility
Centralized client for OpenAI Assistant API operations, used by agents and other components.
"""

import json
import requests
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OpenAIAssistantClient:
    """
    Client for OpenAI Assistant API operations.
    Used by agents to manage assistants, threads, and conversations.
    """
    
    def __init__(self, api_key: str, organization: str = None, base_url: str = None):
        """
        Initialize the OpenAI Assistant API client.
        
        Args:
            api_key: OpenAI API key
            organization: Optional organization ID
            base_url: Optional custom base URL
        """
        self.api_key = api_key
        self.organization = organization
        self.base_url = base_url or "https://api.openai.com/v1"
        
        # Setup headers
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v2'
        }
        
        if self.organization:
            self.headers['OpenAI-Organization'] = self.organization
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the connection to OpenAI Assistant API."""
        try:
            response = requests.get(
                f"{self.base_url}/assistants",
                headers=self.headers,
                params={"limit": 1},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "message": "Successfully connected to OpenAI Assistant API",
                    "data": {
                        "connection_status": "success",
                        "assistants_count": len(data.get('data', [])),
                        "api_version": response.headers.get('openai-version', 'unknown')
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to connect: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}"
            }
    
    def create_assistant(self, name: str, description: str = "", instructions: str = "",
                        model: str = "gpt-4-turbo-preview", tools: List[Dict] = None,
                        file_ids: List[str] = None, metadata: Dict = None) -> Dict[str, Any]:
        """
        Create a new OpenAI Assistant.
        
        Args:
            name: Assistant name
            description: Assistant description
            instructions: System instructions
            model: OpenAI model to use
            tools: List of tools (e.g., [{"type": "file_search"}])
            file_ids: List of file IDs to attach
            metadata: Additional metadata
            
        Returns:
            Result dict with success status and assistant data
        """
        try:
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
            
            response = requests.post(
                f"{self.base_url}/assistants",
                headers=self.headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                assistant_data = response.json()
                logger.info(f"Created assistant: {assistant_data['id']}")
                return {
                    "success": True,
                    "message": f"Assistant '{name}' created successfully",
                    "data": assistant_data,
                    "assistant_id": assistant_data['id']
                }
            else:
                error_msg = f"Failed to create assistant: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = f"Error creating assistant: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def update_assistant(self, assistant_id: str, name: str = None, description: str = None,
                        instructions: str = None, model: str = None, tools: List[Dict] = None,
                        file_ids: List[str] = None, metadata: Dict = None) -> Dict[str, Any]:
        """
        Update an existing OpenAI Assistant.
        
        Args:
            assistant_id: ID of the assistant to update
            name: New name (optional)
            description: New description (optional)
            instructions: New instructions (optional)
            model: New model (optional)
            tools: New tools list (optional)
            file_ids: New file IDs (optional)
            metadata: New metadata (optional)
            
        Returns:
            Result dict with success status and assistant data
        """
        try:
            data = {}
            
            # Only include fields that are provided
            if name is not None:
                data["name"] = name
            if description is not None:
                data["description"] = description
            if instructions is not None:
                data["instructions"] = instructions
            if model is not None:
                data["model"] = model
            if tools is not None:
                data["tools"] = tools
            if file_ids is not None:
                data["file_ids"] = file_ids
            if metadata is not None:
                data["metadata"] = metadata
            
            response = requests.post(
                f"{self.base_url}/assistants/{assistant_id}",
                headers=self.headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                assistant_data = response.json()
                logger.info(f"Updated assistant: {assistant_id}")
                return {
                    "success": True,
                    "message": f"Assistant '{assistant_id}' updated successfully",
                    "data": assistant_data,
                    "assistant_id": assistant_id
                }
            else:
                error_msg = f"Failed to update assistant: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = f"Error updating assistant: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_assistant(self, assistant_id: str) -> Dict[str, Any]:
        """
        Get details of a specific assistant.
        
        Args:
            assistant_id: ID of the assistant
            
        Returns:
            Result dict with success status and assistant data
        """
        try:
            response = requests.get(
                f"{self.base_url}/assistants/{assistant_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                assistant_data = response.json()
                return {
                    "success": True,
                    "data": assistant_data,
                    "assistant_id": assistant_id
                }
            else:
                error_msg = f"Failed to get assistant: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = f"Error getting assistant: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def list_assistants(self, limit: int = 20) -> Dict[str, Any]:
        """
        List all available assistants.
        
        Args:
            limit: Maximum number of assistants to return
            
        Returns:
            Result dict with success status and assistants list
        """
        try:
            response = requests.get(
                f"{self.base_url}/assistants",
                headers=self.headers,
                params={"limit": limit, "order": "desc"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                assistants = data.get("data", [])
                return {
                    "success": True,
                    "data": assistants,
                    "count": len(assistants)
                }
            else:
                error_msg = f"Failed to list assistants: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = f"Error listing assistants: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def delete_assistant(self, assistant_id: str) -> Dict[str, Any]:
        """
        Delete an assistant.
        
        Args:
            assistant_id: ID of the assistant to delete
            
        Returns:
            Result dict with success status
        """
        try:
            response = requests.delete(
                f"{self.base_url}/assistants/{assistant_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Deleted assistant: {assistant_id}")
                return {
                    "success": True,
                    "message": f"Assistant '{assistant_id}' deleted successfully",
                    "data": result
                }
            else:
                error_msg = f"Failed to delete assistant: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = f"Error deleting assistant: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def create_thread(self, messages: List[Dict] = None, metadata: Dict = None) -> Dict[str, Any]:
        """
        Create a new conversation thread.
        
        Args:
            messages: Optional initial messages
            metadata: Optional metadata
            
        Returns:
            Result dict with success status and thread data
        """
        try:
            data = {}
            if messages:
                data["messages"] = messages
            if metadata:
                data["metadata"] = metadata
            
            response = requests.post(
                f"{self.base_url}/threads",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                thread_data = response.json()
                logger.info(f"Created thread: {thread_data['id']}")
                return {
                    "success": True,
                    "message": "Thread created successfully",
                    "data": thread_data,
                    "thread_id": thread_data['id']
                }
            else:
                error_msg = f"Failed to create thread: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = f"Error creating thread: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def add_message_to_thread(self, thread_id: str, content: str, role: str = "user",
                             file_ids: List[str] = None, metadata: Dict = None) -> Dict[str, Any]:
        """
        Add a message to a thread.
        
        Args:
            thread_id: ID of the thread
            content: Message content
            role: Message role (user or assistant)
            file_ids: Optional file IDs to attach
            metadata: Optional metadata
            
        Returns:
            Result dict with success status and message data
        """
        try:
            data = {
                "role": role,
                "content": content
            }
            
            if file_ids:
                data["file_ids"] = file_ids
            if metadata:
                data["metadata"] = metadata
            
            response = requests.post(
                f"{self.base_url}/threads/{thread_id}/messages",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                message_data = response.json()
                return {
                    "success": True,
                    "message": "Message added to thread successfully",
                    "data": message_data
                }
            else:
                error_msg = f"Failed to add message: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = f"Error adding message to thread: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def create_run(self, thread_id: str, assistant_id: str, instructions: str = None,
                  additional_instructions: str = None, tools: List[Dict] = None,
                  metadata: Dict = None) -> Dict[str, Any]:
        """
        Create and start a run on a thread.
        
        Args:
            thread_id: ID of the thread
            assistant_id: ID of the assistant
            instructions: Optional override instructions
            additional_instructions: Optional additional instructions
            tools: Optional tool overrides
            metadata: Optional metadata
            
        Returns:
            Result dict with success status and run data
        """
        try:
            data = {
                "assistant_id": assistant_id
            }
            
            if instructions:
                data["instructions"] = instructions
            if additional_instructions:
                data["additional_instructions"] = additional_instructions
            if tools:
                data["tools"] = tools
            if metadata:
                data["metadata"] = metadata
            
            response = requests.post(
                f"{self.base_url}/threads/{thread_id}/runs",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                run_data = response.json()
                logger.info(f"Created run: {run_data['id']} on thread: {thread_id}")
                return {
                    "success": True,
                    "message": "Run created successfully",
                    "data": run_data,
                    "run_id": run_data['id']
                }
            else:
                error_msg = f"Failed to create run: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = f"Error creating run: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_run_status(self, thread_id: str, run_id: str) -> Dict[str, Any]:
        """
        Get the status of a run.
        
        Args:
            thread_id: ID of the thread
            run_id: ID of the run
            
        Returns:
            Result dict with success status and run data
        """
        try:
            response = requests.get(
                f"{self.base_url}/threads/{thread_id}/runs/{run_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                run_data = response.json()
                return {
                    "success": True,
                    "data": run_data,
                    "status": run_data.get('status')
                }
            else:
                error_msg = f"Failed to get run status: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = f"Error getting run status: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def wait_for_run_completion(self, thread_id: str, run_id: str, 
                               timeout: int = 60, poll_interval: int = 2) -> Dict[str, Any]:
        """
        Wait for a run to complete.
        
        Args:
            thread_id: ID of the thread
            run_id: ID of the run
            timeout: Maximum time to wait in seconds
            poll_interval: How often to check status in seconds
            
        Returns:
            Result dict with success status and final run data
        """
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                status_result = self.get_run_status(thread_id, run_id)
                
                if not status_result["success"]:
                    return status_result
                
                status = status_result["status"]
                
                if status == "completed":
                    return {
                        "success": True,
                        "message": "Run completed successfully",
                        "data": status_result["data"],
                        "status": status
                    }
                elif status in ["failed", "cancelled", "expired"]:
                    return {
                        "success": False,
                        "error": f"Run {status}",
                        "data": status_result["data"],
                        "status": status
                    }
                elif status in ["queued", "in_progress"]:
                    # Continue waiting
                    time.sleep(poll_interval)
                else:
                    logger.warning(f"Unknown run status: {status}")
                    time.sleep(poll_interval)
            
            return {
                "success": False,
                "error": f"Timeout waiting for run completion after {timeout} seconds",
                "status": "timeout"
            }
            
        except Exception as e:
            error_msg = f"Error waiting for run completion: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_thread_messages(self, thread_id: str, limit: int = 20, 
                           order: str = "desc") -> Dict[str, Any]:
        """
        Get messages from a thread.
        
        Args:
            thread_id: ID of the thread
            limit: Maximum number of messages to return
            order: Order of messages (asc or desc)
            
        Returns:
            Result dict with success status and messages
        """
        try:
            response = requests.get(
                f"{self.base_url}/threads/{thread_id}/messages",
                headers=self.headers,
                params={"limit": limit, "order": order},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get("data", [])
                return {
                    "success": True,
                    "data": messages,
                    "count": len(messages)
                }
            else:
                error_msg = f"Failed to get messages: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = f"Error getting thread messages: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def chat_with_assistant(self, assistant_id: str, message: str, thread_id: str = None,
                           additional_instructions: str = None, timeout: int = 60) -> Dict[str, Any]:
        """
        High-level method to chat with an assistant.
        
        Args:
            assistant_id: ID of the assistant
            message: Message to send
            thread_id: Optional existing thread ID
            additional_instructions: Optional additional instructions
            timeout: Maximum time to wait for response
            
        Returns:
            Result dict with success status and response
        """
        try:
            # Create thread if not provided
            if not thread_id:
                thread_result = self.create_thread()
                if not thread_result["success"]:
                    return thread_result
                thread_id = thread_result["thread_id"]
            
            # Add message to thread
            message_result = self.add_message_to_thread(thread_id, message)
            if not message_result["success"]:
                return message_result
            
            # Create and start run
            run_data = {"assistant_id": assistant_id}
            if additional_instructions:
                run_data["additional_instructions"] = additional_instructions
            
            run_result = self.create_run(thread_id, assistant_id, 
                                       additional_instructions=additional_instructions)
            if not run_result["success"]:
                return run_result
            
            run_id = run_result["run_id"]
            
            # Wait for completion
            completion_result = self.wait_for_run_completion(thread_id, run_id, timeout)
            if not completion_result["success"]:
                return completion_result
            
            # Get the response message
            messages_result = self.get_thread_messages(thread_id, limit=1)
            if not messages_result["success"]:
                return messages_result
            
            messages = messages_result["data"]
            if messages:
                content = messages[0]["content"]
                if content and content[0]["type"] == "text":
                    response_text = content[0]["text"]["value"]
                    return {
                        "success": True,
                        "message": response_text,
                        "data": {
                            "thread_id": thread_id,
                            "run_id": run_id,
                            "response": response_text
                        },
                        "thread_id": thread_id
                    }
            
            return {
                "success": False,
                "error": "No response received from assistant"
            }
            
        except Exception as e:
            error_msg = f"Error chatting with assistant: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }


def create_client_from_config(config: Dict[str, Any]) -> OpenAIAssistantClient:
    """
    Create an OpenAI Assistant client from configuration.
    
    Args:
        config: Configuration dict with api_key, organization, etc.
        
    Returns:
        OpenAIAssistantClient instance
    """
    return OpenAIAssistantClient(
        api_key=config.get('api_key', ''),
        organization=config.get('organization'),
        base_url=config.get('base_url')
    )


def create_client_from_tool(tool_data: Dict[str, Any]) -> Optional[OpenAIAssistantClient]:
    """
    Create an OpenAI Assistant client from tool configuration.
    
    Args:
        tool_data: Tool data dict with config_params
        
    Returns:
        OpenAIAssistantClient instance or None if invalid config
    """
    try:
        config_params = tool_data.get('config_params', {})
        api_key = config_params.get('api_key', '')
        
        if not api_key:
            logger.error("No API key found in tool configuration")
            return None
        
        return OpenAIAssistantClient(
            api_key=api_key,
            organization=config_params.get('organization'),
            base_url=config_params.get('base_url')
        )
    except Exception as e:
        logger.error(f"Error creating client from tool: {str(e)}")
        return None
