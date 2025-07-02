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
            # Extract agent configuration for assistant creation
            assistant_config = {
                'name': agent.get('name', 'Unnamed Agent'),
                'instructions': agent.get('system_instruction', ''),
                'model': agent.get('model', 'gpt-3.5-turbo'),
                'tools': self._prepare_tools(agent.get('tools', [])),
                'description': f"Assistant for agent: {agent.get('name', 'Unnamed')}"
            }
            
            # Create the assistant
            result = self.assistant_api.create_assistant(assistant_config)
            
            if result.get('success', False):
                assistant_id = result.get('data', {}).get('id')
                if assistant_id:
                    # Update the agent with the new assistant ID
                    agent['assistant_id'] = assistant_id
                    agents_manager.update(agent['id'], agent)
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
            
            # Prepare update parameters
            update_params = {
                'name': agent.get('name', 'Unnamed Agent'),
                'instructions': agent.get('system_instruction', ''),
                'model': agent.get('model', 'gpt-3.5-turbo'),
                'tools': self._prepare_tools(agent.get('tools', [])),
                'description': f"Assistant for agent: {agent.get('name', 'Unnamed')}"
            }
            
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
    
    def _prepare_tools(self, agent_tools: list) -> list:
        """
        Convert agent tools to OpenAI Assistant API format
        
        Args:
            agent_tools: List of agent tool configurations
            
        Returns:
            list: Formatted tools for OpenAI Assistant API
        """
        assistant_tools = []
        
        # Always include code interpreter for now
        assistant_tools.append({"type": "code_interpreter"})
        
        # Add retrieval if agent has knowledge base
        # This is a placeholder - would need to be implemented based on agent configuration
        if agent_tools:
            assistant_tools.append({"type": "retrieval"})
        
        # Convert custom tools (this would need more sophisticated mapping)
        for tool in agent_tools:
            if isinstance(tool, dict) and tool.get('type') == 'function':
                assistant_tools.append(tool)
        
        return assistant_tools


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
