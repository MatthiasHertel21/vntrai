"""
API routes for agents - RESTful API endpoints for external access
Handles legacy API endpoints and general agent API functions
"""

from flask import Blueprint, request, jsonify, current_app
from app.utils.data_manager import agents_manager, tools_manager
from datetime import datetime
import uuid

# Get blueprint from the parent module
from app.routes.agents import agents_bp

@agents_bp.route('/api/task', methods=['POST'])
def api_create_task():
    """Create task via API - DEPRECATED"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        task_data = data.get('task', {})
        
        if not agent_id or not task_data:
            return jsonify({'error': 'Missing agent_id or task data'}), 400
        
        success = agents_manager.add_task(agent_id, task_data)
        if success:
            return jsonify({'message': 'Task created successfully'})
        else:
            return jsonify({'error': 'Failed to create task'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/task/<task_id>', methods=['PUT'])
def api_update_task(task_id):
    """Update task via API - DEPRECATED"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        task_data = data.get('task', {})
        
        if not agent_id:
            return jsonify({'error': 'Missing agent_id'}), 400
        
        success = agents_manager.update_task(agent_id, task_id, task_data)
        if success:
            return jsonify({'message': 'Task updated successfully'})
        else:
            return jsonify({'error': 'Failed to update task'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/task/<task_id>', methods=['DELETE'])
def api_delete_task(task_id):
    """Delete task via API - DEPRECATED"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({'error': 'Missing agent_id'}), 400
        
        success = agents_manager.remove_task(agent_id, task_id)
        if success:
            return jsonify({'message': 'Task deleted successfully'})
        else:
            return jsonify({'error': 'Failed to delete task'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/tasks/reorder', methods=['POST'])
def api_reorder_tasks():
    """DEPRECATED: Legacy task reorder API - use Sprint 18 Task Management API instead"""
    return jsonify({
        'error': 'This API endpoint has been deprecated. Please use the Sprint 18 Task Management API: /api/task_management/agent/<agent_uuid>/tasks/reorder',
        'deprecated': True,
        'migration_url': '/api/task_management/agent/<agent_uuid>/tasks/reorder'
    }), 410  # HTTP 410 Gone

@agents_bp.route('/knowledge', methods=['POST'])
def api_create_knowledge():
    """Create knowledge item via API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        knowledge_data = data.get('knowledge', {})
        
        if not agent_id or not knowledge_data:
            return jsonify({'error': 'Missing agent_id or knowledge data'}), 400
        
        success = agents_manager.add_knowledge_item(agent_id, knowledge_data)
        if success:
            return jsonify({'message': 'Knowledge item created successfully'})
        else:
            return jsonify({'error': 'Failed to create knowledge item'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/knowledge/<knowledge_id>', methods=['PUT'])
def api_update_knowledge(knowledge_id):
    """Update knowledge item via API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        knowledge_data = data.get('knowledge', {})
        
        if not agent_id:
            return jsonify({'error': 'Missing agent_id'}), 400
        
        success = agents_manager.update_knowledge_item(agent_id, knowledge_id, knowledge_data)
        if success:
            return jsonify({'message': 'Knowledge item updated successfully'})
        else:
            return jsonify({'error': 'Failed to update knowledge item'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/knowledge/<knowledge_id>', methods=['DELETE'])
def api_delete_knowledge(knowledge_id):
    """Delete knowledge item via API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({'error': 'Missing agent_id'}), 400
        
        success = agents_manager.remove_knowledge_item(agent_id, knowledge_id)
        if success:
            return jsonify({'message': 'Knowledge item deleted successfully'})
        else:
            return jsonify({'error': 'Failed to delete knowledge item'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/quick-actions/<agent_id>', methods=['GET', 'POST'])
def api_quick_actions(agent_id):
    """Manage quick actions for an agent"""
    try:
        if request.method == 'GET':
            # Load agent and return quick actions
            agent = agents_manager.load(agent_id)
            if not agent:
                return jsonify({'error': 'Agent not found'}), 404
            
            quick_actions = agent.get('quick_actions', [])
            return jsonify({'quick_actions': quick_actions})
        
        else:  # POST
            # Update quick actions
            data = request.get_json()
            quick_actions = data.get('quick_actions', [])
            
            agent = agents_manager.load(agent_id)
            if not agent:
                return jsonify({'error': 'Agent not found'}), 404
            
            agent['quick_actions'] = quick_actions
            agent['updated_at'] = datetime.now().isoformat()
            
            agents_manager.save(agent)
            
            return jsonify({'message': 'Quick actions updated successfully'})
            
    except Exception as e:
        current_app.logger.error(f"Error managing quick actions for agent {agent_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/clear-data/<agent_id>', methods=['POST'])
def api_clear_agent_data(agent_id):
    """Clear agent data (tasks, knowledge base)"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        # Get clear options from request
        data = request.get_json() or {}
        clear_tasks = data.get('clear_tasks', True)
        clear_knowledge = data.get('clear_knowledge', True)
        clear_variables = data.get('clear_variables', False)
        
        cleared_items = []
        
        if clear_tasks:
            agent['tasks'] = []
            cleared_items.append('tasks')
        
        if clear_knowledge:
            agent['knowledge_base'] = []
            cleared_items.append('knowledge base')
        
        if clear_variables:
            agent['global_variables'] = {}
            cleared_items.append('global variables')
        
        # Update timestamp
        agent['updated_at'] = datetime.now().isoformat()
        
        # Save agent
        agents_manager.save(agent)
        
        return jsonify({
            'message': f'Agent data cleared successfully: {", ".join(cleared_items)}',
            'cleared': cleared_items
        })
        
    except Exception as e:
        current_app.logger.error(f"Error clearing agent data for {agent_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/assistant-enabled-tools', methods=['GET'])
def api_get_assistant_enabled_tools():
    """Get tools that can be enabled for OpenAI Assistant integration"""
    try:
        # Get all tools and filter for assistant-compatible ones
        all_tools = tools_manager.get_all()
        assistant_tools = []
        
        for tool in all_tools:
            if tool.get('assistant_compatible', False):
                assistant_tools.append({
                    'id': tool.get('id'),
                    'name': tool.get('name'),
                    'description': tool.get('description'),
                    'type': tool.get('type', 'function')
                })
        
        return jsonify({'tools': assistant_tools})
        
    except Exception as e:
        current_app.logger.error(f"Error getting assistant-enabled tools: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/api/tools', methods=['GET'])
def api_get_tools():
    """Get all available tools for agent configuration"""
    try:
        # Get all tools from tools manager
        all_tools = tools_manager.get_all()
        
        # Filter for AI assistant compatible tools
        ai_tools = []
        for tool in all_tools:
            if tool.get('type') in ['openai_chatcompletion', 'openai_assistant_api', 'anthropic', 'google_gemini']:
                ai_tools.append({
                    'id': tool.get('id'),
                    'name': tool.get('name'),
                    'type': tool.get('type'),
                    'description': tool.get('description', ''),
                    'display_name': f"{tool.get('name', 'Unknown')} ({tool.get('type', 'Unknown')})"
                })
        
        return jsonify({
            'success': True,
            'tools': ai_tools
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting tools: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'tools': []
        }), 500
