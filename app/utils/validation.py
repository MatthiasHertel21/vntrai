"""
Validation utilities for vntrai data
"""

import re
from typing import Dict, List, Any, Optional, Tuple

class ValidationError(Exception):
    """Custom validation error"""
    pass

class DataValidator:
    """Validates integration and tool data"""
    
    @staticmethod
    def validate_integration(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate integration data structure"""
        errors = []
        
        # Required fields
        required_fields = ['id', 'name', 'vendor', 'type']
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Field validations
        if 'name' in data:
            if not isinstance(data['name'], str) or len(data['name'].strip()) < 1:
                errors.append("Name must be a non-empty string")
            elif len(data['name']) > 100:
                errors.append("Name must not exceed 100 characters")
        
        if 'vendor' in data:
            if not isinstance(data['vendor'], str) or len(data['vendor'].strip()) < 1:
                errors.append("Vendor must be a non-empty string")
            elif len(data['vendor']) > 50:
                errors.append("Vendor must not exceed 50 characters")
        
        if 'type' in data:
            valid_types = ['api', 'webhook', 'database', 'file', 'service', 'other']
            if data['type'] not in valid_types:
                errors.append(f"Type must be one of: {', '.join(valid_types)}")
        
        if 'status' in data:
            valid_statuses = ['active', 'inactive', 'testing', 'error']
            if data['status'] not in valid_statuses:
                errors.append(f"Status must be one of: {', '.join(valid_statuses)}")
        
        if 'description' in data and isinstance(data['description'], str):
            if len(data['description']) > 500:
                errors.append("Description must not exceed 500 characters")
        
        if 'version' in data:
            if not isinstance(data['version'], str):
                errors.append("Version must be a string")
            elif not re.match(r'^\d+\.\d+\.\d+$', data['version']):
                errors.append("Version must follow semantic versioning (x.y.z)")
        
        # Validate config structure
        if 'config' in data and not isinstance(data['config'], dict):
            errors.append("Config must be a dictionary")
        
        if 'auth' in data and not isinstance(data['auth'], dict):
            errors.append("Auth must be a dictionary")
        
        if 'endpoints' in data and not isinstance(data['endpoints'], dict):
            errors.append("Endpoints must be a dictionary")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_tool(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate tool data structure"""
        errors = []
        
        # Required fields
        required_fields = ['id', 'name', 'category', 'type']
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Field validations
        if 'name' in data:
            if not isinstance(data['name'], str) or len(data['name'].strip()) < 1:
                errors.append("Name must be a non-empty string")
            elif len(data['name']) > 100:
                errors.append("Name must not exceed 100 characters")
        
        if 'category' in data:
            valid_categories = [
                'utility', 'analysis', 'automation', 'monitoring', 
                'reporting', 'integration', 'security', 'development', 
                'communication', 'other'
            ]
            if data['category'] not in valid_categories:
                errors.append(f"Category must be one of: {', '.join(valid_categories)}")
        
        if 'type' in data:
            valid_types = ['script', 'executable', 'web', 'api', 'service', 'other']
            if data['type'] not in valid_types:
                errors.append(f"Type must be one of: {', '.join(valid_types)}")
        
        if 'status' in data:
            valid_statuses = ['active', 'inactive', 'testing', 'error', 'maintenance']
            if data['status'] not in valid_statuses:
                errors.append(f"Status must be one of: {', '.join(valid_statuses)}")
        
        if 'description' in data and isinstance(data['description'], str):
            if len(data['description']) > 500:
                errors.append("Description must not exceed 500 characters")
        
        if 'version' in data:
            if not isinstance(data['version'], str):
                errors.append("Version must be a string")
            elif not re.match(r'^\d+\.\d+\.\d+$', data['version']):
                errors.append("Version must follow semantic versioning (x.y.z)")
        
        # Validate executable path
        if 'executable' in data and data['executable']:
            if not isinstance(data['executable'], str):
                errors.append("Executable must be a string")
        
        # Validate arguments
        if 'arguments' in data:
            if not isinstance(data['arguments'], list):
                errors.append("Arguments must be a list")
            else:
                for i, arg in enumerate(data['arguments']):
                    if not isinstance(arg, str):
                        errors.append(f"Argument {i} must be a string")
        
        # Validate dependencies
        if 'dependencies' in data:
            if not isinstance(data['dependencies'], list):
                errors.append("Dependencies must be a list")
            else:
                for i, dep in enumerate(data['dependencies']):
                    if not isinstance(dep, str):
                        errors.append(f"Dependency {i} must be a string")
        
        # Validate dictionaries
        if 'environment' in data and not isinstance(data['environment'], dict):
            errors.append("Environment must be a dictionary")
        
        if 'config' in data and not isinstance(data['config'], dict):
            errors.append("Config must be a dictionary")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_json_structure(data: Any) -> Tuple[bool, List[str]]:
        """Validate basic JSON structure"""
        errors = []
        
        if not isinstance(data, dict):
            errors.append("Data must be a JSON object")
            return False, errors
        
        # Check for basic structure
        if 'id' in data and data['id']:
            if not isinstance(data['id'], str):
                errors.append("ID must be a string")
            elif not re.match(r'^[a-f0-9-]{36}$', data['id']):
                errors.append("ID must be a valid UUID")
        
        # Check timestamps
        timestamp_fields = ['created_at', 'updated_at']
        for field in timestamp_fields:
            if field in data and data[field]:
                if not isinstance(data[field], str):
                    errors.append(f"{field} must be a string")
                elif not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', data[field]):
                    errors.append(f"{field} must be in ISO format")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            return ""
        
        # Remove potentially dangerous characters
        value = re.sub(r'[<>"\']', '', value)
        
        # Trim whitespace and limit length
        value = value.strip()[:max_length]
        
        return value
    
    @staticmethod
    def sanitize_integration_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize integration data"""
        sanitized = {}
        
        # String fields
        string_fields = {
            'name': 100,
            'vendor': 50,
            'type': 20,
            'description': 500,
            'status': 20,
            'version': 20,
            'implementation': 100  # CRITICAL FIX: implementation field hinzugefügt
        }
        
        for field, max_len in string_fields.items():
            if field in data:
                sanitized[field] = DataValidator.sanitize_string(data[field], max_len)
        
        # Copy other fields as-is (with type validation)
        if 'id' in data:
            sanitized['id'] = str(data['id'])
        
        if 'config' in data and isinstance(data['config'], dict):
            sanitized['config'] = data['config']
        
        if 'auth' in data and isinstance(data['auth'], dict):
            sanitized['auth'] = data['auth']
        
        if 'endpoints' in data and isinstance(data['endpoints'], dict):
            sanitized['endpoints'] = data['endpoints']
        
        # CRITICAL FIX: JSON-Parameter Felder hinzufügen
        if 'config_params' in data and isinstance(data['config_params'], list):
            sanitized['config_params'] = data['config_params']
            
        if 'input_params' in data and isinstance(data['input_params'], list):
            sanitized['input_params'] = data['input_params']
            
        if 'output_params' in data and isinstance(data['output_params'], list):
            sanitized['output_params'] = data['output_params']
        
        # Copy metadata
        if 'metadata' in data and isinstance(data['metadata'], dict):
            sanitized['metadata'] = data['metadata']
            # Only copy endpoints if it exists
            if 'endpoints' in data:
                sanitized['endpoints'] = data['endpoints']
        
        # Copy timestamps
        for field in ['created_at', 'updated_at']:
            if field in data:
                sanitized[field] = str(data[field])
        
        return sanitized
    
    @staticmethod
    def sanitize_tool_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize tool data"""
        sanitized = {}
        
        # String fields
        string_fields = {
            'name': 100,
            'category': 30,
            'type': 20,
            'description': 500,
            'status': 20,
            'executable': 255,
            'version': 20
        }
        
        for field, max_len in string_fields.items():
            if field in data:
                sanitized[field] = DataValidator.sanitize_string(data[field], max_len)
        
        # Copy other fields as-is (with type validation)
        if 'id' in data:
            sanitized['id'] = str(data['id'])
        
        if 'arguments' in data and isinstance(data['arguments'], list):
            sanitized['arguments'] = [str(arg) for arg in data['arguments']]
        
        if 'dependencies' in data and isinstance(data['dependencies'], list):
            sanitized['dependencies'] = [str(dep) for dep in data['dependencies']]
        
        if 'environment' in data and isinstance(data['environment'], dict):
            sanitized['environment'] = data['environment']
        
        if 'config' in data and isinstance(data['config'], dict):
            sanitized['config'] = data['config']
        
        # Copy timestamps
        for field in ['created_at', 'updated_at']:
            if field in data:
                sanitized[field] = str(data[field])
        
        return sanitized
    
    @staticmethod
    def sanitize_agent_data(agent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize agent data to ensure only allowed fields are saved
        """
        allowed_fields = {
            'id', 'name', 'category', 'description', 'status',
            'assistant_id', 'assistant_tool_id', 'ai_assistant_tool', 'model', 'instructions',
            'assistant_tools',  # New field for Assistant Tools (file_search, code_interpreter, etc.)
            'use_as_agent', 'use_as_insight', 'quick_actions',  # New fields for insights functionality
            'tasks', 'knowledge_base', 'files', 'global_variables', 'system_prompt', 'metadata',
            'version', 'created_at', 'updated_at'
        }
        
        # Create sanitized copy with only allowed fields
        sanitized = {}
        
        for field in allowed_fields:
            if field in agent:
                sanitized[field] = agent[field]
        
        # Ensure required fields exist with defaults
        if 'status' not in sanitized:
            sanitized['status'] = 'inactive'
        
        if 'tasks' not in sanitized:
            sanitized['tasks'] = []
        
        if 'knowledge_base' not in sanitized:
            sanitized['knowledge_base'] = []
        
        if 'files' not in sanitized:
            sanitized['files'] = []
        
        if 'global_variables' not in sanitized:
            sanitized['global_variables'] = {}
        
        if 'metadata' not in sanitized:
            sanitized['metadata'] = {
                'icon': 'default',
                'color': 'blue',
                'tags': []
            }
        
        # Ensure tasks have required id field (Sprint 18 compatibility fix)
        if 'tasks' in sanitized and isinstance(sanitized['tasks'], list):
            for task in sanitized['tasks']:
                if isinstance(task, dict):
                    # Ensure both id and uuid exist for compatibility
                    if 'uuid' in task and 'id' not in task:
                        task['id'] = task['uuid']
                    elif 'id' in task and 'uuid' not in task:
                        task['uuid'] = task['id']
                    elif 'id' not in task and 'uuid' not in task:
                        # Generate new UUID for task without any identifier
                        import uuid as uuid_module
                        new_uuid = str(uuid_module.uuid4())
                        task['uuid'] = new_uuid
                        task['id'] = new_uuid
        
        return sanitized

    @staticmethod
    def validate_agent_data(agent: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate agent data structure and content
        """
        errors = []
        
        # Required fields
        required_fields = ['id', 'name']
        for field in required_fields:
            if field not in agent or not agent[field]:
                errors.append(f"Missing required field: {field}")
        
        # Name validation
        if 'name' in agent:
            if not isinstance(agent['name'], str) or len(agent['name'].strip()) < 1:
                errors.append("Agent name must be a non-empty string")
            elif len(agent['name']) > 100:
                errors.append("Agent name must not exceed 100 characters")
        
        # Category validation
        if 'category' in agent:
            if not isinstance(agent['category'], str):
                errors.append("Category must be a string")
            elif len(agent['category']) > 50:
                errors.append("Category must not exceed 50 characters")
        
        # Status validation
        if 'status' in agent:
            valid_statuses = ['active', 'inactive', 'testing', 'error']
            if agent['status'] not in valid_statuses:
                errors.append(f"Status must be one of: {', '.join(valid_statuses)}")
        
        # Description validation
        if 'description' in agent and isinstance(agent['description'], str):
            if len(agent['description']) > 1000:
                errors.append("Description must not exceed 1000 characters")
        
        # Tasks validation
        if 'tasks' in agent:
            if not isinstance(agent['tasks'], list):
                errors.append("Tasks must be a list")
            else:
                for i, task in enumerate(agent['tasks']):
                    if not isinstance(task, dict):
                        errors.append(f"Task {i} must be a dictionary")
                    elif 'id' not in task:
                        errors.append(f"Task {i} missing required field: id")
                    elif 'type' in task and task['type'] not in ['ai', 'tool']:
                        errors.append(f"Task {i} type must be 'ai' or 'tool'")
        
        # Knowledge base validation
        if 'knowledge_base' in agent:
            if not isinstance(agent['knowledge_base'], list):
                errors.append("Knowledge base must be a list")
            else:
                for i, item in enumerate(agent['knowledge_base']):
                    if not isinstance(item, dict):
                        errors.append(f"Knowledge item {i} must be a dictionary")
                    elif 'id' not in item:
                        errors.append(f"Knowledge item {i} missing required field: id")
        
        # Global variables validation
        if 'global_variables' in agent and not isinstance(agent['global_variables'], dict):
            errors.append("Global variables must be a dictionary")
        
        # AI Assistant Tool validation
        if 'ai_assistant_tool' in agent and agent['ai_assistant_tool']:
            ai_tool = agent['ai_assistant_tool']
            if ai_tool.startswith('tool:'):
                # Validate that the tool exists and is assistant-enabled
                from app.utils.data_manager import DataManager
                tools_manager = DataManager('tools')
                try:
                    tool_id = ai_tool[5:]  # Remove 'tool:' prefix
                    tool = tools_manager.load(tool_id)
                    if not tool:
                        errors.append(f"AI Assistant Tool not found: {tool_id}")
                    else:
                        assistant_options = tool.get('options', {}).get('assistant', {})
                        if not assistant_options.get('enabled', False):
                            errors.append(f"Tool {tool.get('name', tool_id)} is not assistant-enabled")
                except Exception as e:
                    errors.append(f"Error validating AI Assistant Tool: {str(e)}")
            else:
                errors.append("AI Assistant Tool must start with 'tool:' prefix for tool-based assistants")
        
        return len(errors) == 0, errors
    
class ToolValidator:
    """Validator für Tool-Daten basierend auf v036 Schema"""
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> List[str]:
        """Validiert Tool-Daten und gibt Fehlerliste zurück"""
        errors = []
        
        # Required fields
        required_fields = ['id', 'name', 'tool_definition']
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Pflichtfeld fehlt: {field}")
        
        # Field validations
        if 'name' in data:
            if not isinstance(data['name'], str) or len(data['name'].strip()) < 1:
                errors.append("Name muss ein nicht-leerer String sein")
            elif len(data['name']) > 100:
                errors.append("Name darf maximal 100 Zeichen haben")
        
        if 'description' in data and data['description']:
            if not isinstance(data['description'], str):
                errors.append("Beschreibung muss ein String sein")
            elif len(data['description']) > 500:
                errors.append("Beschreibung darf maximal 500 Zeichen haben")
        
        if 'tool_definition' in data:
            if not isinstance(data['tool_definition'], str) or len(data['tool_definition'].strip()) < 1:
                errors.append("Tool-Definition muss ein nicht-leerer String sein")
        
        # Validate JSON fields
        json_fields = ['config', 'prefilled_inputs']
        for field in json_fields:
            if field in data and data[field] is not None:
                if not isinstance(data[field], dict):
                    errors.append(f"{field} muss ein Dictionary sein")
        
        # Validate locked_inputs
        if 'locked_inputs' in data and data['locked_inputs'] is not None:
            if not isinstance(data['locked_inputs'], list):
                errors.append("locked_inputs muss eine Liste sein")
            else:
                for item in data['locked_inputs']:
                    if not isinstance(item, str):
                        errors.append("locked_inputs muss eine Liste von Strings sein")
        
        # Validate status
        if 'status' in data:
            valid_statuses = ['connected', 'not_connected', 'error']
            if data['status'] not in valid_statuses:
                errors.append(f"Status muss einer von {valid_statuses} sein")
        
        return errors

class IntegrationValidator:
    """Validator für Integration-Daten basierend auf v036 Schema"""
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> List[str]:
        """Validiert Integration-Daten und gibt Fehlerliste zurück"""
        errors = []
        
        # Required fields
        required_fields = ['id', 'name', 'vendor']
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Pflichtfeld fehlt: {field}")
        
        # Field validations
        if 'name' in data:
            if not isinstance(data['name'], str) or len(data['name'].strip()) < 1:
                errors.append("Name muss ein nicht-leerer String sein")
            elif len(data['name']) > 100:
                errors.append("Name darf maximal 100 Zeichen haben")
        
        if 'vendor' in data:
            if not isinstance(data['vendor'], str) or len(data['vendor'].strip()) < 1:
                errors.append("Vendor muss ein nicht-leerer String sein")
            elif len(data['vendor']) > 50:
                errors.append("Vendor darf maximal 50 Zeichen haben")
        
        if 'description' in data and data['description']:
            if not isinstance(data['description'], str):
                errors.append("Beschreibung muss ein String sein")
            elif len(data['description']) > 500:
                errors.append("Beschreibung darf maximal 500 Zeichen haben")
        
        # Validate parameter arrays
        param_fields = ['config_params', 'input_params', 'output_params']
        for field in param_fields:
            if field in data and data[field] is not None:
                if not isinstance(data[field], list):
                    errors.append(f"{field} muss eine Liste sein")
                else:
                    for i, param in enumerate(data[field]):
                        if not isinstance(param, dict):
                            errors.append(f"{field}[{i}] muss ein Dictionary sein")
                        else:
                            # Validate parameter structure
                            if 'name' not in param or not param['name']:
                                errors.append(f"{field}[{i}] fehlt 'name'")
                            if 'type' not in param or not param['type']:
                                errors.append(f"{field}[{i}] fehlt 'type'")
        
        return errors

# Global validator instance
validator = DataValidator()
