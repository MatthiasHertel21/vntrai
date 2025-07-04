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
    """Manager for agents data with Sprint 18 Task Management Revolution"""
    
    def __init__(self):
        super().__init__('agents')
    
    def create_agent(self, name: str, category: str = 'general', description: str = '') -> Dict[str, Any]:
        """Create new agent with Sprint 18 task structure"""
        agent = {
            'uuid': str(uuid.uuid4()),  # Primary UUID
            'id': str(uuid.uuid4()),     # Secondary ID for compatibility
            'name': name,
            'category': category,
            'description': description,
            'status': 'active',
            
            # Sprint 18: Task definitions stored in agent
            'tasks': [],  # Array of task definitions
            
            # Knowledge base and files
            'knowledge_base': [],
            'files': [],
            
            # AI Assistant configuration
            'ai_assistant_tool': '',  # Tool ID with assistant option
            'assistant_id': '',
            'assistant_model': 'gpt-4-turbo-preview',
            'assistant_tools_retrieval': False,
            'assistant_tools_code_interpreter': False,
            'use_openai_assistant': False,
            
            # Agent usage modes (from Sprint 17.5)
            'use_as_agent': True,
            'use_as_insight': False,
            'quick_actions': [],
            
            # Metadata
            'metadata': {
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

    # Sprint 18: Task Management Methods
    def add_task_definition(self, agent_id: str, task: Dict[str, Any]) -> bool:
        """Add task definition to agent (Sprint 18)"""
        agent = self.load(agent_id)
        if not agent:
            return False
        
        # Ensure task has required fields for Sprint 18
        if 'uuid' not in task:
            task['uuid'] = str(uuid.uuid4())
        # Ensure both id and uuid exist for compatibility
        if 'id' not in task:
            task['id'] = task['uuid']  # Use uuid as id for validator compatibility
        if 'type' not in task:
            task['type'] = 'ai'  # Default to AI task
        if 'name' not in task:
            task['name'] = f"Task {len(agent['tasks']) + 1}"
        if 'order' not in task:
            task['order'] = len(agent['tasks']) + 1
        if 'created_at' not in task:
            task['created_at'] = datetime.now().isoformat()
        
        task['updated_at'] = datetime.now().isoformat()
        
        if 'tasks' not in agent:
            agent['tasks'] = []
        
        agent['tasks'].append(task)
        agent['updated_at'] = datetime.now().isoformat()
        return self.save(agent)
    
    def update_task_definition(self, agent_id: str, task_uuid: str, task_data: Dict[str, Any]) -> bool:
        """Update task definition in agent (Sprint 18)"""
        agent = self.load(agent_id)
        if not agent or 'tasks' not in agent:
            return False
        
        for i, task in enumerate(agent['tasks']):
            if task.get('uuid') == task_uuid:
                task_data['uuid'] = task_uuid
                task_data['updated_at'] = datetime.now().isoformat()
                # Preserve order and creation time
                if 'order' not in task_data:
                    task_data['order'] = task.get('order', i + 1)
                if 'created_at' not in task_data:
                    task_data['created_at'] = task.get('created_at', datetime.now().isoformat())
                
                agent['tasks'][i] = {**task, **task_data}
                agent['updated_at'] = datetime.now().isoformat()
                return self.save(agent)
        
        return False
    
    def remove_task_definition(self, agent_id: str, task_uuid: str) -> bool:
        """Remove task definition from agent (Sprint 18)"""
        agent = self.load(agent_id)
        if not agent or 'tasks' not in agent:
            return False
        
        original_count = len(agent['tasks'])
        agent['tasks'] = [task for task in agent['tasks'] if task.get('uuid') != task_uuid]
        
        if len(agent['tasks']) < original_count:
            # Reorder remaining tasks
            for i, task in enumerate(agent['tasks']):
                task['order'] = i + 1
            agent['updated_at'] = datetime.now().isoformat()
            return self.save(agent)
        
        return False
    
    def reorder_task_definitions(self, agent_id: str, task_uuids: List[str]) -> bool:
        """Reorder task definitions in agent (Sprint 18)"""
        agent = self.load(agent_id)
        if not agent or 'tasks' not in agent:
            return False
        
        # Create task dictionary for quick lookup
        tasks_dict = {task['uuid']: task for task in agent['tasks']}
        
        # Reorder tasks and update order field
        reordered_tasks = []
        for i, task_uuid in enumerate(task_uuids):
            if task_uuid in tasks_dict:
                task = tasks_dict[task_uuid]
                task['order'] = i + 1
                task['updated_at'] = datetime.now().isoformat()
                reordered_tasks.append(task)
        
        # Add any tasks that weren't in the reorder list
        for task in agent['tasks']:
            if task['uuid'] not in task_uuids:
                task['order'] = len(reordered_tasks) + 1
                reordered_tasks.append(task)
        
        agent['tasks'] = reordered_tasks
        agent['updated_at'] = datetime.now().isoformat()
        return self.save(agent)
    
    def get_task_definition(self, agent_id: str, task_uuid: str) -> Optional[Dict[str, Any]]:
        """Get specific task definition from agent (Sprint 18)"""
        agent = self.load(agent_id)
        if not agent or 'tasks' not in agent:
            return None
        
        for task in agent['tasks']:
            if task.get('uuid') == task_uuid:
                return task
        
        return None
    
    def get_task_definitions(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all task definitions from agent (Sprint 18)"""
        agent = self.load(agent_id)
        if not agent or 'tasks' not in agent:
            return []
        
        # Sort by order field
        return sorted(agent['tasks'], key=lambda x: x.get('order', 0))

    # Assistant-enabled tools filtering for Sprint 18
    def get_assistant_enabled_tools(self) -> List[Dict[str, Any]]:
        """Get tools that have assistant option enabled (Sprint 18)"""
        return tools_manager.get_tools_with_assistant_enabled()
    
    def validate_assistant_tool_selection(self, agent_id: str, tool_id: str) -> bool:
        """Validate that selected tool has assistant option enabled (Sprint 18)"""
        if not tool_id:
            return False
        
        tool = tools_manager.get_by_id(tool_id)
        if not tool:
            return False
        
        return tools_manager.is_assistant_enabled(tool_id)

    def get_agent_statistics(self) -> Dict[str, Any]:
        """Get statistics about agents for overview page"""
        all_agents = self.load_all()
        
        # Count by status
        status_counts = {
            'active': 0,
            'inactive': 0,
            'draft': 0
        }
        
        # Count by category
        category_counts = {}
        
        # Count by use_as field (Sprint 17.5)
        use_as_counts = {
            'agent': 0,
            'insight': 0,
            'both': 0
        }
        
        # Task statistics (Sprint 18)
        total_tasks = 0
        agents_with_tasks = 0
        
        for agent in all_agents:
            # Status counts
            status = agent.get('status', 'inactive')
            if status in status_counts:
                status_counts[status] += 1
            
            # Category counts
            category = agent.get('category', 'general')
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # Use as counts (Sprint 17.5)
            use_as_agent = agent.get('use_as_agent', True)
            use_as_insight = agent.get('use_as_insight', False)
            
            if use_as_agent and use_as_insight:
                use_as_counts['both'] += 1
            elif use_as_insight:
                use_as_counts['insight'] += 1
            else:
                use_as_counts['agent'] += 1
            
            # Task statistics (Sprint 18)
            tasks = agent.get('tasks', [])
            if tasks:
                agents_with_tasks += 1
                total_tasks += len(tasks)
        
        # Calculate averages
        total_agents = len(all_agents)
        avg_tasks_per_agent = round(total_tasks / total_agents, 1) if total_agents > 0 else 0
        
        return {
            'total_agents': total_agents,
            'status_counts': status_counts,
            'category_counts': category_counts,
            'use_as_counts': use_as_counts,
            'task_statistics': {
                'total_tasks': total_tasks,
                'agents_with_tasks': agents_with_tasks,
                'avg_tasks_per_agent': avg_tasks_per_agent
            }
        }

    def get_single_agent_statistics(self, agent_id: str) -> Dict[str, Any]:
        """Get statistics for a single agent"""
        agent = self.load(agent_id)
        if not agent:
            return {}
        
        # Count tasks (Sprint 18)
        tasks = agent.get('tasks', [])
        task_counts = {
            'total': len(tasks),
            'ai_tasks': len([t for t in tasks if t.get('type') == 'ai']),
            'tool_tasks': len([t for t in tasks if t.get('type') == 'tool'])
        }
        
        # Count files
        files = agent.get('files', [])
        file_count = len(files)
        
        # Count knowledge base items
        knowledge_base = agent.get('knowledge_base', [])
        knowledge_count = len(knowledge_base)
        
        # Assistant status
        has_assistant = bool(agent.get('assistant_id'))
        assistant_tool = agent.get('ai_assistant_tool')
        
        return {
            'task_counts': task_counts,
            'file_count': file_count,
            'knowledge_count': knowledge_count,
            'has_assistant': has_assistant,
            'assistant_tool': assistant_tool,
            'status': agent.get('status', 'inactive'),
            'category': agent.get('category', 'general'),
            'use_as_agent': agent.get('use_as_agent', True),
            'use_as_insight': agent.get('use_as_insight', False)
        }

    # Legacy task methods - maintained for backward compatibility but marked for removal
    def add_task(self, agent_id: str, task: Dict[str, Any]) -> bool:
        """Legacy method - use add_task_definition instead (Sprint 18)"""
        # Redirect to new method
        return self.add_task_definition(agent_id, task)
    
    def update_task(self, agent_id: str, task_id: str, task_data: Dict[str, Any]) -> bool:
        """Legacy method - use update_task_definition instead (Sprint 18)"""
        # Try to find by id or uuid
        agent = self.load(agent_id)
        if not agent or 'tasks' not in agent:
            return False
        
        # Find task by id or uuid
        task_uuid = None
        for task in agent['tasks']:
            if task.get('id') == task_id or task.get('uuid') == task_id:
                task_uuid = task.get('uuid', task.get('id'))
                break
        
        if task_uuid:
            return self.update_task_definition(agent_id, task_uuid, task_data)
        
        return False
    
    def remove_task(self, agent_id: str, task_id: str) -> bool:
        """Legacy method - use remove_task_definition instead (Sprint 18)"""
        # Try to find by id or uuid
        agent = self.load(agent_id)
        if not agent or 'tasks' not in agent:
            return False
        
        # Find task by id or uuid
        task_uuid = None
        for task in agent['tasks']:
            if task.get('id') == task_id or task.get('uuid') == task_id:
                task_uuid = task.get('uuid', task.get('id'))
                break
        
        if task_uuid:
            return self.remove_task_definition(agent_id, task_uuid)
        
        return False
    
    def reorder_tasks(self, agent_id: str, task_ids: List[str]) -> bool:
        """Legacy method - use reorder_task_definitions instead (Sprint 18)"""
        # Convert ids to uuids if needed
        agent = self.load(agent_id)
        if not agent or 'tasks' not in agent:
            return False
        
        task_uuids = []
        for task_id in task_ids:
            for task in agent['tasks']:
                if task.get('id') == task_id or task.get('uuid') == task_id:
                    task_uuids.append(task.get('uuid', task.get('id')))
                    break
        
        return self.reorder_task_definitions(agent_id, task_uuids)

class AgentRunManager(DataManager):
    """Manager for agent runs with Sprint 18 task execution"""
    
    def __init__(self):
        super().__init__('agentrun')
        self._save_locks = {}  # Track save operations to prevent concurrent writes
    
    def save(self, item: Dict[str, Any]) -> bool:
        """Save agent run using uuid instead of id"""
        uuid_val = item.get('uuid')
        if not uuid_val:
            uuid_val = str(uuid.uuid4())
            item['uuid'] = uuid_val
        
        # Remove id field if it exists to avoid duplication
        if 'id' in item:
            del item['id']
        
        # Update timestamp
        item['updated_at'] = datetime.now().isoformat()
        if 'created_at' not in item:
            item['created_at'] = item['updated_at']
        
        file_path = self.data_dir / f"{uuid_val}.json"
        
        # Safe write with temporary file to prevent corruption
        temp_path = file_path.with_suffix('.tmp')
        try:
            # Write to temporary file first
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(item, f, indent=2, ensure_ascii=False)
            
            # Validate JSON by reading it back
            with open(temp_path, 'r', encoding='utf-8') as f:
                json.load(f)  # This will raise an exception if JSON is invalid
            
            # If validation passes, move temp file to final location
            import shutil
            shutil.move(str(temp_path), str(file_path))
            return True
            
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error saving {self.data_type} {uuid_val}: {e}")
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            return False
    
    def load(self, uuid_val: str) -> Optional[Dict[str, Any]]:
        """Load agent run by uuid"""
        file_path = self.data_dir / f"{uuid_val}.json"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Ensure uuid field exists and remove id field if present
            if 'uuid' not in data:
                data['uuid'] = uuid_val
            if 'id' in data:
                del data['id']
                
            return data
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading {self.data_type} {uuid_val}: {e}")
            return None
    
    def create_agent_run(self, agent_id: str, name: str = '') -> Dict[str, Any]:
        """Create new agent run with Sprint 18 task state structure"""
        agent_run = {
            'uuid': str(uuid.uuid4()),
            'agent_uuid': agent_id,
            'name': name or f"Run {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            'status': 'created',
            
            # Sprint 18: Task execution states stored in agentrun
            'task_states': [],  # Array of task execution states
            
            # Run context and inputs
            'inputs': {},
            'context': {},
            'outputs': {},
            
            # Metadata
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'started_at': None,
            'completed_at': None
        }
        
        # Initialize task states from agent's task definitions
        agent = agents_manager.load(agent_id)
        if agent and 'tasks' in agent:
            for task_def in agent['tasks']:
                task_state = {
                    'task_uuid': task_def['uuid'],
                    'status': 'pending',
                    'inputs': {},
                    'outputs': {},
                    'results': {},
                    'error': None,
                    'started_at': None,
                    'completed_at': None,
                    'execution_time': None
                }
                agent_run['task_states'].append(task_state)
        
        if self.save(agent_run):
            return agent_run
        return None
    
    def get_task_state(self, run_id: str, task_uuid: str) -> Optional[Dict[str, Any]]:
        """Get task execution state from agent run (Sprint 18)"""
        agent_run = self.load(run_id)
        if not agent_run or 'task_states' not in agent_run:
            return None
        
        for task_state in agent_run['task_states']:
            if task_state.get('task_uuid') == task_uuid:
                return task_state
        
        return None
    
    def update_task_state(self, run_id: str, task_uuid: str, state_data: Dict[str, Any]) -> bool:
        """Update task execution state in agent run (Sprint 18)"""
        print(f"[DEBUG] update_task_state called with run_id={run_id}, task_uuid={task_uuid}, state_data={state_data}")
        
        # Prevent concurrent modifications of the same run
        if run_id in self._save_locks:
            print(f"[DEBUG] Save operation already in progress for run_id={run_id}, skipping")
            return False
            
        self._save_locks[run_id] = True
        
        try:
            agent_run = self.load(run_id)
            if not agent_run:
                print(f"[DEBUG] Agent run not found: {run_id}")
                return False
                
            if 'task_states' not in agent_run:
                print(f"[DEBUG] No task_states in agent run: {run_id}, creating empty list")
                agent_run['task_states'] = []
            
            print(f"[DEBUG] Found {len(agent_run['task_states'])} task states")
            
            # Look for existing task state
            for i, task_state in enumerate(agent_run['task_states']):
                print(f"[DEBUG] Checking task state {i}: task_uuid={task_state.get('task_uuid')}")
                if task_state.get('task_uuid') == task_uuid:
                    print(f"[DEBUG] Found matching task state at index {i}")
                    # Update state data while preserving task_uuid
                    updated_state = {**task_state, **state_data}
                    updated_state['task_uuid'] = task_uuid
                    updated_state['updated_at'] = datetime.now().isoformat()
                    
                    agent_run['task_states'][i] = updated_state
                    agent_run['updated_at'] = datetime.now().isoformat()
                    
                    result = self.save(agent_run)
                    print(f"[DEBUG] Save result: {result}")
                    return result
            
            # No existing task state found, create a new one
            print(f"[DEBUG] No matching task state found for task_uuid: {task_uuid}, creating new one")
            new_task_state = {
                'task_uuid': task_uuid,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                **state_data  # Add the provided state data
            }
            
            agent_run['task_states'].append(new_task_state)
            agent_run['updated_at'] = datetime.now().isoformat()
            
            result = self.save(agent_run)
            print(f"[DEBUG] Created new task state, save result: {result}")
            return result
            
        finally:
            # Always release the lock
            if run_id in self._save_locks:
                del self._save_locks[run_id]
    
    def set_task_status(self, run_id: str, task_uuid: str, status: str, error: str = None) -> bool:
        """Set task status (Sprint 18)"""
        state_data = {'status': status}
        
        if status == 'running' and not self.get_task_state(run_id, task_uuid).get('started_at'):
            state_data['started_at'] = datetime.now().isoformat()
        elif status in ['completed', 'error', 'skipped']:
            state_data['completed_at'] = datetime.now().isoformat()
            
            # Calculate execution time if started
            task_state = self.get_task_state(run_id, task_uuid)
            if task_state and task_state.get('started_at'):
                started = datetime.fromisoformat(task_state['started_at'].replace('Z', '+00:00'))
                completed = datetime.now()
                execution_time = (completed - started).total_seconds()
                state_data['execution_time'] = execution_time
        
        if error:
            state_data['error'] = error
        
        return self.update_task_state(run_id, task_uuid, state_data)
    
    def set_task_inputs(self, run_id: str, task_uuid: str, inputs: Dict[str, Any]) -> bool:
        """Set task inputs (Sprint 18)"""
        return self.update_task_state(run_id, task_uuid, {'inputs': inputs})
    
    def set_task_outputs(self, run_id: str, task_uuid: str, outputs: Dict[str, Any]) -> bool:
        """Set task outputs (Sprint 18)"""
        return self.update_task_state(run_id, task_uuid, {'outputs': outputs})
    
    def set_task_results(self, run_id: str, task_uuid: str, results: Dict[str, Any]) -> bool:
        """Set task results (Sprint 18)"""
        return self.update_task_state(run_id, task_uuid, {'results': results})
    
    def get_task_progress(self, run_id: str) -> Dict[str, Any]:
        """Get overall task progress for agent run (Sprint 18)"""
        agent_run = self.load(run_id)
        if not agent_run or 'task_states' not in agent_run:
            return {
                'total': 0,
                'pending': 0,
                'running': 0,
                'completed': 0,
                'error': 0,
                'skipped': 0,
                'progress_percent': 0
            }
        
        task_states = agent_run['task_states']
        total = len(task_states)
        
        status_counts = {
            'pending': 0,
            'running': 0,
            'completed': 0,
            'error': 0,
            'skipped': 0
        }
        
        for task_state in task_states:
            status = task_state.get('status', 'pending')
            if status in status_counts:
                status_counts[status] += 1
        
        completed_count = status_counts['completed'] + status_counts['error'] + status_counts['skipped']
        progress_percent = (completed_count / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'progress_percent': round(progress_percent, 1),
            **status_counts
        }
    
    def get_task_definitions_with_states(self, run_id: str) -> List[Dict[str, Any]]:
        """Get task definitions combined with their execution states (Sprint 18)"""
        try:
            agent_run = self.load(run_id)
            if not agent_run:
                return []
            
            agent = agents_manager.load(agent_run['agent_uuid'])
            if not agent or 'tasks' not in agent:
                return []
            
            # Combine task definitions with their states
            combined_tasks = []
            task_states_dict = {ts['task_uuid']: ts for ts in agent_run.get('task_states', [])}
            
            for task_def in sorted(agent['tasks'], key=lambda x: x.get('order', 0)):
                try:
                    task_uuid = task_def.get('uuid', '')
                    if not task_uuid:
                        current_app.logger.warning(f"Task without UUID found in agent {agent_run['agent_uuid']}")
                        continue
                        
                    task_state = task_states_dict.get(task_uuid, {
                        'task_uuid': task_uuid,
                        'status': 'pending',
                        'inputs': {},
                        'outputs': {},
                        'results': {},
                        'error': None
                    })
                    
                    combined_task = {
                        'definition': task_def,
                        'state': task_state,
                        'uuid': task_uuid,
                        'name': task_def.get('name', 'Unnamed Task'),
                        'type': task_def.get('type', 'ai'),
                        'status': task_state.get('status', 'pending')
                    }
                    combined_tasks.append(combined_task)
                except Exception as task_error:
                    current_app.logger.error(f"Error processing task {task_def}: {str(task_error)}")
                    continue
            
            return combined_tasks
        except Exception as e:
            current_app.logger.error(f"Error in get_task_definitions_with_states: {str(e)}")
            return []
    
    def sync_task_definitions(self, run_id: str) -> bool:
        """Sync task definitions from agent to agent run (Sprint 18)"""
        agent_run = self.load(run_id)
        if not agent_run:
            return False
        
        agent = agents_manager.load(agent_run['agent_uuid'])
        if not agent or 'tasks' not in agent:
            return False
        
        # Get existing task states
        existing_states = {ts['task_uuid']: ts for ts in agent_run.get('task_states', [])}
        
        # Create new task states based on current agent task definitions
        new_task_states = []
        for task_def in agent['tasks']:
            task_uuid = task_def['uuid']
            
            # Preserve existing state if it exists, otherwise create new
            if task_uuid in existing_states:
                new_task_states.append(existing_states[task_uuid])
            else:
                new_task_states.append({
                    'task_uuid': task_uuid,
                    'status': 'pending',
                    'inputs': {},
                    'outputs': {},
                    'results': {},
                    'error': None,
                    'started_at': None,
                    'completed_at': None,
                    'execution_time': None
                })
        
        agent_run['task_states'] = new_task_states
        agent_run['updated_at'] = datetime.now().isoformat()
        return self.save(agent_run)

    def get_agent_runs(self, agent_uuid: str) -> List[Dict[str, Any]]:
        """Get all agent runs for a specific agent"""
        all_runs = self.get_all()
        agent_runs = [run for run in all_runs if run.get('agent_uuid') == agent_uuid]
        # Sort by created_at timestamp (newest first)
        return sorted(agent_runs, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def get_most_recent_run(self, agent_uuid: str) -> Optional[Dict[str, Any]]:
        """Get the most recent agent run for a specific agent"""
        agent_runs = self.get_agent_runs(agent_uuid)
        return agent_runs[0] if agent_runs else None
    
    def set_language_preference(self, run_id: str, language: str) -> bool:
        """Set language preference for an agent run"""
        try:
            agent_run = self.load(run_id)
            if not agent_run:
                return False
            
            # Set language preference in agent run
            agent_run['language_preference'] = language
            agent_run['updated_at'] = datetime.now().isoformat()
            
            return self.save(agent_run)
            
        except Exception as e:
            print(f"Error setting language preference for run {run_id}: {e}")
            return False
    
    def get_language_preference(self, run_id: str) -> str:
        """Get language preference for an agent run"""
        try:
            agent_run = self.load(run_id)
            if not agent_run:
                return 'auto'
            
            return agent_run.get('language_preference', 'auto')
            
        except Exception as e:
            print(f"Error getting language preference for run {run_id}: {e}")
            return 'auto'

# Global instances for Sprint 18
integrations_manager = IntegrationsManager()
tools_manager = ToolsManager()
agents_manager = AgentsManager()
agent_run_manager = AgentRunManager()
icon_manager = IconManager()

# Update global instances
