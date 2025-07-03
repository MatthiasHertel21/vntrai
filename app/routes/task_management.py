"""
Sprint 18 Task Management Revolution - API Routes
Task execution and management API endpoints for the new agent-integrated task system
"""

from flask import Blueprint, request, jsonify, session, abort
from flask_wtf.csrf import validate_csrf
from wtforms.validators import ValidationError
from datetime import datetime
import uuid
import json

from app.utils.data_manager import agents_manager, agent_run_manager, tools_manager

# Blueprint for Sprint 18 task management
task_management_bp = Blueprint('task_management', __name__, url_prefix='/api/task_management')

@task_management_bp.route('/agent/<agent_uuid>/tasks', methods=['GET'])
def get_agent_tasks(agent_uuid):
    """Get all task definitions for an agent (Sprint 18)"""
    try:
        agent = agents_manager.load(agent_uuid)
        if not agent:
            return jsonify({'success': False, 'error': 'Agent not found'}), 404
        
        tasks = agents_manager.get_task_definitions(agent_uuid)
        
        return jsonify({
            'success': True,
            'tasks': tasks,
            'count': len(tasks)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@task_management_bp.route('/agent/<agent_uuid>/tasks', methods=['POST'])
def create_agent_task(agent_uuid):
    """Create new task definition for an agent (Sprint 18)"""
    try:
        # Validate CSRF token
        try:
            validate_csrf(request.headers.get('X-CSRFToken'))
        except ValidationError:
            return jsonify({'success': False, 'error': 'CSRF token validation failed'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'success': False, 'error': 'Task name is required'}), 400
        
        if not data.get('type') or data['type'] not in ['ai', 'tool']:
            return jsonify({'success': False, 'error': 'Task type must be "ai" or "tool"'}), 400
        
        # Create task definition
        task_def = {
            'uuid': str(uuid.uuid4()),
            'name': data['name'],
            'type': data['type'],
            'description': data.get('description', ''),
            'order': data.get('order', 1),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Add type-specific fields
        if data['type'] == 'ai':
            task_def.update({
                'ai_config': {
                    'instructions': data.get('instructions', ''),
                    'goals': data.get('goals', ''),
                    'input_fields': data.get('input_fields', []),
                    'output_type': data.get('output_type', 'text'),
                    'output_description': data.get('output_description', '')
                }
            })
        elif data['type'] == 'tool':
            task_def.update({
                'tool_config': {
                    'tool_uuid': data.get('tool_uuid', ''),
                    'input_mapping': data.get('input_mapping', {}),
                    'output_mapping': data.get('output_mapping', {})
                }
            })
        
        # Add task to agent
        success = agents_manager.add_task_definition(agent_uuid, task_def)
        
        if success:
            return jsonify({
                'success': True,
                'task': task_def,
                'message': 'Task created successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create task'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@task_management_bp.route('/agent/<agent_uuid>/tasks/<task_uuid>', methods=['PUT'])
def update_agent_task(agent_uuid, task_uuid):
    """Update task definition for an agent (Sprint 18)"""
    try:
        # Validate CSRF token
        try:
            validate_csrf(request.headers.get('X-CSRFToken'))
        except ValidationError:
            return jsonify({'success': False, 'error': 'CSRF token validation failed'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Preserve UUID and update timestamp
        data['uuid'] = task_uuid
        data['updated_at'] = datetime.now().isoformat()
        
        success = agents_manager.update_task_definition(agent_uuid, task_uuid, data)
        
        if success:
            task = agents_manager.get_task_definition(agent_uuid, task_uuid)
            return jsonify({
                'success': True,
                'task': task,
                'message': 'Task updated successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to update task'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@task_management_bp.route('/agent/<agent_uuid>/tasks/<task_uuid>', methods=['DELETE'])
def delete_agent_task(agent_uuid, task_uuid):
    """Delete task definition from an agent (Sprint 18)"""
    try:
        # Validate CSRF token
        try:
            validate_csrf(request.headers.get('X-CSRFToken'))
        except ValidationError:
            return jsonify({'success': False, 'error': 'CSRF token validation failed'}), 400
        
        success = agents_manager.remove_task_definition(agent_uuid, task_uuid)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Task deleted successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to delete task'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@task_management_bp.route('/agent/<agent_uuid>/tasks/reorder', methods=['POST'])
def reorder_agent_tasks(agent_uuid):
    """Reorder task definitions for an agent (Sprint 18)"""
    try:
        # Validate CSRF token
        try:
            validate_csrf(request.headers.get('X-CSRFToken'))
        except ValidationError:
            return jsonify({'success': False, 'error': 'CSRF token validation failed'}), 400
        
        data = request.get_json()
        if not data or 'task_uuids' not in data:
            return jsonify({'success': False, 'error': 'task_uuids array required'}), 400
        
        success = agents_manager.reorder_task_definitions(agent_uuid, data['task_uuids'])
        
        if success:
            tasks = agents_manager.get_task_definitions(agent_uuid)
            return jsonify({
                'success': True,
                'tasks': tasks,
                'message': 'Tasks reordered successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to reorder tasks'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# AgentRun Task Execution API (Sprint 18)

@task_management_bp.route('/run/<run_uuid>/tasks', methods=['GET'])
def get_run_tasks(run_uuid):
    """Get task definitions with execution states for an agent run (Sprint 18)"""
    try:
        tasks = agent_run_manager.get_task_definitions_with_states(run_uuid)
        progress = agent_run_manager.get_task_progress(run_uuid)
        
        return jsonify({
            'success': True,
            'tasks': tasks,
            'progress': progress
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@task_management_bp.route('/run/<run_uuid>/tasks/<task_uuid>/execute', methods=['POST'])
def execute_task(run_uuid, task_uuid):
    """Execute a task in an agent run (Sprint 18)"""
    try:
        # Debug: Log incoming request details
        print(f"[DEBUG] Task execute called with run_uuid={run_uuid}, task_uuid={task_uuid}")
        print(f"[DEBUG] Request content type: {request.content_type}")
        print(f"[DEBUG] Request data: {request.data}")
        
        # Validate CSRF token
        try:
            validate_csrf(request.headers.get('X-CSRFToken'))
        except ValidationError:
            print(f"[DEBUG] CSRF validation failed")
            return jsonify({'success': False, 'error': 'CSRF token validation failed'}), 400
        
        data = request.get_json()
        print(f"[DEBUG] Parsed JSON data: {data}")
        
        inputs = data.get('inputs', {}) if data else {}
        print(f"[DEBUG] Extracted inputs: {inputs}")
        
        # Get task definition and current state
        agent_run = agent_run_manager.load(run_uuid)
        if not agent_run:
            print(f"[DEBUG] Agent run not found: {run_uuid}")
            return jsonify({'success': False, 'error': 'Agent run not found'}), 404
        
        print(f"[DEBUG] Agent run found, agent_uuid: {agent_run.get('agent_uuid')}")
        
        agent = agents_manager.load(agent_run['agent_uuid'])
        if not agent:
            print(f"[DEBUG] Agent not found: {agent_run['agent_uuid']}")
            return jsonify({'success': False, 'error': 'Agent not found'}), 404
        
        print(f"[DEBUG] Agent found: {agent.get('name', 'Unknown')}")
        
        task_def = agents_manager.get_task_definition(agent_run['agent_uuid'], task_uuid)
        if not task_def:
            print(f"[DEBUG] Task definition not found: {task_uuid}")
            return jsonify({'success': False, 'error': 'Task definition not found'}), 404
        
        print(f"[DEBUG] Task definition found, type: {task_def.get('type')}")
        
        # Set task as running
        status_result = agent_run_manager.set_task_status(run_uuid, task_uuid, 'running')
        print(f"[DEBUG] Set task status to running: {status_result}")
        
        inputs_result = agent_run_manager.set_task_inputs(run_uuid, task_uuid, inputs)
        print(f"[DEBUG] Set task inputs: {inputs_result}")
        
        try:
            # Execute task based on type
            if task_def['type'] == 'ai':
                result = execute_ai_task(agent, task_def, inputs)
            elif task_def['type'] == 'tool':
                result = execute_tool_task(task_def, inputs)
            else:
                raise ValueError(f"Unknown task type: {task_def['type']}")
            
            # Save results and mark as completed
            agent_run_manager.set_task_results(run_uuid, task_uuid, result)
            agent_run_manager.set_task_status(run_uuid, task_uuid, 'completed')
            
            return jsonify({
                'success': True,
                'result': result,
                'message': 'Task executed successfully'
            })
        
        except Exception as execution_error:
            # Mark task as error
            agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', str(execution_error))
            
            return jsonify({
                'success': False,
                'error': f'Task execution failed: {str(execution_error)}'
            }), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@task_management_bp.route('/run/<run_uuid>/tasks/<task_uuid>/status', methods=['GET'])
def get_task_status(run_uuid, task_uuid):
    """Get task execution status (Sprint 18)"""
    try:
        task_state = agent_run_manager.get_task_state(run_uuid, task_uuid)
        
        if task_state:
            return jsonify({
                'success': True,
                'status': task_state['status'],
                'state': task_state
            })
        else:
            return jsonify({'success': False, 'error': 'Task state not found'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@task_management_bp.route('/run/<run_uuid>/progress', methods=['GET'])
def get_run_progress(run_uuid):
    """Get overall task execution progress for an agent run (Sprint 18)"""
    try:
        progress = agent_run_manager.get_task_progress(run_uuid)
        
        return jsonify({
            'success': True,
            'progress': progress
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@task_management_bp.route('/run/<run_uuid>/sync_tasks', methods=['POST'])
def sync_run_tasks(run_uuid):
    """Sync task definitions from agent to agent run (Sprint 18)"""
    try:
        # Validate CSRF token
        try:
            validate_csrf(request.headers.get('X-CSRFToken'))
        except ValidationError:
            return jsonify({'success': False, 'error': 'CSRF token validation failed'}), 400
        
        success = agent_run_manager.sync_task_definitions(run_uuid)
        
        if success:
            tasks = agent_run_manager.get_task_definitions_with_states(run_uuid)
            return jsonify({
                'success': True,
                'tasks': tasks,
                'message': 'Task definitions synced successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to sync task definitions'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Tools Options API (Sprint 18)

@task_management_bp.route('/tools/assistant-enabled', methods=['GET'])
def get_assistant_enabled_tools():
    """Get tools with assistant option enabled (Sprint 18)"""
    try:
        tools = tools_manager.get_assistant_enabled_tools()
        
        return jsonify({
            'success': True,
            'tools': tools,
            'count': len(tools)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@task_management_bp.route('/tools/<tool_id>/options', methods=['GET'])
def get_tool_options(tool_id):
    """Get tool options (Sprint 18)"""
    try:
        tool = tools_manager.get_by_id(tool_id)
        if not tool:
            return jsonify({'success': False, 'error': 'Tool not found'}), 404
        
        # Ensure options field exists
        tools_manager.ensure_options_field(tool_id)
        tool = tools_manager.get_by_id(tool_id)
        
        return jsonify({
            'success': True,
            'options': tool.get('options', {}),
            'assistant_enabled': tools_manager.is_assistant_enabled(tool_id)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@task_management_bp.route('/tools/<tool_id>/options', methods=['PUT'])
def update_tool_options(tool_id):
    """Update tool options (Sprint 18)"""
    try:
        # Validate CSRF token
        try:
            validate_csrf(request.headers.get('X-CSRFToken'))
        except ValidationError:
            return jsonify({'success': False, 'error': 'CSRF token validation failed'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        tool = tools_manager.get_by_id(tool_id)
        if not tool:
            return jsonify({'success': False, 'error': 'Tool not found'}), 404
        
        # Update options
        if 'options' not in tool:
            tool['options'] = {}
        
        tool['options'].update(data)
        tool['updated_at'] = datetime.now().isoformat()
        
        success = tools_manager.save(tool)
        
        if success:
            return jsonify({
                'success': True,
                'options': tool['options'],
                'message': 'Tool options updated successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to update tool options'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Task execution helper functions

def execute_ai_task(agent: dict, task_def: dict, inputs: dict) -> dict:
    """Execute an AI task using the agent's assistant"""
    # TODO: Implement AI task execution using OpenAI Assistant API
    # This will be integrated with the existing assistant implementation
    
    ai_config = task_def.get('ai_config', {})
    instructions = ai_config.get('instructions', '')
    
    # Placeholder implementation
    return {
        'type': 'ai_result',
        'content': f"AI task '{task_def['name']}' executed with instructions: {instructions}",
        'inputs_used': inputs,
        'timestamp': datetime.now().isoformat()
    }

def execute_tool_task(task_def: dict, inputs: dict) -> dict:
    """Execute a tool task"""
    tool_config = task_def.get('tool_config', {})
    tool_uuid = tool_config.get('tool_uuid')
    
    if not tool_uuid:
        raise ValueError("Tool UUID not specified in tool task")
    
    # Execute tool using existing implementation
    # Note: For now, simplified to non-async. In production, this should
    # properly integrate with the tools execution system
    result = {
        'success': True,
        'output': f"Tool {tool_uuid} executed successfully",
        'timestamp': datetime.now().isoformat()
    }
    
    return {
        'type': 'tool_result',
        'tool_result': result,
        'inputs_used': inputs,
        'timestamp': datetime.now().isoformat()
    }
