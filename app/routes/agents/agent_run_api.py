"""
Agent Run Management API Routes - Part 1
Handles task input management and basic agent run operations
"""

from flask import request, jsonify, current_app
from app.routes.agents import agents_bp
from app.utils.data_manager import agent_run_manager, agents_manager
from .api_utils import (validate_json_request, success_response, error_response, 
                        get_agent_or_404, current_timestamp, log_error, log_info)
from app import csrf
from datetime import datetime
from .prompt_builder import build_context_prompt


@agents_bp.route('/api/agent_run/<run_uuid>/task_input/<task_uuid>', methods=['POST'])
@csrf.exempt
def api_save_task_input(run_uuid, task_uuid):
    """Save task input values for an agent run task"""
    try:
        # Debug: Log incoming request details
        log_info(f"API save_task_input called with run_uuid={run_uuid}, task_uuid={task_uuid}")
        log_info(f"Request content type: {request.content_type}")
        log_info(f"Request data: {request.data}")
        
        data = request.get_json()
        log_info(f"Parsed JSON data: {data}")
        
        inputs = data.get('inputs', {}) if data else {}
        log_info(f"Extracted inputs: {inputs}")
        
        # Validate that the agent run exists
        agent_run = agent_run_manager.load(run_uuid)
        if not agent_run:
            log_error(f"Agent run not found: {run_uuid}")
            return error_response('Agent run not found', 404)
        
        log_info(f"Agent run found, has task_states: {'task_states' in agent_run}")
        
        # Save the task inputs
        success = agent_run_manager.set_task_inputs(run_uuid, task_uuid, inputs)
        log_info(f"set_task_inputs result: {success}")
        
        if success:
            return success_response('Task inputs saved successfully')
        else:
            log_error(f"Failed to save task inputs for run {run_uuid}, task {task_uuid}")
            return error_response('Failed to save task inputs', 500)
            
    except Exception as e:
        log_error(f"Error saving task inputs: {str(e)}")
        return error_response(str(e), 500)


@agents_bp.route('/api/agent_run/<run_uuid>/selected_task', methods=['POST'])
@csrf.exempt
def api_save_selected_task(run_uuid):
    """Save the currently selected task for an agent run"""
    try:
        data = request.get_json()
        task_index = data.get('task_index') if data else None
        
        if task_index is None:
            return error_response('Missing task_index')
        
        # Validate that the agent run exists
        agent_run = agent_run_manager.load(run_uuid)
        if not agent_run:
            return error_response('Agent run not found', 404)
        
        # Save selected task index in agent run metadata
        agent_run['selected_task_index'] = task_index
        agent_run['updated_at'] = current_timestamp()
        
        success = agent_run_manager.save(agent_run)
        
        if success:
            return success_response('Selected task saved successfully')
        else:
            return error_response('Failed to save selected task', 500)
            
    except Exception as e:
        log_error(f"Error saving selected task: {str(e)}")
        return error_response(str(e), 500)


@agents_bp.route('/api/agent_run/<run_uuid>/selected_task', methods=['GET'])
@csrf.exempt
def api_get_selected_task(run_uuid):
    """Get the currently selected task for an agent run"""
    try:
        # Load the agent run
        agent_run = agent_run_manager.load(run_uuid)
        if not agent_run:
            return error_response('Agent run not found', 404)
        
        selected_task_index = agent_run.get('selected_task_index', 0)
        
        return jsonify({
            'success': True,
            'selected_task_index': selected_task_index
        })
            
    except Exception as e:
        log_error(f"Error getting selected task: {str(e)}")
        return error_response(str(e), 500)


@agents_bp.route('/api/agent_run/<run_uuid>/task/<task_uuid>/prompt', methods=['GET', 'POST'])
@csrf.exempt
def api_get_task_prompt(run_uuid, task_uuid):
    """Get the context prompt for a specific task in an agent run"""
    try:
        # Load agent run and validate
        agent_run = agent_run_manager.load(run_uuid)
        if not agent_run:
            return error_response('Agent run not found', 404)
        
        # Load agent
        agent = agents_manager.load(agent_run['agent_uuid'])
        if not agent:
            return error_response('Agent not found', 404)
        
        # Find task definition
        task_def = None
        for task in agent.get('tasks', []):
            if task.get('uuid') == task_uuid:
                task_def = task
                break
        
        if not task_def:
            return error_response('Task definition not found', 404)
        
        # Get task inputs - try from request data first, then from saved state
        task_inputs = {}
        if request.method == 'POST':
            data = request.get_json()
            task_inputs = data.get('inputs', {}) if data else {}
        
        # If no inputs from request, try to get saved inputs
        if not task_inputs:
            task_states = agent_run.get('task_states', {})
            task_state = task_states.get(task_uuid, {})
            task_inputs = task_state.get('inputs', {})
        
        log_info(f"Building prompt for task {task_uuid} with inputs: {task_inputs}")
        
        # Build the context prompt using the same logic as task execution
        context_prompt = build_context_prompt(task_def, task_inputs, agent, agent_run)
        
        return jsonify({
            'success': True,
            'prompt': context_prompt,
            'task_name': task_def.get('name', 'Unnamed Task'),
            'task_uuid': task_uuid
        })
            
    except Exception as e:
        log_error(f"Error getting task prompt: {str(e)}")
        return error_response(str(e), 500)


@agents_bp.route('/api/agent_run/<run_uuid>/language', methods=['POST'])
@csrf.exempt
def api_set_language_preference(run_uuid):
    """Set language preference for an agent run"""
    try:
        data = request.get_json()
        language = data.get('language', 'auto') if data else 'auto'
        
        # Validate that the agent run exists
        agent_run = agent_run_manager.load(run_uuid)
        if not agent_run:
            return error_response('Agent run not found', 404)
        
        # Set the language preference
        success = agent_run_manager.set_language_preference(run_uuid, language)
        
        if success:
            return success_response('Language preference saved successfully')
        else:
            return error_response('Failed to save language preference', 500)
            
    except Exception as e:
        log_error(f"Error setting language preference: {e}")
        return error_response(f'Failed to set language preference: {str(e)}', 500)


@agents_bp.route('/api/agent_run/<run_uuid>/language', methods=['GET'])
def api_get_language_preference(run_uuid):
    """Get language preference for an agent run"""
    try:
        # Validate that the agent run exists
        agent_run = agent_run_manager.load(run_uuid)
        if not agent_run:
            return error_response('Agent run not found', 404)
        
        # Get the language preference
        language = agent_run_manager.get_language_preference(run_uuid)
        
        return jsonify({
            'success': True,
            'language': language
        })
            
    except Exception as e:
        log_error(f"Error getting language preference: {e}")
        return error_response(f'Failed to get language preference: {str(e)}', 500)
