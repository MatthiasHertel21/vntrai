"""
Knowledge Management API Routes
Handles CRUD operations for agent knowledge items
"""

from flask import request, jsonify
from app.routes.agents import agents_bp
from app.utils.data_manager import agents_manager
from .api_utils import validate_json_request, success_response, error_response, get_agent_or_404


@agents_bp.route('/knowledge', methods=['POST'])
def api_create_knowledge():
    """Create knowledge item via API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        knowledge_data = data.get('knowledge', {})
        
        if not agent_id or not knowledge_data:
            return error_response('Missing agent_id or knowledge data')
        
        success = agents_manager.add_knowledge_item(agent_id, knowledge_data)
        if success:
            return success_response('Knowledge item created successfully')
        else:
            return error_response('Failed to create knowledge item', 500)
            
    except Exception as e:
        return error_response(str(e), 500)


@agents_bp.route('/knowledge/<knowledge_id>', methods=['PUT'])
def api_update_knowledge(knowledge_id):
    """Update knowledge item via API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        knowledge_data = data.get('knowledge', {})
        
        if not agent_id:
            return error_response('Missing agent_id')
        
        success = agents_manager.update_knowledge_item(agent_id, knowledge_id, knowledge_data)
        if success:
            return success_response('Knowledge item updated successfully')
        else:
            return error_response('Failed to update knowledge item', 500)
            
    except Exception as e:
        return error_response(str(e), 500)


@agents_bp.route('/knowledge/<knowledge_id>', methods=['DELETE'])
def api_delete_knowledge(knowledge_id):
    """Delete knowledge item via API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return error_response('Missing agent_id')
        
        success = agents_manager.remove_knowledge_item(agent_id, knowledge_id)
        if success:
            return success_response('Knowledge item deleted successfully')
        else:
            return error_response('Failed to delete knowledge item', 500)
            
    except Exception as e:
        return error_response(str(e), 500)
