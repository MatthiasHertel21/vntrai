"""
Shared utilities for agent API routes
"""

from flask import jsonify, current_app
from app.utils.data_manager import agents_manager, tools_manager, agent_run_manager
from datetime import datetime
import uuid
import json


def get_agent_or_404(agent_id):
    """Get agent by ID or return 404 error"""
    agent = agents_manager.get_agent(agent_id)
    if not agent:
        return None, jsonify({'error': 'Agent not found'}), 404
    return agent, None, None


def get_tool_config_by_reference(tool_reference):
    """Get tool config by reference (tool:uuid or integration:uuid)"""
    if not tool_reference:
        return None
        
    if tool_reference.startswith('tool:'):
        tool_uuid = tool_reference.replace('tool:', '')
        return tools_manager.get_tool(tool_uuid)
    elif tool_reference.startswith('integration:'):
        # Handle integration reference if needed
        return None
    return None


def validate_json_request():
    """Validate that request contains valid JSON"""
    if not request.json:
        return jsonify({'error': 'No JSON data provided'}), 400
    return None


def success_response(message="Success", data=None):
    """Standard success response"""
    response = {'success': True, 'message': message}
    if data:
        response['data'] = data
    return jsonify(response)


def error_response(message, status_code=400):
    """Standard error response"""
    return jsonify({'success': False, 'error': message}), status_code


def generate_uuid():
    """Generate a new UUID string"""
    return str(uuid.uuid4())


def current_timestamp():
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()


def log_info(message):
    """Log info message without Flask context dependency"""
    print(f"[INFO] {message}")


def log_debug(message):
    """Log debug message without Flask context dependency"""
    print(f"[DEBUG] {message}")


def log_error(message):
    """Log error message without Flask context dependency"""
    print(f"[ERROR] {message}")
