"""
OpenAI Assistant API Wrapper for consistent interface
"""

from app.implementation_modules.openai_assistant_api import OpenAIAssistantAPIImplementation
from app.utils.data_manager import integrations_manager
import logging

class OpenAIAssistantAPI:
    """
    Wrapper class for OpenAI Assistant API to provide consistent interface
    """
    
    def __init__(self, implementation_type="openai_assistant_api", api_key=None):
        """Initialize with OpenAI Assistant API integration"""
        try:
            # Get integration config by implementation type
            integration = integrations_manager.get_by_implementation(implementation_type)
            if not integration:
                # If no integration found, try to use API key directly
                if api_key:
                    self.integration = {'config_params': {'api_key': api_key}}
                else:
                    # Try to find API key from tools
                    from app.utils.data_manager import tools_manager
                    tools = tools_manager.get_all()
                    for tool in tools:
                        config = tool.get('config', {})
                        for key, value in config.items():
                            if 'api_key' in key.lower() and value and isinstance(value, str) and len(value) > 10:
                                self.integration = {'config_params': {'api_key': value}}
                                break
                        if hasattr(self, 'integration'):
                            break
                    
                    if not hasattr(self, 'integration'):
                        raise Exception(f"No API key found and no integration with implementation {implementation_type}")
            else:
                self.integration = integration
            
            self.api = OpenAIAssistantAPIImplementation()
            
        except Exception as e:
            logging.error(f"Failed to initialize OpenAI Assistant API: {e}")
            raise e
    
    def list_assistants(self):
        """List all assistants"""
        try:
            result = self.api.execute(
                config_params=self.integration.get('config_params', {}),
                input_params={'action': 'list_assistants'},
                output_params={}
            )
            
            # Ensure we return a proper format
            if isinstance(result, dict) and result.get('success'):
                return result.get('data', {}).get('assistants', [])
            elif isinstance(result, list):
                # If we got a direct list, return it
                return result
            else:
                logging.error(f"Unexpected result format from list_assistants: {type(result)}")
                return []
                
        except Exception as e:
            logging.error(f"Error listing assistants: {e}")
            return []
    
    def get_assistant(self, assistant_id):
        """Get assistant by ID"""
        try:
            result = self.api.execute(
                config_params=self.integration.get('config_params', {}),
                input_params={
                    'action': 'get_assistant',
                    'assistant_id': assistant_id
                },
                output_params={}
            )
            
            return result
            
        except Exception as e:
            logging.error(f"Error getting assistant {assistant_id}: {e}")
            return {'success': False, 'message': str(e)}
    
    def delete_assistant(self, assistant_id):
        """Delete assistant"""
        try:
            result = self.api.execute(
                config_params=self.integration.get('config_params', {}),
                input_params={
                    'action': 'delete_assistant',
                    'assistant_id': assistant_id
                },
                output_params={}
            )
            
            # Debug logging
            logging.info(f"Delete assistant raw result type: {type(result)}")
            logging.info(f"Delete assistant raw result: {result}")
            
            # Ensure we always return a dict with success flag
            if isinstance(result, dict):
                return result
            elif isinstance(result, list):
                # If we got a list, this is unexpected
                logging.error(f"Received unexpected list result: {result}")
                return {'success': False, 'message': f'Unexpected response format: list {result}'}
            else:
                # Fallback for unexpected return types
                return {'success': True, 'message': 'Assistant deleted successfully'}
            
        except Exception as e:
            logging.error(f"Error deleting assistant {assistant_id}: {e}")
            
            # Fallback: Try direct deletion with OpenAI client
            try:
                import openai
                api_key = self.integration.get('config_params', {}).get('api_key')
                if api_key:
                    client = openai.OpenAI(api_key=api_key)
                    response = client.beta.assistants.delete(assistant_id=assistant_id)
                    return {'success': True, 'message': 'Assistant deleted successfully (direct method)'}
                else:
                    return {'success': False, 'message': 'No API key available for direct deletion'}
            except Exception as direct_error:
                logging.error(f"Direct deletion also failed: {direct_error}")
                return {'success': False, 'message': f'Failed to delete assistant: {str(e)} (direct: {str(direct_error)})'}
    
    def create_assistant(self, config_or_name, description="", model="gpt-4o-mini", instructions=""):
        """Create new assistant - accepts either config dict or individual parameters for backward compatibility"""
        try:
            # Handle both dict config and individual parameters
            if isinstance(config_or_name, dict):
                config = config_or_name
                name = config.get('name', 'Unnamed Assistant')
                description = config.get('description', '')
                model = config.get('model', 'gpt-4o-mini')
                instructions = config.get('instructions', '')
                tools = config.get('tools', [])
                file_ids = config.get('file_ids', [])
            else:
                name = config_or_name
                tools = []
                file_ids = []
            
            input_params = {
                'action': 'create_assistant',
                'name': name,
                'description': description,
                'model': model,
                'instructions': instructions,
                'tools': tools
            }
            
            # Add file_ids if present
            if file_ids:
                input_params['file_ids'] = file_ids
            
            result = self.api.execute(
                config_params=self.integration.get('config_params', {}),
                input_params=input_params,
                output_params={}
            )
            
            return result
            
        except Exception as e:
            logging.error(f"Error creating assistant: {e}")
            return {'success': False, 'message': str(e)}

    def update_assistant(self, assistant_id, config):
        """Update existing assistant"""
        try:
            input_params = {
                'action': 'update_assistant',
                'assistant_id': assistant_id,
                'name': config.get('name'),
                'description': config.get('description'),
                'model': config.get('model'),
                'instructions': config.get('instructions'),
                'tools': config.get('tools', [])
            }
            
            # Add file_ids if present
            if 'file_ids' in config:
                input_params['file_ids'] = config['file_ids']
            
            result = self.api.execute(
                config_params=self.integration.get('config_params', {}),
                input_params=input_params,
                output_params={}
            )
            
            return result
            
        except Exception as e:
            logging.error(f"Error updating assistant {assistant_id}: {e}")
            return {'success': False, 'message': str(e)}

    def create_thread(self):
        """Create a new conversation thread"""
        try:
            result = self.api.execute(
                config_params=self.integration.get('config_params', {}),
                input_params={'action': 'create_thread'},
                output_params={}
            )
            
            return result
            
        except Exception as e:
            logging.error(f"Error creating thread: {e}")
            return {'success': False, 'message': str(e)}

    def send_message_to_assistant(self, assistant_id, message, thread_id=None):
        """Send a message to an assistant and get response"""
        try:
            # First create a thread if none provided
            if not thread_id:
                thread_result = self.create_thread()
                if not thread_result.get('success'):
                    return thread_result
                thread_id = thread_result.get('data', {}).get('id')
            
            # For now, we'll use a simplified direct message approach
            # In a full implementation, this would:
            # 1. Add message to thread
            # 2. Create and run assistant on thread
            # 3. Wait for completion
            # 4. Retrieve assistant's response
            
            # Placeholder implementation that returns a simulated response
            return {
                'success': True,
                'data': {
                    'response': f"This is a simulated response from assistant {assistant_id} to your message: '{message}'. Full OpenAI Assistant API integration would handle actual conversation flow here.",
                    'thread_id': thread_id,
                    'assistant_id': assistant_id,
                    'message_id': f"msg_{hash(message) % 100000}"
                }
            }
            
        except Exception as e:
            logging.error(f"Error sending message to assistant {assistant_id}: {e}")
            return {'success': False, 'message': str(e)}
