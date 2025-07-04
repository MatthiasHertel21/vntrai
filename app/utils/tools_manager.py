"""
Tools Manager for vntrai Data Management
Handles tools data operations with Implementation Module integration
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from .base_manager import DataManager

# Implementation Module Integration
try:
    from app.implementation_modules import implementation_manager
    IMPLEMENTATION_MODULES_AVAILABLE = True
except ImportError:
    IMPLEMENTATION_MODULES_AVAILABLE = False

class ToolsManager(DataManager):
    """Manager for tools data with Implementation Module integration"""
    
    def __init__(self):
        super().__init__('tools')
        self.implementation_manager = implementation_manager if IMPLEMENTATION_MODULES_AVAILABLE else None
    
    def create_tool(self, name: str, category: str = 'utility', tool_type: str = 'script') -> Dict[str, Any]:
        """Create new tool with defaults"""
        tool = {
            'id': str(uuid.uuid4()),
            'name': name,
            'category': category,
            'type': tool_type,
            'description': '',
            'status': 'inactive',
            'executable': '',
            'arguments': [],
            'environment': {},
            'config': {},
            'dependencies': [],
            'version': '1.0.0',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            # Neue Options-Struktur für erweiterte Funktionen
            'options': {
                'assistant': {
                    'enabled': False,
                    'assistant_id': '',
                    'model': 'gpt-4-turbo-preview',
                    'instructions': '',
                    'auto_create': True,
                    'thread_management': 'auto'
                }
            }
        }
        
        if self.save(tool):
            return tool
        return None
    
    def get_implementation_module_for_tool(self, tool: Dict[str, Any]) -> Optional[str]:
        """
        Ermittelt das passende Implementation Module für ein Tool.
        Löst es über die Integration auf (saubere Architektur).
        """
        if not self.implementation_manager:
            return None
        
        # Tool Definition ermitteln - erst direkt, dann in metadata.original_data
        tool_definition = tool.get('tool_definition', '')
        if not tool_definition and 'metadata' in tool and 'original_data' in tool['metadata']:
            tool_definition = tool['metadata']['original_data'].get('tool_definition', '')
        
        if not tool_definition:
            return None
        
        # SAUBERE LÖSUNG: Integration laden und Implementation Module von dort holen
        integration = None
        
        # Versuche zuerst über integration_id zu finden
        integration_id = tool.get('integration_id')
        if integration_id:
            from .integrations_manager import integrations_manager
            integration = integrations_manager.get_by_id(integration_id)
        
        # Falls nicht gefunden, versuche über Namen
        if not integration:
            from .integrations_manager import integrations_manager
            integration = next(
                (i for i in integrations_manager.get_all() 
                 if i['name'] == tool_definition), 
                None
            )
        
        # Implementation Module von Integration holen
        if integration and integration.get('implementation'):
            return integration['implementation']
        
        # FALLBACK: Alte Mapping-Logik für Legacy-Tools
        integration_to_module_mapping = {
            'ChatGPT': 'openai_chatcompletion',
            'OpenAI': 'openai_chatcompletion',
            'OpenAI Chat Completion': 'openai_chatcompletion',
            'OpenAI Assistant API': 'openai_assistant_api',
            'GoogleSheets': 'google_sheets',  
            'Google Sheets': 'google_sheets',
            'Google Workspace': 'google_sheets'
        }
        
        # Direkte Zuordnung versuchen
        module_name = integration_to_module_mapping.get(tool_definition)
        if module_name:
            return module_name
        
        # Letzter Fallback: Nach ähnlichen Namen suchen
        available_modules = self.implementation_manager.list_available_implementations()
        for module_info in available_modules:
            module_name_lower = module_info.get('name', '').lower()
            tool_definition_lower = tool_definition.lower()
            
            if module_name_lower in tool_definition_lower or tool_definition_lower in module_name_lower:
                return module_info.get('name')
        
        return None
    
    async def test_tool_with_implementation(self, tool_id: str, test_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Testet ein Tool über sein Implementation Module.
        """
        try:
            tool = self.get_by_id(tool_id)
            if not tool:
                return {'success': False, 'message': 'Tool nicht gefunden'}
            
            if not self.implementation_manager:
                return {'success': False, 'message': 'Implementation Module System nicht verfügbar'}
            
            # Implementation Module ermitteln
            module_name = self.get_implementation_module_for_tool(tool)
            if not module_name:
                return {'success': False, 'message': 'Kein passendes Implementation Module gefunden'}
            
            # Konfiguration zusammenstellen
            config = tool.get('config', {})
            if test_config:
                config.update(test_config)
            
            # Test über Implementation Manager ausführen
            test_result = await self.implementation_manager.test_implementation(module_name, config)
            
            # Test-Ergebnis im Tool speichern
            tool['last_test'] = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'result': test_result,
                'module_used': module_name
            }
            
            # Status aktualisieren
            tool['status'] = 'connected' if test_result.get('success') else 'error'
            tool['updated_at'] = datetime.utcnow().isoformat() + 'Z'
            
            self.update(tool_id, tool)
            
            return test_result
            
        except Exception as e:
            error_result = {
                'success': False,
                'message': f'Test-Fehler: {str(e)}',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            
            # Speichere Fehler-Ergebnis
            if tool:
                tool['last_test'] = {
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'result': error_result
                }
                tool['status'] = 'error'
                tool['updated_at'] = datetime.utcnow().isoformat() + 'Z'
                self.update(tool_id, tool)
            
            return error_result
    
    async def execute_tool_with_implementation(self, tool_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führt ein Tool über sein Implementation Module aus.
        """
        try:
            tool = self.get_by_id(tool_id)
            if not tool:
                return {'success': False, 'message': 'Tool nicht gefunden'}
            
            if not self.implementation_manager:
                return {'success': False, 'message': 'Implementation Module System nicht verfügbar'}
            
            # Implementation Module ermitteln
            module_name = self.get_implementation_module_for_tool(tool)
            if not module_name:
                return {'success': False, 'message': 'Kein passendes Implementation Module gefunden'}
            
            # Konfiguration und Parameter zusammenstellen
            config = tool.get('config', {})
            
            # Prefilled und Locked Inputs berücksichtigen
            final_inputs = tool.get('prefilled_inputs', {}).copy()
            locked_inputs = tool.get('locked_inputs', [])
            
            for key, value in inputs.items():
                if key not in locked_inputs:
                    final_inputs[key] = value
            
            # Execution über Implementation Manager
            execution_result = await self.implementation_manager.execute_implementation(
                module_name, config, final_inputs
            )
            
            # Execution-Ergebnis im Tool speichern
            tool['last_execution'] = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'inputs': final_inputs,
                'result': execution_result,
                'module_used': module_name
            }
            
            tool['updated_at'] = datetime.utcnow().isoformat() + 'Z'
            self.update(tool_id, tool)
            
            return execution_result
            
        except Exception as e:
            error_result = {
                'success': False,
                'message': f'Execution-Fehler: {str(e)}',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            
            # Speichere Fehler-Ergebnis
            if tool:
                tool['last_execution'] = {
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'inputs': inputs,
                    'result': error_result
                }
                tool['updated_at'] = datetime.utcnow().isoformat() + 'Z'
                self.update(tool_id, tool)
            
            return error_result
    
    def get_available_implementation_modules(self) -> List[Dict[str, Any]]:
        """
        Gibt alle verfügbaren Implementation Module zurück.
        """
        if not self.implementation_manager:
            return []
        
        return self.implementation_manager.list_available_implementations()
    
    def get_tool_implementation_status(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ermittelt den Implementation-Status eines Tools.
        """
        if not self.implementation_manager:
            return {
                'has_implementation': False,
                'module_name': None,
                'status': 'unavailable'
            }
        
        module_name = self.get_implementation_module_for_tool(tool)
        
        return {
            'has_implementation': module_name is not None,
            'module_name': module_name,
            'status': 'available' if module_name else 'not_found'
        }
    
    def update_assistant_options(self, tool_id: str, assistant_options: Dict[str, Any]) -> bool:
        """Update assistant options for a tool."""
        tool = self.get_by_id(tool_id)
        if not tool:
            return False
        
        # Initialize options if not exists
        if 'options' not in tool:
            tool['options'] = {}
        
        # Update assistant options
        tool['options']['assistant'] = assistant_options
        tool['updated_at'] = datetime.now().isoformat()
        
        return self.save(tool)
    
    def get_assistant_options(self, tool_id: str) -> Dict[str, Any]:
        """Get assistant options for a tool."""
        tool = self.get_by_id(tool_id)
        if not tool:
            return {}
        
        return tool.get('options', {}).get('assistant', {
            'enabled': False,
            'assistant_id': '',
            'model': 'gpt-4-turbo-preview',
            'instructions': '',
            'auto_create': True,
            'thread_management': 'auto'
        })
    
    def is_assistant_enabled(self, tool_id: str) -> bool:
        """Check if assistant is enabled for a tool."""
        assistant_options = self.get_assistant_options(tool_id)
        return assistant_options.get('enabled', False)
    
    def get_tools_with_assistant_enabled(self) -> List[Dict[str, Any]]:
        """Get all tools that have assistant functionality enabled."""
        all_tools = self.get_all()
        return [tool for tool in all_tools if self.is_assistant_enabled(tool['id'])]
    
    def ensure_options_field(self, tool_id: str) -> bool:
        """Ensure options field exists for a tool (Sprint 18)"""
        tool = self.get_by_id(tool_id)
        if not tool:
            return False
        
        if 'options' not in tool:
            tool['options'] = {}
        
        if 'assistant' not in tool['options']:
            tool['options']['assistant'] = {
                'enabled': False,
                'assistant_id': '',
                'model': 'gpt-4-turbo-preview',
                'instructions': '',
                'auto_create': True,
                'thread_management': 'auto'
            }
            
            tool['updated_at'] = datetime.now().isoformat()
            return self.save(tool)
        
        return True

    async def create_assistant_for_tool(self, tool_id: str, force_recreate: bool = False) -> Dict[str, Any]:
        """Create an OpenAI Assistant for a tool if it has assistant options enabled."""
        try:
            tool = self.get_by_id(tool_id)
            if not tool:
                return {'success': False, 'error': 'Tool not found'}
            
            assistant_options = self.get_assistant_options(tool_id)
            if not assistant_options.get('enabled', False):
                return {'success': False, 'error': 'Assistant not enabled for this tool'}
            
            # Check if assistant already exists and force_recreate is False
            if assistant_options.get('assistant_id') and not force_recreate:
                return {
                    'success': True, 
                    'assistant_id': assistant_options['assistant_id'],
                    'message': 'Assistant already exists'
                }
            
            if not self.implementation_manager:
                return {'success': False, 'error': 'Implementation module system not available'}
            
            # Get tool's configuration for API key
            config = tool.get('config', {})
            
            # Map tool config to implementation config format
            impl_config = self._map_tool_config_to_implementation(config, 'openai_assistant_api')
            
            # Get OpenAI Assistant API implementation with tool's configuration
            openai_assistant_module = self.implementation_manager.get_implementation('openai_assistant_api', impl_config)
            if not openai_assistant_module:
                return {'success': False, 'error': 'OpenAI Assistant API implementation not found or configuration invalid'}
            
            # Create assistant configuration
            assistant_name = f"Tool Assistant: {tool.get('name', 'Unnamed Tool')}"
            assistant_description = f"AI Assistant for tool '{tool.get('name')}' - {tool.get('description', '')}"
            instructions = assistant_options.get('instructions', '') or f"You are an AI assistant for the tool '{tool.get('name')}'. Help users with tasks related to this tool."
            model = assistant_options.get('model', 'gpt-4-turbo-preview')
            
            # Create the assistant via implementation module
            create_result = await openai_assistant_module.execute_async({
                'action': 'create_assistant',
                'assistant_name': assistant_name,
                'assistant_description': assistant_description,
                'instructions': instructions,
                'model': model,
                'metadata': json.dumps({
                    'tool_id': tool_id,
                    'tool_name': tool.get('name'),
                    'created_by': 'vntrai_tool_system'
                })
            })
            
            if create_result.get('success'):
                assistant_id = create_result.get('assistant_id')
                
                # Update tool with assistant ID
                assistant_options['assistant_id'] = assistant_id
                self.update_assistant_options(tool_id, assistant_options)
                
                return {
                    'success': True,
                    'assistant_id': assistant_id,
                    'message': f'Assistant created successfully for tool {tool.get("name")}'
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to create assistant: {create_result.get("error", "Unknown error")}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error creating assistant: {str(e)}'
            }
    
    async def chat_with_tool_assistant(self, tool_id: str, message: str, thread_id: str = None) -> Dict[str, Any]:
        """Chat with a tool's assistant."""
        try:
            tool = self.get_by_id(tool_id)
            if not tool:
                return {'success': False, 'error': 'Tool not found'}
            
            assistant_options = self.get_assistant_options(tool_id)
            if not assistant_options.get('enabled', False):
                return {'success': False, 'error': 'Assistant not enabled for this tool'}
            
            assistant_id = assistant_options.get('assistant_id')
            if not assistant_id:
                # Auto-create assistant if enabled
                if assistant_options.get('auto_create', True):
                    create_result = await self.create_assistant_for_tool(tool_id)
                    if not create_result.get('success'):
                        return create_result
                    assistant_id = create_result.get('assistant_id')
                else:
                    return {'success': False, 'error': 'No assistant configured for this tool'}
            
            if not self.implementation_manager:
                return {'success': False, 'error': 'Implementation module system not available'}
            
            # Get tool's configuration for API key
            config = tool.get('config', {})
            
            # Map tool config to implementation config format
            impl_config = self._map_tool_config_to_implementation(config, 'openai_assistant_api')
            
            # Get OpenAI Assistant API implementation with tool's configuration
            openai_assistant_module = self.implementation_manager.get_implementation('openai_assistant_api', impl_config)
            if not openai_assistant_module:
                return {'success': False, 'error': 'OpenAI Assistant API implementation not found or configuration invalid'}
            
            # Chat with assistant
            chat_params = {
                'action': 'chat',
                'assistant_id': assistant_id,
                'message': message
            }
            
            if thread_id:
                chat_params['thread_id'] = thread_id
            
            chat_result = await openai_assistant_module.execute_async(chat_params)
            
            return chat_result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error chatting with assistant: {str(e)}'
            }
    
    def _map_tool_config_to_implementation(self, config: Dict[str, Any], implementation_name: str) -> Dict[str, Any]:
        """Map tool configuration to implementation configuration format"""
        impl_config = config.copy()
        
        # Mapping für OpenAI Assistant API
        if implementation_name == 'openai_assistant_api':
            if 'openai_api_key' in config and 'api_key' not in config:
                impl_config['api_key'] = config['openai_api_key']
        
        return impl_config

# Global instance
tools_manager = ToolsManager()
