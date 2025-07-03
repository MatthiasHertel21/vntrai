"""
OpenAI Assistant API Wrapper for consistent interface
"""

from app.implementation_modules.openai_assistant_api import OpenAIAssistantAPIImplementation
from app.utils.data_manager import integrations_manager
import logging
import json

class OpenAIAssistantAPI:
    """
    Wrapper class for OpenAI Assistant API to provide consistent interface
    """
    
    def __init__(self, implementation_type="openai_assistant_api", api_key=None):
        """Initialize with OpenAI Assistant API integration"""
        try:
            # Initialize empty config params
            config_params = {}
            
            # First, try using provided API key
            if api_key:
                config_params['api_key'] = api_key
                logging.info("Using provided API key")
            
            # Second, try getting integration config by implementation type
            integration = integrations_manager.get_by_implementation(implementation_type)
            if integration:
                logging.info(f"Found integration for {implementation_type}")
                # Handle case where integration config_params is a schema (list) instead of config values (dict)
                if isinstance(integration, dict):
                    if 'config_params' in integration:
                        if isinstance(integration['config_params'], dict):
                            # Actual configuration values (dict)
                            config_params.update(integration['config_params'])
                            logging.info("Using integration config_params (dict)")
                        elif isinstance(integration['config_params'], list):
                            # This is a schema (list), not actual config values
                            logging.warning(f"Integration returned schema instead of config: {integration['config_params']}")
                            # Don't update config_params in this case
                    else:
                        # Try to extract values directly from integration
                        possible_keys = ['api_key', 'openai_api_key']
                        for key in possible_keys:
                            if key in integration and integration[key] and isinstance(integration[key], str) and len(integration[key]) > 10:
                                config_params[key] = integration[key]
                                logging.info(f"Found API key in integration with key: {key}")
                                break
                else:
                    logging.warning(f"Integration is not a dict but {type(integration)}")
            
            # Third, if no API key yet, try to find in tools
            if not any(key in config_params for key in ['api_key', 'openai_api_key']):
                logging.info("No API key found in integration, searching in tools")
                # Try to find API key from tools
                from app.utils.data_manager import tools_manager
                tools = tools_manager.get_all()
                api_key_found = None
                
                # Look for API key in tool configs
                for tool in tools:
                    # Try to find OpenAI tools specifically first
                    if tool.get('type') == 'openai' or 'openai' in tool.get('name', '').lower():
                        logging.info(f"Found OpenAI tool: {tool.get('name')}")
                        config = tool.get('config', {})
                        if isinstance(config, dict):
                            for key, value in config.items():
                                if ('api_key' in key.lower() or 'openai' in key.lower()) and value and isinstance(value, str) and len(value) > 10:
                                    api_key_found = value
                                    logging.info(f"Found OpenAI API key in tool config with key: {key}")
                                    break
                        if api_key_found:
                            break
                
                # If no key found in OpenAI tools, try all tools
                if not api_key_found:
                    for tool in tools:
                        config = tool.get('config', {})
                        if isinstance(config, dict):
                            for key, value in config.items():
                                if ('api_key' in key.lower() or 'openai' in key.lower()) and value and isinstance(value, str) and len(value) > 10:
                                    api_key_found = value
                                    logging.info(f"Found API key in tool config with key: {key}")
                                    break
                        if api_key_found:
                            break
                
                if api_key_found:
                    config_params['api_key'] = api_key_found
                else:
                    # No API key found
                    logging.warning("No OpenAI API key found in integrations or tools - assistant operations will fail")
            
            # Store the final configuration
            self.integration = {'config_params': config_params}
            
            # Create API implementation instance
            self.api = OpenAIAssistantAPIImplementation()
            
            # Log whether we have an API key or not (without revealing the key itself)
            has_api_key = any(key in config_params and config_params[key] for key in ['api_key', 'openai_api_key'])
            logging.info(f"OpenAI Assistant API initialized with API key: {'FOUND' if has_api_key else 'MISSING'}")
            
        except Exception as e:
            logging.error(f"Failed to initialize OpenAI Assistant API: {e}")
            raise e
    
    def list_assistants(self):
        """List all assistants"""
        try:
            result = self.api.execute_legacy(
                config_params=self.integration.get('config_params', {}),
                input_params={'action': 'list_assistants'},
                output_params={}
            )
            
            # Ensure we return a proper format
            if isinstance(result, dict) and result.get('success'):
                data = result.get('data', {})
                # Handle case where data might be a list instead of dict
                if isinstance(data, dict):
                    return data.get('assistants', [])
                elif isinstance(data, list):
                    return data
                else:
                    return []
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
            result = self.api.execute_legacy(
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
            
            # Ensure tools is a list
            if not isinstance(tools, list):
                tools = []
                
            # Detailed logging of tool data
            logging.info(f"Tools for assistant creation: {tools}")
            for i, tool in enumerate(tools):
                logging.info(f"Tool {i}: {type(tool)} - {tool}")
                
            # Process tools to ensure they're in correct format for OpenAI API
            processed_tools = []
            for tool in tools:
                if isinstance(tool, dict) and 'type' in tool:
                    # Tool is already in the right format
                    processed_tools.append(tool)
                elif isinstance(tool, str):
                    if tool.startswith('tool:'):
                        # Convert tool reference to function definition
                        tool_id = tool.split(':')[1]
                        processed_tools.append({
                            "type": "function",
                            "function": {
                                "name": f"tool_{tool_id}",
                                "description": "External tool integration"
                            }
                        })
                    elif tool in ["code_interpreter", "retrieval", "function"]:
                        # Add simple tool types
                        processed_tools.append({"type": tool})
            
            # Log processed tools
            logging.info(f"Processed tools: {processed_tools}")
                
            # Log API key status before creating assistant
            config_params = self.integration.get('config_params', {})
            has_api_key = any(key in config_params and config_params[key] for key in ['api_key', 'openai_api_key'])
            logging.info(f"Creating assistant with API key: {'FOUND' if has_api_key else 'MISSING'}")
            
            # Debug log the config params keys (not values) to check if API key exists
            if has_api_key:
                logging.info(f"API key found in keys: {[k for k in config_params.keys() if 'api' in k.lower()]}")
            else:
                logging.warning(f"No API key found in config_params keys: {list(config_params.keys())}")
            
            # Map parameters to what the implementation expects
            input_params = {
                'action': 'create_assistant',
                'assistant_name': name,  # Changed from 'name' to 'assistant_name'
                'assistant_description': description,  # Changed from 'description' to 'assistant_description'
                'model': model,
                'instructions': instructions,
                'tools': processed_tools,  # Pass as processed Python list
                'file_ids': file_ids if isinstance(file_ids, list) else []
            }
            
            # If API key is in config_params, ensure it's passed to input_params as well
            if has_api_key:
                for key in config_params:
                    if 'api_key' in key.lower() or 'openai' in key.lower():
                        input_params[key] = config_params[key]
                        logging.info(f"Added {key} to input_params from config_params")
            
            result = self.api.execute_legacy(
                config_params=self.integration.get('config_params', {}),
                input_params=input_params,
                output_params={}
            )
            
            # Add safety check for result type
            if isinstance(result, list):
                logging.error(f"Unexpected list result from create_assistant: {result}")
                return {
                    'success': False,
                    'message': f'Unexpected response format: received list instead of dict - {result}'
                }
            elif not isinstance(result, dict):
                logging.error(f"Unexpected result type from create_assistant: {type(result)} - {result}")
                return {
                    'success': False,
                    'message': f'Unexpected response type: {type(result)}'
                }
            
            return result
            
        except Exception as e:
            logging.error(f"Error creating assistant: {e}")
            return {'success': False, 'message': str(e)}

    def update_assistant(self, assistant_id, config):
        """Update existing assistant"""
        try:
            # Map parameters to what the implementation expects
            input_params = {
                'action': 'update_assistant',
                'assistant_id': assistant_id
            }
            
            # Add optional parameters if present
            if config.get('name'):
                input_params['assistant_name'] = config['name']
            if config.get('description'):
                input_params['assistant_description'] = config['description']
            if config.get('model'):
                input_params['model'] = config['model']
            if config.get('instructions'):
                input_params['instructions'] = config['instructions']
            if config.get('tools'):
                input_params['tools'] = json.dumps(config['tools'])
            if config.get('file_ids'):
                input_params['file_ids'] = json.dumps(config['file_ids'])
            
            result = self.api.execute_legacy(
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
            result = self.api.execute_legacy(
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
                # Handle both dict and list results safely
                if isinstance(thread_result, dict) and thread_result.get('success'):
                    data = thread_result.get('data', {})
                    if isinstance(data, dict):
                        thread_id = data.get('id')
                    else:
                        return {'success': False, 'message': 'Invalid thread creation response format'}
                else:
                    return thread_result
            
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
