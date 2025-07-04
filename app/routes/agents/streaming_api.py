"""
Task Streaming Execution API
Handles real-time task execution with OpenAI Assistant integration
"""

from flask import request, jsonify, Response
from app.routes.agents import agents_bp
from app.utils.data_manager import agent_run_manager, agents_manager, tools_manager
from .api_utils import log_error, log_info
from app import csrf
from datetime import datetime
import time
import json
import requests
import threading

# Global locks for OpenAI thread management to prevent concurrent access
_thread_locks = {}
_thread_locks_lock = threading.Lock()

def get_thread_lock(thread_id):
    """Get or create a lock for a specific OpenAI thread"""
    with _thread_locks_lock:
        if thread_id not in _thread_locks:
            _thread_locks[thread_id] = threading.Lock()
        return _thread_locks[thread_id]


def force_cancel_all_active_runs(thread_id, headers):
    """Force cancel all active runs on a thread - last resort cleanup"""
    try:
        log_info(f"Force cancelling all active runs on thread {thread_id}")
        runs_response = requests.get(
            f'https://api.openai.com/v1/threads/{thread_id}/runs?limit=20',
            headers=headers,
            timeout=30
        )
        
        if runs_response.status_code == 200:
            runs_data = runs_response.json()
            active_runs = []
            
            for run in runs_data.get('data', []):
                if run.get('status') in ['queued', 'in_progress', 'requires_action']:
                    active_runs.append(run['id'])
            
            log_info(f"Found {len(active_runs)} active runs to cancel")
            
            # Cancel all active runs
            for run_id in active_runs:
                try:
                    cancel_response = requests.post(
                        f'https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}/cancel',
                        headers=headers,
                        timeout=30
                    )
                    log_info(f"Force cancelled run {run_id}: {cancel_response.status_code}")
                except Exception as e:
                    log_error(f"Failed to force cancel run {run_id}: {e}")
            
            # Wait a bit for cancellations to take effect
            if active_runs:
                time.sleep(5)
                
        return True
        
    except Exception as e:
        log_error(f"Error in force_cancel_all_active_runs: {e}")
        return False


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
        try:
            # Update task status to running
            agent_run_manager.set_task_status(run_uuid, task_uuid, 'running')
            
            # Generate initial HTML
            start_html = '<div class="task-execution-output">'
            yield f"data: {json.dumps({'type': 'html_chunk', 'content': start_html})}\n\n"
            
            # Only execute AI tasks with OpenAI Assistant
            if task_def.get('type') == 'ai':
                yield from _execute_ai_task(run_uuid, task_uuid, task_def, task_inputs, agent, request_method)
            else:
                yield from _execute_tool_task(run_uuid, task_uuid, task_def, task_inputs)
            
            # Close the main container
            end_html = '</div>'
            yield f"data: {json.dumps({'type': 'html_chunk', 'content': end_html})}\n\n"
            
            # Save task inputs
            agent_run_manager.set_task_inputs(run_uuid, task_uuid, task_inputs)
            
            # Signal completion
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
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


