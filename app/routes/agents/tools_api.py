"""
Tools and Quick Actions API Routes
Handles tool management and quick actions for agents
"""

from flask import request, jsonify, current_app
from app.routes.agents import agents_bp
from app.utils.data_manager import agents_manager, tools_manager
from .api_utils import (validate_json_request, success_response, error_response, 
                        get_agent_or_404, current_timestamp, log_error)


@agents_bp.route('/quick-actions/<agent_id>', methods=['GET', 'POST'])
def api_quick_actions(agent_id):
    """Manage quick actions for an agent"""
    try:
        if request.method == 'GET':
            # Load agent and return quick actions
            agent = agents_manager.load(agent_id)
            if not agent:
                return error_response('Agent not found', 404)
            
            quick_actions = agent.get('quick_actions', [])
            return jsonify({'quick_actions': quick_actions})
        
        else:  # POST
            # Update quick actions
            data = request.get_json()
            quick_actions = data.get('quick_actions', [])
            
            agent = agents_manager.load(agent_id)
            if not agent:
                return error_response('Agent not found', 404)
            
            agent['quick_actions'] = quick_actions
            agent['updated_at'] = current_timestamp()
            
            agents_manager.save(agent)
            
            # Sync assistant if configured (quick actions might affect assistant behavior)
            try:
                if agent.get('assistant_id') and agent.get('ai_assistant_tool'):
                    from app.utils.assistant_manager import assistant_manager
                    assistant_manager.update_assistant_for_agent(agent)
            except Exception as e:
                log_error(f"Error syncing assistant after quick actions update for agent {agent_id}: {str(e)}")
            
            return success_response('Quick actions updated successfully')
            
    except Exception as e:
        log_error(f"Error managing quick actions for agent {agent_id}: {str(e)}")
        return error_response(str(e), 500)


@agents_bp.route('/clear-data/<agent_id>', methods=['POST'])
def api_clear_agent_data(agent_id):
    """Clear agent data (tasks, knowledge base)"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return error_response('Agent not found', 404)
        
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
        agent['updated_at'] = current_timestamp()
        
        # Save agent
        agents_manager.save(agent)
        
        # Sync assistant if configured (cleared data might affect assistant behavior)
        try:
            if agent.get('assistant_id') and agent.get('ai_assistant_tool'):
                from app.utils.assistant_manager import assistant_manager
                assistant_manager.update_assistant_for_agent(agent)
        except Exception as e:
            log_error(f"Error syncing assistant after data clear for agent {agent_id}: {str(e)}")
        
        return success_response(
            f'Agent data cleared successfully: {", ".join(cleared_items)}',
            {'cleared': cleared_items}
        )
        
    except Exception as e:
        log_error(f"Error clearing agent data for {agent_id}: {str(e)}")
        return error_response(str(e), 500)


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
