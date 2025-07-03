"""
Assistant Management API Routes
Handles OpenAI Assistant creation, sync, and management for agents
"""

from flask import request, jsonify, current_app, make_response
from app.routes.agents import agents_bp
from app.utils.data_manager import agents_manager, tools_manager
from .api_utils import (validate_json_request, success_response, error_response, 
                        get_agent_or_404, current_timestamp, log_error, log_info)
from datetime import datetime
import time
import json


@agents_bp.route('/api/<agent_id>/reassign_assistant', methods=['POST'])
def api_reassign_assistant(agent_id):
    """Reassign assistant to an agent"""
    try:
        data = request.get_json()
        new_assistant_id = data.get('new_assistant_id')
        
        if not new_assistant_id:
            return error_response('New assistant ID is required')
        
        # Load the agent
        agent = agents_manager.load(agent_id)
        if not agent:
            return error_response('Agent not found', 404)
        
        # Use assistant manager to reassign the assistant
        from app.utils.assistant_manager import assistant_manager
        success = assistant_manager.reassign_assistant(agent, new_assistant_id)
        
        if success:
            return success_response(
                f'Assistant successfully reassigned to {new_assistant_id}',
                {'assistant_id': new_assistant_id}
            )
        else:
            return error_response('Failed to reassign assistant. Please check the assistant ID and try again.')
            
    except Exception as e:
        log_error(f"Error reassigning assistant for agent {agent_id}: {str(e)}")
        return error_response(f'Internal error: {str(e)}', 500)


@agents_bp.route('/api/<agent_id>/create_assistant', methods=['POST'])
def api_create_assistant(agent_id):
    """Create and assign assistant to an agent with comprehensive traceability"""
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
        log_info(f"Assistant Creation Trace - {step}: {status} - {details or ''}")
    
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
            log_info(summary)
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
        log_error(f"Error creating assistant for agent {agent_id}: {error_msg}")
        
        return jsonify({
            'success': False,
            'message': f'Internal error: {error_msg}',
            'trace_log': trace_log
        }), 500


@agents_bp.route('/api/<agent_id>/remove_assistant', methods=['POST'])
def api_remove_assistant(agent_id):
    """Remove assistant from an agent"""
    try:
        log_info(f"Removing assistant from agent {agent_id}")
        
        # Get agent from database
        agent = agents_manager.load(agent_id)
        if not agent:
            log_error(f"Agent {agent_id} not found")
            return error_response('Agent not found', 404)
        
        # Check if agent has an assistant
        if not agent.get('assistant_id'):
            return error_response('No assistant assigned to this agent')
        
        assistant_id = agent['assistant_id']
        log_info(f"Removing assistant {assistant_id} from agent {agent_id}")
        
        # Remove assistant_id from agent
        agent['assistant_id'] = None
        agents_manager.save(agent)
        
        log_info(f"Successfully removed assistant from agent {agent_id}")
        
        return success_response(
            'Assistant removed',
            {
                'agent_id': agent_id,
                'removed_assistant_id': assistant_id
            }
        )
        
    except Exception as e:
        error_msg = str(e)
        log_error(f"Error removing assistant from agent {agent_id}: {error_msg}")
        return error_response(f'Internal error: {error_msg}', 500)


