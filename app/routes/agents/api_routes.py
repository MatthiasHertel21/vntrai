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

@agents_bp.route('/api/<agent_id>/reassign_assistant', methods=['POST'])
def api_reassign_assistant(agent_id):
    """Reassign assistant to an agent"""
    try:
        data = request.get_json()
        new_assistant_id = data.get('new_assistant_id')
        
        if not new_assistant_id:
            return jsonify({
                'success': False,
                'message': 'New assistant ID is required'
            }), 400
        
        # Load the agent
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({
                'success': False,
                'message': 'Agent not found'
            }), 404
        
        # Use assistant manager to reassign the assistant
        from app.utils.assistant_manager import assistant_manager
        success = assistant_manager.reassign_assistant(agent, new_assistant_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Assistant successfully reassigned to {new_assistant_id}',
                'assistant_id': new_assistant_id
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to reassign assistant. Please check the assistant ID and try again.'
            }), 400
            
    except Exception as e:
        current_app.logger.error(f"Error reassigning assistant for agent {agent_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Internal error: {str(e)}'
        }), 500

@agents_bp.route('/api/<agent_id>/create_assistant', methods=['POST'])
def api_create_assistant(agent_id):
    """Create and assign assistant to an agent with comprehensive traceability"""
    import time
    from datetime import datetime
    
    trace_log = []
    
    def add_trace(step, status, details=None, error=None):
        """Add entry to trace log"""
        entry = {
            'step': step,
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details,
            'error': error
        }
        trace_log.append(entry)
        current_app.logger.info(f"Assistant Creation Trace - {step}: {status} - {details or ''}")
    
    try:
        add_trace("Request Received", "SUCCESS", f"Creating assistant for agent {agent_id}")
        
        data = request.get_json()
        tool_id = data.get('tool_id')
        trace_level = data.get('trace_level', 'basic')
        
        if not tool_id:
            add_trace("Validation", "FAILED", "Tool ID is required")
            return jsonify({
                'success': False,
                'message': 'Tool ID is required',
                'trace_log': trace_log
            }), 400
        
        add_trace("Input Validation", "SUCCESS", f"Tool ID: {tool_id}, Trace Level: {trace_level}")
        
        # Load the agent
        add_trace("Agent Loading", "IN_PROGRESS", f"Loading agent {agent_id}")
        agent = agents_manager.load(agent_id)
        if not agent:
            add_trace("Agent Loading", "FAILED", f"Agent {agent_id} not found")
            return jsonify({
                'success': False,
                'message': 'Agent not found',
                'trace_log': trace_log
            }), 404
        
        add_trace("Agent Loading", "SUCCESS", f"Agent '{agent.get('name', 'Unknown')}' loaded successfully")
        
        # Check if agent already has an assistant
        if agent.get('assistant_id'):
            add_trace("Assistant Check", "WARNING", f"Agent already has assistant: {agent.get('assistant_id')}")
            return jsonify({
                'success': False,
                'message': f'Agent already has an assistant: {agent.get("assistant_id")}',
                'trace_log': trace_log
            }), 400
        
        add_trace("Assistant Check", "SUCCESS", "Agent has no existing assistant")
        
        # Load the tool
        add_trace("Tool Loading", "IN_PROGRESS", f"Loading tool {tool_id}")
        tool = tools_manager.load(tool_id)
        if not tool:
            add_trace("Tool Loading", "FAILED", f"Tool {tool_id} not found")
            return jsonify({
                'success': False,
                'message': 'Tool not found',
                'trace_log': trace_log
            }), 404
        
        # Check if tool has assistant integration enabled
        assistant_enabled = tool.get('options', {}).get('assistant', {}).get('enabled', False)
        if not assistant_enabled:
            add_trace("Tool Validation", "FAILED", "Tool does not have AI Assistant Integration enabled")
            return jsonify({
                'success': False,
                'message': 'Tool does not have AI Assistant Integration enabled',
                'trace_log': trace_log
            }), 400
        
        add_trace("Tool Loading", "SUCCESS", f"Tool '{tool.get('name', 'Unknown')}' loaded and validated")
        
        # Set the AI assistant tool in the agent
        add_trace("Agent Configuration", "IN_PROGRESS", "Setting AI assistant tool")
        agent['ai_assistant_tool'] = f"tool:{tool_id}"
        
        # Use assistant manager to create the assistant
        add_trace("Assistant Creation", "IN_PROGRESS", "Initiating assistant creation")
        from app.utils.assistant_manager import assistant_manager
        
        creation_start_time = time.time()
        assistant_id = assistant_manager.create_assistant_for_agent(agent)
        creation_duration = time.time() - creation_start_time
        
        if assistant_id:
            add_trace("Assistant Creation", "SUCCESS", 
                     f"Assistant created successfully: {assistant_id} (Duration: {creation_duration:.2f}s)")
            
            # Verify the agent was updated
            updated_agent = agents_manager.load(agent_id)
            if updated_agent and updated_agent.get('assistant_id') == assistant_id:
                add_trace("Agent Update", "SUCCESS", f"Agent successfully updated with assistant ID: {assistant_id}")
            else:
                add_trace("Agent Update", "WARNING", "Agent may not have been properly updated with assistant ID")
            
            # Get assistant details for response
            assistant_details = {
                'assistant_id': assistant_id,
                'model': agent.get('model', 'Unknown'),
                'tools_count': len(agent.get('tools', [])),
                'files_count': len(agent.get('knowledge_base', [])),
                'creation_time': datetime.utcnow().isoformat(),
                'creation_duration': f"{creation_duration:.2f}s"
            }
            
            add_trace("Response Preparation", "SUCCESS", 
                     f"Assistant details compiled: Model={assistant_details['model']}, " +
                     f"Tools={assistant_details['tools_count']}, Files={assistant_details['files_count']}")
            
            # Log comprehensive creation summary
            summary = f"""
=== ASSISTANT CREATION SUMMARY ===
Agent ID: {agent_id}
Agent Name: {agent.get('name', 'Unknown')}
Tool ID: {tool_id}
Tool Name: {tool.get('name', 'Unknown')}
Assistant ID: {assistant_id}
Model: {assistant_details['model']}
Tools Configured: {assistant_details['tools_count']}
Files Attached: {assistant_details['files_count']}
Creation Duration: {assistant_details['creation_duration']}
Creation Time: {assistant_details['creation_time']}
Trace Entries: {len(trace_log)}
"""
            current_app.logger.info(summary)
            add_trace("Creation Complete", "SUCCESS", "Assistant creation process completed successfully")
            
            return jsonify({
                'success': True,
                'message': 'Assistant created and assigned successfully',
                'details': assistant_details,
                'trace_log': trace_log if trace_level == 'detailed' else trace_log[-3:],  # Last 3 entries for basic
                'summary': summary.strip()
            })
        else:
            add_trace("Assistant Creation", "FAILED", "Assistant creation returned no ID")
            
            # Try to get more specific error information from the assistant manager logs
            try:
                # Check if it's a problem with the assistant API
                test_result = assistant_manager.assistant_api.list_assistants()
                if isinstance(test_result, list) or (isinstance(test_result, dict) and test_result.get('success')):
                    add_trace("API Connection Test", "SUCCESS", "Assistant API connection is working")
                else:
                    add_trace("API Connection Test", "FAILED", f"Assistant API issue: {test_result}")
            except Exception as api_test_error:
                add_trace("API Connection Test", "ERROR", f"Could not test API connection: {str(api_test_error)}")
            
            return jsonify({
                'success': False,
                'message': 'Failed to create assistant - check server logs for details',
                'trace_log': trace_log
            }), 500
            
    except Exception as e:
        error_msg = str(e)
        add_trace("Exception Occurred", "ERROR", f"Unexpected error: {error_msg}")
        current_app.logger.error(f"Error creating assistant for agent {agent_id}: {error_msg}", exc_info=True)
        
        return jsonify({
            'success': False,
            'message': f'Internal error: {error_msg}',
            'trace_log': trace_log
        }), 500
