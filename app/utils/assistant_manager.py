"""
Assistant Manager - Manages OpenAI Assistants for agents
Provides high-level interface for creating, updating, and managing assistants
"""

import logging
from typing import Dict, Any, Optional
from app.utils.openai_assistant_wrapper import OpenAIAssistantAPI
from app.utils.data_manager import agents_manager

class AssistantManager:
    """
    Manager class for handling OpenAI Assistants associated with agents
    """
    
    def __init__(self):
        """Initialize the assistant manager"""
        self.logger = logging.getLogger(__name__)
        self._assistant_api = None
    
    @property
    def assistant_api(self):
        """Lazy initialization of assistant API"""
        if self._assistant_api is None:
            try:
                self._assistant_api = OpenAIAssistantAPI()
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI Assistant API: {e}")
                # Return a mock object that will handle graceful failures
                return MockAssistantAPI()
        return self._assistant_api
    
    def create_assistant_for_agent(self, agent: Dict[str, Any]) -> Optional[str]:
        """
        Create a new OpenAI Assistant for the given agent
        
        Args:
            agent: Agent dictionary containing configuration
            
        Returns:
            str: Assistant ID if successful, None if failed
        """
        try:
            # Check if agent has knowledge base or files
            has_knowledge_base = bool(agent.get('knowledge_base'))
            has_files = bool(agent.get('files'))
            
            # Extract agent configuration for assistant creation
            assistant_config = {
                'name': agent.get('name', 'Unnamed Agent'),
                'instructions': agent.get('system_instruction', ''),
                'model': agent.get('model', 'gpt-4o-mini'),
                'tools': self._prepare_tools(agent.get('tools', []), has_knowledge_base, has_files),
                'description': f"Assistant for agent: {agent.get('name', 'Unnamed')}"
            }
            
            # Prepare files for upload
            file_ids = self._prepare_files(agent)
            if file_ids:
                assistant_config['file_ids'] = file_ids
            
            # Create the assistant
            result = self.assistant_api.create_assistant(assistant_config)
            
            if result.get('success', False):
                assistant_id = result.get('data', {}).get('id')
                if assistant_id:
                    # Don't update the agent here - let the caller handle it
                    self.logger.info(f"Created assistant {assistant_id} for agent {agent['id']}")
                    return assistant_id
            else:
                self.logger.error(f"Failed to create assistant for agent {agent['id']}: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"Error creating assistant for agent {agent['id']}: {e}")
            
        return None
    
    def update_assistant_for_agent(self, agent: Dict[str, Any]) -> bool:
        """
        Update an existing OpenAI Assistant with agent configuration
        
        Args:
            agent: Agent dictionary containing updated configuration
            
        Returns:
            bool: True if successful, False if failed
        """
        try:
            assistant_id = agent.get('assistant_id')
            if not assistant_id:
                self.logger.warning(f"No assistant ID found for agent {agent['id']}")
                return False
            
            # Check if agent has knowledge base or files
            has_knowledge_base = bool(agent.get('knowledge_base'))
            has_files = bool(agent.get('files'))
            
            # Prepare update parameters
            update_params = {
                'name': agent.get('name', 'Unnamed Agent'),
                'instructions': agent.get('system_instruction', ''),
                'model': agent.get('model', 'gpt-4o-mini'),
                'tools': self._prepare_tools(agent.get('tools', []), has_knowledge_base, has_files),
                'description': f"Assistant for agent: {agent.get('name', 'Unnamed')}"
            }
            
            # Prepare files for upload
            file_ids = self._prepare_files(agent)
            if file_ids:
                update_params['file_ids'] = file_ids
            
            # Update the assistant
            result = self.assistant_api.update_assistant(assistant_id, update_params)
            
            if result.get('success', False):
                self.logger.info(f"Updated assistant {assistant_id} for agent {agent['id']}")
                return True
            else:
                self.logger.error(f"Failed to update assistant {assistant_id}: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"Error updating assistant for agent {agent['id']}: {e}")
            
        return False
    
    def reassign_assistant(self, agent: Dict[str, Any], new_assistant_id: str) -> bool:
        """
        Reassign a different assistant to an agent
        
        Args:
            agent: Agent dictionary
            new_assistant_id: ID of the new assistant to assign
            
        Returns:
            bool: True if successful, False if failed
        """
        try:
            # Verify the new assistant exists
            result = self.assistant_api.get_assistant(new_assistant_id)
            
            if result.get('success', False):
                # Update the agent with new assistant ID
                old_assistant_id = agent.get('assistant_id')
                agent['assistant_id'] = new_assistant_id
                agents_manager.update(agent['id'], agent)
                
                self.logger.info(f"Reassigned agent {agent['id']} from assistant {old_assistant_id} to {new_assistant_id}")
                return True
            else:
                self.logger.error(f"Assistant {new_assistant_id} not found or inaccessible")
                
        except Exception as e:
            self.logger.error(f"Error reassigning assistant for agent {agent['id']}: {e}")
            
        return False
    
    def get_assistant_info(self, assistant_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an existing assistant
        
        Args:
            assistant_id: ID of the assistant to check
            
        Returns:
            dict: Assistant information if successful, None if failed
        """
        try:
            result = self.assistant_api.get_assistant(assistant_id)
            
            if result.get('success', False):
                self.logger.info(f"Retrieved assistant info for {assistant_id}")
                return result.get('data', {})
            else:
                self.logger.error(f"Failed to get assistant info for {assistant_id}: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"Error getting assistant info for {assistant_id}: {e}")
            
        return None
    
    def list_assistants(self) -> list:
        """
        List all available assistants
        
        Returns:
            list: List of assistants
        """
        try:
            result = self.assistant_api.list_assistants()
            if isinstance(result, list):
                self.logger.info(f"Retrieved {len(result)} assistants")
                return result
            else:
                self.logger.warning("No assistants found or unexpected result format")
                return []
        except Exception as e:
            self.logger.error(f"Error listing assistants: {e}")
            return []
    
    def _prepare_tools(self, agent_tools: list, has_knowledge_base: bool = False, has_files: bool = False) -> list:
        """
        Convert agent tools to OpenAI Assistant API format
        
        Args:
            agent_tools: List of agent tool configurations
            has_knowledge_base: Whether agent has knowledge base items
            has_files: Whether agent has uploaded files
            
        Returns:
            list: Formatted tools for OpenAI Assistant API
        """
        assistant_tools = []
        
        # Always include code interpreter for agents
        assistant_tools.append({"type": "code_interpreter"})
        
        # Add file search if agent has knowledge base or files
        if has_knowledge_base or has_files:
            assistant_tools.append({"type": "file_search"})
        
        # Convert custom tools (this would need more sophisticated mapping)
        for tool in agent_tools:
            if isinstance(tool, dict) and tool.get('type') == 'function':
                assistant_tools.append(tool)
        
        return assistant_tools
    
    def _prepare_files(self, agent: Dict[str, Any]) -> list:
        """
        Prepare files for OpenAI Assistant
        
        Args:
            agent: Agent dictionary containing files and knowledge base
            
        Returns:
            list: File IDs for OpenAI Assistant
        """
        file_ids = []
        
        try:
            # Add uploaded files
            if agent.get('files'):
                for file_info in agent['files']:
                    # In a full implementation, this would upload files to OpenAI
                    # For now, we'll just log the files that would be uploaded
                    self.logger.info(f"Would upload file: {file_info.get('filename', 'Unknown')}")
            
            # Create knowledge base file if knowledge items exist
            if agent.get('knowledge_base'):
                knowledge_content = self._create_knowledge_base_content(agent['knowledge_base'])
                # In a full implementation, this would upload the knowledge base as a file
                self.logger.info(f"Would create knowledge base file with {len(agent['knowledge_base'])} items")
                
        except Exception as e:
            self.logger.error(f"Error preparing files for agent {agent.get('id', 'unknown')}: {e}")
        
        return file_ids
    
    def _create_knowledge_base_content(self, knowledge_items: list) -> str:
        """
        Create a formatted text file content from knowledge base items
        
        Args:
            knowledge_items: List of knowledge base items
            
        Returns:
            str: Formatted knowledge base content
        """
        content_lines = ["# Agent Knowledge Base", ""]
        
        for item in knowledge_items:
            title = item.get('title', 'Untitled Knowledge Item')
            content = item.get('content', '')
            use_case = item.get('use_case', '')
            rating = item.get('rating', '')
            
            content_lines.append(f"## {title}")
            if use_case:
                content_lines.append(f"**Use Case:** {use_case}")
            if rating:
                content_lines.append(f"**Rating:** {rating}/5")
            content_lines.append("")
            content_lines.append(content)
            content_lines.append("")
            content_lines.append("---")
            content_lines.append("")
        
        return "\n".join(content_lines)


class MockAssistantAPI:
    """
    Mock assistant API for graceful failure handling when OpenAI API is not available
    """
    
    def create_assistant(self, config):
        """Mock create assistant"""
        return {'success': False, 'message': 'OpenAI Assistant API not available'}
    
    def update_assistant(self, assistant_id, config):
        """Mock update assistant"""
        return {'success': False, 'message': 'OpenAI Assistant API not available'}
    
    def get_assistant(self, assistant_id):
        """Mock get assistant"""
        return {'success': False, 'message': 'OpenAI Assistant API not available'}


# Create global instance
assistant_manager = AssistantManager()
