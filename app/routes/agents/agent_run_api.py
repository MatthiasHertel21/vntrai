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
