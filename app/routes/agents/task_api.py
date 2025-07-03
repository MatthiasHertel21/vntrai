"""
Task Management API Routes
Handles CRUD operations for agent tasks
"""

from flask import request, jsonify
from app.routes.agents import agents_bp
from app.utils.data_manager import agents_manager
from .api_utils import validate_json_request, success_response, error_response, get_agent_or_404


@agents_bp.route('/api/task', methods=['POST'])
def api_create_task():
    """Create task via API - DEPRECATED"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        task_data = data.get('task', {})
        
        if not agent_id or not task_data:
            return error_response('Missing agent_id or task data')
        
        success = agents_manager.add_task(agent_id, task_data)
        if success:
            return success_response('Task created successfully')
        else:
            return error_response('Failed to create task', 500)
            
    except Exception as e:
        return error_response(str(e), 500)


@agents_bp.route('/task/<task_id>', methods=['PUT'])
def api_update_task(task_id):
    """Update task via API - DEPRECATED"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        task_data = data.get('task', {})
        
        if not agent_id:
            return error_response('Missing agent_id')
        
        success = agents_manager.update_task(agent_id, task_id, task_data)
        if success:
            return success_response('Task updated successfully')
        else:
            return error_response('Failed to update task', 500)
            
    except Exception as e:
        return error_response(str(e), 500)


@agents_bp.route('/task/<task_id>', methods=['DELETE'])
def api_delete_task(task_id):
    """Delete task via API - DEPRECATED"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return error_response('Missing agent_id')
        
        success = agents_manager.remove_task(agent_id, task_id)
        if success:
            return success_response('Task deleted successfully')
        else:
            return error_response('Failed to delete task', 500)
            
    except Exception as e:
        return error_response(str(e), 500)


@agents_bp.route('/tasks/reorder', methods=['POST'])
def api_reorder_tasks():
    """DEPRECATED: Legacy task reorder API - use Sprint 18 Task Management API instead"""
    return jsonify({
        'error': 'This API endpoint has been deprecated. Please use the Sprint 18 Task Management API: /api/task_management/agent/<agent_uuid>/tasks/reorder',
        'deprecated': True,
        'migration_url': '/api/task_management/agent/<agent_uuid>/tasks/reorder'
    }), 410  # HTTP 410 Gone
