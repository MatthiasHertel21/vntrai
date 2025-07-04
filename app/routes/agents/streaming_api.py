"""
Task Streaming Execution API
Simplified Flask routes for real-time task execution
"""

from flask import request, jsonify, Response
from app.routes.agents import agents_bp
from app.utils.data_manager import agent_run_manager, agents_manager, tools_manager
from .api_utils import log_error, log_info
from app import csrf
import json

# Import modular components
from .task_executor import TaskExecutor
from .thread_management import get_thread_lock, force_cancel_all_active_runs


@agents_bp.route('/api/agent_run/<run_uuid>/task_execute/<task_uuid>/stream', methods=['GET', 'POST'])
@csrf.exempt
def api_stream_execute_task(run_uuid, task_uuid):
    """Stream execute a task with real-time HTML output and OpenAI Assistant integration"""
    
    # IMPORTANT: Extract all request data OUTSIDE the generator to avoid Flask context issues
    try:
        # Load agent run and validate
        agent_run = agent_run_manager.load(run_uuid)
        if not agent_run:
            return Response(
                f"data: {json.dumps({'error': 'Agent run not found'})}\n\n",
                mimetype='text/event-stream'
            )
        
        # Load agent and get task definition
        agent = agents_manager.load(agent_run['agent_uuid'])
        if not agent:
            return Response(
                f"data: {json.dumps({'error': 'Agent not found'})}\n\n",
                mimetype='text/event-stream'
            )
        
        # Find task definition
        task_def = None
        for task in agent.get('tasks', []):
            if task.get('uuid') == task_uuid:
                task_def = task
                break
        
        if not task_def:
            return Response(
                f"data: {json.dumps({'error': 'Task definition not found'})}\n\n",
                mimetype='text/event-stream'
            )
        
        # Get task inputs from request (support both GET and POST)
        try:
            if request.method == 'POST':
                request_data = request.get_json()
                task_inputs = request_data.get('inputs', {}) if request_data else {}
                log_info(f"POST method - task inputs from request: {task_inputs}")
            else:  # GET request
                # For EventSource GET requests, get inputs from task state or use empty dict
                task_state = agent_run_manager.get_task_state(run_uuid, task_uuid)
                task_inputs = task_state.get('inputs', {}) if task_state else {}
                log_info(f"GET method - task inputs from state: {task_inputs}")
        except Exception as e:
            log_error(f"Error getting task inputs: {str(e)}")
            task_inputs = {}
        
        # Store request method for use in generator
        request_method = request.method
        
    except Exception as e:
        log_error(f"Error in request preparation: {str(e)}")
        return Response(
            f"data: {json.dumps({'error': f'Request preparation failed: {str(e)}'})}\n\n",
            mimetype='text/event-stream'
        )
    
    def generate_task_execution_stream():
        """Generator function for streaming task execution"""
        try:
            # Create and execute task
            executor = TaskExecutor(run_uuid, task_uuid, task_def, task_inputs, agent, request_method)
            yield from executor.execute()
            
        except Exception as e:
            log_error(f"Error in task execution stream: {str(e)}")
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


@agents_bp.route('/api/agent_run/<run_uuid>/task_execute/<task_uuid>/stop', methods=['POST'])
@csrf.exempt
def api_stop_task_execution(run_uuid, task_uuid):
    """Stop/cancel the current task execution"""
    try:
        # Load agent run and validate
        agent_run = agent_run_manager.load(run_uuid)
        if not agent_run:
            return jsonify({'error': 'Agent run not found'}), 404
        
        # Load agent and get task definition
        agent = agents_manager.load(agent_run['agent_uuid'])
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        # Find task definition
        task_def = None
        for task in agent.get('tasks', []):
            if task.get('uuid') == task_uuid:
                task_def = task
                break
        
        if not task_def:
            return jsonify({'error': 'Task definition not found'}), 404
        
        # Only AI tasks use OpenAI threads that can be cancelled
        if task_def.get('type') != 'ai':
            return jsonify({'error': 'Only AI tasks can be stopped'}), 400
        
        # Get the task state to find the thread ID
        task_state = agent_run_manager.get_task_state(run_uuid, task_uuid)
        thread_id = task_state.get('user_session_id') if task_state else None
        
        if not thread_id:
            return jsonify({'error': 'No active session found for this task'}), 400
        
        # Get API key from the agent's AI assistant tool configuration
        ai_assistant_tool = agent.get('ai_assistant_tool', '')
        if ai_assistant_tool.startswith('tool:'):
            tool_id = ai_assistant_tool.replace('tool:', '')
            tool = tools_manager.load(tool_id)
            if tool:
                tool_config = tool.get('config', {})
                api_key = tool_config.get('openai_api_key')
                
                if not api_key or api_key == 'test-key-placeholder':
                    return jsonify({'error': 'No valid OpenAI API key found'}), 400
            else:
                return jsonify({'error': 'AI assistant tool not found'}), 400
        else:
            return jsonify({'error': 'No AI assistant tool configured'}), 400
        
        # Prepare headers for OpenAI API
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v2'
        }
        
        # Acquire thread lock to prevent race conditions
        thread_lock = get_thread_lock(thread_id)
        if not thread_lock.acquire(timeout=10):  # 10 second timeout for stop operation
            return jsonify({'error': 'Cannot stop task - thread is busy'}), 409
        
        try:
            # Force cancel all active runs on the thread
            success = force_cancel_all_active_runs(thread_id, headers)
            
            if success:
                # Update task status to cancelled
                agent_run_manager.set_task_status(run_uuid, task_uuid, 'cancelled', 'Task stopped by user')
                log_info(f"Successfully stopped task {task_uuid} in run {run_uuid}")
                
                return jsonify({
                    'success': True,
                    'message': 'Task execution stopped successfully'
                })
            else:
                return jsonify({'error': 'Failed to stop task execution'}), 500
                
        finally:
            thread_lock.release()
            log_info(f"Released lock for thread {thread_id}")
    
    except Exception as e:
        log_error(f"Error stopping task execution: {str(e)}")
        return jsonify({'error': f'Failed to stop task: {str(e)}'}), 500