@agents_bp.route('/api/<agent_id>/sync_assistant', methods=['POST'])
def api_sync_assistant(agent_id):
    """Synchronize agent configuration with OpenAI assistant with detailed response"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return error_response('Agent not found', 404)
        
        assistant_id = agent.get('assistant_id')
        if not assistant_id:
            return error_response('No assistant configured for this agent')
        
        # Get AI assistant tool
        ai_tool = agent.get('ai_assistant_tool', '')
        if not ai_tool or not ai_tool.startswith('tool:'):
            return error_response('No AI assistant tool configured')
        
        # Extract tool ID and validate the tool exists and is an AI assistant tool
        tool_id = ai_tool.replace('tool:', '')
        
        try:
            tool_data = tools_manager.get_by_id(tool_id)
            if not tool_data:
                return error_response('Selected AI assistant tool not found')
            
            # Check if it's an OpenAI Assistant tool by checking integration or tool definition
            tool_definition = tool_data.get('tool_definition', '')
            integration_id = tool_data.get('integration_id', '')
            
            # Load integration to verify it's an OpenAI Assistant integration
            if integration_id:
                from app.utils.data_manager import integrations_manager
                integration_data = integrations_manager.get_by_id(integration_id)
                if not integration_data or integration_data.get('implementation') != 'openai_assistant_api':
                    return error_response('Selected tool is not an OpenAI Assistant tool')
            elif tool_definition != 'OpenAI Assistant API':
                return error_response('Selected tool is not an OpenAI Assistant tool')
        except Exception as e:
            log_error(f"Error validating AI assistant tool: {str(e)}")
            return error_response('Error validating AI assistant tool configuration', 500)
        
        # Sync assistant with comprehensive parameter update
        try:
            from app.utils.assistant_manager import assistant_manager
            
            log_info(f"Synchronizing assistant {assistant_id} with agent {agent_id} parameters")
            
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
                
                return success_response('Assistant synchronized successfully', sync_details)
            else:
                return error_response('Failed to synchronize assistant configuration', 500)
            
        except Exception as e:
            log_error(f"Error synchronizing assistant for agent {agent_id}: {str(e)}")
            return error_response(f'Synchronization error: {str(e)}', 500)
        
    except Exception as e:
        log_error(f"Error in sync_assistant API for agent {agent_id}: {str(e)}")
        return error_response(f'Internal error: {str(e)}', 500)


@agents_bp.route('/api/<agent_id>/export', methods=['POST'])
def export_agent_api(agent_id):
    """Export agent configuration as JSON file"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return error_response('Agent not found', 404)
        
        # Create export data with full agent configuration
        export_data = {
            'version': '1.0',
            'export_timestamp': datetime.now().isoformat(),
            'agent': agent
        }
        
        # Create response as downloadable JSON
        response = make_response(json.dumps(export_data, indent=2))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename="{agent.get("name", "agent")}-export.json"'
        
        return response
        
    except Exception as e:
        log_error(f"Error exporting agent {agent_id}: {str(e)}")
        return error_response(str(e), 500)


@agents_bp.route('/api/<agent_id>/reconnect', methods=['POST'])
def reconnect_agent_api(agent_id):
    """Reconnect agent (refresh assistant connection, reset status)"""
    try:
        agent = agents_manager.load(agent_id)
        if not agent:
            return error_response('Agent not found', 404)
        
        # Reset agent status and clear any error states
        agent['status'] = 'active'
        agent['updated_at'] = current_timestamp()
        
        # If agent has assistant_id, try to reconnect to OpenAI Assistant
        if agent.get('assistant_id'):
            try:
                from app.utils.assistant_manager import assistant_manager
                # Verify the assistant still exists
                assistant = assistant_manager.get_assistant(agent['assistant_id'])
                if assistant:
                    log_info(f"Agent {agent_id} reconnected to assistant {agent['assistant_id']}")
                else:
                    # Assistant not found, clear the connection
                    agent['assistant_id'] = None
                    log_error(f"Assistant not found for agent {agent_id}, cleared connection")
            except Exception as assistant_error:
                log_error(f"Error reconnecting assistant for agent {agent_id}: {str(assistant_error)}")
                agent['assistant_id'] = None
        
        # Save the updated agent
        if agents_manager.save(agent):
            return success_response(
                'Agent reconnected successfully',
                {'agent_status': agent['status']}
            )
        else:
            return error_response('Failed to save agent changes', 500)
            
    except Exception as e:
        log_error(f"Error reconnecting agent {agent_id}: {str(e)}")
        return error_response(str(e), 500)
