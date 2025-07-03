"""
API routes for agents - RESTful API endpoints for external access
Handles legacy API endpoints and general agent API functions
"""

from flask import Blueprint, request, jsonify, current_app, Response
from app.utils.data_manager import agents_manager, tools_manager, agent_run_manager
from datetime import datetime
import uuid
import json
import time
import requests

# Import CSRF protection to exempt API endpoints
from app import csrf

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
            
            # Sync assistant if configured (quick actions might affect assistant behavior)
            try:
                if agent.get('assistant_id') and agent.get('ai_assistant_tool'):
                    from app.utils.assistant_manager import assistant_manager
                    assistant_manager.update_assistant_for_agent(agent)
            except Exception as e:
                current_app.logger.error(f"Error syncing assistant after quick actions update for agent {agent_id}: {str(e)}")
            
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
        
        # Sync assistant if configured (cleared data might affect assistant behavior)
        try:
            if agent.get('assistant_id') and agent.get('ai_assistant_tool'):
                from app.utils.assistant_manager import assistant_manager
                assistant_manager.update_assistant_for_agent(agent)
        except Exception as e:
            current_app.logger.error(f"Error syncing assistant after data clear for agent {agent_id}: {str(e)}")
        
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
                'message': 'OK',
                'details': assistant_details,
                'trace_log': trace_log if trace_level == 'detailed' else []  # No trace log for basic level
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

@agents_bp.route('/api/<agent_id>/remove_assistant', methods=['POST'])
def api_remove_assistant(agent_id):
    """Remove assistant from an agent"""
    try:
        current_app.logger.info(f"Removing assistant from agent {agent_id}")
        
        # Get agent from database
        agent = agent_storage.get_agent(agent_id)
        if not agent:
            current_app.logger.error(f"Agent {agent_id} not found")
            return jsonify({
                'success': False,
                'message': 'Agent not found'
            }), 404
        
        # Check if agent has an assistant
        if not agent.get('assistant_id'):
            return jsonify({
                'success': False,
                'message': 'No assistant assigned to this agent'
            }), 400
        
        assistant_id = agent['assistant_id']
        current_app.logger.info(f"Removing assistant {assistant_id} from agent {agent_id}")
        
        # Remove assistant_id from agent
        agent['assistant_id'] = None
        agent_storage.save_agent(agent)
        
        current_app.logger.info(f"Successfully removed assistant from agent {agent_id}")
        
        return jsonify({
            'success': True,
            'message': 'Assistant removed',
            'agent_id': agent_id,
            'removed_assistant_id': assistant_id
        })
        
    except Exception as e:
        error_msg = str(e)
        current_app.logger.error(f"Error removing assistant from agent {agent_id}: {error_msg}", exc_info=True)
        
        return jsonify({
            'success': False,
            'message': f'Internal error: {error_msg}'
        }), 500

