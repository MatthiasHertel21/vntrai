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


@agents_bp.route('/api/agent_run/<run_uuid>/task_execute/<task_uuid>/stream', methods=['GET', 'POST'])
@csrf.exempt
def api_stream_execute_task(run_uuid, task_uuid):
    """Stream execute a task with real-time HTML output and OpenAI Assistant integration"""
    
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
                yield from _execute_ai_task(run_uuid, task_uuid, task_def, task_inputs, agent)
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


def _execute_ai_task(run_uuid, task_uuid, task_def, task_inputs, agent):
    """Execute AI task with OpenAI Assistant integration"""
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
            # Get the thread ID after creation
            task_state = agent_run_manager.get_task_state(run_uuid, task_uuid)
            thread_id = task_state.get('user_session_id') if task_state else None
            if not thread_id:
                return  # Error already handled in _create_openai_thread
        else:
            session_html = f'<div class="session-section mb-6"><h4 class="font-medium text-gray-700 mb-2">🔄 Using Existing Session</h4><div class="bg-blue-50 p-4 rounded-lg"><div class="text-blue-700">Thread ID: <code>{thread_id}</code></div></div></div>'
            yield f"data: {json.dumps({'type': 'html_chunk', 'content': session_html})}\n\n"
        
        # Build and execute context prompt
        yield from _execute_openai_prompt(api_key, thread_id, assistant_id, task_def, task_inputs, agent, run_uuid, task_uuid)
        
    except Exception as ai_error:
        error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Exception: {str(ai_error)}</div></div></div>'
        yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
        agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', str(ai_error))


def _create_openai_thread(api_key, run_uuid, task_uuid):
    """Create a new OpenAI thread for the task"""
    session_html = '<div class="session-section mb-6"><h4 class="font-medium text-gray-700 mb-2">🔄 Creating User Session</h4><div class="bg-blue-50 p-4 rounded-lg"><div class="text-blue-700">Creating new conversation thread...</div></div></div>'
    yield f"data: {json.dumps({'type': 'html_chunk', 'content': session_html})}\n\n"
    time.sleep(0.3)
    
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


def _execute_openai_prompt(api_key, thread_id, assistant_id, task_def, task_inputs, agent, run_uuid, task_uuid):
    """Execute the context prompt via OpenAI Assistant API"""
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
        yield from _poll_openai_completion(headers, thread_id, run_id, task_def, context_prompt, assistant_id, run_uuid, task_uuid)
        
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
        
    else:
        error_msg = f"Failed to get messages: {messages_response.status_code}"
        error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: {error_msg}</div></div></div>'
        yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
        agent_run_manager.set_task_status(run_uuid, task_uuid, 'error', error_msg)


def _execute_tool_task(run_uuid, task_uuid, task_def, task_inputs):
    """Execute tool task (simulation)"""
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
