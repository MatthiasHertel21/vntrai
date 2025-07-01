"""
File Operations Utilities für vntrai Data Management
Handles JSON file operations for integrations and tools
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from werkzeug.utils import secure_filename

# Implementation Module Integration
try:
    from app.implementation_modules import implementation_manager
    IMPLEMENTATION_MODULES_AVAILABLE = True
except ImportError:
    IMPLEMENTATION_MODULES_AVAILABLE = False

class DataManager:
    """Base class for data management operations"""
    
    def __init__(self, data_type: str):
        self.data_type = data_type  # 'integrations' or 'tools'
        
        # Try to use Flask app config if available, otherwise use relative path
        try:
            from flask import current_app
            self.data_dir = Path(current_app.config.get('DATA_DIR', '/app/data')) / data_type
        except (ImportError, RuntimeError):
            # Fallback for when not in Flask app context
            self.data_dir = Path(__file__).parent.parent.parent / "data" / data_type
            
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def get_all_ids(self) -> List[str]:
        """Get all item IDs"""
        return [f.stem for f in self.data_dir.glob("*.json")]
    
    def exists(self, item_id: str) -> bool:
        """Check if item exists"""
        return (self.data_dir / f"{item_id}.json").exists()
    
    def load(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Load single item by ID"""
        file_path = self.data_dir / f"{item_id}.json"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {self.data_type} {item_id}: {e}")
            return None
    
    def load_all(self) -> List[Dict[str, Any]]:
        """Load all items"""
        items = []
        for file_path in self.data_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    item = json.load(f)
                    items.append(item)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading {file_path}: {e}")
                continue
        
        return sorted(items, key=lambda x: x.get('name', ''))
    
    def save(self, item: Dict[str, Any]) -> bool:
        """Save single item"""
        item_id = item.get('id')
        if not item_id:
            item_id = str(uuid.uuid4())
            item['id'] = item_id
        
        # Update timestamp
        item['updated_at'] = datetime.now().isoformat()
        if 'created_at' not in item:
            item['created_at'] = item['updated_at']
        
        file_path = self.data_dir / f"{item_id}.json"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(item, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving {self.data_type} {item_id}: {e}")
            return False
    
    def delete(self, item_id: str) -> bool:
        """Delete single item"""
        file_path = self.data_dir / f"{item_id}.json"
        if not file_path.exists():
            return False
        
        try:
            file_path.unlink()
            return True
        except IOError as e:
            print(f"Error deleting {self.data_type} {item_id}: {e}")
            return False
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all items - alias for load_all"""
        return self.load_all()
    
    def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get item by ID - alias for load"""
        return self.load(item_id)
    
    def create(self, data: Dict[str, Any]) -> bool:
        """Create new item with provided data"""
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow().isoformat() + 'Z'
        
        data['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        
        return self.save(data)
    
    def update(self, item_id: str, data: Dict[str, Any]) -> bool:
        """Update existing item"""
        data['id'] = item_id  # Ensure ID is set
        data['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        
        return self.save(data)
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search items by query"""
        all_items = self.load_all()
        query_lower = query.lower()
        
        results = []
        for item in all_items:
            # Search in name, description, and vendor (if exists)
            searchable_text = (
                item.get('name', '').lower() + ' ' +
                item.get('description', '').lower() + ' ' +
                item.get('vendor', '').lower() + ' ' +
                item.get('tool_definition', '').lower()
            )
            
            if query_lower in searchable_text:
                results.append(item)
        
        return results

    def filter_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Filter items by status"""
        all_items = self.load_all()
        return [item for item in all_items if item.get('status') == status]
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about items"""
        all_items = self.load_all()
        
        stats = {
            'total': len(all_items),
            'active': 0,
            'inactive': 0,
            'other': 0
        }
        
        for item in all_items:
            status = item.get('status', 'unknown')
            if status == 'active':
                stats['active'] += 1
            elif status == 'inactive':
                stats['inactive'] += 1
            else:
                stats['other'] += 1
        
        return stats


class IntegrationsManager(DataManager):
    """Manager for integrations data"""
    
    def __init__(self):
        super().__init__('integrations')
    
    def create_integration(self, name: str, vendor: str, integration_type: str = 'api') -> Dict[str, Any]:
        """Create new integration with v036 format"""
        integration = {
            'id': str(uuid.uuid4()),
            'name': name,
            'vendor': vendor,
            'type': integration_type,
            'description': '',
            'status': 'inactive',
            'config_params': [],
            'input_params': [],
            'output_params': [],
            'api_documentation_link': '',
            'vendor_icon': '',
            'version': '1.0.0',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        if self.save(integration):
            return integration
        return None
    
    def filter_by_vendor(self, vendor: str) -> List[Dict[str, Any]]:
        """Filter integrations by vendor"""
        all_integrations = self.load_all()
        return [item for item in all_integrations if item.get('vendor', '').lower() == vendor.lower()]
    
    def filter_by_type(self, integration_type: str) -> List[Dict[str, Any]]:
        """Filter integrations by type"""
        all_integrations = self.load_all()
        return [item for item in all_integrations if item.get('type') == integration_type]
    
    def get_by_implementation(self, implementation: str) -> Optional[Dict[str, Any]]:
        """Get integration by implementation type"""
        all_integrations = self.load_all()
        for integration in all_integrations:
            if integration.get('implementation') == implementation:
                return integration
        return None


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
            from app.utils.data_manager import IntegrationsManager
            integrations_manager = IntegrationsManager()
            integration = integrations_manager.get_by_id(integration_id)
        
        # Falls nicht gefunden, versuche über Namen
        if not integration:
            from app.utils.data_manager import IntegrationsManager
            integrations_manager = IntegrationsManager()
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


class IconManager:
    """Manager for vendor icons"""
    
    def __init__(self):
        self.icons_dir = Path(__file__).parent.parent / "static" / "icons" / "vendors"
        self.icons_dir.mkdir(parents=True, exist_ok=True)
    
    def get_icon_path(self, integration_id: str) -> Optional[str]:
        """Get icon path for integration"""
        # Check for various formats
        for ext in ['.png', '.jpg', '.jpeg', '.svg']:
            icon_path = self.icons_dir / f"{integration_id}{ext}"
            if icon_path.exists():
                return f"/static/icons/vendors/{integration_id}{ext}"
        
        return None
    
    def has_icon(self, integration_id: str) -> bool:
        """Check if integration has an icon"""
        return self.get_icon_path(integration_id) is not None
    
    def save_icon(self, integration_id: str, file_data: bytes, filename: str) -> bool:
        """Save icon file"""
        # Get file extension
        ext = Path(filename).suffix.lower()
        if ext not in ['.png', '.jpg', '.jpeg', '.svg']:
            return False
        
        icon_path = self.icons_dir / f"{integration_id}{ext}"
        try:
            with open(icon_path, 'wb') as f:
                f.write(file_data)
            return True
        except IOError:
            return False
    
    def delete_icon(self, integration_id: str) -> bool:
        """Delete icon file"""
        for ext in ['.png', '.jpg', '.jpeg', '.svg']:
            icon_path = self.icons_dir / f"{integration_id}{ext}"
            if icon_path.exists():
                try:
                    icon_path.unlink()
                    return True
                except IOError:
                    pass
        return False


class AgentsManager(DataManager):
    """Agent data management operations"""
    
    def __init__(self):
        super().__init__('agents')
    
    def create_agent(self, name: str, category: str = 'General', description: str = '') -> Dict[str, Any]:
        """Create new agent with foundation structure"""
        agent = {
            'id': str(uuid.uuid4()),
            'name': name,
            'category': category,
            'description': description,
            'status': 'inactive',
            'assistant_id': None,
            'assistant_tool_id': None,
            'use_as_agent': True,  # Default: can be used as agent
            'use_as_insight': False,  # Default: not for insights
            'quick_actions': [],  # Custom quick actions for insights
            'tasks': [],
            'knowledge_base': [],
            'files': [],
            'global_variables': {},
            'system_prompt': '',
            'metadata': {
                'icon': 'default',
                'color': 'blue',
                'tags': []
            },
            'version': '1.0.0',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        if self.save(agent):
            return agent
        return None
    
    def get_agent_statistics(self, agent_id: str) -> Dict[str, Any]:
        """Get agent run statistics"""
        # TODO: Will be implemented in Sprint 19 (AgentRun system)
        return {
            'total_runs': 0,
            'active_runs': 0,
            'completed_runs': 0,
            'failed_runs': 0,
            'last_run': None
        }
    
    def filter_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Filter agents by category"""
        all_agents = self.load_all()
        return [agent for agent in all_agents if agent.get('category', '').lower() == category.lower()]
    
    def filter_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Filter agents by status"""
        all_agents = self.load_all()
        return [agent for agent in all_agents if agent.get('status') == status]
    
    def add_task(self, agent_id: str, task: Dict[str, Any]) -> bool:
        """Add task to agent"""
        agent = self.load(agent_id)
        if not agent:
            return False
        
        # Ensure task has required fields
        if 'id' not in task:
            task['id'] = str(uuid.uuid4())
        if 'status' not in task:
            task['status'] = 'pending'
        if 'created_at' not in task:
            task['created_at'] = datetime.now().isoformat()
        
        task['updated_at'] = datetime.now().isoformat()
        
        agent['tasks'].append(task)
        return self.save(agent)
    
    def update_task(self, agent_id: str, task_id: str, task_data: Dict[str, Any]) -> bool:
        """Update specific task in agent"""
        agent = self.load(agent_id)
        if not agent:
            return False
        
        for i, task in enumerate(agent['tasks']):
            if task.get('id') == task_id:
                task_data['id'] = task_id
                task_data['updated_at'] = datetime.now().isoformat()
                agent['tasks'][i] = {**task, **task_data}
                return self.save(agent)
        
        return False
    
    def remove_task(self, agent_id: str, task_id: str) -> bool:
        """Remove task from agent"""
        agent = self.load(agent_id)
        if not agent:
            return False
        
        agent['tasks'] = [task for task in agent['tasks'] if task.get('id') != task_id]
        return self.save(agent)
    
    def reorder_tasks(self, agent_id: str, task_ids: List[str]) -> bool:
        """Reorder tasks in agent"""
        agent = self.load(agent_id)
        if not agent:
            return False
        
        # Create new task order based on provided IDs
        tasks_dict = {task['id']: task for task in agent['tasks']}
        agent['tasks'] = [tasks_dict[task_id] for task_id in task_ids if task_id in tasks_dict]
        
        return self.save(agent)
    
    def add_knowledge_item(self, agent_id: str, knowledge_item: Dict[str, Any]) -> bool:
        """Add knowledge item to agent"""
        agent = self.load(agent_id)
        if not agent:
            return False
        
        if 'id' not in knowledge_item:
            knowledge_item['id'] = str(uuid.uuid4())
        if 'created_at' not in knowledge_item:
            knowledge_item['created_at'] = datetime.now().isoformat()
        
        knowledge_item['updated_at'] = datetime.now().isoformat()
        
        agent['knowledge_base'].append(knowledge_item)
        return self.save(agent)
    
    def update_knowledge_item(self, agent_id: str, knowledge_id: str, knowledge_data: Dict[str, Any]) -> bool:
        """Update specific knowledge item in agent"""
        agent = self.load(agent_id)
        if not agent:
            return False
        
        for i, item in enumerate(agent['knowledge_base']):
            if item.get('id') == knowledge_id:
                knowledge_data['id'] = knowledge_id
                knowledge_data['updated_at'] = datetime.now().isoformat()
                agent['knowledge_base'][i] = {**item, **knowledge_data}
                return self.save(agent)
        
        return False
    
    def remove_knowledge_item(self, agent_id: str, knowledge_id: str) -> bool:
        """Remove knowledge item from agent"""
        agent = self.load(agent_id)
        if not agent:
            return False
        
        agent['knowledge_base'] = [item for item in agent['knowledge_base'] if item.get('id') != knowledge_id]
        return self.save(agent)
    
    def load(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load agent by ID with migration for missing fields"""
        agent = super().load(agent_id)
        if agent:
            # Migrate old agents to have use_as fields if they don't exist
            updated = False
            if 'use_as_agent' not in agent:
                agent['use_as_agent'] = True  # Default for existing agents
                updated = True
            if 'use_as_insight' not in agent:
                agent['use_as_insight'] = False  # Default for existing agents  
                updated = True
            if 'quick_actions' not in agent:
                agent['quick_actions'] = []  # Default empty quick actions
                updated = True
            
            # Save migrated agent
            if updated:
                self.save(agent)
                
        return agent


# Global instances
integrations_manager = IntegrationsManager()
tools_manager = ToolsManager()
agents_manager = AgentsManager()
icon_manager = IconManager()