@agents_bp.route('/api/<agent_id>/sync_assistant', methods=['POST'])
def api_sync_assistant(agent_id):
    """Synchronize agent configuration with OpenAI assistant with detailed response"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({'success': False, 'message': 'Agent not found'}), 404
        
        assistant_id = agent.get('assistant_id')
        if not assistant_id:
            return jsonify({'success': False, 'message': 'No assistant configured for this agent'}), 400
        
        # Get AI assistant tool
        ai_tool = agent.get('ai_assistant_tool', '')
        if not ai_tool or not ai_tool.startswith('tool:'):
            return jsonify({'success': False, 'message': 'No AI assistant tool configured'}), 400
        
        # Extract tool ID and validate the tool exists and is an AI assistant tool
        tool_id = ai_tool.replace('tool:', '')
        
        try:
            tool_data = tools_manager.get_by_id(tool_id)
            if not tool_data:
                return jsonify({'success': False, 'message': 'Selected AI assistant tool not found'}), 400
            
            # Check if it's an OpenAI Assistant tool by checking integration or tool definition
            tool_definition = tool_data.get('tool_definition', '')
            integration_id = tool_data.get('integration_id', '')
            
            # Load integration to verify it's an OpenAI Assistant integration
            if integration_id:
                from app.utils.data_manager import integrations_manager
                integration_data = integrations_manager.get_by_id(integration_id)
                if not integration_data or integration_data.get('implementation') != 'openai_assistant_api':
                    return jsonify({'success': False, 'message': 'Selected tool is not an OpenAI Assistant tool'}), 400
            elif tool_definition != 'OpenAI Assistant API':
                return jsonify({'success': False, 'message': 'Selected tool is not an OpenAI Assistant tool'}), 400
        except Exception as e:
            current_app.logger.error(f"Error validating AI assistant tool: {str(e)}")
            return jsonify({'success': False, 'message': 'Error validating AI assistant tool configuration'}), 500
        
        # Sync assistant with comprehensive parameter update
        try:
            from app.utils.assistant_manager import assistant_manager
            
            current_app.logger.info(f"Synchronizing assistant {assistant_id} with agent {agent_id} parameters")
            
            success = assistant_manager.update_assistant_for_agent(agent)
            
            if success:
                # Prepare detailed sync information
                sync_details = {
                    'assistant_id': assistant_id,
                    'agent_name': agent.get('name', 'Unknown'),
                    'model': agent.get('model', 'Default'),
                    'instructions_updated': bool(agent.get('system_instruction')),
                    'tools_count': len(agent.get('tools', [])),
                    'files_count': len(agent.get('knowledge_base', [])),
                    'sync_timestamp': datetime.now().isoformat()
                }
                
                return jsonify({
                    'success': True,
                    'message': 'Assistant synchronized successfully',
                    'details': sync_details
                })
            else:
                return jsonify({
                    'success': False, 
                    'message': 'Failed to synchronize assistant configuration'
                }), 500
            
        except Exception as e:
            current_app.logger.error(f"Error synchronizing assistant for agent {agent_id}: {str(e)}")
            return jsonify({'success': False, 'message': f'Synchronization error: {str(e)}'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Error in sync_assistant API for agent {agent_id}: {str(e)}")
        return jsonify({'success': False, 'message': f'Internal error: {str(e)}'}), 500

@agents_bp.route('/api/<agent_id>/export', methods=['POST'])
def export_agent_api(agent_id):
    """Export agent configuration as JSON file"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        # Create export data with full agent configuration
        export_data = {
            'version': '1.0',
            'export_timestamp': datetime.now().isoformat(),
            'agent': agent
        }
        
        # Create response as downloadable JSON
        from flask import make_response
        import json
        
        response = make_response(json.dumps(export_data, indent=2))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename="{agent.get("name", "agent")}-export.json"'
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"Error exporting agent {agent_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/api/<agent_id>/reconnect', methods=['POST'])
def reconnect_agent_api(agent_id):
    """Reconnect agent (refresh assistant connection, reset status)"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        # Reset agent status and clear any error states
        agent['status'] = 'active'
        agent['updated_at'] = datetime.now().isoformat()
        
        # If agent has assistant_id, try to reconnect to OpenAI Assistant
        if agent.get('assistant_id'):
            try:
                # Verify the assistant still exists
                assistant = assistant_manager.get_assistant(agent['assistant_id'])
                if assistant:
                    current_app.logger.info(f"Agent {agent_id} reconnected to assistant {agent['assistant_id']}")
                else:
                    # Assistant not found, clear the connection
                    agent['assistant_id'] = None
                    current_app.logger.warning(f"Assistant not found for agent {agent_id}, cleared connection")
            except Exception as assistant_error:
                current_app.logger.error(f"Error reconnecting assistant for agent {agent_id}: {str(assistant_error)}")
                agent['assistant_id'] = None
        
        # Save the updated agent
        if agents_manager.save(agent):
            return jsonify({
                'success': True, 
                'message': 'Agent reconnected successfully',
                'agent_status': agent['status']
            })
        else:
            return jsonify({'error': 'Failed to save agent changes'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error reconnecting agent {agent_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============================================================================
# Sessions API Endpoints
# =============================================================================

@agents_bp.route('/api/<agent_id>/sessions', methods=['GET'])
@csrf.exempt
def get_agent_sessions(agent_id):
    """Get all sessions/runs for an agent"""
    try:
        # Get agent runs from agent_run_manager
        agent_runs = agent_run_manager.get_agent_runs(agent_id)
        
        # Format sessions for frontend display
        sessions = []
        for run_data in agent_runs:
            try:
                run_id = run_data.get('id', run_data.get('uuid', 'unknown'))
                
                # Calculate session age in days
                created_at = run_data.get('created_at')
                if created_at:
                    if isinstance(created_at, str):
                        from datetime import datetime
                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        created_date = created_at
                    
                    age_days = (datetime.now() - created_date.replace(tzinfo=None)).days
                else:
                    age_days = 0
                
                # Get task completion status
                tasks = run_data.get('tasks', [])
                completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
                total_tasks = len(tasks)
                
                session = {
                    'id': run_id,
                    'status': run_data.get('status', 'unknown'),
                    'created_at': created_at,
                    'updated_at': run_data.get('updated_at'),
                    'age_days': age_days,
                    'completed_tasks': completed_tasks,
                    'total_tasks': total_tasks,
                    'last_activity': run_data.get('updated_at', created_at)
                }
                sessions.append(session)
                
            except Exception as session_error:
                current_app.logger.warning(f"Error processing session {run_id}: {str(session_error)}")
                continue
        
        # Sort sessions by last activity (newest first)
        sessions.sort(key=lambda x: x.get('last_activity', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'total_count': len(sessions)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error loading sessions for agent {agent_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/api/<agent_id>/sessions/<session_id>', methods=['DELETE'])
@csrf.exempt
def delete_agent_session(agent_id, session_id):
    """Delete a specific session"""
    try:
        # Delete the session using agent_run_manager
        success = agent_run_manager.delete(session_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Session deleted successfully'
            })
        else:
            return jsonify({'error': 'Failed to delete session'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error deleting session {session_id} for agent {agent_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/api/<agent_id>/sessions/cleanup', methods=['POST'])
@csrf.exempt
def cleanup_agent_sessions(agent_id):
    """Clean up closed and error sessions for an agent"""
    try:
        data = request.get_json() or {}
        cleanup_types = data.get('types', ['closed', 'error'])
        
        # Get all agent runs
        agent_runs = agent_run_manager.get_agent_runs(agent_id)
        
        deleted_count = 0
        for run_data in agent_runs:
            run_id = run_data.get('id', run_data.get('uuid'))
            status = run_data.get('status', 'unknown')
            if status in cleanup_types:
                if agent_run_manager.delete(run_id):
                    deleted_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {deleted_count} sessions',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        current_app.logger.error(f"Error cleaning up sessions for agent {agent_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Agent Run Task Input Management API

@agents_bp.route('/api/agent_run/<run_uuid>/task_input/<task_uuid>', methods=['POST'])
@csrf.exempt
def api_save_task_input(run_uuid, task_uuid):
    """Save task input values for an agent run task"""
    try:
        # Debug: Log incoming request details
        current_app.logger.info(f"API save_task_input called with run_uuid={run_uuid}, task_uuid={task_uuid}")
        current_app.logger.info(f"Request content type: {request.content_type}")
        current_app.logger.info(f"Request data: {request.data}")
        
        data = request.get_json()
        current_app.logger.info(f"Parsed JSON data: {data}")
        
        inputs = data.get('inputs', {}) if data else {}
        current_app.logger.info(f"Extracted inputs: {inputs}")
        
        # Validate that the agent run exists
        agent_run = agent_run_manager.load(run_uuid)
        if not agent_run:
            current_app.logger.error(f"Agent run not found: {run_uuid}")
            return jsonify({'success': False, 'error': 'Agent run not found'}), 404
        
        current_app.logger.info(f"Agent run found, has task_states: {'task_states' in agent_run}")
        
        # Save the task inputs
        success = agent_run_manager.set_task_inputs(run_uuid, task_uuid, inputs)
        current_app.logger.info(f"set_task_inputs result: {success}")
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Task inputs saved successfully'
            })
        else:
            current_app.logger.error(f"Failed to save task inputs for run {run_uuid}, task {task_uuid}")
            return jsonify({'success': False, 'error': 'Failed to save task inputs'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error saving task inputs: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@agents_bp.route('/api/agent_run/<run_uuid>/selected_task', methods=['POST'])
@csrf.exempt
def api_save_selected_task(run_uuid):
    """Save the currently selected task for an agent run"""
    try:
        data = request.get_json()
        task_index = data.get('task_index') if data else None
        
        if task_index is None:
            return jsonify({'success': False, 'error': 'Missing task_index'}), 400
        
        # Validate that the agent run exists
        agent_run = agent_run_manager.load(run_uuid)
        if not agent_run:
            return jsonify({'success': False, 'error': 'Agent run not found'}), 404
        
        # Save selected task index in agent run metadata
        agent_run['selected_task_index'] = task_index
        agent_run['updated_at'] = datetime.now().isoformat()
        
        success = agent_run_manager.save(agent_run)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Selected task saved successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to save selected task'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error saving selected task: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@agents_bp.route('/api/agent_run/<run_uuid>/selected_task', methods=['GET'])
@csrf.exempt
def api_get_selected_task(run_uuid):
    """Get the currently selected task for an agent run"""
    try:
        # Load the agent run
        agent_run = agent_run_manager.load(run_uuid)
        if not agent_run:
            return jsonify({'success': False, 'error': 'Agent run not found'}), 404
        
        selected_task_index = agent_run.get('selected_task_index', 0)
        
        return jsonify({
            'success': True,
            'selected_task_index': selected_task_index
        })
            
    except Exception as e:
        current_app.logger.error(f"Error getting selected task: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@agents_bp.route('/api/agent_run/<run_uuid>/task_execute/<task_uuid>/stream', methods=['GET', 'POST'])
@csrf.exempt
def api_stream_execute_task(run_uuid, task_uuid):
    """Stream execute a task with real-time HTML output and OpenAI Assistant integration"""
    import time
    import json
    from flask import Response
    
    def generate_task_execution_stream():
        try:
            # Load agent run and validate
            agent_run = agent_run_manager.load(run_uuid)
            if not agent_run:
                yield f"data: {json.dumps({'error': 'Agent run not found'})}\n\n"
                return
            
            # Load agent and get task definition
            agent = agents_manager.load(agent_run['agent_uuid'])
            if not agent:
                yield f"data: {json.dumps({'error': 'Agent not found'})}\n\n"
                return
            
            # Find task definition
            task_def = None
            for task in agent.get('tasks', []):
                if task.get('uuid') == task_uuid:
                    task_def = task
                    break
            
            if not task_def:
                yield f"data: {json.dumps({'error': 'Task definition not found'})}\n\n"
                return
            
            # Get task inputs from request (support both GET and POST)
            try:
                if request.method == 'POST':
                    request_data = request.get_json()
                    task_inputs = request_data.get('inputs', {}) if request_data else {}
                else:  # GET request
                    # For EventSource GET requests, get inputs from task state or use empty dict
                    task_state = agent_run_manager.get_task_state(run_uuid, task_uuid)
                    task_inputs = task_state.get('inputs', {}) if task_state else {}
            except:
                task_inputs = {}
            
            # Update task status to running
            agent_run_manager.set_task_status(run_uuid, task_uuid, 'running')
            
            # Generate initial HTML
            start_html = '<div class="task-execution-output">'
            yield f"data: {json.dumps({'type': 'html_chunk', 'content': start_html})}\n\n"
            time.sleep(0.1)
            
            # Task Header
            header_html = f'<div class="task-header"><h3 class="text-lg font-semibold text-gray-900 mb-4">🚀 Executing Task: {task_def.get("name", "Unnamed Task")}</h3></div>'
            yield f"data: {json.dumps({'type': 'html_chunk', 'content': header_html})}\n\n"
            time.sleep(0.2)
            
            # Only execute AI tasks with OpenAI Assistant
            if task_def.get('type') == 'ai':
                # Create or get user session for this task
                task_state = agent_run_manager.get_task_state(run_uuid, task_uuid)
                thread_id = task_state.get('user_session_id') if task_state else None
                
                # Initialize OpenAI Assistant API
                assistant_id = agent.get('assistant_id')
                if not assistant_id:
                    error_html = '<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: No Assistant ID found for this agent</div></div></div>'
                    yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                    agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', 'No Assistant ID')
                    return
                
                try:
                    # Get API key from the agent's AI assistant tool configuration
                    ai_assistant_tool = agent.get('ai_assistant_tool', '')
                    print(f"[DEBUG] Agent AI assistant tool: {ai_assistant_tool}")
                    
                    if ai_assistant_tool.startswith('tool:'):
                        tool_id = ai_assistant_tool.replace('tool:', '')
                        print(f"[DEBUG] Loading tool with ID: {tool_id}")
                        tool = tools_manager.load(tool_id)
                        if tool:
                            tool_config = tool.get('config', {})
                            api_key = tool_config.get('openai_api_key')
                            print(f"[DEBUG] API key found: {'Yes' if api_key and api_key != 'test-key-placeholder' else 'No'}")
                            
                            if not api_key or api_key == 'test-key-placeholder':
                                error_html = '<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: No valid OpenAI API key found in tool configuration</div></div></div>'
                                yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                                agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', 'No valid OpenAI API key')
                                return
                        else:
                            error_html = '<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: AI assistant tool not found</div></div></div>'
                            yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                            agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', 'AI assistant tool not found')
                            return
                    else:
                        error_html = '<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: No AI assistant tool configured</div></div></div>'
                        yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                        agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', 'No AI assistant tool configured')
                        return
                    
                    # Initialize OpenAI API configuration
                    config_for_implementation = {
                        'api_key': api_key,
                        'model': tool_config.get('default_model', 'gpt-4'),
                        'organization_id': tool_config.get('organization_id', ''),
                        'base_url': 'https://api.openai.com/v1',
                        'timeout': 30
                    }
                    
                    # Create thread if not exists
                    if not thread_id:
                        session_html = '<div class="session-section mb-6"><h4 class="font-medium text-gray-700 mb-2">🔄 Creating User Session</h4><div class="bg-blue-50 p-4 rounded-lg"><div class="text-blue-700">Creating new conversation thread...</div></div></div>'
                        yield f"data: {json.dumps({'type': 'html_chunk', 'content': session_html})}\n\n"
                        time.sleep(0.3)
                        
                        # Create thread using requests instead of asyncio
                        import requests
                        try:
                            headers = {
                                'Authorization': f'Bearer {api_key}',
                                'Content-Type': 'application/json',
                                'OpenAI-Beta': 'assistants=v2'
                            }
                            response = requests.post(
                                'https://api.openai.com/v1/threads',
                                headers=headers,
                                json={},
                                timeout=30
                            )
                            
                            if response.status_code == 200:
                                thread_data = response.json()
                                thread_id = thread_data['id']
                                # Save thread ID to agent run
                                agent_run_manager.update_task_state(run_uuid, task_uuid, {'user_session_id': thread_id})
                                
                                session_success_html = f'<div class="session-section mb-6"><h4 class="font-medium text-gray-700 mb-2">✅ User Session Created</h4><div class="bg-green-50 p-4 rounded-lg"><div class="text-green-700">Thread ID: <code>{thread_id}</code></div></div></div>'
                                yield f"data: {json.dumps({'type': 'html_chunk', 'content': session_success_html})}\n\n"
                            else:
                                error_msg = f"HTTP {response.status_code}: {response.text}"
                                error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error creating session: {error_msg}</div></div></div>'
                                yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                                agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', f'Session creation failed: {error_msg}')
                                return
                        except Exception as e:
                            error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error creating session: {str(e)}</div></div></div>'
                            yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                            agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', f'Session creation failed: {str(e)}')
                            return
                    else:
                        session_html = f'<div class="session-section mb-6"><h4 class="font-medium text-gray-700 mb-2">🔄 Using Existing Session</h4><div class="bg-blue-50 p-4 rounded-lg"><div class="text-blue-700">Thread ID: <code>{thread_id}</code></div></div></div>'
                        yield f"data: {json.dumps({'type': 'html_chunk', 'content': session_html})}\n\n"
                    
                    # Build context prompt
                    prompt_html = '<div class="prompt-section mb-6"><h4 class="font-medium text-gray-700 mb-2">📝 Building Context Prompt</h4><div class="bg-yellow-50 p-4 rounded-lg"><div class="text-yellow-700">Generating prompt from task definition and inputs...</div></div></div>'
                    yield f"data: {json.dumps({'type': 'html_chunk', 'content': prompt_html})}\n\n"
                    time.sleep(0.5)
                    
                    context_prompt = build_context_prompt(task_def, task_inputs, agent)
                    
                    prompt_display_html = f'<div class="prompt-display mb-6"><h4 class="font-medium text-gray-700 mb-2">📋 Context Prompt</h4><div class="bg-gray-50 p-4 rounded-lg border max-h-64 overflow-y-auto"><pre class="text-sm text-gray-800 whitespace-pre-wrap">{context_prompt[:500]}{"..." if len(context_prompt) > 500 else ""}</pre></div></div>'
                    yield f"data: {json.dumps({'type': 'html_chunk', 'content': prompt_display_html})}\n\n"
                    time.sleep(0.3)
                    
                    # Execute prompt with OpenAI Assistant using requests
                    execution_html = '<div class="execution-section mb-6"><h4 class="font-medium text-gray-700 mb-2">🤖 AI Processing</h4><div class="bg-purple-50 p-4 rounded-lg"><div class="flex items-center"><div class="w-3 h-3 bg-purple-500 rounded-full mr-2 animate-pulse"></div><div class="text-purple-700">Sending prompt to OpenAI Assistant...</div></div></div></div>'
                    yield f"data: {json.dumps({'type': 'html_chunk', 'content': execution_html})}\n\n"
                    time.sleep(0.5)
                    
                    try:
                        headers = {
                            'Authorization': f'Bearer {api_key}',
                            'Content-Type': 'application/json',
                            'OpenAI-Beta': 'assistants=v2'
                        }
                        
                        # Add message to thread
                        message_response = requests.post(
                            f'https://api.openai.com/v1/threads/{thread_id}/messages',
                            headers=headers,
                            json={"role": "user", "content": context_prompt},
                            timeout=30
                        )
                        
                        if message_response.status_code != 200:
                            error_msg = f"Failed to add message: {message_response.status_code} - {message_response.text}"
                            error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: {error_msg}</div></div></div>'
                            yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                            agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', error_msg)
                            return
                        
                        # Create run
                        run_response = requests.post(
                            f'https://api.openai.com/v1/threads/{thread_id}/runs',
                            headers=headers,
                            json={"assistant_id": assistant_id},
                            timeout=30
                        )
                        
                        if run_response.status_code != 200:
                            error_msg = f"Failed to create run: {run_response.status_code} - {run_response.text}"
                            error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: {error_msg}</div></div></div>'
                            yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                            agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', error_msg)
                            return
                        
                        run_data = run_response.json()
                        run_id = run_data['id']
                        
                        # Poll for completion
                        max_attempts = 60  # 60 seconds timeout
                        attempt = 0
                        while attempt < max_attempts:
                            attempt += 1
                            time.sleep(1)
                            
                            status_response = requests.get(
                                f'https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}',
                                headers=headers,
                                timeout=30
                            )
                            
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                status = status_data.get('status')
                                
                                if status == 'completed':
                                    # Get messages
                                    messages_response = requests.get(
                                        f'https://api.openai.com/v1/threads/{thread_id}/messages',
                                        headers=headers,
                                        timeout=30
                                    )
                                    
                                    if messages_response.status_code == 200:
                                        messages_data = messages_response.json()
                                        messages = messages_data.get('data', [])
                                        
                                        # Get the latest assistant message
                                        response_content = "No response received"
                                        for message in messages:
                                            if message.get('role') == 'assistant':
                                                content_blocks = message.get('content', [])
                                                if content_blocks and len(content_blocks) > 0:
                                                    text_content = content_blocks[0].get('text', {})
                                                    response_content = text_content.get('value', 'No content')
                                                break
                                        
                                        # Render response based on task output type
                                        output_type = task_def.get('output', {}).get('type', 'text')
                                        rendered_content = render_response_content(response_content, output_type)
                                        
                                        # Display result
                                        result_html = f'<div class="result-section mb-6"><h4 class="font-medium text-gray-700 mb-2">✨ AI Response</h4><div class="bg-white p-6 rounded-lg border shadow-sm">{rendered_content}</div></div>'
                                        yield f"data: {json.dumps({'type': 'html_chunk', 'content': result_html})}\n\n"
                                        
                                        # Save results to agent run
                                        results_data = {
                                            'html_output': rendered_content,
                                            'raw_response': response_content,
                                            'prompt_used': context_prompt,
                                            'thread_id': thread_id,
                                            'assistant_id': assistant_id
                                        }
                                        agent_run_manager.set_task_results(run_uuid, task_uuid, results_data)
                                        agent_run_manager.set_task_status(run_uuid, task_uuid, 'completed')
                                        
                                        execution_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        status_html = f'<div class="execution-status mb-6"><h4 class="font-medium text-gray-700 mb-2">⚡ Execution Status</h4><div class="bg-green-50 p-4 rounded-lg"><div class="flex items-center"><div class="w-3 h-3 bg-green-500 rounded-full mr-2"></div><span class="text-green-700 font-medium">Task executed successfully</span></div><div class="text-sm text-gray-600 mt-2">Execution completed at: {execution_time}</div></div></div>'
                                        yield f"data: {json.dumps({'type': 'html_chunk', 'content': status_html})}\n\n"
                                        break
                                        
                                    else:
                                        error_msg = f"Failed to get messages: {messages_response.status_code}"
                                        error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: {error_msg}</div></div></div>'
                                        yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                                        agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', error_msg)
                                        break
                                        
                                elif status in ['failed', 'cancelled', 'expired']:
                                    error_msg = f"Run {status}: {status_data.get('last_error', {}).get('message', 'Unknown error')}"
                                    error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">AI Execution Error: {error_msg}</div></div></div>'
                                    yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                                    agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', error_msg)
                                    break
                                    
                                # Status is still in_progress, queued, or requires_action - continue polling
                                
                            else:
                                error_msg = f"Failed to check run status: {status_response.status_code}"
                                error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: {error_msg}</div></div></div>'
                                yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                                agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', error_msg)
                                break
                        
                        if attempt >= max_attempts:
                            error_msg = "Timeout waiting for AI response"
                            error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: {error_msg}</div></div></div>'
                            yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                            agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', error_msg)
                            
                    except requests.RequestException as e:
                        error_msg = f"Request error: {str(e)}"
                        error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: {error_msg}</div></div></div>'
                        yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                        agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', error_msg)
                        
                except Exception as ai_error:
                    error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Exception: {str(ai_error)}</div></div></div>'
                    yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                    agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', str(ai_error))
                    
            else:
                # For non-AI tasks, show the old simulation
                task_type = task_def.get('type', 'tool')
                task_desc = task_def.get('description', 'No description provided')
                
                # Task Information Section
                info_start_html = '<div class="task-info mb-6"><h4 class="font-medium text-gray-700 mb-2">📋 Task Information</h4>'
                yield f"data: {json.dumps({'type': 'html_chunk', 'content': info_start_html})}\n\n"
                time.sleep(0.1)
                
                # Basic task details
                details_html = f'<div class="bg-gray-50 p-4 rounded-lg mb-4"><div class="grid grid-cols-2 gap-4"><div><span class="font-medium">Type:</span> <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800">{task_type.upper()}</span></div><div><span class="font-medium">UUID:</span> <code class="text-sm text-gray-600">{task_uuid}</code></div></div></div>'
                yield f"data: {json.dumps({'type': 'html_chunk', 'content': details_html})}\n\n"
                time.sleep(0.3)
                
                desc_html = f'<div class="mb-4"><span class="font-medium">Description:</span><p class="text-gray-700 mt-1">{task_desc}</p></div></div>'
                yield f"data: {json.dumps({'type': 'html_chunk', 'content': desc_html})}\n\n"
                time.sleep(0.2)
                
                # Execution Status (simulated for tool tasks)
                execution_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                status_html = f'<div class="execution-status mb-6"><h4 class="font-medium text-gray-700 mb-2">⚡ Execution Status</h4><div class="bg-green-50 p-4 rounded-lg"><div class="flex items-center"><div class="w-3 h-3 bg-green-500 rounded-full mr-2 animate-pulse"></div><span class="text-green-700 font-medium">Tool task simulation completed</span></div><div class="text-sm text-gray-600 mt-2">Execution completed at: {execution_time}</div></div></div>'
                yield f"data: {json.dumps({'type': 'html_chunk', 'content': status_html})}\n\n"
                time.sleep(0.3)
                
                agent_run_manager.set_task_status(run_uuid, task_uuid, 'completed')
            
            # Close the main container
            end_html = '</div>'
            yield f"data: {json.dumps({'type': 'html_chunk', 'content': end_html})}\n\n"
            
            # Save task inputs
            agent_run_manager.set_task_inputs(run_uuid, task_uuid, task_inputs)
            
            # Signal completion
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            print(f"[ERROR] Error in task execution stream: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            # Set task status to error
            try:
                agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', str(e))
            except:
                pass
    
    return Response(
        generate_task_execution_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',  # Disable nginx buffering
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )


def build_context_prompt(task_def: dict, task_inputs: dict, agent: dict) -> str:
    """Build a context prompt from task definition, inputs, and agent data"""
    
    # Start with agent context
    agent_name = agent.get('name', 'AI Assistant')
    agent_description = agent.get('description', '')
    
    prompt_parts = [
        f"You are {agent_name}.",
        f"Agent Description: {agent_description}" if agent_description else "",
        "",
        f"Task: {task_def.get('name', 'Unnamed Task')}",
        f"Task Description: {task_def.get('description', 'No description provided')}",
        ""
    ]
    
    # Add AI configuration if available
    ai_config = task_def.get('ai_config', {})
    if ai_config.get('system_prompt'):
        prompt_parts.extend([
            "System Instructions:",
            ai_config['system_prompt'],
            ""
        ])
    
    # Add task inputs
    if task_inputs:
        prompt_parts.append("Input Parameters:")
        for key, value in task_inputs.items():
            prompt_parts.append(f"- {key}: {value}")
        prompt_parts.append("")
    
    # Add output format instructions
    output_config = task_def.get('output', {})
    output_type = output_config.get('type', 'text')
    output_description = output_config.get('description', '')
    
    if output_type or output_description:
        prompt_parts.append("Output Requirements:")
        if output_description:
            prompt_parts.append(f"- {output_description}")
        if output_type == 'html':
            prompt_parts.append("- Format your response as HTML")
        elif output_type == 'markdown':
            prompt_parts.append("- Format your response as Markdown")
        elif output_type == 'text':
            prompt_parts.append("- Format your response as plain text")
        prompt_parts.append("")
    
    # Add knowledge base items if available
    knowledge_base = agent.get('knowledge_base', [])
    if knowledge_base:
        prompt_parts.append("Available Knowledge:")
        for item in knowledge_base[:5]:  # Limit to first 5 items
            prompt_parts.append(f"- {item.get('title', 'Knowledge Item')}: {item.get('content', '')[:200]}")
        prompt_parts.append("")
    
    prompt_parts.append("Please provide your response based on the above information.")
    
    return "\n".join(filter(None, prompt_parts))


def render_response_content(content: str, output_type: str) -> str:
    """Render AI response content based on output type"""
    
    if output_type == 'html':
        # Return HTML content directly
        return content
    elif output_type == 'markdown':
        # For now, wrap in pre tags - could add markdown parser later
        return f'<div class="markdown-content"><pre class="whitespace-pre-wrap">{content}</pre></div>'
    else:  # text or default
        # Escape HTML and preserve formatting
        import html
        escaped_content = html.escape(content)
        return f'<div class="text-content"><pre class="whitespace-pre-wrap">{escaped_content}</pre></div>'