def _execute_ai_task(run_uuid, task_uuid, task_def, task_inputs, agent, request_method):
    """Execute AI task with OpenAI Assistant integration"""
    # Create or get user session for this task
    task_state = agent_run_manager.get_task_state(run_uuid, task_uuid)
    thread_id = task_state.get('user_session_id') if task_state else None
    
    # Acquire thread lock to prevent concurrent access to the same OpenAI thread
    if thread_id:
        thread_lock = get_thread_lock(thread_id)
        log_info(f"Acquiring lock for thread {thread_id}")
        if not thread_lock.acquire(timeout=30):  # 30 second timeout
            error_html = '<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: Thread is busy with another request. Please wait and try again.</div></div></div>'
            yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
            agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', 'Thread busy')
            return
        log_info(f"Acquired lock for thread {thread_id}")
    else:
        thread_lock = None
    
    try:
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
            log_info(f"Agent AI assistant tool: {ai_assistant_tool}")
            
            if ai_assistant_tool.startswith('tool:'):
                tool_id = ai_assistant_tool.replace('tool:', '')
                log_info(f"Loading tool with ID: {tool_id}")
                tool = tools_manager.load(tool_id)
                if tool:
                    tool_config = tool.get('config', {})
                    api_key = tool_config.get('openai_api_key')
                    log_info(f"API key found: {'Yes' if api_key and api_key != 'test-key-placeholder' else 'No'}")
                    
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
                yield from _create_openai_thread(api_key, run_uuid, task_uuid)
                # Get the thread ID after creation and acquire lock
                task_state = agent_run_manager.get_task_state(run_uuid, task_uuid)
                thread_id = task_state.get('user_session_id') if task_state else None
                if not thread_id:
                    return  # Error already handled in _create_openai_thread
                
                # Now we have a thread_id, acquire the lock
                thread_lock = get_thread_lock(thread_id)
                log_info(f"Acquiring lock for newly created thread {thread_id}")
                if not thread_lock.acquire(timeout=30):  # 30 second timeout
                    error_html = '<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: Unable to acquire lock for new thread. Please try again.</div></div></div>'
                    yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                    agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', 'Lock acquisition failed')
                    return
                log_info(f"Acquired lock for newly created thread {thread_id}")
            
            # Build and execute context prompt
            yield from _execute_openai_prompt(api_key, thread_id, assistant_id, task_def, task_inputs, agent, run_uuid, task_uuid)
            
        except Exception as ai_error:
            error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Exception: {str(ai_error)}</div></div></div>'
            yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
            agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', str(ai_error))
        
    finally:
        # Always release the thread lock if we acquired one
        if thread_lock:
            log_info(f"Releasing lock for thread {thread_id}")
            thread_lock.release()


def _create_openai_thread(api_key, run_uuid, task_uuid):
    """Create a new OpenAI thread for the task"""
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


def _execute_openai_prompt(api_key, thread_id, assistant_id, task_def, task_inputs, agent, run_uuid, task_uuid):
    """Execute the context prompt via OpenAI Assistant API"""
    # Build context prompt
    context_prompt = build_context_prompt(task_def, task_inputs, agent)
    
    # Display context prompt
    prompt_display_html = f'<div class="prompt-display mb-6"><h4 class="font-medium text-gray-700 mb-2">📋 Context Prompt</h4><div class="bg-gray-50 p-4 rounded-lg border"><pre class="text-sm text-gray-800 whitespace-pre-wrap">{context_prompt}</pre></div></div>'
    yield f"data: {json.dumps({'type': 'html_chunk', 'content': prompt_display_html})}\n\n"
    
    # Add separator
    separator_html = '<hr class="my-6 border-gray-300">'
    yield f"data: {json.dumps({'type': 'html_chunk', 'content': separator_html})}\n\n"
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v2'
        }
        
        # Critical section: Check for active runs and cancel if needed (within the thread lock)
        # This ensures only one request per thread can perform this operation at a time
        active_run_id = None
        runs_response = requests.get(
            f'https://api.openai.com/v1/threads/{thread_id}/runs?limit=5',
            headers=headers,
            timeout=30
        )
        
        if runs_response.status_code == 200:
            runs_data = runs_response.json()
            for run in runs_data.get('data', []):
                if run.get('status') in ['queued', 'in_progress', 'requires_action']:
                    active_run_id = run['id']
                    log_info(f"Found active run: {active_run_id} with status: {run.get('status')}")
                    break
        
        # If there's an active run, cancel it and wait for cancellation
        if active_run_id:
            log_info(f"Cancelling active run: {active_run_id}")
            cancel_response = requests.post(
                f'https://api.openai.com/v1/threads/{thread_id}/runs/{active_run_id}/cancel',
                headers=headers,
                timeout=30
            )
            log_info(f"Cancel response: {cancel_response.status_code}")
            
            # Wait for cancellation to complete with simpler logic
            max_wait_time = 60  # 60 seconds maximum wait
            wait_interval = 2   # Check every 2 seconds
            waited_time = 0
            
            while waited_time < max_wait_time:
                time.sleep(wait_interval)
                waited_time += wait_interval
                
                status_response = requests.get(
                    f'https://api.openai.com/v1/threads/{thread_id}/runs/{active_run_id}',
                    headers=headers,
                    timeout=30
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    current_status = status_data.get('status')
                    log_info(f"Cancel wait {waited_time}s: Run status is {current_status}")
                    
                    if current_status in ['cancelled', 'failed', 'completed', 'expired']:
                        log_info(f"Run successfully cancelled/completed: {current_status}")
                        break
                else:
                    log_error(f"Failed to check run status: {status_response.status_code}")
            else:
                # Timeout waiting for cancellation
                error_msg = f"Timeout waiting for run {active_run_id} to cancel after {max_wait_time} seconds"
                log_error(error_msg)
                error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: {error_msg}<br>Please wait a few minutes and try again.</div></div></div>'
                yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', error_msg)
                return
        
        # Add message to thread
        log_info(f"Adding message to thread {thread_id}")
        message_response = requests.post(
            f'https://api.openai.com/v1/threads/{thread_id}/messages',
            headers=headers,
            json={"role": "user", "content": context_prompt},
            timeout=30
        )
        
        if message_response.status_code != 200:
            error_msg = f"Failed to add message: {message_response.status_code} - {message_response.text}"
            log_error(error_msg)
            error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: {error_msg}</div></div></div>'
            yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
            agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', error_msg)
            return
        
        log_info("Message added successfully, creating new run")
        # Create new run
        run_response = requests.post(
            f'https://api.openai.com/v1/threads/{thread_id}/runs',
            headers=headers,
            json={"assistant_id": assistant_id},
            timeout=30
        )
        
        if run_response.status_code != 200:
            error_msg = f"Failed to create run: {run_response.status_code} - {run_response.text}"
            log_error(error_msg)
            error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: {error_msg}</div></div></div>'
            yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
            agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', error_msg)
            return
        
        run_data = run_response.json()
        new_run_id = run_data['id']
        log_info(f"Created new run: {new_run_id}")
        
        # Poll for completion
        yield from _poll_openai_completion(headers, thread_id, new_run_id, task_def, context_prompt, assistant_id, run_uuid, task_uuid)
        
    except requests.RequestException as e:
        error_msg = f"Request error: {str(e)}"
        error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: {error_msg}</div></div></div>'
        yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
        agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', error_msg)


def _poll_openai_completion(headers, thread_id, run_id, task_def, context_prompt, assistant_id, run_uuid, task_uuid):
    """Poll OpenAI for completion and handle the response"""
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
                yield from _handle_completion(headers, thread_id, task_def, context_prompt, assistant_id, run_uuid, task_uuid)
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


def _handle_completion(headers, thread_id, task_def, context_prompt, assistant_id, run_uuid, task_uuid):
    """Handle successful completion of OpenAI Assistant run"""
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
        
        # Display result without extra formatting
        result_html = f'<div class="result-section mb-6"><h4 class="font-medium text-gray-700 mb-2">✨ AI Response</h4><div class="bg-white p-6 rounded-lg border">{rendered_content}</div></div>'
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
        
    else:
        error_msg = f"Failed to get messages: {messages_response.status_code}"
        error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: {error_msg}</div></div></div>'
        yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
        agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', error_msg)


def _execute_tool_task(run_uuid, task_uuid, task_def, task_inputs):
    """Execute tool task (simple completion)"""
    # For tool tasks, just mark as completed without additional output
    agent_run_manager.set_task_status(run_uuid, task_uuid, 'completed')


def build_context_prompt(task_def: dict, task_inputs: dict, agent: dict) -> str:
    """Build a context prompt from task definition, inputs, and agent data"""
    log_info(f"Building context prompt for task: {task_def.get('name', 'Unknown')}")
    log_info(f"Task inputs: {task_inputs}")
    log_info(f"Task definition keys: {list(task_def.keys())}")
    
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
    
    # Add task instructions from multiple possible locations
    ai_config = task_def.get('ai_config', {})
    
    # Check for instructions in multiple locations (priority order)
    instructions_sources = [
        ('ai_config.instructions', ai_config.get('instructions', '')),
        ('top-level instruction', task_def.get('instruction', '')),
        ('top-level instructions', task_def.get('instructions', '')),
        ('ai_config.instruction', ai_config.get('instruction', ''))
    ]
    
    task_instruction = ''
    instruction_source = 'none'
    for source, instruction in instructions_sources:
        if instruction and instruction.strip():
            task_instruction = instruction
            instruction_source = source
            break
    
    log_info(f"Task instruction found from {instruction_source}: {bool(task_instruction)}")
    if task_instruction:
        log_info(f"Original instruction: {task_instruction}")
        # Resolve {{variables}} in instruction with input values
        resolved_instruction = resolve_variables(task_instruction, task_inputs)
        log_info(f"Resolved instruction: {resolved_instruction}")
        prompt_parts.extend([
            "Task Instructions:",
            resolved_instruction,
            ""
        ])
    
    # Add task goals from multiple possible locations
    goals_sources = [
        ('ai_config.goals', ai_config.get('goals', [])),
        ('top-level goals', task_def.get('goals', []))
    ]
    
    task_goals = []
    goals_source = 'none'
    for source, goals in goals_sources:
        if goals:
            task_goals = goals if isinstance(goals, list) else [goals]
            goals_source = source
            break
    
    log_info(f"Task goals found from {goals_source}: {len(task_goals)} goals")
    if task_goals:
        prompt_parts.append("Goals:")
        for i, goal in enumerate(task_goals):
            log_info(f"Original goal {i}: {goal}")
            # Resolve variables in each goal
            resolved_goal = resolve_variables(str(goal), task_inputs)
            log_info(f"Resolved goal {i}: {resolved_goal}")
            prompt_parts.append(f"- {resolved_goal}")
        prompt_parts.append("")
    
    # Add AI configuration system prompt if available
    if ai_config.get('system_prompt'):
        log_info(f"System prompt found in ai_config: {bool(ai_config.get('system_prompt'))}")
        # Resolve variables in system prompt
        resolved_system_prompt = resolve_variables(ai_config['system_prompt'], task_inputs)
        prompt_parts.extend([
            "System Instructions:",
            resolved_system_prompt,
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
    output_rendering = output_config.get('rendering', '')
    
    if output_type or output_description or output_rendering:
        prompt_parts.append("Output Requirements:")
        if output_description:
            # Resolve variables in output description
            resolved_output_desc = resolve_variables(output_description, task_inputs)
            prompt_parts.append(f"- Description: {resolved_output_desc}")
        
        if output_type == 'html':
            prompt_parts.append("- Format: HTML")
        elif output_type == 'markdown':
            prompt_parts.append("- Format: Markdown")
        elif output_type == 'text':
            prompt_parts.append("- Format: Plain text")
        
        if output_rendering:
            # Resolve variables in output rendering instructions
            resolved_rendering = resolve_variables(output_rendering, task_inputs)
            prompt_parts.append(f"- Rendering: {resolved_rendering}")
        
        prompt_parts.append("")
    
    # Add knowledge base items if available
    knowledge_base = agent.get('knowledge_base', [])
    if knowledge_base:
        prompt_parts.append("Available Knowledge:")
        for item in knowledge_base[:5]:  # Limit to first 5 items
            item_title = item.get('title', 'Knowledge Item')
            item_content = item.get('content', '')[:200]
            # Resolve variables in knowledge base content
            resolved_title = resolve_variables(item_title, task_inputs)
            resolved_content = resolve_variables(item_content, task_inputs)
            prompt_parts.append(f"- {resolved_title}: {resolved_content}")
        prompt_parts.append("")
    
    # Add global variables from agent if available
    global_variables = agent.get('global_variables', {})
    if global_variables:
        prompt_parts.append("Global Variables:")
        for key, value in global_variables.items():
            prompt_parts.append(f"- {key}: {value}")
        prompt_parts.append("")
    
    prompt_parts.append("Please provide your response based on the above information.")
    
    final_prompt = "\n".join(filter(None, prompt_parts))
    log_info(f"Final prompt length: {len(final_prompt)} characters")
    return final_prompt


def resolve_variables(text: str, variables: dict) -> str:
    """Resolve {{variable}} placeholders in text with actual values"""
    if not text or not variables:
        log_info(f"resolve_variables: text={bool(text)}, variables={bool(variables)}")
        return text
    
    log_info(f"Resolving variables in text: '{text[:100]}...'")
    log_info(f"Available variables: {variables}")
    
    resolved_text = text
    for key, value in variables.items():
        # Replace {{key}} with the actual value
        placeholder = f"{{{{{key}}}}}"
        if placeholder in resolved_text:
            log_info(f"Replacing {placeholder} with '{value}'")
            resolved_text = resolved_text.replace(placeholder, str(value))
    
    log_info(f"Resolved text: '{resolved_text[:100]}...'")
    return resolved_text


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
